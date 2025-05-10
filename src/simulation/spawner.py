import random
from typing import Any

from src.simulation.vehicle import Vehicle
from src.simulation.world import World


class Spawner:
    """
    Handles vehicle spawning based on configured spawn points and timing.
    """

    def __init__(self, config: dict[str, Any], world: World) -> None:
        """
        Initialize the Spawner.

        Args:
            config (dict): Configuration dictionary loaded from YAML.
            world (World): The simulation world to add vehicles to.
        """
        spawn_config = config.get("spawn", {})
        self.spawn_points = spawn_config.get("points", [])
        self.spawn_interval = spawn_config.get("interval", 0.5)
        self.time_since_last_spawn = 0.0
        self.world = world

    def spawn(self, dt: float) -> None:
        """
        Attempt to spawn a vehicle if the interval has elapsed.

        Args:
            dt (float): Time delta since last frame, in seconds.
        """
        if not self.spawn_points:
            return

        self.time_since_last_spawn += dt

        if self.time_since_last_spawn >= self.spawn_interval:
            self._spawn_vehicle()
            self.time_since_last_spawn = 0.0

    def _spawn_vehicle(self) -> None:
        """
        Spawn a single vehicle at a random spawn point.
        """
        spawn_data = random.choice(self.spawn_points)  # Controlled chaos

        pos = spawn_data.get("pos")
        direction = spawn_data.get("direction")

        if pos is None or direction is None:
            return  # Skip malformed entries silently

        vehicle = Vehicle(pos, direction)
        self.world.vehicles.append(vehicle)
