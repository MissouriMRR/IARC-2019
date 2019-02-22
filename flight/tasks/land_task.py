"""A TaskBase subclass for landing the drone."""

from dronekit import VehicleMode

from task_base import TaskBase
from flight import constants as c

class Land(TaskBase):
    """A task that makes the drone land.

    Attributes
    ----------
    _land_mode : dronekit.VehicleMode
        A reference to dronekit's land mode object
    """

    def __init__(self, drone):
        """Initialize a task for landing.

        Parameters
        ----------
        drone : dronekit.Vehicle
            The drone being controlled.
        """
        super(Land, self).__init__(drone)
        self._land_mode = VehicleMode(c.Modes.LAND.value)

    def perform(self):
        """Perform one iteration of land."""
        if not self._drone.mode == self._land_mode:
            self._drone.mode = self._land_mode
            return False

        return not self._drone.armed
