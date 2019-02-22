"""
A class that acts as an interface to the physical drone, allowing for the
reading of sensor data and control of movement.
"""

from dronekit import Vehicle, VehicleMode
import logging
from math import radians
from pymavlink import mavutil
import time

from optical_flow_attribute import OpticalFlow
from flight import constants as c
from flight.utils.helpers import to_quaternion

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

    def __init__(self, *args):
        super(Drone, self).__init__(*args)
        self._id = None
        self._logger = logging.getLogger(__name__)

        self._optical_flow = OpticalFlow()

        # Allow us to listen for optical flow dat
        @self.on_message(c.OPTICAL_FLOW_MESSAGE)
        def listener(self, name, message):
            """
            The listener is called for messages that contain the string specified
            in the decorator,passing the vehicle, message name, and the message.
            """
            self._optical_flow.time_usec = message.time_usec
            self._optical_flow.sensor_id = message.sensor_id
            self._optical_flow.flow_x = message.flow_x
            self._optical_flow.flow_y = message.flow_y
            self._optical_flow.flow_comp_m_x = message.flow_comp_m_x
            self._optical_flow.flow_comp_m_y = message.flow_comp_m_y
            self._optical_flow.quality = message.quality
            self._optical_flow.ground_distance = message.ground_distance

            # Notify all observers of new message (with new value)
            #   Note that argument `cache=False` by default so listeners
            #   are updaed with every new message
            self.notify_attribute_listeners(
                c.OPTICAL_FLOW_MESSAGE.lower(), self._optical_flow)

    @property
    def optical_flow(self):
        """Get data from the optical flow sensor.

        Notes
        -----
        See optical_flow_attribute.py for what kind of data you can get.
        """
        return self._optical_flow

    @property
    def id(self):
        """Get the drone's id"""
        return self._id

    @id.setter
    def id(self, identifier):
        """Set the drone's id."""
        self._id = identifier

    def set_attitude(self, roll, pitch, yaw, thrust):
        """Set the drones attitude.

        Parameters
        ----------
        roll : float
            The roll angle.
        pitch : float
            The pitch angle.
        yaw : float
            The yaw rate.
        thrust : float between 0 and 1
            The thrust value.

        Notes
        -----
        If thrust < 0.5, the drone will lose altitude
        If thrust == 0.5, the drone will retain its altitude
        If thrust > 0.5, the drone will gain altitude
        """
        msg = self._make_attitude_message(roll, pitch, yaw, thrust)

        self.send_mavlink(msg)

    def send_velocity(self, north, east, down):
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

    def arm(self, mode=c.Modes.GUIDED.value):
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
        self.mode = VehicleMode(mode)

        self._logger.info('Arming...')
        while not self.armed:
            self.armed = True
            time.sleep(c.ARM_RETRY_DELAY)

        if self.armed:
            self._logger.info('Armed')
        else:
            self._logger.error('Failed to arm')

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
            c.MavBitmasks.SET_POSITION_TARGET.value, # type_mask (only speeds enabled)
            0, # lat_int - X Position in WGS84 frame in 1e7 * meters
            0, # lon_int - Y Position in WGS84 frame in 1e7 * meters
            0, # alt - Altitude in meters in AMSL altitude(not WGS84 if absolute or relative)
            # altitude above terrain if GLOBAL_TERRAIN_ALT_INT
            north, # X velocity in NED frame in m/s
            east, # Y velocity in NED frame in m/s
            down, # Z velocity in NED frame in m/s
            0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
            0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)

    def _make_attitude_message(self, roll, pitch, yaw, thrust):
        """Set the attitude of the drone.

        Parameters
        ----------
        roll : float
            The roll angle.
        pitch : float
            The pitch angle.
        yaw : float
            The yaw rate.
        thrust : float between 0 and 1
            The thrust value.
        """
        # Thrust >  0.5: Ascend
        # Thrust == 0.5: Hold the altitude
        # Thrust <  0.5: Descend
        return self.message_factory.set_attitude_target_encode(
            0, # time_boot_ms
            1, # Target system
            1, # Target component
            c.MavBitmasks.SET_ATTITUDE_TARGET.value, # Type mask: bit 1 is LSB
            to_quaternion(roll, pitch), # Quaternion
            0, # Body roll rate in radians
            0, # Body pitch rate in radians
            radians(yaw), # Body yaw rate in radians
            thrust  # Thrust
        )
