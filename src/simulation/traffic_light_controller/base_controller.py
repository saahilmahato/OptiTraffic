class BaseTrafficLightController:
    """Base class for traffic light control strategies."""

    def update(self, dt: float) -> None:
        """
        Updates the controller's state.

        Parameters:
            dt (float): Time delta in seconds since the last update.
        """
        raise NotImplementedError("Subclasses must implement the update method.")
