# Standard Library
import coloredlogs
import heapq
import logging
from time import sleep
import traceback
import sys

# Ours
from drone_controller_base import DroneControllerBase
from ..Instructions.movement_instruction import MovementInstruction
from ..Tasks.hover_task import HoverTask
from ..Tasks.takeoff_task import TakeoffTask
from ..Utilities import constants as c
from ..Utilities import drone_exceptions
from ..Utilities.helper import current_thread_name
from ..Utilities.lock import SharedLock

class DroneController(DroneControllerBase):
    """Manages the control logic of a drone.

    Notes
    -----
    See drone_controller_base.py for documentation.
    """
    def __init__(self, drone):
        super(DroneController, self).__init__()

        self._logger = logging.getLogger(__name__)
        self._debug = True

        self.drone = drone

        coloredlogs.install(level='DEBUG')

        # The following two lines are purely for testing purposes. Instructions
        # will be pushed onto the heap as a result of the swarm controller
        # sending instructions or inter-drone communication.
        heapq.heappush(
            self._instruction_queue, (0, MovementInstruction((5, 5, 0))))
        heapq.heappush(
            self._instruction_queue, (0, MovementInstruction((-5, -5, 0))))

    def run_loop(self):
        SharedLock.get_lock().acquire()
        self._logger.info(
            '{}: Main control loop starting'.format(current_thread_name()))
        SharedLock.get_lock().release()

        try:
            # Connect to low-level controller
            self.drone.connect(c.DRONES[c.Drones.LEONARDO_SIM])

            # Arm the drone for flight
            self.drone.arm()

            # Set up a takeoff task
            self._task = TakeoffTask(self.drone, 1)

            # NOTE: the only way to stop the loop is to raise an exceptions,
            # such as with a keyboard interrupt
            while True:
                self.do_safety_checks()
                self._update()
                sleep(c.SHORT_INTERVAL)

        except BaseException as e:
            self._logger.warning(
                '{}: Emergency landing initiated'.format(
                    current_thread_name()))
            # Only print stack trace for completely unexpected things
            self._logger.critical(type(e).__name__)
            if self._debug is True:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)

            # If a connection was never establish in the first place, return
            if not self.drone.connected:
                return True

            # If currently have a task, exit it
            if self._task is not None and not self._task.done:
                exit_event = self._task.exit_task()
                exit_event.wait()

            # Land the drone
            land = self.drone.land()
            land.wait()
            self._logger.info(
                '{}: Landing complete - main control loop stopping'.format(
                    current_thread_name()))

    def _update(self):
        if self._task is not None:
            # Do one iteration of whichever task we are in
            result = self._task.perform()

            # If we are done, set the task to None so that
            # we can move on to the next instruction
            if result:
                self._task = None

        if isinstance(self._task, HoverTask) or self._task is None:
            # Process remaining instructions
            if len(self._instruction_queue):
                # Stop hovering, if we were doing so
                if isinstance(self._task, HoverTask):
                    stop_hover_event = self._task.exit_task()
                    stop_hover_event.wait()
                    self._task = None
                self._read_next_instruction()
            # If there are no instructions, begin to hover
            else:
                if self._task is None:
                    self._task = HoverTask(self.drone)

    def _read_next_instruction(self):
        if len(self._instruction_queue):
            self._current_instruction = heapq.heappop(
                self._instruction_queue)[1]
            self._task = self._current_instruction.get_task(self.drone)

    def do_safety_checks(self):
        """Check for exceptional conditions."""
        if not self.drone.connected:
            return

        if self.drone.speed > c.SPEED_THRESHOLD:
            raise drone_exceptions.VelocityExceededThreshold()

        if (self.drone.altitude_rangefinder > c.MAXIMUM_ALLOWED_ALTITUDE
                or self.drone.altitude_barometer > c.MAXIMUM_ALLOWED_ALTITUDE):
            raise drone_exceptions.AltitudeExceededThreshold()

        if (self.drone.altitude_rangefinder
                < c.RANGEFINDER_MIN - c.RANGEFINDER_EPSILON -.5):
            raise drone_exceptions.RangefinderMalfunction()

        # TODO: Add more safety checks here
