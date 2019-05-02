"""
A class that acts as an interface to the physical drone, allowing for the
reading of sensor data and control of movement.
"""

from dronekit import Vehicle, VehicleMode
import logging
from math import radians, sin, cos
from pymavlink import mavutil
import time

ARM_RETRY_DELAY = 0.1
GUIDED = "GUIDED"
LAND = "LAND"

def to_quaternion(roll=0.0, pitch=0.0, yaw=0.0):
    """Convert degrees to quaternions.
    Parameters
    ----------
    roll : float
        The roll angle.
    pitch : float
        The pitch angle.
    yaw : float
        The yaw rate.
    See https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Source_Code
    """
    t0 = cos(radians(yaw * 0.5))
    t1 = sin(radians(yaw * 0.5))
    t2 = cos(radians(roll * 0.5))
    t3 = sin(radians(roll * 0.5))
    t4 = cos(radians(pitch * 0.5))
    t5 = sin(radians(pitch * 0.5))

    w = t0 * t2 * t4 + t1 * t3 * t5
    x = t0 * t3 * t4 - t1 * t2 * t5
    y = t0 * t2 * t5 + t1 * t3 * t4
    z = t1 * t2 * t4 - t0 * t3 * t5

    return [w, x, y, z]

class Drone(Vehicle):
    """Interface to drone and its sensors.
    Attributes
    ----------
    _id : int
        A unique identifier for this drone.
    _optical_flow : OpticalFlow
        An interface to the optical flow sensor
    Notes
    -----
    See http://python.dronekit.io/guide/vehicle_state_and_parameters.html for
    all of the attributes we get by subclassing dronekit.Vehicle.
    """
    current_altitude = 0 #current altitude

    def __init__(self, *args):
        super(Drone, self).__init__(*args)
        self._id = 1
        self.doing_command = False
        self._logger = logging.getLogger(__name__)

    @property
    def id(self):
        """Get the drone's id"""
        return self._id

    @id.setter
    def id(self, identifier):
        """Set the drone's id."""
        self._id = identifier

    def send_velocity(self, north=0, east=0, down=0):
        """Send velocity to the drone.
        Parameters
        ----------
        north : float
        east : float
        down : float
        Notes
        -----
        This method used the NED coordinate system. Of note is that sending a
        positive value for down will make the drone lose altitude.
        """
        msg = self._make_velocity_message(north, east, down)
        self.send_mavlink(msg)

    def send_rel_pos(self, north=0, east=0, down=0):
        """Send position drone should travel in.
        Parameters
        ----------
        north : float
        east : float
        down : float
        Notes
        -----
        This method used the NED coordinate system. Of note is that sending a
        positive value for down will make the drone lose altitude.
        """
        msg = self._make_relative_move_message(north, east, down)
        self.send_mavlink(msg)

    def send_yaw(self, heading, direction):
        """Send yaw to the drone.
        Parameters
        ----------
        heading : int
            the relative heading for the drone to move
        direction : int
            -1 for ccw and 1 for cw
        """
        # create the CONDITION_YAW command using command_long_encode()
        msg = self._make_yaw_message(heading, yaw_direction=direction)
        # send command to vehicle
        self.send_mavlink(msg)

    def arm(self, mode=GUIDED):
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
        self._logger.info('Drone {}: Entering GUIDED mode...'.format(self.id))
        while self.mode != GUIDED:
            self.mode = VehicleMode(mode)
        self._logger.info('Drone {}: Now in GUIDED mode...'.format(self.id))

        self._logger.info('Drone {}: Arming...'.format(self.id))
        while not self.armed:
            self.armed = True
            time.sleep(ARM_RETRY_DELAY)

        if self.armed:
            self._logger.info('Drone {}: Armed'.format(self.id))
        else:
            self._logger.error('Drone {}: Failed to arm'.format(self.id))

    def land(self):
        self._logger.info('Drone {}: Trying to land...'.format(self.id))
        while self.mode != LAND:
            self.mode = VehicleMode(LAND)
        self._logger.info('Drone {}: land mode achieved'.format(self.id))

    def _make_velocity_message(self, north, east, down):
        """Construct a mavlink message for sending velocity.
        Parameters
        ----------
        north : float
        east : float
        down : float
        Returns
        -------
        MAVLink_message (a DroneKit object)
            Message which moves the drone at a certain velocity.
        see http://python.dronekit.io/examples/guided-set-speed-yaw-demo.html#send-global-velocity
        """
        return self.message_factory.set_position_target_global_int_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame
            0b0000111111000111, # type_mask (only speeds enabled)
            0, # lat_int - X Position in WGS84 frame in 1e7 * meters
            0, # lon_int - Y Position in WGS84 frame in 1e7 * meters
            0, # alt - Altitude in meters in AMSL altitude(not WGS84 if absolute or relative)
            # altitude above terrain if GLOBAL_TERRAIN_ALT_INT
            north, # X velocity in NED frame in m/s
            east, # Y velocity in NED frame in m/s
            down, # Z velocity in NED frame in m/s
            0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    def _make_relative_move_message(self, north, east, down):
        """Construct a mavlink message for sending velocity.
        Parameters
        ----------
        north : float
        east : float
        down : float
        Returns
        -------
        MAVLink_message (a DroneKit object)
            Message which moves the drone at a certain velocity.
        see http://python.dronekit.io/examples/guided-set-speed-yaw-demo.html#send-global-velocity
        """
        return self.message_factory.set_position_target_local_ned_encode(
            0,       # time_boot_ms (not used)
            0, 0,    # target system, target component
            mavutil.mavlink.MAV_FRAME_BODY_OFFSET_NED, # frame
            0b0000111111111000, # type_mask (only speeds enabled)
            north, # lat_int - X Position in WGS84 frame in 1e7 * meters
            east, # lon_int - Y Position in WGS84 frame in 1e7 * meters
            down, # alt - Altitude in meters in AMSL altitude(not WGS84 if absolute or relative)
            # altitude above terrain if GLOBAL_TERRAIN_ALT_INT
            0, 0, 0, # x, y, z velocity in m/s
            0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    def _make_yaw_message(self, heading, yaw_speed=1, yaw_direction=1, relative=True):
        return self.message_factory.command_long_encode(
            0, 0, # target system, target component
            mavutil.mavlink.MAV_CMD_CONDITION_YAW, #command
            0, #confirmation
            heading, # param 1, yaw in degrees
            yaw_speed, # param 2, yaw speed deg/s
            yaw_direction, # param 3, direction -1 ccw, 1 cw
            relative, # param 4, relative offset 1, absolute angle 0
            0, 0, 0) # param 5 ~ 7 not used

    def _set_altitude(self): #checks and modifies current altitude
        if self.rangefinder.distance >= 1 and abs(self.rangefinder.distance - self.location.global_frame.alt) < 25:
            Drone.current_altitude = self.rangefinder.distance
            return 
        elif self.rangefinder.distance >= 1 and abs(self.rangefinder.distance - self.location.global_frame.alt) > .25:
            Drone.current_altitude = self.location.global_frame.alt
            return 
        elif self.rangefinder.distance < 1 and abs(self.rangefinder.distance - self.location.global_frame.alt) < .25: 
            Drone.current_altitude = self.rangefinder.distance
            return
        else: return
