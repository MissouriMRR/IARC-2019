"""
A TaskBase subclass for moving forward, backward, left, right, up,
and down.
"""

from task_base import TaskBase
from simple_pid import PID

import config
from flight import constants as c

# See https://en.wikipedia.org/wiki/PID_controller
KP = 0.25 # Proportional term
KI = 0 # Integral term
KD = 0 # Derivative term

class LinearMovement(TaskBase):
    """A task that moves the drone along an axis.

    Attributes
    ----------
    _duration : float
        How long to move for in seconds.
    _pid_alt : simple_pid.PID
        A PID controller used for altitude.
    _count : int
        An internval variable for keeping track of state.
    _vx : double
        Velocity in the x direction.
    _vy : double
        Velocity in the y direction.
    _vz : double
        Velocity in the z direction.
    _target_altitude : double
        The altitude in metters which the drone should maintain during the
        movement.
    """

    def __init__(self, drone, direction, duration, altitude=config.DEFAULT_ALTITUDE):
        """Initialize a task for moving along an axis.

        Parameters
        ----------
        drone : dronekit.Vehicle
            The drone being controlled.
        direction : Directions.{LEFT, RIGHT, FORWARD, BACK}
            The direction to travel in.
        duration : float
            How many seconds to travel for.
        """
        super(LinearMovement, self).__init__(drone)
        self._pid_alt = PID(KP, KI, KP, setpoint=config.DEFAULT_ALTITUDE)
        self._count = duration * (1.0/c.DELAY_INTERVAL)
        velocities = []
        for v in direction.value:
            velocities.append(v * config.DEFAULT_SPEED)
        self._vx = velocities[0]
        self._vy = velocities[1]
        self._vz = velocities[2]
        self._target_altitude = altitude

    def perform(self):
        """Perform one iteration of linear movement."""
        # Determine if we need to correct altitude
        current_alt = self._drone.rangefinder.distance
        if abs(current_alt - self._target_altitude) > c.ACCEPTABLE_ALTITUDE_DEVIATION:
            zv = -self._pid_alt(self._drone.rangefinder.distance)
        else:
            zv = 0
        # Send 0 velocities to drone (excepting altitude correction)
        self._drone.send_velocity(self._vx, self._vy, zv)
        self._count -= 1

        return self._count <= 0
