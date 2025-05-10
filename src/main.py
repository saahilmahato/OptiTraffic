import sys
import pygame

from src.utils.config import load_config
from src.simulation.world import World
from src.simulation.spawner import Spawner
from src.rendering.renderer import Renderer


def initialize(
    config_path: str,
) -> tuple[pygame.Surface, pygame.time.Clock, dict, World, Spawner, Renderer]:
    """
    Initialize the simulation environment, including Pygame, world, and renderer.

    Args:
        config_path (str): Path to the YAML config file.

    Returns:
        Tuple containing the screen, clock, config, world, spawner, and renderer.
    """
    config = load_config(config_path)

    if "windowSize" not in config or not isinstance(config["windowSize"], dict):
        raise ValueError("Invalid config format: missing or malformed 'windowSize'")

    width = config["windowSize"]["width"]
    height = config["windowSize"]["height"]

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    world = World(config)
    spawner = Spawner(config, world)
    renderer = Renderer(screen, world, config)

    return screen, clock, config, world, spawner, renderer


def handle_events(paused: bool) -> bool:
    """
    Handle Pygame events and toggle pause if space is pressed.

    Args:
        paused (bool): Current paused state.

    Returns:
        bool: Updated paused state.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused  # Toggle pause
    return paused


def run_simulation():
    """
    Main simulation loop.
    """
    screen, clock, config, world, spawner, renderer = initialize("configs/default.yaml")
    fps = config["fps"]
    paused = False

    while True:
        dt = clock.tick(fps) / 1000.0
        paused = handle_events(paused)

        if not paused:
            renderer.draw()
            spawner.spawn(dt)
            world.draw(screen, dt)

        pygame.display.flip()


if __name__ == "__main__":
    run_simulation()
