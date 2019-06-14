import logging
import threading
import time
from enum import Enum
from math import cos, pi, sin
from timeit import default_timer as timer

import coloredlogs
from sweeppy import Sweep
from utils.modes import Modes

#from flight import Modes

DISTANCE_THRESHOLD = 150  # in cm
DEVICE = '/dev/ttyUSB0'  # linux style
#DEVICE = 'COM5' # windows style
MESSAGE_RESEND_RATE = 15.0  # resend movement instruction at this HZ
REACT_DURATION = 3  # go in opposite direction for this many seconds
LOG_LEVEL = logging.INFO
SIGNAL_THRESHOLD = 100
SECTOR_ANGLE = 360 / 8  # how many degrees each sector covers


class Sectors(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8


def anglify(sector):
    offset = 5 + (sector.value - 1) * 2
    return (-sin(offset * pi / 8), -cos(offset * pi / 8), 0)


# These should all be unit vectors in the appropriate opposite direction
REACT_DIRECTION = {x: anglify(x) for x in Sectors}


class CollisionAvoidance(threading.Thread):
    """
    Responsible for taking control of the drone when an obstacle is
    encountered. It will move the drone a short distance in the opposing
    direciton of the obstacle.
    """

    def __init__(self, flight_session):
        super(CollisionAvoidance, self).__init__()
        self.flight_session = flight_session
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    DoingReaction = False  # static variable

    class Reaction(threading.Thread):
        """
        Represents the drone's response to a detected obstacle.
        """

        def __init__(self, sector, flight_session):
            super(CollisionAvoidance.Reaction, self).__init__()
            self.sector = sector
            self.fs = flight_session

        def run(self):
            """
            Moves the drone in the opposite direction of the obstacle.
            """
            drone = self.fs.drone
            direction = REACT_DIRECTION[self.sector]
            n, e, d = direction
            print(n, e, d)
            if self.fs.net_client:
                print("Moving swarm north: {} east: {} down: {}".format(
                    n, e, d))
                self.fs.net_client.send_teamwork({
                    "command": "move",
                    "north": n,
                    "east": e,
                    "down": d,
                    "duration": REACT_DURATION
                })
            # move in opposite direction
            # actual drone.send_rel_pos(n, e, d)
            drone.send_rel_pos(
                n, e, -0.15
            )  # Testing with a slight move up to prevent loss of altitude
            start = timer()
            while timer() - start < REACT_DURATION:
                time.sleep(1.0 / MESSAGE_RESEND_RATE)

            # stabilize movement with a short hover
            HOVER_DURATION = 1
            start = timer()
            while timer() - start < HOVER_DURATION:
                drone.send_velocity()
                time.sleep(1.0 / MESSAGE_RESEND_RATE)

            CollisionAvoidance.DoingReaction = False
            self.fs.mode = Modes.NETWORK_CONTROLLED

    def run(self):
        """
        Constantly checks for obstacles in any one of the eight sectors.
        If an obstacle is detected, the drone will try to move in the
        opposite direction for a short duration.
        """
        self.logger.info("Trying to start lidar sample collection...")
        with Sweep(DEVICE) as sweep:
            sweep.set_motor_speed(6)
            sweep.set_sample_rate(100)
            sweep.start_scanning()
            self.logger.info("Lidar has begun giving samples")
            for scan in sweep.get_scans():

                # check if flight controller has said to stop
                if self.stop_event.is_set():
                    self.logger.info("trying to stop scanning...")
                    sweep.stop_scanning()
                    return
                # look through lidar samples
                sorted_samples = sorted(
                    scan.samples,
                    key=lambda s: s.signal_strength,
                    reverse=True)
                for sample in sorted_samples:
                    # check that the no reaction is currently happening and
                    # that the sample is worthy of being acted upon
                    if (CollisionAvoidance.DoingReaction
                            or not self.meets_requirements(sample)):
                        continue
                    s_angle = int(sample.angle / 1000)

                    count = 1
                    print(s_angle)
                    for sector in Sectors:
                        if (
                                count - 1
                        ) * SECTOR_ANGLE <= s_angle and s_angle <= count * SECTOR_ANGLE:
                            self.log_collision(sector, sample)
                            self.react(sector)
                            break
                        count += 1

    def log_collision(self, sector, sample):
        msg = ("Collision detected - {} (distance - {}, confidence - {})"
               .format(sector, sample.distance, sample.signal_strength))
        self.logger.info(msg)

    def meets_requirements(self, sample):
        """
        Checks that a number of conditions are met before recognizing
        that this sample is worthy of being acted upon.

        If the sample is worth acting upon, returns True (False otherwise).
        """
        return (sample.signal_strength >= SIGNAL_THRESHOLD
                and sample.distance != 1
                and sample.distance <= DISTANCE_THRESHOLD)

    def react(self, sector):
        """
        Reacts to an obstacle detected in this sector by travelling
        in the opposite direction for a short duration of time.

        Parameters:
        -----------
        sector (enum): the sector that an obstacle has been detected in.
        """
        if not self.flight_session.drone.armed:
            pass
        if CollisionAvoidance.DoingReaction:
            return

        self.flight_session.mode = Modes.OBSTACLE_AVOIDANCE
        CollisionAvoidance.DoingReaction = True

        if self.flight_session.current_command is not None:
            self.flight_session.current_command.stop()
            self.flight_session.current_command.join()

        self.Reaction(sector, self.flight_session).start()
