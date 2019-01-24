# Standard Library
import threading

# Ours
from task_base import TaskBase
from ..Utilities import constants as c

class HoverTask(TaskBase):

    def __init__(self, drone, duration=c.DEFAULT_HOVER_DURATION):
        super(HoverTask, self).__init__(drone)
        self._movement = None
        self._duration = duration # 8 minutes default

    def perform(self):
        if self._movement is None:
            self._movement = self._drone.hover(self._duration, self._stop_event)
        elif self._movement.is_set():
            self._done = True
            return True

        return False

    @property
    def done(self):
        return self._done

    def exit_task(self):
        self._stop_event.set()
        if self._movement is not None:
            return self._movement
        else:
            cancel_event = threading.Event()
            cancel_event.set()
            return cancel_event
