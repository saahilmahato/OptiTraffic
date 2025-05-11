import numpy as np

from src.simulation.traffic_light import TrafficLight, LightState
from src.simulation.traffic_light_controller.traffic_light_controller import (
    TrafficLightController,
)


class World:
    """Simulates the traffic world, including vehicles and traffic lights."""

    def __init__(self, config):
        """
        Initializes the simulation world.

        Parameters:
            config (dict): Configuration dictionary for the world.
        """
        self.config = config
        self.vehicles = []
        self.total_vehicles_passed = 0

        self.traffic_lights = self._create_traffic_lights()
        self.traffic_light_controller = TrafficLightController(
            self.traffic_lights, config
        )

    def draw(self, screen, dt):
        """
        Renders the world (vehicles and traffic lights) on the screen.

        Parameters:
            screen (Surface): Pygame screen surface.
            dt (float): Delta time since the last update.
        """
        # Update vehicle and traffic light data
        self.update_traffic_data(dt)

        # Draw the remaining vehicles
        for vehicle in self.vehicles:
            vehicle.draw(screen)

        # Draw traffic lights
        for light in self.traffic_lights:
            light.draw(screen)

    def update_traffic_data(self, dt):
        """
        Updates the simulation state for vehicles and traffic lights.

        Parameters:
            dt (float): Delta time since the last update.
        """
        self.clear_traffic_data()
        self.add_traffic_data()
        self.traffic_light_controller.update(dt)

        before_count = len(self.vehicles)
        # Vectorized filtering of vehicles within bounds using numpy
        self.vehicles = [
            vehicle for vehicle in self.vehicles if self.is_within_bounds(vehicle)
        ]
        self.total_vehicles_passed += before_count - len(self.vehicles)

        for vehicle in self.vehicles:
            speed = 0 if self.should_stop(vehicle) else 100
            vehicle.update(speed, dt)

    def _create_traffic_lights(self):
        """
        Creates traffic lights from config-defined coordinates.

        Returns:
            list: List of TrafficLight instances.
        """
        coordinates = self.config.get("lights", {}).get("points", [])
        return [
            TrafficLight(position=(int(x), int(y)), light_id=f"L{x}-{y}")
            for x, y in coordinates
        ]

    def clear_traffic_data(self):
        """Clears all approaching vehicle data from each traffic light."""
        for light in self.traffic_lights:
            light.clear_approaching_vehicles()

    def add_traffic_data(self):
        """Adds vehicle approach data to traffic lights."""
        for vehicle in self.vehicles:
            for i in range(len(self.traffic_lights)):
                self.check_for_traffic(i, vehicle)

    def check_for_traffic(self, index, vehicle):
        """
        Checks if a vehicle is approaching a specific traffic light.

        Parameters:
            index (int): The index of the traffic light to check.
            vehicle (Vehicle): The vehicle instance to evaluate.
        """
        dx, dy = vehicle.direction

        traffic_conditions = {
            (1, 0): self._check_east_bound_traffic,  # east bound
            (-1, 0): self._check_west_bound_traffic,  # west bound
            (0, 1): self._check_north_bound_traffic,  # north bound
            (0, -1): self._check_south_bound_traffic,  # south bound
        }

        # Check if a function exists for this vehicle's direction
        if (dx, dy) in traffic_conditions:
            # Call the appropriate condition function
            condition_fn = traffic_conditions[(dx, dy)]
            if condition_fn(index, vehicle):
                self.traffic_lights[index].add_approaching_vehicle(vehicle)
                vehicle.update_light_distance(np.linalg.norm(vehicle.position - self.traffic_lights[index].position))

    def _check_east_bound_traffic(self, index, vehicle):
        """
        Checks if an eastbound vehicle is approaching a traffic light.

        Parameters:
            index (int): The index of the traffic light.
            vehicle (Vehicle): The vehicle instance to check.

        Returns:
            bool: True if the vehicle is approaching the traffic light, False otherwise.
        """
        x, y = vehicle.position
        if index == 0:
            return y == 280 and 0 <= x <= 300
        if index == 1:
            return y == 280 and 300 <= x <= 600
        if index == 2:
            return y == 580 and 0 <= x <= 300
        if index == 3:
            return y == 580 and 300 <= x <= 600
        return False

    def _check_west_bound_traffic(self, index, vehicle):
        """
        Checks if a westbound vehicle is approaching a traffic light.

        Parameters:
            index (int): The index of the traffic light.
            vehicle (Vehicle): The vehicle instance to check.

        Returns:
            bool: True if the vehicle is approaching the traffic light, False otherwise.
        """
        x, y = vehicle.position
        if index == 0:
            return y == 320 and 300 <= x <= 600
        if index == 1:
            return y == 320 and 600 <= x <= 900
        if index == 2:
            return y == 620 and 300 <= x <= 600
        if index == 3:
            return y == 620 and 600 <= x <= 900
        return False

    def _check_north_bound_traffic(self, index, vehicle):
        """
        Checks if a northbound vehicle is approaching a traffic light.

        Parameters:
            index (int): The index of the traffic light.
            vehicle (Vehicle): The vehicle instance to check.

        Returns:
            bool: True if the vehicle is approaching the traffic light, False otherwise.
        """
        x, y = vehicle.position
        if index == 0:
            return x == 320 and 0 <= y <= 300
        if index == 1:
            return x == 620 and 0 <= y <= 300
        if index == 2:
            return x == 320 and 300 <= y <= 600
        if index == 3:
            return x == 620 and 300 <= y <= 600
        return False

    def _check_south_bound_traffic(self, index, vehicle):
        """
        Checks if a southbound vehicle is approaching a traffic light.

        Parameters:
            index (int): The index of the traffic light.
            vehicle (Vehicle): The vehicle instance to check.

        Returns:
            bool: True if the vehicle is approaching the traffic light, False otherwise.
        """
        x, y = vehicle.position
        if index == 0:
            return x == 280 and 300 <= y <= 600
        if index == 1:
            return x == 580 and 300 <= y <= 600
        if index == 2:
            return x == 280 and 600 <= y <= 900
        if index == 3:
            return x == 580 and 600 <= y <= 900
        return False

    def should_stop(self, vehicle):
        """
        Determines if the vehicle should stop due to lights or other vehicles.

        Parameters:
            vehicle (Vehicle): The vehicle instance.

        Returns:
            bool: True if vehicle should stop, False otherwise.
        """
        return self._stop_due_to_light(vehicle) or self._stop_due_to_vehicle_ahead(
            vehicle
        )

    def _stop_due_to_light(self, vehicle):
        """
        Evaluates if vehicle should stop based on the light state.

        Parameters:
            vehicle (Vehicle): The vehicle instance.

        Returns:
            bool: True if vehicle should stop, False otherwise.
        """
        for light in self.traffic_lights:
            if vehicle not in light.get_approaching_vehicles():
                continue

            # Optimized using numpy for distance calculation
            dist = np.linalg.norm(np.array(light.position) - np.array(vehicle.position))
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
        """
        Checks if another vehicle is too close ahead in the same lane.

        Parameters:
            vehicle (Vehicle): The vehicle instance.

        Returns:
            bool: True if vehicle should stop, False otherwise.
        """
        for other in self.vehicles:
            if other is vehicle:
                continue

            if not np.array_equal(vehicle.direction, other.direction):
                continue

            # Optimized using numpy for lane comparison
            same_lane = (
                abs(vehicle.position[1] - other.position[1]) < 1
                if abs(vehicle.direction[0]) > 0
                else abs(vehicle.position[0] - other.position[0]) < 1
            )

            if not same_lane:
                continue

            delta = other.position - vehicle.position
            if np.dot(delta, vehicle.direction) <= 0:
                continue

            if np.linalg.norm(delta) < 13:
                return True

        return False

    def is_within_bounds(self, vehicle):
        """
        Determines if a vehicle is within the visible screen bounds.

        Parameters:
            vehicle (Vehicle): The vehicle instance.

        Returns:
            bool: True if vehicle is within bounds, False otherwise.
        """
        x, y = vehicle.position
        width = self.config["windowSize"]["width"]
        height = self.config["windowSize"]["height"]

        if abs(vehicle.direction[0]) > abs(vehicle.direction[1]):
            return x < width if vehicle.direction[0] > 0 else x > 0
        else:
            return y < height if vehicle.direction[1] > 0 else y > 0
