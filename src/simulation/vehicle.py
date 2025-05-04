import numpy as np
import pygame
from src.constants import VEHICLE_WIDTH, VEHICLE_LENGTH, VEHICLE_COLOR

class Vehicle:
    def __init__(self, pos, direction, speed=100):
        self.pos = np.array(pos, dtype=float)
        self.direction = np.array(direction, dtype=float)
        self.speed = speed

    def update(self, dt):
        self.pos += self.direction * self.speed * dt

    def rect(self):
        x, y = self.pos
        # Determine if moving primarily horizontally
        horizontal = abs(self.direction[0]) > abs(self.direction[1])
        if horizontal:
            w, h = VEHICLE_LENGTH, VEHICLE_WIDTH
        else:
            w, h = VEHICLE_WIDTH, VEHICLE_LENGTH

        # Center the rect on (x, y)
        return pygame.Rect(x - w/2, y - h/2, w, h)

    def draw(self, surface):
        pygame.draw.rect(surface, VEHICLE_COLOR, self.rect())
