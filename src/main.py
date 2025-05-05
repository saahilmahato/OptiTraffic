import pygame, sys

from src.utils.config import load_config
from src.simulation.world import World
from src.simulation.spawner import Spawner
from src.rendering.renderer import Renderer

def main():
    config = load_config('configs/default.yaml')
    window_size = config['windowSize']
    fps = config['fps']

    pygame.init()
    screen = pygame.display.set_mode((window_size, window_size))
    clock = pygame.time.Clock()

    world = World(config)
    spawner = Spawner(config, world)
    renderer = Renderer(screen, world, config)

    while True:
        dt = clock.tick(fps) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        renderer.draw()
        spawner.spawn(dt)
        world.draw(screen, dt)
        pygame.display.flip()


if __name__ == '__main__':
    main()