"""
Contains a thread class which continuously checks for unsafe conditions, reacting to
such situations appropriately.
"""
import coloredlogs
from enum import Enum
import logging
import time
import threading

class DroneState(Enum):
    LANDED = 1
    TAKING_OFF = 2
    FLYING = 3

class SafetyThread(threading.Thread):
    """
    Responsible for checking and responding to unsafe conditions. The main thread
    will occasionally need to update this thread on the status of the drone (ex.
    landed, taking off, flying) so that appropriate monitoring can be done.
    """

    def __init__(self, flight_session):
        super(SafetyThread, self).__init__()
        self.flight_session = flight_session
        self.daemon = True
        self.logger = logging.getLogger(__name__)

    State = DroneState.LANDED
    

    class Reaction(threading.Thread):
        """
        Represents the drone's response to an unsafe condition.

        Note: currently not used, but could be in the future
        for fine tuned repsponses.
        """

        def __init__(self, policy, flight_session):
            super(SafetyThread.Reaction, self).__init__()
            self.policy = policy # a function
            self.fs = flight_session

        def run(self):
            """
            Moves the drone in the opposite direction of the obstacle.
            """
            policy()

    def run(self):
        """
        Constantly checks for unsafe conditions and initiates a reaction
        when appropriate.
        """
        self.logger.info("Starting to monitor environment for unsafe conditions...")
        drone = self.flight_session.drone
        while True:
            state = SafetyThread.State
            unsafe = False
            if state == DroneState.TAKING_OFF:
<<<<<<< HEAD
                if drone.rangefinder.distance < 0:#more conditions can probably be added
                    unsafe = True
                """print("Safety: take off state (for demo purposes - take this out later)")"""
            elif state == DroneState.FLYING:
                # TODO: monitor for unsafe flying conditions
                """print("Safety: flying state (for demo purposes - take this out later)")"""
=======
                # TODO: monitor for unsafe takeoff conditions
                #print("Safety: take off state (for demo purposes - take this out later)")
                pass
            elif state == DroneState.FLYING:
                # TODO: monitor for unsafe flying conditions
                #print("Safety: flying state (for demo purposes - take this out later)")
                pass
>>>>>>> cd1141cead23eaa49937fc3586ec4cb25b95c27e
                if drone.airspeed > 1.5:
                    unsafe = True
                if drone.rangefinder.distance > 5:
                    unsafe = True
            elif state == DroneState.LANDED:
<<<<<<< HEAD
                """print("Safety: landed state (for demo purposes - take this out later)")"""
=======
                #print("Safety: landed state (for demo purposes - take this out later)")
                pass
>>>>>>> cd1141cead23eaa49937fc3586ec4cb25b95c27e

            if unsafe:
                self.logger.critical("Unsafe condition detected - landing!")
                SafetyThread.State = DroneState.LANDED
                drone.land()

            time.sleep(1) # sleep a second
