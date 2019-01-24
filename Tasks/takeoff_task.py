# Standard Library
import threading

# Ours
from task_base import TaskBase
from ..Utilities.drone_exceptions import TakeoffTimeoutException

class TakeoffTask(TaskBase):

    def __init__(self, drone, alt):
        super(TakeoffTask, self).__init__(drone)
        self._target_alt = alt
        self._finish_event = None
        self._error_event = None

    def perform(self):
        if self._finish_event is None:
            self._finish_event, self._error_event = self._drone.takeoff(
                self._target_alt, self._stop_event)
        elif self._error_event.is_set():
            self._error_event = None
            raise TakeoffTimeoutException
        elif self._finish_event.is_set():
            self._done = True
            return True

        return False

    @property
    def done(self):
        return self._done

    def exit_task(self):
        self._stop_event.set()
        if self._finish_event is not None and self._error_event is not None:
            return self._finish_event
        else:
            cancel_event = threading.Event()
            cancel_event.set()
            return cancel_event
