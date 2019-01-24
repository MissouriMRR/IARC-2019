# Standard Library
import threading

# Ours
from task_base import TaskBase

class MovementTask(TaskBase):

    def __init__(self, drone, movement_queue):
        super(MovementTask, self).__init__(drone)
        self._currentMovement = None
        self._movement_queue = movement_queue

    def perform(self):
        # If there is not current movement and the queue is not empty,
        # pop the queue and start the movement
        if self._currentMovement is None and len(self._movement_queue):
            direction, distance = self._movement_queue.popleft()
            self._currentMovement = self._drone.move(
                direction, distance, self._stop_event)

        # If current movement is still none, we ran out of movements and are
        # done
        if self._currentMovement is None:
            self._done = True
            return True
        # If the movement is finished, set current movement to none
        elif self._currentMovement.is_set():
            # Reset the current movement and allow a new movement to begin
            self._currentMovement = None

        return False

    @property
    def done(self):
        return self._done

    def exit_task(self):
        self._stop_event.set()

        if self._currentMovement is not None:
            return self._currentMovement
        else:
            cancel_event = threading.Event()
            cancel_event.set()
            return cancel_event

