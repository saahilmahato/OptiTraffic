from typing import List, Any
from src.simulation.traffic_light import LightState


class BaseTrafficLightController:
    """Base class for traffic light control strategies."""

    def update(self, dt: float) -> None:
        """
        Updates the controller's state.

        Parameters:
            dt (float): Time delta in seconds since the last update.
        """
        raise NotImplementedError("Subclasses must implement the update method.")


class FixedCycleTrafficLightController(BaseTrafficLightController):
    """Controller that cycles lights with fixed timing."""

    def __init__(self, traffic_lights: List[Any], config: dict) -> None:
        """
        Initializes the fixed cycle controller.

        Parameters:
            traffic_lights (List[Any]): List of traffic light objects.
            config (dict): Configuration dictionary.
        """
        self.traffic_lights = traffic_lights
        self._load_durations(config)

        self.state: LightState = LightState.GREEN
        self._previous_state: LightState = LightState.RED
        self._time_in_state: float = 0.0

    def _load_durations(self, config: dict) -> None:
        """
        Loads state durations from the configuration.

        Parameters:
            config (dict): Configuration dictionary.
        """
        lights_cfg = config.get("lights", {})
        self._green_duration = lights_cfg.get("greenTime", 5)
        self._yellow_duration = lights_cfg.get("yellowTime", 2)
        self._red_duration = lights_cfg.get("redTime", 5)

    def update(self, dt: float) -> None:
        """
        Updates the traffic light state and applies it to all lights.

        Parameters:
            dt (float): Time delta in seconds since the last update.
        """
        self._time_in_state += dt
        self._handle_state_transition()

        for light in self.traffic_lights:
            light.update(self.state)

    def _handle_state_transition(self) -> None:
        """Determines and handles transitions between light states."""
        if (
            self.state == LightState.GREEN
            and self._time_in_state >= self._green_duration
        ):
            self._switch_state(LightState.YELLOW)
        elif (
            self.state == LightState.YELLOW
            and self._time_in_state >= self._yellow_duration
        ):
            next_state = (
                LightState.RED
                if self._previous_state == LightState.GREEN
                else LightState.GREEN
            )
            self._switch_state(next_state)
        elif self.state == LightState.RED and self._time_in_state >= self._red_duration:
            self._switch_state(LightState.YELLOW)

    def _switch_state(self, new_state: LightState) -> None:
        """
        Changes the current traffic light state.

        Parameters:
            new_state (LightState): The new state to switch to.
        """
        self._previous_state = self.state
        self.state = new_state
        self._time_in_state = 0.0


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

        raise ValueError(f"Unknown traffic light controller type: '{controller_type}'")

    def update(self, dt: float) -> None:
        """
        Updates the current control strategy.

        Parameters:
            dt (float): Time delta in seconds since the last update.
        """
        self.strategy.update(dt)
