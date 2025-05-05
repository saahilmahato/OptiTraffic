import numpy as np
import pygame

VEHICLE_COLOR = (0, 0, 255)
VEHICLE_LENGTH = 10
VEHICLE_WIDTH = 5

class Vehicle:
    def __init__(self, position, direction, speed=100):
        self.position = np.array(position, dtype=float)
        self.direction = np.array(direction, dtype=float)
        self.speed = speed
        self.approaching_light = None

    def update(self, dt):
        self.position += self.direction * self.speed * dt

    def rect(self):
        x, y = self.position
        horizontal = abs(self.direction[0]) > abs(self.direction[1])
        if horizontal:
            w, h = VEHICLE_LENGTH, VEHICLE_WIDTH
        else:
            w, h = VEHICLE_WIDTH, VEHICLE_LENGTH

        return pygame.Rect(x - w/2, y - h/2, w, h)

    def draw(self, screen):
        pygame.draw.rect(screen, VEHICLE_COLOR, self.rect())

    def update_approaching_light(self, light):
        self.approaching_light = light
