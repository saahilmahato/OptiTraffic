import pygame
from enum import Enum

class LightState(Enum):
    RED = 0
    GREEN = 1
    YELLOW = 2

class TrafficLight:
    """
    Simple traffic light with red, green, yellow states and configurable durations.
    """
    def __init__(self, position, red_duration=5.0, green_duration=5.0, yellow_duration=2.0):
        """
        Args:
            position (tuple): (x, y) center position of the light in pixels.
            red_duration (float): seconds for red phase.
            green_duration (float): seconds for green phase.
            yellow_duration (float): seconds for yellow phase.
        """
        self.position = position
        self.durations = {
            LightState.RED: red_duration,
            LightState.GREEN: green_duration,
            LightState.YELLOW: yellow_duration
        }
        self.state = LightState.RED
        self._timer = 0.0

    def update(self, dt):
        """
        Advance internal timer and switch state if duration exceeded.

        Args:
            dt (float): time elapsed since last update (in seconds).
        """
        self._timer += dt
        if self._timer >= self.durations[self.state]:
            self._timer -= self.durations[self.state]
            self._advance_state()

    def _advance_state(self):
        """
        Cycle through RED -> GREEN -> YELLOW -> RED.
        """
        if self.state == LightState.RED:
            self.state = LightState.GREEN
        elif self.state == LightState.GREEN:
            self.state = LightState.YELLOW
        elif self.state == LightState.YELLOW:
            self.state = LightState.RED

    def draw(self, surface):
        """
        Draw the traffic light as three colored circles (red, yellow, green).

        Args:
            surface (pygame.Surface): the surface to draw on.
        """
        x, y = self.position
        radius = 10

        # order: red (top), yellow (middle), green (bottom)
        colors = {
            LightState.RED: (255, 0, 0),
            LightState.YELLOW: (255, 255, 0),
            LightState.GREEN: (0, 255, 0)
        }

        active_color = colors[LightState.RED]
        if self.state == LightState.RED:
            active_color = colors[LightState.RED]
        elif self.state == LightState.YELLOW:
            active_color = colors[LightState.YELLOW]
        elif self.state == LightState.GREEN:
            active_color = colors[LightState.GREEN]

        pygame.draw.circle(surface, active_color, (x, y), radius)

    def get_state(self):  # optional accessor
        """
        Returns the current LightState.
        """
        return self.state

    def reset(self):
        """
        Reset the light to RED and timer to zero.
        """
        self.state = LightState.RED
        self._timer = 0.0
