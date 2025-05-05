import numpy as np
from src.simulation.traffic_light import TrafficLight, LightState
from src.simulation.traffic_light_controller import TrafficLightController


class World:
    def __init__(self, config):
        self.config = config
        self.vehicles = []

        self.traffic_lights = self._create_traffic_lights()
        self.traffic_light_controller = TrafficLightController(self.traffic_lights, config)


    def draw(self, screen, dt):
        self.traffic_light_controller.update(dt)

        for vehicle in self.vehicles:
            vehicle.update(dt)
            vehicle.draw(screen)
        
        for light in self.traffic_lights:
            light.draw(screen)

    def _create_traffic_lights(self):
        coordinates = self.config.get("lights", {}).get("points", [])
        lights = []
        for x, y in coordinates:
            light_id = f"L{x}-{y}"
            lights.append(TrafficLight(position=(int(x), int(y)), light_id=light_id))
        return lights
