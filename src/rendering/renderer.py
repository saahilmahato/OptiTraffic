import pygame

GRASS_COLOR = (34, 139, 34)
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (255, 255, 255)

class Renderer:
    def __init__(self, screen, world, config):
        self.screen = screen
        self.world = world
        self.config = config

    def draw(self):
        self.screen.fill(GRASS_COLOR)
        self.draw_vertical_roads()
        self.draw_horizontal_roads()

    def draw_vertical_roads(self):
        road_width = 80
        window_height = self.config['windowSize']
        line_width = 2
        dash_length = 20
        dash_gap = 20

        # Draw the roads
        pygame.draw.rect(self.screen, ROAD_COLOR, pygame.Rect(260, 0, road_width, window_height))
        pygame.draw.rect(self.screen, ROAD_COLOR, pygame.Rect(560, 0, road_width, window_height))

        # Draw dashed lines in the center of each road
        for x in [260 + road_width // 2, 560 + road_width // 2]:
            y = 0
            while y < window_height:
                pygame.draw.line(
                    self.screen,
                    LINE_COLOR,
                    (x, y),
                    (x, y + dash_length),
                    line_width
                )
                y += dash_length + dash_gap

    def draw_horizontal_roads(self):
        road_width = 80
        window_width = self.config['windowSize']
        line_width = 2
        dash_length = 20
        dash_gap = 20

        # Draw the roads
        pygame.draw.rect(self.screen, ROAD_COLOR, pygame.Rect(0, 260, window_width, road_width))
        pygame.draw.rect(self.screen, ROAD_COLOR, pygame.Rect(0, 560, window_width, road_width))

        # Draw dashed lines in the center of each road
        for y in [260 + road_width // 2, 560 + road_width // 2]:
            x = 0
            while x < window_width:
                pygame.draw.line(
                    self.screen,
                    LINE_COLOR,
                    (x, y),
                    (x + dash_length, y),
                    line_width
                )
                x += dash_length + dash_gap



