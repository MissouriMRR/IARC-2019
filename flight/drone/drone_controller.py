"""
A class for managing the order in which tasks are given to the drone,
checking for unsafe conditions, and sending data out to be graphed and
logged.
"""

import coloredlogs
from dronekit import connect, VehicleMode
import logging
import sys
from threading import Event
from time import sleep
import traceback

from math import radians
import config
from flight import constants as c
from drone import Drone
import exceptions
from flight.tasks import Hover, Takeoff, LinearMovement, Land, Exit, TakeoffSim, Yaw
from flight.utils.priority_queue import PriorityQueue
from flight.utils.timer import Timer
from tools.data_distributor.data_splitter import DataSplitter

SAFETY_CHECKS_TAG = "Safety Checks"
LOGGING_AND_RTG_TAG = "Logging and RTG"

LOG_LEVEL = logging.INFO

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
    _is_simulation : bool
        Set to true when the code is intended for the simulator.
    _splitter : tools.data_distributor.DataSplitter
        Used to send (split) data between the logger and the real-time grapher.
    """

    def __init__(self, is_simulation=False):
        """Construct a drone controller.

        Parameters
        ----------
        drone : c.Drone.{DRONE_NAME}
        is_simulation : bool, optional
            Set to true if being run with the simualator.
        """

        if is_simulation:
            drone_version = c.Drones.LEONARDO_SIM
        else:
            drone_version = c.Drones.LEONARDO

        self._task_queue = PriorityQueue()
        self._current_task = None
        self._safety_event = Event()

        self._is_simulation = is_simulation

        # Initialize the logger
        self._logger = logging.getLogger(__name__)
        coloredlogs.install(LOG_LEVEL)

        # Initialize the data splitter
        # NOTE: Real-time graphing not yet tested
        self._splitter = DataSplitter(
            logger_desired_headers=[header for header in
                                    c.ATTRIBUTE_TO_FUNCTION.keys()],
            use_rtg=False
        )

        # Connect to the drone
        self._logger.info('Connecting...')
        connection_string = c.CONNECTION_STR_DICT[drone_version]
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
            timer = Timer()
            # Start up safety checking
            timer.add_callback(
                SAFETY_CHECKS_TAG, c.SAFETY_CHECKS_DELAY,
                self._do_safety_checks,
                recurring=True)

            # Start up logging/real-time-graphing (if active)
            if self._splitter.active_tools:
                timer.add_callback(LOGGING_AND_RTG_TAG, c.LOGGING_DELAY,
                                   lambda: self._splitter.send(
                                       self._gather_data()),
                                   recurring=True)

            # NOTE: the only way to stop the loop is to raise an exception,
            # such as with a keyboard interrupt
            while self._update():
                # Check that safe conditions have not been violated
                if self._safety_event.is_set():
                    timer.stop_callback(SAFETY_CHECKS_TAG)
                    raise self._exception  # Only set when exception is found
                # Let the program breath
                sleep(c.DELAY_INTERVAL)

        except BaseException as e:
            self._logger.warning('Emergency landing initiated!')

            # Only print stack trace for completely unexpected things
            self._logger.critical(type(e).__name__)
            if config.DEBUG is True:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,
                                          limit=2, file=sys.stdout)

            # Land the drone
            self._land()
            self._logger.info('Finished emergency land')

            # Stop logging/graphing
            timer.stop_callback(LOGGING_AND_RTG_TAG)
            sleep(c.DELAY_INTERVAL)  # Sleep in case was doing write operation
            self._splitter.exit()

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
        new_task = Hover(self._drone, altitude, duration)
        self._task_queue.push(priority, new_task)

    def add_takeoff_task(self, altitude, priority=c.Priorities.HIGH):
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
        if self._is_simulation:
            new_task = TakeoffSim(self._drone, altitude)
        else:
            new_task = Takeoff(self._drone, altitude)

        self._task_queue.push(priority, new_task)

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
        new_task = LinearMovement(self._drone, direction, duration)
        self._task_queue.push(priority, new_task)

    def add_land_task(self, priority=c.Priorities.MEDIUM):
        """Instruct the drone to land.

        Parameters
        ----------
        priority : Priorities.{LOW, MEDIUM, HIGH}, optional
            The importance of this task.
        """
        new_task = Land(self._drone)
        self._task_queue.push(priority, new_task)

    def add_exit_task(self, priority=c.Priorities.HIGH):
        """Causes the controller to shut itself down.

        Notes
        -----
        Always has high priority
        """
        new_task = Exit(self._drone)
        self._task_queue.push(priority, new_task)
    
    def add_yaw_task(self, heading, priority=c.Priorities.MEDIUM):
        """Instructs the drone to yaw.
        Parameters
        ----------
        heading : int
            The heading for the drone to go to.
        priority : constants.Priorities
            The priority of the yaw task
        """
        new_task = Yaw(self._drone, heading)
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
                if isinstance(self._current_task, Exit):
                    return False
                self._task_queue.pop()

        # Grab reference of previous task for comparison
        prev_task = self._current_task

        # Set new task, if one of higher priority exists
        self._current_task = self._task_queue.top()

        # If task has been updated and not updated to None...
        if (prev_task is not self._current_task and
                self._current_task is not None):
            self._logger.info('Starting {}...'.format(
                type(self._current_task).__name__))

        # If there are no more tasks, begin to hover.
        if self._drone.armed and self._current_task is None:
            self._logger.info('No more tasks - beginning long hover')
            self.add_hover_task(config.DEFAULT_ALTITUDE,
                                c.DEFAULT_HOVER_DURATION)

        return True

    def _do_safety_checks(self):
        """Check for exceptional conditions."""
        try:
            if self._drone.airspeed > config.SPEED_THRESHOLD:
                raise exceptions.VelocityExceededThreshold()

            if (
                    self._drone.rangefinder.distance > config.MAXIMUM_ALLOWED_ALTITUDE):
                raise exceptions.AltitudeExceededThreshold()
            if abs(self._drone.attitude.roll) > radians(c.MAXIMUM_PITCH_ROLL):
                raise exceptions.RollExceededMaximum()

            if abs(self._drone.attitude.pitch) > radians(c.MAXIMUM_PITCH_ROLL):
                raise exceptions.PitchExceededMaximum()

        except Exception as e:
            self._exception = e  # This variable only set when exception found
            self._safety_event.set()

        # TODO: Add more safety checks here

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

    def _gather_data(self):
        """Puts all gatherable data into a dictionary.

        Notes
        -----
        Used to send a dictionary of data to a DataSplitter object, which logs
        and potential graphs the data.

        Some of the attributes we graph require pulling class attributes:
            Ex. rangefinder.distance
        While for other just the class itself is fine:
            Ex. airspeed
        In addition, some attributes require you to index into them for data:
            Ex. velocity[0] => x velocity

        Hence the ugly if elif elif structure beow.

        Returns
        -------
        dict
        """
        data = {}
        for attr_name, attr in c.ATTRIBUTE_TO_FUNCTION.iteritems():
            if len(attr) == 1:
                data[attr_name] = getattr(self._drone, attr[c.ATTR_NAME])
            elif len(attr) == 2 and isinstance(attr[c.ATTR_DETAIL], int):
                data[attr_name] = getattr(
                    self._drone, attr[c.ATTR_NAME])[attr[c.ATTR_DETAIL]]
            elif len(attr) == 2 and isinstance(attr[c.ATTR_DETAIL], str):
                data[attr_name] = getattr(
                    getattr(self._drone, attr[c.ATTR_NAME]),
                    attr[c.ATTR_DETAIL])

        return data