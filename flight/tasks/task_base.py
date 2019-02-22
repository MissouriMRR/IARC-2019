"""A class that abstracts the duties of a task the drone might perform."""

# Standard Library
import abc

class TaskBase():
    """A task the the drone can perform.

    Responsible for implementing the core logic of the various actions that a
    drone can take (ex. Movement, Follow, Heal, Decode). Must implement
    perform().

    Attributes
    ----------
    _drone: dronekit.vehicle
        An interface to the drone.
    _done: bool
        The status of the task.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, drone):
        self._drone = drone
        self._done = False

    @abc.abstractmethod
    def perform(self):
        """Do one iteration of the logic for this task.

        Returns
        --------
        bool
            True if the task is done with its goal, and false otherwise.
        """
        pass

    @property
    def done(self):
        return self._done
