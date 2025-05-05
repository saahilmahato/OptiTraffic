from src.simulation.traffic_light import LightState

class TrafficLightController:
    def __init__(self, traffic_lights, config):
        self.traffic_lights = traffic_lights
        self.green_duration = config.get("lights", {}).get("greenTime", 5)
        self.yellow_duration = config.get("lights", {}).get("yellowTime", 2)
        self.red_duration = config.get("lights", {}).get("redTime", 5)

        self.cycle_time = self.green_duration + self.yellow_duration + self.red_duration
        self.time_elapsed = 0.0

    def update(self, dt):
        self.time_elapsed += dt
        t = self.time_elapsed % self.cycle_time

        if t < self.green_duration:
            state = LightState.GREEN
        elif t < self.green_duration + self.yellow_duration:
            state = LightState.YELLOW
        else:
            state = LightState.RED

        for light in self.traffic_lights:
            light.update(state)
