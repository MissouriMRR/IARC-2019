import coloredlogs
from dronekit import connect, VehicleMode
import logging
import sys
from threading import Event
from time import sleep
import traceback

from drone import Drone
import exceptions
from .. import constants as c
from ..tasks.hover_task import HoverTask
from ..tasks.land_task import LandTask
from ..tasks.linear_movement_task import LinearMovementTask
from ..tasks.takeoff_task import TakeoffTask
from ..utils.priority_queue import PriorityQueue
from ..utils.timer import Timer
from ... import flightconfig as f

class DroneController(object):
    """Controls the actions of a drone.

    Responsible for managing the execution of tasks and checking for unsafe
    conditions.

    Attributes
    ----------
    _current_task : TaskBase subclass
        The task the drone is currently working on.
    _task_queue : list of InstructionBase subclass
        A PriorityQueue holding tasks to be performed.
    _safety_event : Event
        Set when an unsafe condition is observed.
    """

    def __init__(self, drone):
        """Construct a drone controller.

        Parameters
        ----------
        drone : c.Drone.{DRONE_NAME}"""
        self._task_queue = PriorityQueue()
        self._current_task = None
        self._safety_event = Event()

        # Initialize the logger
        self._logger = logging.getLogger(__name__)
        coloredlogs.install(level=logging.INFO)

        # Connect to the drone
        self._logger.info('Connecting...')
        connection_string = c.CONNECTION_STR_DICT[drone]
        self._drone = connect(
            connection_string, wait_ready=True,
            heartbeat_timeout=c.CONNECT_TIMEOUT, status_printer=None,
            vehicle_class=Drone)
        self._logger.info('Connected')

    def run(self):
        """Start the controller.

        Notes
        -----
        This method will block execution until it has finished.
        """
        self._logger.info('Controller starting')
        try:
            # Arm the drone for flight
            self._arm()

            # Start up safety checking
            safety_checks_timer = Timer()
            safety_checks_timer.add_callback(
                "safety_checks", c.SAFETY_CHECKS_DELAY, self._do_safety_checks,
                recurring=True)

            # NOTE: the only way to stop the loop is to raise an exception,
            # such as with a keyboard interrupt
            while self._update():
                # Check that safe conditions have not been violated
                if self._safety_event.is_set():
                    safety_checks_timer.shutdown()
                    raise self._exception # Only set when exception is found
                # Let the program breath
                sleep(c.DELAY_INTERVAL)

        except BaseException as e:
            self._logger.warning('Emergency landing initiated!')

            # Only print stack trace for completely unexpected things
            self._logger.critical(type(e).__name__)
            if f.DEBUG is True:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)

            # Land the drone
            self._land()
            self._logger.info('Finished emergency land')

    def add_hover_task(self, altitude, duration, priority=c.Priorities.LOW):
        """Instruct the drone to hover.

        Parameters
        ----------
        altitude : float
            The target altitude to hover at.
        duration : float
            How long to hover for.
        priority : Priorities.{LOW, MEDIUM, HIGH}, optional
            The importance of this task.
        """
        new_task = HoverTask(self._drone, altitude, duration)
        self._task_queue.push(priority, new_task)

    def add_takeoff_task(self, altitude):
        """Instruct the drone to takeoff.

        Parameters
        ----------
        altitude : float
            The target altitude to hover at.
        duration : float
            How long to hover for.

        Notes
        -----
        Internally, the priority of this task is always set to HIGH.
        """
        new_task = TakeoffTask(self._drone, altitude)
        self._task_queue.push(c.Priorities.HIGH, new_task)

    def add_linear_movement_task(
            self, direction, duration, priority=c.Priorities.MEDIUM):
        """Instruct the drone to move along one of cardinal axes.

        Parameters
        ----------
        direction : Directions.{UP, DOWN, LEFT, RIGHT, FORWARD, BACKWARD}
            The direction to travel in.
        duration : float
            How long to move for.
        priority : Priorities.{LOW, MEDIUM, HIGH}, optional
            The importance of this task.
        """
        new_task = LinearMovementTask(self._drone, direction, duration)
        self._task_queue.push(priority, new_task)


    def add_land_task(self, priority=c.Priorities.MEDIUM):
        """Instruct the drone to land.

        Parameters
        ----------
        priority : Priorities.{LOW, MEDIUM, HIGH}, optional
            The importance of this task.
        """
        new_task = LandTask(self._drone)
        self._task_queue.push(priority, new_task)

    def _update(self):
        """Execute one iteration of control logic.

        Returns
        -------
        True if should be called again, and false otherwise.
        """
        if self._current_task is not None:
            # Do one iteration of whichever task we are in
            result = self._current_task.perform()

            # If we are done, set the task to None so that
            # we can move on to the next instruction
            if result:
                # We are done with the task
                self._logger.info('Finished {}...'.format(
                    type(self._current_task).__name__))
                if isinstance(self._current_task, LandTask):
                    return False
                self._task_queue.pop()

        # Grab reference of previous task for comparison
        prev_task = self._current_task

        # Set new task, if one of higher priority exists
        self._current_task = self._task_queue.top()

        # If this condition is true, we have ourselves a new task
        if (prev_task is not self._current_task and
                self._current_task is not None):
            self._logger.info('Starting {}...'.format(
                type(self._current_task).__name__))

        # If there are no more tasks, begin to hover.
        if self._current_task is None:
            self._logger.info('No more tasks - beginning long hover')
            self.add_hover_task(f.DEFAULT_ALTITUDE, c.DEFAULT_HOVER_DURATION)

        return True

    def _do_safety_checks(self):
        """Check for exceptional conditions."""
        try:
            if self._drone.airspeed > f.SPEED_THRESHOLD:
                raise exceptions.VelocityExceededThreshold()

            if (self._drone.rangefinder.distance > f.MAXIMUM_ALLOWED_ALTITUDE):
                raise exceptions.AltitudeExceededThreshold()

        except Exception as e:
            self._exception = e # This variable only set when exception found
            self._safety_event.set()

        # TODO: Add more safety checks here

    def _arm(self, mode=c.Modes.GUIDED.value):
        """Arm the drone for flight.

        Upon successfully arming, the drone is now suitable to take off. The
        drone should be connected before calling this function.

        Parameters
        ----------
        mode : {GUIDED}, optional


        Notes
        -----
        Only guided mode is currently supported.
        """
        self._drone.mode = VehicleMode(mode)

        self._logger.info('Arming...')
        while not self._drone.armed:
            self._drone.armed = True
            sleep(c.ARM_RETRY_DELAY)

        status_msg = 'Failed to arm' if not self._drone.armed else 'Armed'
        logging_function = (self._logger.info if self._drone.armed
            else self._logger.error)
        logging_function('{}'.format(status_msg))

    def _land(self):
        """Land the drone.

        The flight mode is set to land.

        Returns
        -------
        finished : threading.Event
            The finished event is set upon successful landing
        """

        land_mode = VehicleMode(c.Modes.LAND.value)

        self._logger.info('Starting land...')
        while not self._drone.mode == land_mode:
            self._drone.mode = land_mode

        self._logger.info('Waiting for disarm...')
        while self._drone.armed:
            sleep(c.DELAY_INTERVAL)
        self._logger.info('Disarm complete')
        self._logger.info('Finished land')
