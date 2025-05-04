import numpy as np
from src.simulation.vehicle import Vehicle

class Spawner:
    def __init__(self, config, world):
        self.world = world
        self.rates = config['spawning']
        self.fps = config['fps']

        # road layout from config
        self.num_roads = config['roads']
        self.road_width = config.get('road_width', 100)
        # lane offset: half of half the road width = quarter road width
        self.lane_offset = self.road_width / 4

        # precompute road center positions
        w, h = world.width, world.height
        # x-centers of vertical roads
        self.road_centers_x = [i * w / (self.num_roads + 1) for i in range(1, self.num_roads + 1)]
        # y-centers of horizontal roads
        self.road_centers_y = [j * h / (self.num_roads + 1) for j in range(1, self.num_roads + 1)]
    
    def spawn(self):
        dt = 1 / self.fps
        for edge, rate in self.rates.items():
            lam = rate * dt
            n = np.random.poisson(lam)
            for _ in range(n):
                pos, direction = self._get_spawn(edge)
                veh = Vehicle(pos, direction)
                self.world.add_vehicle(veh)

    def _get_spawn(self, edge):
        w, h = self.world.width, self.world.height
        # choose a random road index
        if edge in ('top', 'bottom'):
            # select a vertical road
            x_center = float(np.random.choice(self.road_centers_x))
            # offset into left lane relative to travel direction
            if edge == 'top':
                # moving down, left lane is to vehicle's left -> screen +x
                x_spawn = x_center + self.lane_offset
                y_spawn = 0
                direction = [0, 1]
            else:
                # 'bottom', moving up, left lane -> screen -x
                x_spawn = x_center - self.lane_offset
                y_spawn = h
                direction = [0, -1]
            return [x_spawn, y_spawn], direction

        if edge in ('left', 'right'):
            # select a horizontal road
            y_center = float(np.random.choice(self.road_centers_y))
            if edge == 'left':
                # moving right, left lane -> screen -y
                x_spawn = 0
                y_spawn = y_center - self.lane_offset
                direction = [1, 0]
            else:
                # 'right', moving left, left lane -> screen +y
                x_spawn = w
                y_spawn = y_center + self.lane_offset
                direction = [-1, 0]
            return [x_spawn, y_spawn], direction

        # fallback
        return [0, 0], [0, 0]
