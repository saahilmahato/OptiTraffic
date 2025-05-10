import random
from src.simulation.vehicle import Vehicle


class Spawner:
    def __init__(self, config, world):
        self.spawn_points = config.get("spawn", {}).get("points", [])
        self.world = world
        self.spawn_interval = config.get("spawn", {}).get("interval", 0.5)
        self.time_since_last_spawn = 0.0

    def spawn(self, dt):
        if not self.spawn_points:
            return

        self.time_since_last_spawn += dt

        if self.time_since_last_spawn >= self.spawn_interval:
            spawn_data = random.choice(self.spawn_points)
            pos = spawn_data["pos"]
            direction = spawn_data["direction"]
            vehicle = Vehicle(pos, direction)
            self.world.vehicles.append(vehicle)
            self.time_since_last_spawn = 0.0
