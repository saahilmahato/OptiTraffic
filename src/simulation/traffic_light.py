import pygame
from enum import Enum
from typing import Optional
from src.simulation.vehicle import Vehicle


class LightState(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)


class TrafficLight:
    """
    Represents a traffic light that tracks vehicles approaching from four cardinal directions.
    """

    def __init__(
        self, position: tuple[int, int], light_id: Optional[str] = None
    ) -> None:
        """
        Initialize the traffic light.

        Args:
            position (tuple): (x, y) screen position.
            light_id (Optional[str]): Optional identifier for the light.
        """
        self.position = position
        self.light_id = light_id
        self.state = LightState.RED
        self.approaching: dict[str, list[Vehicle]] = {
            "N": [],
            "S": [],
            "E": [],
            "W": [],
        }
        self.font = pygame.font.SysFont(None, 24)

    def update(self, state: LightState) -> None:
        """
        Update the current light state.

        Args:
            state (LightState): The new state (RED, GREEN, YELLOW).
        """
        self.state = state

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the traffic light and vehicle count.

        Args:
            surface (pygame.Surface): The surface to draw on.
        """
        x, y = self.position
        radius = 10
        pygame.draw.circle(surface, self.state.value, (x, y), radius)

        vehicle_count = sum(len(vlist) for vlist in self.approaching.values())
        text_surface = self.font.render(str(vehicle_count), True, (0, 0, 0))
        surface.blit(text_surface, (x - radius // 2, y - radius // 2))

    def get_state(self) -> LightState:
        """
        Get the current light state.

        Returns:
            LightState: Current state.
        """
        return self.state

    def clear_approaching_vehicles(self) -> None:
        """
        Clear all tracked approaching vehicles.
        """
        for direction in self.approaching:
            self.approaching[direction].clear()

    def add_approaching_vehicle(self, vehicle: Vehicle) -> None:
        """
        Add a vehicle to the appropriate direction list based on its movement.

        Args:
            vehicle (Vehicle): The approaching vehicle.

        Raises:
            ValueError: If vehicle direction is not valid.
        """
        dir_map = {
            (0, 1): "N",
            (0, -1): "S",
            (1, 0): "E",
            (-1, 0): "W",
        }

        direction_key = tuple(int(d) for d in vehicle.direction)

        if direction_key in dir_map:
            self.approaching[dir_map[direction_key]].append(vehicle)
        else:
            raise ValueError(f"Invalid vehicle direction: {vehicle.direction}")

    def get_approaching_vehicles(self):
        """
        Return a flat list of all vehicles approaching from any direction.

        Returns:
            list: All approaching vehicles combined from N, S, E, and W.
        """
        vehicles = []
        for direction in self.approaching.values():
            vehicles.extend(direction)
        return vehicles
