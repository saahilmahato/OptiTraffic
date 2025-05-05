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
        self.approaching_vehicles = []

        # Create font once to reuse
        self.font = pygame.font.SysFont(None, 24)

    def update(self, state):
        self.state = state

    def draw(self, surface):
        x, y = self.position
        radius = 10

        # Draw the light
        pygame.draw.circle(surface, self.state.value, (x, y), radius)

        # Draw vehicle count
        count = len(self.approaching_vehicles)
        text_surface = self.font.render(str(count), True, (0, 0, 0))
        surface.blit(text_surface, (x-radius//2, y-radius//2))

    def get_state(self):
        return self.state
    
    def clear_approaching_vehicles(self):
        self.approaching_vehicles = []
    
    def add_approaching_vehicle(self, vehicle):
        self.approaching_vehicles.append(vehicle)
