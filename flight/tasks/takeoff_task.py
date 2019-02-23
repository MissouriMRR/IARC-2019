"""
A TaskBase subclass for taking off the drone.
"""

import time

from task_base import TaskBase

ALTITUDE_EPSILON = 0.1 # Acceptable error between measured altitude and target altitude
POST_TAKEOFF_HOVER_DURATION = 2 # How long to hover after takeoff in seconds

class Takeoff(TaskBase):
    """A task that takes off the drone from the ground. This task is intended
    for use on the real drone only.

    Attributes
    ----------
    _target_alt : float
        How many meters off the ground to take off to.
    _state_index : int
        The current index into the takeoff tasks agenda. See next attribute.
    _agenda : list of functions
        The ordering in which to execute the various parts of take off.

    Notes
    -----
    This task will not work on the simulated drone.
    """

    def __init__(self, drone, altitude):
        """Initialize a task for taking off.

        Parameters
        ----------
        drone : dronekit.Vehicle
            The drone being controlled
        altitude : float
            How many meters off the ground to take off to.
        """
        super(Takeoff, self).__init__(drone)
        self._target_alt = altitude
        self._state_index = 0
        self._agenda = [self._pre_takeoff_procedure,
                        self._send_takeoff_procedure,
                        self._takeoff_procedure,
                        self._post_takeoff_procedure
                        ]

    def perform(self):
        """Do one iteration of logic for taking off the drone."""
        # Call the function associated with current state
        result = self._agenda[self._state_index]()
        # If returned true, move on to the next state
        if result is True:
            self._state_index += 1
        # Return whether or not the task is done (all states finished)
        return self._state_index == len(self._agenda)

    def _pre_takeoff_procedure(self):
        """Actions taken before take off begins.
        Checks that the drone is armed.
        Returns
        -------
        True if the drone has been armed, and False otherwise.
        """
        if not self._drone.armed:
            self._drone.arm()
            return False
        else:
            return True

    def _send_takeoff_procedure(self):
        """Sends the takeoff MAVLink message to the drone.
        Returns
        -------
        True upon success, and False otherwise.
        """
        self._drone.simple_takeoff(self._target_alt)
        return True

    def _takeoff_procedure(self):
        """Actions as the drone is moving towards the target altitude.
        Checks whether or not the drone has reached its target altitude.
        Returns
        -------
        True if the drone has reached its target altitude, and False otherwise.
        """
        if abs(self._drone.rangefinder.distance - self._target_alt) < ALTITUDE_EPSILON:
            self._start_hover_time = time.time()
            self._drone.send_velocity(0, 0, 0) # Hover
            return True
        else:
            return False

    def _post_takeoff_procedure(self):
        """Actions after the drone has ascending to its target altitude.
        Checks whether or not the post takeoff hover duration has elapsed.
        Returns
        -------
        True if the drone has hovered long enough, and False otherwise.
        """
        if abs(time.time() - self._start_hover_time) < POST_TAKEOFF_HOVER_DURATION:
            self._drone.send_velocity(0, 0, 0) # Resend hover message
            return False
        else:
            return True