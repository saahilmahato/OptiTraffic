import pygame, sys

from src.utils.config import load_config
from src.utils.logger import setup_logging
from src.simulation.world import World
from src.simulation.spawner import Spawner
from src.rendering.renderer import Renderer

def main():
    config = load_config('configs/default.yaml')
    logger = setup_logging()
    width = config['window']['width']
    height = config['window']['height']
    fps = config['fps']

    pygame.init()
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    world = World(width, height)
    spawner = Spawner(config, world)
    renderer = Renderer(screen, world, config)

    while True:
        dt = clock.tick(fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        spawner.spawn()
        world.update(dt)
        renderer.draw()


if __name__ == '__main__':
    main()