import logging
import threading
import time
from enum import Enum
from math import cos, pi, sin
from timeit import default_timer as timer
from math import cos, pi, sin, asin, acos, degrees, radians
from numpy import array, append, dot

import coloredlogs
from sweeppy import Sweep
from utils.modes import Modes


# --OLD CONSTANTS--
# DISTANCE_THRESHOLD = 150  # in cm
# DEVICE = '/dev/ttyUSB0'  # linux style
# # DEVICE = 'COM5' # windows style
# MESSAGE_RESEND_RATE = 15.0  # resend movement instruction at this HZ
# REACT_DURATION = 3  # go in opposite direction for this many seconds
# LOG_LEVEL = logging.INFO
# SIGNAL_THRESHOLD = 100
# SECTOR_ANGLE = 360 / 8  # how many degrees each sector covers

# Parameters to edit
AVOID_SPEED = 1  # m/s
SAFE_DISTANCE = 100  # cm
SECTOR_ANGLE = 10  # degrees
Z_SPEED = -.15  # meters per second, This is used to offset falling caused by avoiding
DRONE_RADIUS = 35  # cm
DEVICE = '/dev/ttyUSB0'  # linux style
# DEVICE = 'COM5' # windows style
MESSAGE_RESEND_RATE = 15.0  # resend movement instruction at this HZ
REACT_DURATION = .3  # go in opposite direction for this many seconds
LOG_LEVEL = logging.INFO
SIGNAL_THRESHOLD = 90
MOTOR_SPEED = 6 # rotations/sec
SAMPLE_RATE = 100 # samples/rotation

# Parameters defined by the previous parameters
DISTANCE_THRESHOLD = DRONE_RADIUS + SAFE_DISTANCE  # in cm
NUMBER_OF_SECTORS = 360/SECTOR_ANGLE

# Global variables for keeping track of the last collision
# avoidance reaction
last_sector = None
last_start_time = None

# -- OLD --
# class Sectors(Enum):
#     ONE = 1
#     TWO = 2
#     THREE = 3
#     FOUR = 4
#     FIVE = 5
#     SIX = 6
#     SEVEN = 7
#     EIGHT = 8


# def anglify(sector):
#     offset = 5 + (sector.value - 1) * 2
#     return (-sin(offset * pi / 8), -cos(offset * pi / 8), 0)

def convert_angle_to_cartessian(angle):
    array_type = type(array([]))
    angle_temp = []
    if (type(angle) != list) and (type(angle) != type(array_type)):
        angle_temp.append(angle)
        print('The given angle is type = ' + str(type(angle)))
        angle = []
        angle.append(angle_temp)
    if len(angle) == 1:
        angle = list(angle)
        angle.append(angle[0])
    unit_vector = ([])
    for a in array(angle):
        unit_vector.append([cos(radians(a)), sin(radians(a))])
    unit_vector = array(unit_vector)
    return unit_vector


def convert_sector_to_cartessian(sector):
    angle = sector*SECTOR_ANGLE
    return convert_angle_to_cartessian(angle)

# -- OLD --
# # These should all be unit vectors in the appropriate opposite direction
# REACT_DIRECTION = {x: anglify(x) for x in Sectors}


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
            self.previous_scan = []

        def run(self):
            """
            Moves the drone in the opposite direction of the obstacle.
            """
            drone = self.fs.drone

            avoid_unit_vector_temp = convert_sector_to_cartessian((self.sector))
            avoid_unit_vector = avoid_unit_vector_temp[0]
            n, e, d = (
                    -AVOID_SPEED*avoid_unit_vector[1],-AVOID_SPEED*avoid_unit_vector[0], Z_SPEED)

            print("OO NED:", n, e, d)
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
            # -- OLD --
            # HOVER_DURATION = 1
            # start = timer()
            # while timer() - start < HOVER_DURATION:
            #     drone.send_velocity()
            #     time.sleep(1.0 / MESSAGE_RESEND_RATE)

            CollisionAvoidance.DoingReaction = False
            self.fs.mode = Modes.NETWORK_CONTROLLED

    def run(self):
        """
        Constantly checks for obstacles in any one of the eight sectors.
        If an obstacle is detected, the drone will try to move in the
        opposite direction for a short duration.
        """
        global last_sector
        global last_start_time

        self.logger.info("Trying to start lidar sample collection...")
        with Sweep(DEVICE) as sweep:
            sweep.set_motor_speed(MOTOR_SPEED)
            sweep.set_sample_rate(SAMPLE_RATE)
            sweep.start_scanning()
            self.logger.info("Lidar has begun giving samples")
            for scan in sweep.get_scans():
                self.previous_scan = scan
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

                acceptable_samples = []

                # Gather list of acceptable samples (meeting criteria of distance
                # and signal strength)
                for sample in sorted_samples:
                    # check that the no reaction is currently happening and
                    # that the sample is worthy of being acted upon
                    if (CollisionAvoidance.DoingReaction
                            or not self.meets_requirements(sample)):
                        continue

                    acceptable_samples.append(sample)

                if acceptable_samples:
                    # Sorting acceptable samples based on their angle
                    acceptable_samples = sorted(
                        acceptable_samples,
                        key=lambda sample: (sample.angle, sample.signal_strength)
                    )

                    # Get just sectors (round up to nearest integer)
                    acceptable_sectors = [
                        int((sample.angle / (SECTOR_ANGLE * 1000)) + 1) for sample in acceptable_samples]
                    # remove duplicate sectors
                    acceptable_sectors = sorted(list(dict.fromkeys(acceptable_sectors)))

                    # obstacle_unit_vectors = convert_sector_to_cartessian(array(acceptable_sectors))

                    sector_difference = []
                    count = 1
                    print("SECTORS W/ OBSTACLES: ", acceptable_sectors)
                    for sectors in acceptable_sectors:
                        if (count) == len(acceptable_sectors):
                            sector_difference.append(
                                acceptable_sectors[0]-sectors+NUMBER_OF_SECTORS)
                        else:
                            sector_difference.append(
                                acceptable_sectors[count]-sectors)
                        count = count + 1

                    avoid_angle = SECTOR_ANGLE * (max(sector_difference)/3 + acceptable_sectors[sector_difference.index(max(sector_difference))])

                    if avoid_angle > 360:
                        avoid_angle = avoid_angle - 360

                    avoid_sector = int(avoid_angle/SECTOR_ANGLE)

                    self.log_collision(avoid_sector, sample)

                    # Keep track of this reaction for making future decisions
                    last_sector = avoid_sector
                    last_start_time = timer()

                    # Do the reaction
                    self.react(avoid_sector)

                    # -- OLD --
                    # count = 1
                    # print(s_angle)
                    # for sector in Sectors:
                    #     if (
                    #             count - 1
                    #     ) * SECTOR_ANGLE <= s_angle and s_angle <= count * SECTOR_ANGLE:
                    #         self.log_collision(sector, sample)
                    #         # Keep track of this reaction for making future decisions
                    #         last_sector = sector
                    #         last_start_time = timer()
                    #         # Do the reaction
                    #         self.react(sector)
                    #         break
                    #     count += 1

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

    def get_previous_samples(self):
        """
        Returns the most recently observed distance observations.
        """
        return self.previous_scan.samples
