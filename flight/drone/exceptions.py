"""
Custom exceptions used throughout the flight code, often describing an
unsafe condition that must be checked for periodically.
"""

class AltitudeException(Exception):
    """
    Thrown when altitude is too low or too high.
    """
    pass


class ThrustException(Exception):
    """
    Thrown when thrust is too low or too high.
    """
    pass


class VelocityException(Exception):
    """
    Thrown when velocity is too low or too high.
    """
    pass


class EmergencyLandException(Exception):
    """
    Thrown when an unrecoverable state is reached and the drone should
    land for the preservation of its safety and the safety of others.
    """
    pass


class VelocityExceededThreshold(Exception):
    """
    Thrown when velocity is too high to be considered safe.
    """
    pass


class AltitudeExceededThreshold(Exception):
    """
    Thrown when altitude is too high to be considered safe.
    """
    pass


class RangefinderMalfunction(Exception):
    """
    Thrown when it is the rangefinder is returning unusual or suspect values.
    """
    pass


class OpticalflowMalfunction(Exception):
    """
    Thrown when the Opticalflow sensor is returning unusual or suspect values.
    """
    pass


class AltitudeNegativeException(Exception):
    """
    Thrown when altitude is observed as negative.
    """
    pass


class TakeoffTimeoutException(Exception):
    """
    Thrown when takeoff times out.
    """
    pass

class RollExceededMaximum(Exception):
    """
    Thrown when the roll of the drone exceeds a safe range.
    """
    pass

class PitchExceededMaximum(Exception):
    """
    Thrown when the pitch of the drone exceeds a safe range.
    """
    pass


# TODO: Add more safety-related exceptions here