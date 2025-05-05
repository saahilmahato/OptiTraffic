from src.simulation.traffic_light import TrafficLight, LightState
from src.simulation.traffic_light_controller import TrafficLightController


class World:
    def __init__(self, config):
        self.config = config
        self.vehicles = []

        self.traffic_lights = self._create_traffic_lights()
        self.traffic_light_controller = TrafficLightController(self.traffic_lights, config)


    def draw(self, screen, dt):
        self.clear_traffic_data()
        self.add_traffic_data()
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
    
    def clear_traffic_data(self):
        for light in self.traffic_lights:
            light.clear_approaching_vehicles()
            
    def add_traffic_data(self):
        for vehicle in self.vehicles:
            for i in range(len(self.traffic_lights)):
                self.check_for_traffic(i, vehicle)

    def check_for_traffic(self, index, vehicle):
        x, y = vehicle.position
        dx, dy = vehicle.direction

        traffic_conditions = [
            {
                (1, 0): lambda: y == 280 and 0 <= x <= 300,
                (-1, 0): lambda: y == 320 and 300 <= x <= 600,
                (0, 1): lambda: x == 320 and 0 <= y <= 300,
                (0, -1): lambda: x == 280 and 300 <= y <= 600
            },
            {
                (1, 0): lambda: y == 280 and 300 <= x <= 600,
                (-1, 0): lambda: y == 320 and 600 <= x <= 900,
                (0, 1): lambda: x == 620 and 0 <= y <= 300,
                (0, -1): lambda: x == 580 and 300 <= y <= 600
            },
            {
                (1, 0): lambda: y == 580 and 0 <= x <= 300,
                (-1, 0): lambda: y == 620 and 300 <= x <= 600,
                (0, 1): lambda: x == 320 and 300 <= y <= 600,
                (0, -1): lambda: x == 280 and 600 <= y <= 900
            },
            {
                (1, 0): lambda: y == 580 and 300 <= x <= 600,
                (-1, 0): lambda: y == 620 and 600 <= x <= 900,
                (0, 1): lambda: x == 620 and 300 <= y <= 600,
                (0, -1): lambda: x == 580 and 600 <= y <= 900
            }
        ]

        conditions = traffic_conditions[index]
        if (dx, dy) in conditions and conditions[(dx, dy)]():
            self.traffic_lights[index].add_approaching_vehicle(vehicle)
            vehicle.add_approaching_light(self.traffic_lights[index])
