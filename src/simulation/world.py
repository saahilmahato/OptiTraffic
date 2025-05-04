from src.simulation.traffic_light import TrafficLight

class World:
    def __init__(self, width, height, config):
        self.width = width
        self.height = height
        self.vehicles = []
        self.traffic_lights = self._create_traffic_lights(config)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def update(self, dt):
        new_list = []
        for v in self.vehicles:
            v.update(dt)
            x, y = v.pos
            if 0 <= x <= self.width and 0 <= y <= self.height:
                new_list.append(v)
        self.vehicles = new_list

        # update traffic lights
        for light in self.traffic_lights:
            light.update(dt)

    def _create_traffic_lights(self, config):
        lights = []
        num_roads = config.get('num_roads', 2)
        screen_w = self.width
        screen_h = self.height

        x_centers = [i * screen_w / (num_roads + 1) for i in range(1, num_roads + 1)]
        y_centers = [j * screen_h / (num_roads + 1) for j in range(1, num_roads + 1)]

        for x in x_centers:
            for y in y_centers:
                lights.append(TrafficLight((int(x), int(y))))
        return lights
