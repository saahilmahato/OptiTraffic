import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque, namedtuple
from typing import List, Any
from src.simulation.traffic_light import LightState
from src.simulation.traffic_light_controller.base_controller import BaseTrafficLightController

# Transition tuple for replay
global Transition
Transition = namedtuple('Transition', ('state', 'action', 'reward', 'next_state', 'done'))

class DQNAgent:
    def __init__(self, input_dim: int, lr: float = 1e-3, gamma: float = 0.99):
        # Improved network: two hidden layers, more neurons
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, len(LightState))
        )
        # target network copy
        self.target_net = nn.Sequential(*[layer for layer in self.net])
        self.optimizer = optim.Adam(self.net.parameters(), lr=lr, weight_decay=0)
        self.gamma = gamma
        self.epsilon = 1.0
        self.eps_min = 0.05
        self.eps_decay = 1e-4
        self.memory = deque(maxlen=10000)
        self.batch_size = 64

    def select_action(self, state_vec: List[float]) -> int:
        if random.random() < self.epsilon:
            return random.randrange(len(LightState))
        with torch.no_grad():
            q = self.net(torch.FloatTensor(state_vec))
            return int(q.argmax().item())

    def store(self, *args: Any) -> None:
        self.memory.append(Transition(*args))

    def update(self) -> float | None:
        if len(self.memory) < self.batch_size:
            return None
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([t.state for t in batch])
        actions = torch.LongTensor([t.action for t in batch]).unsqueeze(1)
        rewards = torch.FloatTensor([t.reward for t in batch])
        next_states = torch.FloatTensor([t.next_state for t in batch])
        dones = torch.FloatTensor([t.done for t in batch])

        q_values = self.net(states).gather(1, actions).squeeze()
        next_q = self.target_net(next_states).max(1)[0]
        target = rewards + self.gamma * next_q * (1 - dones)

        loss = nn.MSELoss()(q_values, target.detach())
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()

        # Epsilon decay
        self.epsilon = max(self.eps_min, self.epsilon - self.eps_decay)
        return loss.item()

class MARLTrafficLightController(BaseTrafficLightController):
    def __init__(self, traffic_lights: List[Any], config: dict):
        self.traffic_lights = traffic_lights
        self.n_agents = len(traffic_lights)
        # each agent obs: counts(4)+distances(4)+moving(4)+spatial(4*2)=20; global state dim
        obs_dim = self.n_agents * 20
        self.agents = [DQNAgent(input_dim=obs_dim) for _ in traffic_lights]
        # timing constraints per agent
        self.time_in_state = [0.0] * self.n_agents
        self.prev_action = [0] * self.n_agents
        self.min_dur = 1.0
        self.max_dur = 10.0

        self.logger = self._init_logger()
        self.tick = 0

    def _init_logger(self):
        import logging
        logger = logging.getLogger('MARLController')
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            ch = logging.StreamHandler()
            fmt = logging.Formatter('%(asctime)s %(message)s')
            ch.setFormatter(fmt)
            logger.addHandler(ch)
        return logger

    def update(self, dt: float) -> None:
        # build global state concatenation
        global_states: List[float] = []
        for light in self.traffic_lights:
            lx, ly = light.position
            counts = [len(light.approaching[d]) for d in ['N','S','E','W']]
            dists  = [sum(v.distance_to_light for v in light.approaching[d]) / max(1,len(light.approaching[d])) for d in ['N','S','E','W']]
            moving = [sum(1 for v in light.approaching[d] if v.get_state()) / max(1,len(light.approaching[d])) for d in ['N','S','E','W']]
            # spatial features: avg relative x and y offsets per direction
            spatial = []
            for d in ['N','S','E','W']:
                dir_list = light.approaching[d]
                if dir_list:
                    avg_dx = sum(v.position[0] - lx for v in dir_list) / len(dir_list)
                    avg_dy = sum(v.position[1] - ly for v in dir_list) / len(dir_list)
                else:
                    avg_dx = avg_dy = 0.0
                spatial += [avg_dx, avg_dy]
            global_states += counts + dists + moving + spatial

        for idx, light in enumerate(self.traffic_lights):
            self.time_in_state[idx] += dt
            state = global_states.copy()

            # propose action
            proposed = self.agents[idx].select_action(state)
            # enforce min/max durations
            if self.time_in_state[idx] < self.min_dur:
                action = self.prev_action[idx]
            elif self.time_in_state[idx] >= self.max_dur:
                # force change to highest Q != prev
                q_vals = self.agents[idx].net(torch.FloatTensor(state))
                sorted_actions = torch.argsort(q_vals, descending=True).tolist()
                action = next(a for a in sorted_actions if a != self.prev_action[idx])
            else:
                action = proposed

            new_state_enum = list(LightState)[action]
            light.update(new_state_enum)

            if action != self.prev_action[idx]:
                self.prev_action[idx] = action
                self.time_in_state[idx] = 0.0

            # reward: moved vehicles minus queue penalty and stopped penalty
            moved = sum(1 for d, dir_list in light.approaching.items()
                        for v in dir_list
                        if ((new_state_enum == LightState.GREEN and d in ['E','W']) or
                            (new_state_enum == LightState.RED   and d in ['N','S']))
                        and v.get_state())
            queue_penalty = 0.1 * sum(len(light.approaching[d]) for d in ['N','S','E','W'])
            # stopped vehicles penalty: heavier
            stopped_count = sum(1 for d in ['N','S','E','W'] for v in light.approaching[d] if not v.get_state())
            stopped_penalty = 0.2 * stopped_count
            reward = moved - queue_penalty - stopped_penalty
            done = False

            # learning
            next_state = state
            loss = self.agents[idx].update()
            self.agents[idx].store(state, action, reward, next_state, done)

            # log
            self.logger.info(
                f"Agent {idx}: action={new_state_enum.name}, time={round(self.time_in_state[idx],2)}, "
                f"moved={moved}, stopped={stopped_count}, reward={round(reward,2)}, loss={loss}"
            )

        self.tick += 1
        if self.tick % 100 == 0:
            for agent in self.agents:
                agent.target_net.load_state_dict(agent.net.state_dict())
