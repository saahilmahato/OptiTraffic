from src.simulation.traffic_light import LightState


class BaseTrafficLightController:
    def update(self, dt):
        raise NotImplementedError("Update method must be implemented by subclasses")


class FixedCycleTrafficLightController(BaseTrafficLightController):
    def __init__(self, traffic_lights, config):
        self.traffic_lights = traffic_lights
        self.green_duration = config.get("lights", {}).get("greenTime", 5)
        self.yellow_duration = config.get("lights", {}).get("yellowTime", 2)
        self.red_duration = config.get("lights", {}).get("redTime", 5)

        self.state = LightState.GREEN
        self.time_in_state = 0.0

    def update(self, dt):
        self.time_in_state += dt

        # Handle transitions
        if self.state == LightState.GREEN and self.time_in_state >= self.green_duration:
            self._switch_state(LightState.YELLOW)
        elif (
            self.state == LightState.YELLOW
            and self.time_in_state >= self.yellow_duration
        ):
            # Flip between GREEN and RED (so yellow is always in between)
            self._switch_state(
                LightState.RED
                if self._previous_state == LightState.GREEN
                else LightState.GREEN
            )
        elif self.state == LightState.RED and self.time_in_state >= self.red_duration:
            self._switch_state(LightState.YELLOW)

        # Update all lights
        for light in self.traffic_lights:
            light.update(self.state)

    def _switch_state(self, new_state):
        self._previous_state = self.state
        self.state = new_state
        self.time_in_state = 0.0


class TrafficLightController:
    def __init__(self, traffic_lights, config):
        self.strategy = self._select_strategy(traffic_lights, config)

    def _select_strategy(self, traffic_lights, config):
        controller_type = config.get("lights", {}).get("controllerType", "fixed")

        if controller_type == "fixed":
            return FixedCycleTrafficLightController(traffic_lights, config)
        # elif controller_type == "adaptive":
        #     return AdaptiveTrafficLightController(traffic_lights, config)
        else:
            raise ValueError(
                f"Unknown traffic light controller type: {controller_type}"
            )

    def update(self, dt):
        self.strategy.update(dt)
