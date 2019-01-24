# Standard Library
from math import radians, sin, cos
from pymavlink import mavutil

# Ours
from constants import DronekitBitmasks

def get_velocity_message(message_factory, (velocity_x, velocity_y, velocity_z)):
    """Construct a mavlink message for sending velocity.

    Parameters
    ----------
    message_factory : dronekit.vehicle.message_factory
        Used to create the message
    (velocity_x, velocity_y, velocity_z) : (Double, Double ,Double)
        The vector to travel along

    Returns
    -------
    MAVLink_message (a DroneKit object)
        Message which moves the drone at a certain velocity.

    see http://python.dronekit.io/examples/guided-set-speed-yaw-demo.html#send-global-velocity
    """
    return message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame
        DronekitBitmasks.SEND_VELOCITY_BITMASK.value, # type_mask (only speeds enabled)
        0, # lat_int - X Position in WGS84 frame in 1e7 * meters
        0, # lon_int - Y Position in WGS84 frame in 1e7 * meters
        0, # alt - Altitude in meters in AMSL altitude(not WGS84 if absolute or relative)
        # altitude above terrain if GLOBAL_TERRAIN_ALT_INT
        velocity_x, # X velocity in NED frame in m/s
        velocity_y, # Y velocity in NED frame in m/s
        velocity_z, # Z velocity in NED frame in m/s
        0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink)


def set_attitude(message_factory, roll_angle = 0.0, pitch_angle = 0.0, yaw_rate = 0.0,
    thrust = 0.5):
    """Set the attitude of the drone."""
    # Thrust >  0.5: Ascend
    # Thrust == 0.5: Hold the altitude
    # Thrust <  0.5: Descend
    return message_factory.set_attitude_target_encode(
        0, # time_boot_ms
        1, # Target system
        1, # Target component
        DronekitBitmasks.SET_ATTITUDE_BITMASK.value, # Type mask: bit 1 is LSB
        to_quaternion(roll_angle, pitch_angle), # Quaternion
        0, # Body roll rate in radian
        0, # Body pitch rate in radian
        radians(yaw_rate), # Body yaw rate in radian
        thrust  # Thrust
    )

def to_quaternion(roll = 0.0, pitch = 0.0, yaw = 0.0):
    """Convert degrees to quaternions.

    Notes
    -----
    Currently not used.
    see https://en.wikipedia.org/wiki/Conversion_between_quaternions_and_Euler_angles#Source_Code
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
