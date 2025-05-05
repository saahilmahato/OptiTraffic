import pygame
from enum import Enum

class LightState(Enum):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    YELLOW = (255, 255, 0)

class TrafficLight:
    def __init__(self, position, light_id=None):
        self.position = position
        self.light_id = light_id

        self.state = LightState.RED

    def update(self, state):
        self.state = state

    def draw(self, surface):
        x, y = self.position
        radius = 10

        pygame.draw.circle(surface, self.state.value, (x, y), radius)

    def get_state(self):
        return self.state
