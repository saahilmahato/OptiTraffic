import numpy as np
import pygame
from typing import Tuple, Optional

VEHICLE_COLOR = (0, 0, 255)
VEHICLE_LENGTH = 10
VEHICLE_WIDTH = 5
DIRECTION_TOLERANCE = 0.1  # For fuzzy direction matching


class Vehicle:
    """
    Represents a single vehicle in the simulation.
    """

    def __init__(
        self,
        position: Tuple[float, float],
        direction: Tuple[float, float],
    ) -> None:
        """
        Initialize a vehicle with position, direction, and speed.

        Args:
            position (tuple): (x, y) position.
            direction (tuple): Normalized direction vector (dx, dy).
        """
        self.position = np.array(position, dtype=float)
        self.direction = np.array(direction, dtype=float)
        self.moving = True
        self.distance_to_light = 300
        self.wait_time: float = 0.0
        self.stop_start_time: Optional[float] = None

    def update(self, speed: float, dt: float) -> None:
        """
        Update vehicle position based on time delta.

        Args:
            speed(float): Speed of the vehicle
            dt (float): Time delta in seconds.
        """
        self.moving = speed > 0
        self.position += self.direction * speed * dt

    def rect(self) -> pygame.Rect:
        """
        Get the vehicle's rectangle for rendering.

        Returns:
            pygame.Rect: Rectangle representing the vehicle.
        """
        x, y = self.position
        horizontal = abs(self.direction[0]) > abs(self.direction[1])
        w, h = (
            (VEHICLE_LENGTH, VEHICLE_WIDTH)
            if horizontal
            else (VEHICLE_WIDTH, VEHICLE_LENGTH)
        )
        return pygame.Rect(x - w / 2, y - h / 2, w, h)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Draw the vehicle on the screen.

        Args:
            screen (pygame.Surface): The Pygame surface to draw on.
        """
        pygame.draw.rect(screen, VEHICLE_COLOR, self.rect())

    def get_direction_label(self) -> str:
        """
        Get cardinal direction (N, S, E, W) based on movement vector.

        Returns:
            str: Direction as 'N', 'S', 'E', or 'W'. Empty if direction is diagonal or invalid.
        """
        dx, dy = self.direction
        if abs(dx) > abs(dy):
            if dx > DIRECTION_TOLERANCE:
                return "E"
            elif dx < -DIRECTION_TOLERANCE:
                return "W"
        else:
            if dy > DIRECTION_TOLERANCE:
                return "S"
            elif dy < -DIRECTION_TOLERANCE:
                return "N"
        return ""

    def get_state(self) -> bool:
        """
        Get vehicle movement state.

        Returns:
            bool: True if the vehicle is moving else False
        """
        return self.moving

    def update_light_distance(self, distance: float) -> None:
        """
        Updates the distance of the vehicle to its approaching light.

        Args:
            distance (float): The Euclidean distance between the vehicle and light

        """
        self.distance_to_light = distance
