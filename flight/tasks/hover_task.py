"""A TaskBase subclass for hovering a set duration."""

from simple_pid import PID

from task_base import TaskBase
from flight import constants as c

# See https://en.wikipedia.org/wiki/PID_controller
KP = 0.25 # Proportional term
KI = 0 # Integral term
KD = 0 # Derivative term

class Hover(TaskBase):
    """A task that makes drone hover for a period of time.

    Attributes
    ----------
    _duration : float
        How long to hover for in seconds.
    _pid_alt : simple_pid.PID
        A PID controller used for altitude.
    _count : int
        An internval variable for keeping track of state.
    """

    def __init__(self, drone, altitude, duration):
        """Initialize a task for hovering.

        Parameters
        ----------
        drone : dronekit.Vehicle
            The drone being controlled.
        altitude : float
            Target altitude to maintain during hover. If none, automatically fills it with the current altitude
        duration : float
            How many seconds to hover for.
        """
        if altitude == None:
            altitude = self._drone.rangefinder.distance
        super(Hover, self).__init__(drone)
        self._duration = duration
        self._target_altitude = altitude
        self._pid_alt = PID(KP, KI, KP, setpoint=altitude)
        self._count = duration * (1.0/c.DELAY_INTERVAL)

    def perform(self):
        """Perform one iteration of hover."""
        # Determine if we need to correct altitude
        current_alt = self._drone.rangefinder.distance
        if abs(current_alt - self._target_altitude) > c.ACCEPTABLE_ALTITUDE_DEVIATION:
            zv = -self._pid_alt(self._drone.rangefinder.distance)
        else:
            zv = 0

        # Send 0 velocities to drone (and possibly and altitude correction)
        self._drone.send_velocity(0, 0, zv)
        self._count -= 1

        return self._count <= 0
