"""A TaskBase subclass for shutting down the drone controller."""

from simple_pid import PID
from dronekit import VehicleMode

from task_base import TaskBase
from flight.drone.exceptions import EmergencyLandException

class Exit(TaskBase):
    """A task that terminates control of the drone."""

    def __init__(self, drone):
        """Initialize a task for terminating control.

        Parameters
        ----------
        drone : dronekit.Vehicle
            The drone being controlled.
        """
        super(Exit, self).__init__(drone)

    def perform(self):
        """Exit the controller.

        Notes
        -----
        This is a sentinel task that will cause the controller to shut down.
        """
        # If exit task was called while still in flight, then land.
        if self._drone.armed:
            raise EmergencyLandException

        # Since this is just a flag task, return immediately
        return True
