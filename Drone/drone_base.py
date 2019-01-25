# Standard Library
import abc
import dronekit
import logging
import time
import threading

# Ours
from ..Utilities import constants as c
from ..Utilities import dronekit_wrappers
from ..Utilities.helper import current_thread_name
from ..Utilities.timer import Timer

class DroneBase(object):
    """Interface to drone and to sensors.

    Attributes
    ----------
    _connected: bool
        True if the drone is connected to ardupilot.
    _vehicle : DroneKit.Vehicle
        Interface for controlling drone.
    _logger
        Write messages to command line.
    _simulation_multiplier : float
        Value by which the default speed is multiplied in order to offset
        simulation the real-time factor.
    devices : list of Device
        Interface to the drone's devices, such as camera

    """
    __metaclass__ = abc.ABCMeta

    count = 0 # Used to identify threads

    def __init__(self):
        self._vehicle = None
        self._connected = False
        self._logger = logging.getLogger(__name__)
        self._simulation_multiplier = None

        self.devices = []

    def connect(self, name, simulation_multiplier=1):
        """Connect drone to ardupilot.

        Upon a successful connection, the drone is now suitable to be armed.

        Parameters
        ----------
        name : str
            The connection string that should be used to connect to drone.
        simulation_multiplier : float
            Value by which the default speed is multiplied in order to offset
            simulation the real-time factor.

        Returns
        -------
        bool
            True if connection was successful and false otherwise.

        Notes
        -----
        See http://python.dronekit.io/automodule.html#dronekit.connect
        """
        self._simulation_multiplier = simulation_multiplier

        self._vehicle = dronekit.connect(
            name, wait_ready=True,
            heartbeat_timeout=c.HEARTBEAT_TIMEOUT, status_printer=None)

        thread_name = current_thread_name()
        self._logger.info(
            '{} : Connecting to ardupilot'.format(
                thread_name))

        if self._vehicle is not None:
            self._connected = True

        return self._connected

    @property
    def altitude_rangefinder(self):
        """Get the drone's altitude as read by rangefinder.

        Returns
        -------
        double
            The distance from the ground.
        """
        return self._vehicle.rangefinder.distance

    @property
    def altitude_barometer(self):
        """Get the drone's altitude as read by barometer.

        Returns
        -------
        double
            The distance from the ground.
        """
        return self._vehicle.location.global_relative_frame.alt

    @property
    def speed(self):
        """Get the drone's air speed.

        Returns
        -------
        double
            Air speed.
        """
        return self._vehicle.airspeed

    def arm(self, timeout=c.DEFAULT_ARM_TIMEOUT, mode=c.Modes.GUIDED.value):
        """Arm the drone for flight.

        Upon successfully arming, the drone is now suitable to take off. The
        drone should be connected before calling this function.

        Parameters
        ----------
        timeout : int, optional
            The duration in seconds that arming should be attempted before
            timing out
        mode : {GUIDED}, optional

        Returns
        -------
        bool
            True if successfully armed and false otherwise.

        Notes
        -----
        Only guided mode is currently supported.
        """
        self._vehicle.mode = dronekit.VehicleMode(mode)

        self._logger.info('{}: Arming'.format(current_thread_name()))
        timer = Timer()
        while (not self._vehicle.armed) and (timer.elapsed < timeout):
            self._vehicle.armed = True
            time.sleep(c.ARM_RETRY_DELAY)

        status_msg = 'Failed to arm' if not self._vehicle.armed else 'Armed'
        logging_function = (self._logger.info if self._vehicle.armed
            else self._logger.error)
        logging_function('{}: {}'.format(current_thread_name(), status_msg))
        return self._vehicle.armed


    @property
    def connected(self):
        """Get connection status.

        Returns
        -------
        bool
            True if the drone is connected to ardupilot and false otherwise.
        """
        return self._connected

    @property
    def armed(self):
        """Get armed status.

        Returns
        -------
        Boolean
            True if the drone is armed and false otherwise.
        """
        return self._vehicle.armed

    def takeoff(self, target_altitude, stop_event,
        cutoff_time=c.DEFAULT_TAKEOFF_TIMEOUT):
        """Fly the drone from resting state.

        Taking off requires that the drone has already been connected and
        armed.

        Parameters
        ----------
        target_altitude : int
            The height in meters the drone should be off the ground after this
            function completes.
        stop_event : threading.Event
            Event which is set when takeoff should be canceled.
        cutoff_time : float, optional
            The time after which takeoff is considered unsuccessful and times
            out.

        Returns
        -------
        finished, error : threading.Event, threading.Event
            The finished event is set upon successful takeoff, and the error
            event is set upon error during takeoff.
        """
        def takeoff_thread(target_altitude, finished, stop_event, error_event,
            timeout=cutoff_time):
            self._logger.info(
                '{}: Starting takeoff'.format(current_thread_name()))
            thrust = c.DEFAULT_TAKEOFF_THRUST

            timeout = False
            timer = Timer()
            while timer.elapsed < cutoff_time:
                if stop_event.is_set():
                    self._logger.info(
                        '{}: Halting takeoff'.format(current_thread_name()))
                    break

                current_altitude = self.altitude_rangefinder

                if (current_altitude >= target_altitude
                        * c.PERCENT_TARGET_ALTITUDE):
                    break
                elif (current_altitude >= target_altitude
                        * c.PERCENT_ALTITUDE_THRUST_ADJUSTMENT_THRESHOLD):
                    thrust = c.SMOOTH_TAKEOFF_THRUST

                msg = dronekit_wrappers.set_attitude(
                    self._vehicle.message_factory, thrust=thrust)
                self._vehicle.send_mavlink(msg)

                time.sleep(c.MAV_ATTITUDE_MSG_RESEND_DELAY)
            else:
                error_event.set()
                return

            logging.info('{}: Finished takeoff'.format(current_thread_name()))
            finished.set()

        finished = threading.Event()
        error = threading.Event()
        thread_name = 'TakeoffThread-{}'.format(str(DroneBase.count))
        threading.Thread(
            target=takeoff_thread, name=thread_name,
            args=(target_altitude, finished, stop_event, error)
            ).start()

        DroneBase.count += 1
        return finished, error

    def land(self):
        """Land the drone.

        The flight mode is set to land.

        Returns
        -------
        finished : threading.Event
            The finished event is set upon successful landing
        """
        def land_thread(finished):
            self._logger.info(
                '{}: Starting land'.format(current_thread_name()))
            land_mode = dronekit.VehicleMode(c.Modes.LAND.value)
            while not self._vehicle.mode == land_mode:
                self._vehicle.mode = land_mode
            while self._vehicle.armed:
                pass

            self._logger.info(
                '{}: Finished land'.format(current_thread_name()))
            finished.set()

        finished = threading.Event()
        thread_name = 'LandThread-{}'.format(str(DroneBase.count))
        threading.Thread(
            target=land_thread, name=thread_name, args=(finished,)
            ).start()
        DroneBase.count += 1
        return finished

    def move(self, direction, distance, stop_event, speed=c.DEFAULT_SPEED,
        send_delay=c.MAV_VELOCITY_MSG_RESEND_DELAY):
        """Move the drone along a path.

        Movements should only be called when the drone has taken off.

        Parameters
        ----------
        direction : {UP, DOWN, LEFT, RIGHT, FORWARD, BACK}
            The direction that the drone should travel in.
        distance : float
            The distance in meters that the drone should travel in the given
            direction.
        emergency_land : threading.Event
            An event to set when movement should be canceled.

        Returns
        -------
        finished : threading.Event
            The finished event is set upon completing the move.

        Notes
        -----
        The directions are defined in the Directions enum (see constants.py).
        """

        # Calculate duration to send velocity command based on distance and
        # velocity
        duration = (distance / speed) * self._simulation_multiplier

        # Multiply unit vector in direction by the velocity
        vector = tuple(speed * n for n in direction.value)

        # Make the mavlink message
        msg = dronekit_wrappers.get_velocity_message(
                self._vehicle.message_factory, vector)

        def move_thread(msg, duration, finished, stop_event,
            delay=send_delay):
            self._logger.info(
                '{}: Starting move'.format(current_thread_name()))
            # Send the message once every delay seconds
            timer = Timer()
            timer.add_callback(
                "move_msg", delay,
                lambda : self._vehicle.send_mavlink(msg),
                recurring=True)

            if stop_event.wait(duration):
                msg = 'Movement halting'
            else:
                msg = 'Movement finished'

            timer.stop_callback("move_msg")
            self._logger.info(
                '{}: {}'.format(current_thread_name(), msg))

            finished.set()

        finished = threading.Event()
        thread_name = 'MovementThread-{}'.format(str(DroneBase.count))
        threading.Thread(
            target=move_thread, name=thread_name,
            args=(msg, duration, finished, stop_event)
            ).start()
        DroneBase.count += 1
        return finished


    def hover(self, duration, emergency_land,
        send_delay=c.MAV_HOVER_MSG_RESEND_DELAY):
        """Hover the drone at current location.

        Hover should only be called when the drone has taken off.

        Parameters
        ----------
        duration : float
            The number of seconds that the drone should hover in place.
        emergency_land : threading.Event
            An event to set when movement should be canceled.

        Returns
        -------
        finished : threading.Event
            The finished event is set upon hovering the requested duration.
        """
        # Make the mavlink message
        msg = dronekit_wrappers.get_velocity_message(
                self._vehicle.message_factory, (0, 0, 0))

        def hover_thread(msg, duration, finished, stop_event,
            delay=send_delay):
            self._logger.info(
                '{}: Starting hover'.format(current_thread_name()))
            # Send the message once every delay seconds
            timer = Timer()
            timer.add_callback(
                "move_msg", delay,
                lambda : self._vehicle.send_mavlink(msg),
                recurring=True)

            if stop_event.wait(duration):
                msg = 'Hover halting'
            else:
                msg = 'Hover finished'

            timer.stop_callback("move_msg")
            self._logger.info(
                '{}: {}'.format(current_thread_name(), msg))

            finished.set()

        finished = threading.Event()
        thread_name = 'HoverThread-{}'.format(str(DroneBase.count))
        threading.Thread(
            target=hover_thread, name=thread_name,
            args=(msg, duration, finished, emergency_land)
            ).start()
        DroneBase.count += 1
        return finished

    @abc.abstractmethod
    def load_devices(self):
        """Load a list of interfaces to physical devices, such as sensors.

        After calling this function, self.devices will be ready to use.
        """
        pass
