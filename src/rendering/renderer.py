import pygame
from src.constants import ROAD_COLOR, BG_COLOR, VEHICLE_COLOR, LINE_COLOR

class Renderer:
    def __init__(self, screen, world, config):
        self.screen = screen
        self.world = world
        self.config = config

    def draw(self):
        self.screen.fill(BG_COLOR)

        screen_w, screen_h = self.screen.get_size()
        num_roads = self.config.get('num_roads', 2)
        road_w = self.config.get('road_width', 100)
        line_w = self.config.get('line_width', 4)
        dash_len = self.config.get('dash_length', 20)
        dash_gap = self.config.get('dash_gap', 20)

        vertical_roads = []
        horizontal_roads = []

        for i in range(1, num_roads + 1):
            x_center = i * screen_w / (num_roads + 1)
            rect = pygame.Rect(x_center - road_w/2, 0, road_w, screen_h)
            pygame.draw.rect(self.screen, ROAD_COLOR, rect)
            vertical_roads.append(rect)

        for j in range(1, num_roads + 1):
            y_center = j * screen_h / (num_roads + 1)
            rect = pygame.Rect(0, y_center - road_w/2, screen_w, road_w)
            pygame.draw.rect(self.screen, ROAD_COLOR, rect)
            horizontal_roads.append(rect)

        intersections = []
        for v_rect in vertical_roads:
            for h_rect in horizontal_roads:
                intersections.append(v_rect.clip(h_rect))

        for v_rect in vertical_roads:
            x = v_rect.centerx
            y = 0
            while y < screen_h:
                seg_start = (x, y)
                seg_end = (x, min(y + dash_len, screen_h))
                seg_rect = pygame.Rect(x - line_w/2, y, line_w, dash_len)
                if not any(seg_rect.colliderect(ix) for ix in intersections):
                    pygame.draw.line(self.screen, LINE_COLOR, seg_start, seg_end, line_w)
                y += dash_len + dash_gap

        for h_rect in horizontal_roads:
            y = h_rect.centery
            x = 0
            while x < screen_w:
                seg_start = (x, y)
                seg_end = (min(x + dash_len, screen_w), y)
                seg_rect = pygame.Rect(x, y - line_w/2, dash_len, line_w)
                if not any(seg_rect.colliderect(ix) for ix in intersections):
                    pygame.draw.line(self.screen, LINE_COLOR, seg_start, seg_end, line_w)
                x += dash_len + dash_gap

        for v in self.world.vehicles:
            rect = v.rect()
            pygame.draw.rect(self.screen, VEHICLE_COLOR, rect)

        # draw traffic lights from world
        for light in self.world.traffic_lights:
            light.draw(self.screen)

        pygame.display.flip()
