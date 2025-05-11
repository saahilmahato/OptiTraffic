import pygame

GRASS_COLOR = (34, 139, 34)
ROAD_COLOR = (50, 50, 50)
LINE_COLOR = (255, 255, 255)


class Renderer:
    """Render the world—including roads, vehicles, and stats—onto the screen."""

    def __init__(self, screen, world, config):
        """
        Initialize the renderer.

        Parameters:
            screen (pygame.Surface): Surface to draw on.
            world (World): World instance with vehicles and traffic lights.
            config (dict): Configuration dict containing 'windowSize' with
                'width' and 'height' keys.
        """
        self.screen = screen
        self.world = world
        self.config = config
        self.font = pygame.font.SysFont(None, 28)

    def draw(self):
        """
        Draw grass, roads, vehicles, traffic lights, and stats.

        Uses the configured window size for road dimensions.
        """
        width = self.config["windowSize"]["width"]
        height = self.config["windowSize"]["height"]

        self.screen.fill(GRASS_COLOR)
        self._draw_vertical_roads(height)
        self._draw_horizontal_roads(width)
        self._draw_vehicles()
        self._draw_traffic_lights()
        self.draw_stats()

    def draw_stats(self):
        """Draws the total number of vehicles passed on the screen."""
        count_text = f"Vehicles Passed: {self.world.total_vehicles_passed}"
        wait_time_text = f"Wait Time: {self.world.total_wait_time:.2f}"
        count_text_surface = self.font.render(count_text, True, (0, 0, 0))  # Black text
        wait_time_text_surface = self.font.render(
            wait_time_text, True, (0, 0, 0)
        )  # Black text
        self.screen.blit(count_text_surface, (10, 10))  # Top-left with padding
        self.screen.blit(wait_time_text_surface, (10, 30))  # Top-left with padding

    def _draw_vehicles(self):
        """Draw all vehicles in the world."""
        for vehicle in self.world.vehicles:
            vehicle.draw(self.screen)

    def _draw_traffic_lights(self):
        """Draw all traffic lights in the world."""
        for light in self.world.traffic_lights:
            light.draw(self.screen)

    def _draw_vertical_roads(self, window_height):
        """
        Draw the two vertical roads with dashed center lines.

        Parameters:
            window_height (int): Height of the window in pixels.
        """
        road_w = 80
        centers = [260 + road_w // 2, 560 + road_w // 2]

        # Road rectangles
        self._draw_road(260, 0, road_w, window_height)
        self._draw_road(560, 0, road_w, window_height)

        # Center dashed lines
        for x in centers:
            self._draw_vertical_dashed_line(x, window_height)

    def _draw_horizontal_roads(self, window_width):
        """
        Draw the two horizontal roads with dashed center lines.

        Parameters:
            window_width (int): Width of the window in pixels.
        """
        road_w = 80
        centers = [260 + road_w // 2, 560 + road_w // 2]

        # Road rectangles
        self._draw_road(0, 260, window_width, road_w)
        self._draw_road(0, 560, window_width, road_w)

        # Center dashed lines
        for y in centers:
            self._draw_horizontal_dashed_line(y, window_width)

    def _draw_road(self, x, y, w, h):
        """
        Draw a solid road rectangle.

        Parameters:
            x (int): X-coordinate of the top-left corner.
            y (int): Y-coordinate of the top-left corner.
            w (int): Width of the road.
            h (int): Height of the road.
        """
        rect = pygame.Rect(x, y, w, h)
        pygame.draw.rect(self.screen, ROAD_COLOR, rect)

    def _draw_vertical_dashed_line(self, x, window_height):
        """
        Draw a dashed vertical line at a given x-position.

        Parameters:
            x (int): X-coordinate for the center of the dashed line.
            window_height (int): Total height to draw over.
        """
        dash_len = 20
        dash_gap = 20
        width = 2
        y = 0
        while y < window_height:
            start = (x, y)
            end = (x, y + dash_len)
            pygame.draw.line(self.screen, LINE_COLOR, start, end, width)
            y += dash_len + dash_gap

    def _draw_horizontal_dashed_line(self, y, window_width):
        """
        Draw a dashed horizontal line at a given y-position.

        Parameters:
            y (int): Y-coordinate for the center of the dashed line.
            window_width (int): Total width to draw over.
        """
        dash_len = 20
        dash_gap = 20
        width = 2
        x = 0
        while x < window_width:
            start = (x, y)
            end = (x + dash_len, y)
            pygame.draw.line(self.screen, LINE_COLOR, start, end, width)
            x += dash_len + dash_gap
