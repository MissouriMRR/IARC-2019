from dronekit import VehicleMode

from task_base import TaskBase
from .. import constants as c

class LandTask(TaskBase):
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
        super(LandTask, self).__init__(drone)
        self._land_mode = VehicleMode(c.Modes.LAND.value)

    def perform(self):
        if not self._drone.mode == self._land_mode:
            self._drone.mode = self._land_mode
            return False

        return not self._drone.armed
