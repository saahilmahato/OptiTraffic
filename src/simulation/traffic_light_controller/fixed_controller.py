from typing import List, Any
from src.simulation.traffic_light import LightState
from src.simulation.traffic_light_controller.base_controller import (
    BaseTrafficLightController,
)


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
