import numpy as np

from src.simulation.traffic_light import TrafficLight, LightState
from src.simulation.traffic_light_controller import TrafficLightController


class World:
    def __init__(self, config):
        self.config = config
        self.vehicles = []

        self.traffic_lights = self._create_traffic_lights()
        self.traffic_light_controller = TrafficLightController(
            self.traffic_lights, config
        )

        self.total_vehicles_passed = 0

    def draw(self, screen, dt):
        self.clear_traffic_data()
        self.add_traffic_data()
        self.traffic_light_controller.update(dt)

        # Track how many vehicles are before filtering
        before_count = len(self.vehicles)

        # Filter vehicles that are within bounds
        self.vehicles = [
            vehicle for vehicle in self.vehicles if self.is_within_bounds(vehicle)
        ]

        # Update total vehicles passed
        passed_count = before_count - len(self.vehicles)
        self.total_vehicles_passed += passed_count

        # Update and draw remaining vehicles
        for vehicle in self.vehicles:
            if not self.should_stop(vehicle):
                vehicle.update(dt)
            vehicle.draw(screen)

        # Draw traffic lights
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
                (0, -1): lambda: x == 280 and 300 <= y <= 600,
            },
            {
                (1, 0): lambda: y == 280 and 300 <= x <= 600,
                (-1, 0): lambda: y == 320 and 600 <= x <= 900,
                (0, 1): lambda: x == 620 and 0 <= y <= 300,
                (0, -1): lambda: x == 580 and 300 <= y <= 600,
            },
            {
                (1, 0): lambda: y == 580 and 0 <= x <= 300,
                (-1, 0): lambda: y == 620 and 300 <= x <= 600,
                (0, 1): lambda: x == 320 and 300 <= y <= 600,
                (0, -1): lambda: x == 280 and 600 <= y <= 900,
            },
            {
                (1, 0): lambda: y == 580 and 300 <= x <= 600,
                (-1, 0): lambda: y == 620 and 600 <= x <= 900,
                (0, 1): lambda: x == 620 and 300 <= y <= 600,
                (0, -1): lambda: x == 580 and 600 <= y <= 900,
            },
        ]

        conditions = traffic_conditions[index]
        if (dx, dy) in conditions and conditions[(dx, dy)]():
            self.traffic_lights[index].add_approaching_vehicle(vehicle)

    def should_stop(self, vehicle):
        return self._stop_due_to_light(vehicle) or self._stop_due_to_vehicle_ahead(
            vehicle
        )

    def _stop_due_to_light(self, vehicle):
        for light in self.traffic_lights:
            if vehicle not in light.approaching_vehicles:
                continue

            light_pos = np.array(light.position, dtype=float)
            vehicle_pos = np.array(vehicle.position, dtype=float)
            dist = np.linalg.norm(light_pos - vehicle_pos)

            if dist > 40:
                continue

            state = light.get_state()
            dx, dy = vehicle.direction

            if state == LightState.YELLOW:
                return True
            if abs(dx) > abs(dy) and state == LightState.RED:
                return True
            if abs(dy) > abs(dx) and state == LightState.GREEN:
                return True

        return False

    def _stop_due_to_vehicle_ahead(self, vehicle):
        for other in self.vehicles:
            if other is vehicle:
                continue

            if not np.array_equal(vehicle.direction, other.direction):
                continue

            # Same horizontal or vertical lane
            if abs(vehicle.direction[0]) > 0:
                same_lane = abs(vehicle.position[1] - other.position[1]) < 1
            else:
                same_lane = abs(vehicle.position[0] - other.position[0]) < 1

            if not same_lane:
                continue

            # Is the other vehicle ahead?
            delta = other.position - vehicle.position
            if np.dot(delta, vehicle.direction) <= 0:
                continue

            if np.linalg.norm(delta) < 13:
                return True

        return False

    def is_within_bounds(self, vehicle):
        x, y = vehicle.position
        screen_width, screen_height = (
            self.config["windowSize"],
            self.config["windowSize"],
        )

        # Check if the vehicle is within the visible window based on its direction
        if abs(vehicle.direction[0]) > abs(vehicle.direction[1]):  # Horizontal movement
            if vehicle.direction[0] > 0:  # Moving right
                return x < screen_width
            elif vehicle.direction[0] < 0:  # Moving left
                return x > 0
        else:  # Vertical movement
            if vehicle.direction[1] > 0:  # Moving down
                return y < screen_height
            elif vehicle.direction[1] < 0:  # Moving up
                return y > 0

        return True  # If vehicle is stationary, it's always within bounds
