import sys
import pygame
import os
import json
import time
import argparse

from src.utils.config import load_config
from src.simulation.world import World
from src.simulation.spawner import Spawner
from src.rendering.renderer import Renderer


def initialize(
    config_path: str, controller_type: str
) -> tuple[pygame.Surface, pygame.time.Clock, dict, World, Spawner, Renderer]:
    config = load_config(config_path)

    # Override controllerType if provided
    if controller_type:
        config["lights"]["controllerType"] = controller_type

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
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            paused = not paused  # Toggle pause
    return paused


def record_traffic_data(controller_type: str, passed: int, wait_time: float):
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


def run_simulation(controller_type: str):
    screen, clock, config, world, spawner, renderer = initialize(
        "configs/default.yaml", controller_type
    )
    fps = config.get("fps", 60)
    sim_minutes = config.get("simTime", 1)
    total_duration = sim_minutes * 60.0  # seconds

    paused = False
    elapsed = 0.0
    controller_type = config.get("lights", {}).get("controllerType", "fixed")

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
    parser = argparse.ArgumentParser(
        description="Run traffic simulation with optional controllerType override."
    )
    parser.add_argument(
        "--controllerType",
        type=str,
        help="Override the controllerType from config file.",
    )
    args = parser.parse_args()

    run_simulation(controller_type=args.controllerType)
