import numpy as np
from src.simulation.traffic_light import TrafficLight

class World:
    def __init__(self, width, height, config):
        self.width = width
        self.height = height
        self.vehicles = []
        self.config = config
        self.traffic_lights = self._create_traffic_lights()

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def update(self, dt):
        self.vehicles = [v for v in self.vehicles if 0 <= v.pos[0] <= self.width and 0 <= v.pos[1] <= self.height]
        for v in self.vehicles:
            v.update(dt)
        for light in self.traffic_lights:
            light.update(dt)

    def _create_traffic_lights(self):
        lights = []
        num_roads = self.config.get('num_roads', 2)
        screen_w = self.width
        screen_h = self.height

        x_centers = [i * screen_w / (num_roads + 1) for i in range(1, num_roads + 1)]
        y_centers = [j * screen_h / (num_roads + 1) for j in range(1, num_roads + 1)]

        for i, x in enumerate(x_centers):
            for j, y in enumerate(y_centers):
                light_id = f"L{i}-{j}"
                lights.append(TrafficLight(position=(int(x), int(y)), light_id=light_id))
        return lights
    
    def get_all_approaching_vehicles(self):
        result = {light.light_id: {'N': [], 'S': [], 'E': [], 'W': []}
                for light in self.traffic_lights}

        assigned = set()  # Avoid assigning vehicles to multiple lights

        for v in self.vehicles:
            v_pos = v.pos
            v_dir = v.direction / (np.linalg.norm(v.direction) + 1e-6)

            best_light = None
            best_dir = None
            best_dist = float('inf')

            for light in self.traffic_lights:
                lx, ly = light.position
                dx, dy = lx - v_pos[0], ly - v_pos[1]
                dist = np.hypot(dx, dy)

                dir_to_light = np.array([dx, dy])
                dir_to_light = dir_to_light / (np.linalg.norm(dir_to_light) + 1e-6)
                alignment = np.dot(v_dir, dir_to_light)

                if alignment < 0.7:
                    continue  # Not heading toward this light

                # Skip lights that are behind the vehicle
                future_pos = v.pos + v_dir * 20  # look a bit ahead
                if np.linalg.norm(np.array([lx, ly]) - future_pos) > dist:
                    continue  # Vehicle is past the light

                # Determine direction of approach
                abs_dx, abs_dy = abs(dx), abs(dy)
                if abs_dx > abs_dy:
                    # E-W movement
                    if dx > 0 and v_dir[0] > 0:
                        direction = 'W'
                    elif dx < 0 and v_dir[0] < 0:
                        direction = 'E'
                    else:
                        continue
                else:
                    # N-S movement
                    if dy > 0 and v_dir[1] > 0:
                        direction = 'N'
                    elif dy < 0 and v_dir[1] < 0:
                        direction = 'S'
                    else:
                        continue

                # Assign to closest valid light
                if dist < best_dist:
                    best_light = light
                    best_dir = direction
                    best_dist = dist

            if best_light and v not in assigned:
                result[best_light.light_id][best_dir].append(v)
                assigned.add(v)

        return result
