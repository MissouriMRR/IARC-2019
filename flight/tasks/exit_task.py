from simple_pid import PID
from dronekit import VehicleMode

from task_base import TaskBase
from .. import constants as c
from ..drone.exceptions import EmergencyLandException

class ExitTask(TaskBase):
    """A task that terminates control of the drone."""

    def __init__(self, drone):
        """Initialize a task for terminating control.

        Parameters
        ----------
        drone : dronekit.Vehicle
            The drone being controlled.
        """
        super(ExitTask, self).__init__(drone)

    def perform(self):
        # If exit task was called while still in flight, then land.
        if self._drone.armed:
            raise EmergencyLandException

        # Since this is just a flag task, return immediately
        return True
