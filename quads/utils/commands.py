"""
The file contains the base Command class and implementation of subclasses.
"""

import logging
import threading
import time
from timeit import default_timer as timer

import coloredlogs
import dronekit
from utils.laser.laser import Laser

VELOCITY = 0.5  # drone will move at this rate in m/s
TAKEOFF_ALT = 1  # drone will take off to this altitude (m)
MESSAGE_RESEND_RATE = 30
LOG_LEVEL = logging.INFO
LASER_PIN = 23


class Command(threading.Thread):
    """
    A general command for controlling the drone (ex. move right 1 meter).
    """

    def __init__(self, drone):
        """
        Parameters:
        -----------
        drone: a dronekit Vehicle object (must already be connect)
        """
        super(Command, self).__init__()
        self.time = time.time()  # timestamp for creation of this command
        self.drone = drone
        self.logger = logging.getLogger(__name__)
        self.stop_event = threading.Event()

    def stop(self):
        self.stop_event.set()

    def run(self):
        """
        This function should be overriden by children of this class.
        """
        pass


class Move(Command):
    """
    Causes a drone to move for a given number of seconds.
    """

    def __init__(self, drone, north, east, down, seconds):
        """
        Parameters:
        -----------
        drone: a dronekit Vehicle object (must already be connect)
        north: x direction (I think?)
        east: y direction (I think?)
        down: negative z direction
        seconds: (float) number of seconds to fly in this direction
        Notes:
        ------
        No matter what (north, east, down) is given, drone will travel in
        that unit direction for the specified number of seconds.
        """
        super(Move, self).__init__(drone)
        # The following four lines scale the movement vector so that it
        # retains its direction, but has a magnitude of the default
        # movement velocity.
        mag = (north**2 + east**2 + down**2)**0.5
        if mag:
            self.north = VELOCITY * north / mag
            self.east = VELOCITY * east / mag
            self.down = VELOCITY * down / mag
        else:
            self.north = 0
            self.east = 0
            self.down = 0

        self.duration = seconds

    def run(self):
        """
        Moves the drone for a set duration of time, then send a stabalizing
        hover message for a short period of time.
        """
        if not isinstance(self.drone, dronekit.Vehicle):
            self.logger.info(
                "Cannot execute this move: drone variable never initialized.")
            return

        if not self.drone.armed:
            self.logger.info("Cannot execute this move: drone not armed.")
            return

        self.drone.doing_command = True

        self.logger.info("Drone {}: starting move".format(self.drone.id))

        self.drone.send_yaw(0, 1)  # heading, direction (cw)

        start = timer()
        while timer() - start < self.duration:
            self.logger.info("Drone {}: starting move interval".format(
                self.drone.id))
            self.drone.send_rel_pos(self.north, self.east, self.down)
            start_interval = timer()
            while timer() - start_interval < 1.0:  # 1 second intervals
                if self.stop_event.isSet():
                    # Send a stablizing command to drone
                    self.drone.send_rel_pos(0, 0, 0)
                    self.drone.doing_command = False
                    return
                time.sleep(1.0 / MESSAGE_RESEND_RATE)

        # Movement finished, now stabalize drone in hover
        stabalize_duration = 0.2
        start = timer()
        while timer() - start < stabalize_duration:
            if self.stop_event.isSet():
                # Send a stablizing command to drone
                self.drone.send_rel_pos(0, 0, 0)
                return
            print("1")
            self.drone.send_velocity(0, 0, 0)
            time.sleep(1.0 / MESSAGE_RESEND_RATE)

        self.logger.info("Drone {}: finished move".format(self.drone.id))

        self.drone.doing_command = False


class Takeoff(Command):
    """
    Causes the drone to take off.
    """

    def __init__(self, drone, alt_target):
        """
        Parameters:
        -----------
        drone: a dronekit Vehicle object (must already be connect)
        alt_target: (float) how high to take off to (meters)
        seconds: (float) number of seconds to fly in this direction
        """
        super(Takeoff, self).__init__(drone)
        self.alt_target = alt_target

    def run(self):
        """
        Arms the drone, takes it off, and then sending a stablizing hover
        message for a short period of time.
        """
        if not isinstance(self.drone, dronekit.Vehicle):
            self.logger.info(
                "Cannot execute this move: drone variable never initialized.")

        self.drone.doing_command = True

        self.logger.info("Drone {}: starting takeoff".format(self.drone.id))

        self.drone.arm()

        # Take off drone
        self.drone.simple_takeoff(self.alt_target)

        # While not within 0.1 of a meter
        #self.drone.location.global_relative_frame.alt
        while abs(self.drone.rangefinder.distance - self.alt_target) > 0.1:
            if self.stop_event.isSet():
                # Send a stablizing command to drone
                self.drone.send_rel_pos(0, 0, 0)
                self.doing_command = False
                return
            time.sleep(0.001)

        # Hover for a short duration to stablize the drone
        start = timer()
        stabalize_duration = 0.2
        while timer() - start < stabalize_duration:
            self.drone.send_rel_pos(0, 0, 0)  # Hover
            time.sleep(1.0 / MESSAGE_RESEND_RATE)

        self.logger.info("Drone {}: finished takeoff".format(self.drone.id))

        self.drone.doing_command = False


class Heal(Command):
    """
    Causes the laser to turn on and the drone to yaw back and forth to that
    the laser has a better chance of hitting the human.
    """

    def __init__(self, drone, range=20, duration=5):
        """
        Parameters:
        -----------
        drone: a dronekit Vehicle object (must already be connect)
        range: how many degrees of heading to yaw back and forth
        duration: (float) number of seconds to yaw for
        """
        super(Heal, self).__init__(drone)
        self.duration = duration
        self.range = range
        self.yaw_time = 1
        self.laser = Laser(LASER_PIN)

    def run(self):
        """
        Goes back and forth between yawing counter-clock-wise and clock-wise.
        Each yaw is given a second to complete. The drone will always return
        to its original heading.
        """
        self.drone.doing_command = True

        self.logger.info("Drone {}: starting heal".format(self.drone.id))

        cw = True  # Start by moving clock-wise

        self.laser.on()
        start = timer()
        while timer() - start < self.duration:
            if self.stop_event.isSet():
                self.doing_command = True
                return
            if cw:
                self.drone.send_yaw(self.range, 1)
                cw = False
                time.sleep(self.yaw_time)
            else:
                self.drone.send_yaw(self.range, -1)
                cw = True
                time.sleep(self.yaw_time)

        # Check if drone has gone back to its initial heading
        if not cw:
            self.drone.send_yaw(self.range, -1)
            cw = True
            time.sleep(self.yaw_time)
        self.laser.off()

        self.logger.info("Drone {}: finished heal".format(self.drone.id))
        self.drone.doing_command = False
