from typing import List, Any
from src.simulation.traffic_light_controller.base_controller import (
    BaseTrafficLightController,
)
from src.simulation.traffic_light_controller.fixed_controller import (
    FixedCycleTrafficLightController,
)
from src.simulation.traffic_light_controller.marl_controller import MARLTrafficLightController


class TrafficLightController:
    """Top-level traffic light controller that delegates to a selected strategy."""

    def __init__(self, traffic_lights: List[Any], config: dict) -> None:
        """
        Initializes the traffic light controller.

        Parameters:
            traffic_lights (List[Any]): List of traffic light objects.
            config (dict): Configuration dictionary.
        """
        self.strategy = self._select_strategy(traffic_lights, config)

    def _select_strategy(
        self, traffic_lights: List[Any], config: dict
    ) -> BaseTrafficLightController:
        """
        Selects a traffic light control strategy.

        Parameters:
            traffic_lights (List[Any]): List of traffic light objects.
            config (dict): Configuration dictionary.

        Returns:
            BaseTrafficLightController: The selected strategy object.

        Raises:
            ValueError: If the controller type is unknown.
        """
        controller_type = (
            config.get("lights", {}).get("controllerType", "fixed").lower()
        )

        if controller_type == "fixed":
            return FixedCycleTrafficLightController(traffic_lights, config)
        
        if controller_type == "marl":
            return  MARLTrafficLightController(traffic_lights, config)

        raise ValueError(f"Unknown traffic light controller type: '{controller_type}'")

    def update(self, dt: float) -> None:
        """
        Updates the current control strategy.

        Parameters:
            dt (float): Time delta in seconds since the last update.
        """
        self.strategy.update(dt)
