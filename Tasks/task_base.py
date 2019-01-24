# Standard Library
import abc
import threading

class TaskBase():
    """A task the the drone can perform.

    Responsible for implementing the core logic of the various actions that a
    drone can take (ex. Movement, Follow, Heal, Decode). Must, at a minimum,
    implement do(), is_done(), and exit_task().

    Attributes
    ----------
    _drone: dronekit.vehicle
        An interface to the drone.
    _done: bool
        The status of the task.
    _stop_event: threading.Event
        An event which is set when the task is exited.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self, drone):
        self._drone = drone
        self._done = False
        self._stop_event = threading.Event()

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
    @abc.abstractmethod
    def done(self):
        """Get the status of this task.

        Returns
        -------
        bool
            True if the task is done doing whatever is does, and False
            otherwise.
        """
        pass

    @abc.abstractmethod
    def exit_task(self):
        """Cancel this task.

        Takes the necessary actions to for the controller to safely exit the
        current task (ex. halting movement).

        Returns
        -------
        threading.Event
            The task has been safely exited once this event is set.
        """
        pass
