"""Helper functions."""

from math import sin, cos, radians

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