"""A TaskBase subclass for taking off the drone."""

import config
from task_base import TaskBase

class Takeoff(TaskBase):
    """A task that takes off the drone from the ground.

    Attributes
    ----------
    _target_alt : float
        How many meters off the ground to take off to.
    """

    def __init__(self, drone, altitude):
        """Initialize a task for taking off.

        Parameters
        ----------
        drone : dronekit.Vehicle
            The drone being controlled
        altitude : float
            How many meters off the ground to take off to.
        """
        super(Takeoff, self).__init__(drone)
        self._target_alt = altitude

    def perform(self):
        """Perform one iteration of takeoff."""
        if not self._drone.armed:
            self._drone.arm()

        current_altitude = self._drone.rangefinder.distance

        if current_altitude >= self._target_alt * config.PERCENT_TARGET_ALTITUDE:
            return True

        thrust = config.DEFAULT_TAKEOFF_THRUST

        self._drone.set_attitude(0, 0, 0, thrust)
        return False
