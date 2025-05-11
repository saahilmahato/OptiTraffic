import sys
import pygame
import os
import json
import time

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


def record_traffic_data(controller_type: str, passed: int, wait_time: float):
    """
    Append final simulation metrics to a JSON file in results/.
    Creates the file if it does not exist.
    """
    os.makedirs("results", exist_ok=True)
    file_path = os.path.join("results", f"{controller_type}.json")

    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
    else:
        data = []

    timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    record = {
        "timestamp": timestamp,
        "vehicles_passed": passed,
        "wait_time": round(wait_time, 2),
    }
    data.append(record)

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def run_simulation():
    """
    Main simulation loop. Runs for a fixed duration from config["simTime"] (in minutes),
    then records aggregated data.
    """
    screen, clock, config, world, spawner, renderer = initialize("configs/default.yaml")
    fps = config.get("fps", 60)
    sim_minutes = config.get("simTime", 1)
    total_duration = sim_minutes * 60.0  # seconds

    paused = False
    elapsed = 0.0
    controller_type = config.get("lights", {}).get("controllerType", "default")

    while elapsed < total_duration:
        dt = clock.tick(fps) / 1000.0
        elapsed += dt
        paused = handle_events(paused)

        if not paused:
            renderer.draw()
            spawner.spawn(dt)
            world.draw(screen, dt)

        pygame.display.flip()

    passed = world.total_vehicles_passed
    wait_time = world.total_wait_time
    record_traffic_data(controller_type, passed, wait_time)

    pygame.quit()
    print(
        f"Simulation completed: {sim_minutes} min; passed={passed}, total_wait_time={wait_time:.2f}s"
    )


if __name__ == "__main__":
    run_simulation()
