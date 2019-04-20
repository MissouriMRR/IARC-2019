from enum import Enum
import logging
import coloredlogs
from sweeppy import Sweep
import time
from timeit import default_timer as timer
import threading

from flight import Modes

DETECTION_RANGE = 100 # in cm
DEVICE = '/dev/ttyUSB0'
MESSAGE_RESEND_RATE = 30.0 # resend movement instruction at this HZ
REACT_DURATION = 0.2 # go in opposite direction for this many seconds
LOG_LEVEL = logging.INFO

class Sectors(Enum):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8

# FILL THESE VALUE IN LATER
react_direction = {
    Sectors.ONE:       (-1, 0, 0),
    Sectors.TWO:       (0, -1, 0),
    Sectors.THREE:     (0, -1, 0),
    Sectors.FOUR:      (1, 0, 0),
    Sectors.FIVE:      (1, 0, 0),
    Sectors.SIX:       (0, 1, 0),
    Sectors.SEVEN:     (0, 1, 0),
    Sectors.EIGHT:     (-1, 0, 0),
}

class CollisionAvoidance(threading.Thread):
    """
    Responsible for taking contorl of the drone when an obstacle is
    encountered. It will move the drone a short distance in the opposing 
    direciton of the obstacle.
    """
    def __init__(self, flight_session):
        super(CollisionAvoidance, self).__init__()
        self.flight_session = flight_session
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    def run(self):
        """ 
        Constantly checks for obstacles in any one of the eight sectors.
        If an obstacle is detected, the drone will try to move in the 
        opposite direction for a short duration.
        """
        with Sweep(DEVICE) as sweep:
            sweep.start_scanning()

            for scan in sweep.get_scans():
                if self.stop_event.is_set():
                    sweep.stop_scanning()
                    return
                for i in range(len(scan.samples)):
                    temp = scan.samples[i]
                    tempAngle = int(temp.angle/1000)
                    if tempAngle >= 0 and tempAngle < 45:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 1")
                            self.react(Sectors.ONE)
                    elif tempAngle >= 45 and tempAngle < 90:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 2")
                            self.react(Sectors.TWO)
                    elif tempAngle >= 90 and tempAngle < 135:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 3")
                            self.react(Sectors.THREE)
                    elif tempAngle >= 135 and tempAngle < 180:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 4")
                            self.react(Sectors.FOUR)
                    elif tempAngle >= 180 and tempAngle < 225:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 5")
                            self.react(Sectors.FIVE)
                    elif tempAngle >= 225 and tempAngle < 270:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 6")
                            self.react(Sectors.SIX)
                    elif tempAngle >= 270 and tempAngle < 315:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 7")
                            self.react(Sectors.SEVEN)
                    elif tempAngle >= 315 and tempAngle < 360:
                        if temp.distance < DETECTION_RANGE:
                            self.logger.info("Collision detected - sector 8")
                            self.react(Sectors.EIGHT)
                    time.sleep(0.0001)
            
    def react(self, sector):
        """
        Reacts to an obstacle detected in this sector by travelling
        in the opposite direction for a short duration of time.

        Parameters:
        -----------
        sector (enum): the sector that an obstacle has been detected in.
        """
        drone = self.flight_session.drone
        if not drone.armed:
            return # do not try to react if not flying

        self.flight_session.mode = Modes.OBSTACLE_AVOIDANCE
        if self.flight_session.current_task is not None:
            self.flight_session.current_task.stop()
            self.flight_session.current_task.join()
        
            start = timer()
            duration = 1 # go in opposite direction for
            direction = react_direction[sector]
            x, y, z = direction
            while timer() - start < duration:
                drone.send_velocity(x, y, z)
                time.sleep(1.0/MESSAGE_RESEND_RATE)
        self.flight_session.mode = Modes.NETWORK_CONTROLLED
