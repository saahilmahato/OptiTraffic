import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque, namedtuple
from typing import List, Any
from src.simulation.traffic_light import LightState
from src.simulation.traffic_light_controller.base_controller import (
    BaseTrafficLightController,
)

# Transition tuple for replay
Transition = namedtuple(
    "Transition", ("state", "action", "reward", "next_state", "done")
)


class DQNAgent:
    def __init__(self, input_dim: int, lr: float = 1e-3, gamma: float = 0.99):
        # Set device to GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(self.device)

        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, len(LightState)),
        ).to(self.device)

        # Target network copy
        self.target_net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, len(LightState)),
        ).to(self.device)
        self.target_net.load_state_dict(self.net.state_dict())

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
            state_tensor = torch.FloatTensor(state_vec).to(self.device)
            q = self.net(state_tensor)
            return int(q.argmax().item())

    def store(self, *args: Any) -> None:
        self.memory.append(Transition(*args))

    def update(self) -> float | None:
        if len(self.memory) < self.batch_size:
            return None
        batch = random.sample(self.memory, self.batch_size)
        states = torch.FloatTensor([t.state for t in batch]).to(self.device)
        actions = torch.LongTensor([t.action for t in batch]).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor([t.reward for t in batch]).to(self.device)
        next_states = torch.FloatTensor([t.next_state for t in batch]).to(self.device)
        dones = torch.FloatTensor([t.done for t in batch]).to(self.device)

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
        obs_dim = self.n_agents * 20  # Global state dimension
        self.agents = [DQNAgent(input_dim=obs_dim) for _ in traffic_lights]
        self.time_in_state = [0.0] * self.n_agents
        self.prev_action = [0] * self.n_agents
        self.min_dur = 1.0
        self.max_dur = 10.0

        self.logger = self._init_logger()
        self.tick = 0

    def _init_logger(self):
        import logging

        logger = logging.getLogger("MARLController")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            ch = logging.StreamHandler()
            fmt = logging.Formatter("%(asctime)s %(message)s")
            ch.setFormatter(fmt)
            logger.addHandler(ch)
        return logger

    def _build_global_state(self) -> List[float]:
        global_states = []
        for light in self.traffic_lights:
            lx, ly = light.position
            counts = [len(light.approaching[d]) for d in ["N", "S", "E", "W"]]
            dists = [
                sum(v.distance_to_light for v in light.approaching[d])
                / max(1, len(light.approaching[d]))
                for d in ["N", "S", "E", "W"]
            ]
            moving = [
                sum(1 for v in light.approaching[d] if v.get_state())
                / max(1, len(light.approaching[d]))
                for d in ["N", "S", "E", "W"]
            ]
            spatial = self._compute_spatial_features(lx, ly, light)
            global_states += counts + dists + moving + spatial
        return global_states

    def _compute_spatial_features(
        self, lx: float, ly: float, light: Any
    ) -> List[float]:
        spatial = []
        for d in ["N", "S", "E", "W"]:
            dir_list = light.approaching[d]
            avg_dx = (
                sum(v.position[0] - lx for v in dir_list) / len(dir_list)
                if dir_list
                else 0.0
            )
            avg_dy = (
                sum(v.position[1] - ly for v in dir_list) / len(dir_list)
                if dir_list
                else 0.0
            )
            spatial += [avg_dx, avg_dy]
        return spatial

    def _select_traffic_light_action(self, idx: int, state: List[float]) -> int:
        proposed = self.agents[idx].select_action(state)
        time_in_state = self.time_in_state[idx]
        if time_in_state < self.min_dur:
            return self.prev_action[idx]
        elif time_in_state >= self.max_dur:
            return self._force_action_change(idx, state)
        return proposed

    def _force_action_change(self, idx: int, state: List[float]) -> int:
        state_tensor = torch.FloatTensor(state).to(self.agents[idx].device)
        q_vals = self.agents[idx].net(state_tensor)
        sorted_actions = torch.argsort(q_vals, descending=True).tolist()
        return next(a for a in sorted_actions if a != self.prev_action[idx])

    def _calculate_reward(self, light: Any, new_state_enum: LightState) -> float:
        moved = sum(
            1
            for d, dir_list in light.approaching.items()
            for v in dir_list
            if (
                (new_state_enum == LightState.GREEN and d in ["E", "W"])
                or (new_state_enum == LightState.RED and d in ["N", "S"])
            )
            and v.get_state()
        )
        queue_penalty = 0.1 * sum(
            len(light.approaching[d]) for d in ["N", "S", "E", "W"]
        )
        stopped_count = sum(
            1
            for d in ["N", "S", "E", "W"]
            for v in light.approaching[d]
            if not v.get_state()
        )
        stopped_penalty = 0.2 * stopped_count
        return moved - queue_penalty - stopped_penalty

    def update(self, dt: float) -> None:
        # Get current global state BEFORE any actions
        current_global_state = self._build_global_state()

        # Collect actions for all agents
        actions = []
        states_for_agents = []
        
        for idx, light in enumerate(self.traffic_lights):
            self.time_in_state[idx] += dt
            state = current_global_state.copy()
            
            # Select action for this agent
            action = self._select_traffic_light_action(idx, state)
            
            actions.append(action)
            states_for_agents.append(state)
        
        # Apply all actions simultaneously
        for idx, (light, action) in enumerate(zip(self.traffic_lights, actions)):
            new_state_enum = list(LightState)[action]
            light.update(new_state_enum)
            
            # Reset time_in_state if action changed
            if action != self.prev_action[idx]:
                self.prev_action[idx] = action
                self.time_in_state[idx] = 0.0
        
        # Get next global state AFTER all actions have been applied
        next_global_state = self._build_global_state()
        
        # Calculate rewards and store transitions
        for idx, (light, action, state) in enumerate(zip(self.traffic_lights, actions, states_for_agents)):
            new_state_enum = list(LightState)[action]
            
            # Calculate reward based on the resulting state
            reward = self._calculate_reward(light, new_state_enum)
            
            # Store transition with correct next_state
            next_state = next_global_state.copy()
            done = False
            self.agents[idx].store(state, action, reward, next_state, done)
            
            # Update agent
            loss = self.agents[idx].update()
            
            # Log information
            if loss is not None:
                self.logger.info(
                    f"Agent {idx}: action={new_state_enum.name}, time={round(self.time_in_state[idx], 2)}, "
                    f"reward={round(reward, 2)}, loss={round(loss, 4)}, epsilon={round(self.agents[idx].epsilon, 3)}"
                )
            else:
                self.logger.info(
                    f"Agent {idx}: action={new_state_enum.name}, time={round(self.time_in_state[idx], 2)}, "
                    f"reward={round(reward, 2)}, epsilon={round(self.agents[idx].epsilon, 3)}"
                )
        
        # Update target networks periodically
        self.tick += 1
        if self.tick % 100 == 0:
            for agent in self.agents:
                agent.target_net.load_state_dict(agent.net.state_dict())
