"""
Central flight controller code meant to be run on a singular, 'hivemind',
ground control station.
"""

from enum import Enum
import dronekit
from pymavlink import mavutil
import logging
import coloredlogs
import time
import threading

from commands import Move, Takeoff, Laser
from drone import Drone
from collision_avoidance import CollisionAvoidance

LOG_LEVEL = logging.INFO

CONNECT_STRING = '127.0.0.1:14552'
#CONNECT_STRING = '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'

class Modes(Enum):
    NETWORK_CONTROLLED = 0
    OBSTACLE_AVOIDANCE = 1

class FlightSession:
    """
    Stores all of the information for this flight, such as references to
    vehicles and commands.
    """
    def __init__(self, drone):
        self.current_command = None # hold the current command the drone is doing
        self.next_command = None # holds the next command for the drone to do
        self.logger = logging.getLogger(__name__)
        self.mode = Modes.NETWORK_CONTROLLED
        self.drone = drone
        self.avoidance_thread = CollisionAvoidance(self)
        self.avoidance_thread.start()

    def loop(self):
        """
        Monitor and control the drones in this loop function. This should
        be customized to contain the desired behavior of the drones and
        check for the arrival of network messages from the tablet.
        """
        # Make sure drone is initialized before attempting commands
        print(type(dronekit.Vehicle))
        if not isinstance(self.drone, dronekit.Vehicle):
            self.logger.info("Drone not yet initialized - failed to enter main loop")
        
        while True:
            try:
                # TODO: Check for network messages that have arrived, add them to commands

                if self.mode == Modes.NETWORK_CONTROLLED:
                    # If finished with current command, set it to none
                    if self.current_command and not self.drone.doing_command:
                        self.current_command = None

                    # If there is no current command, try to give a new one
                    if not self.current_command:
                        if not self.next_command:
                            # hover if no other command
                            self.drone.send_velocity(0, 0, 0) # Hover
                        else:
                            # give the drone the next command
                            self.current_command = self.next_command
                            self.next_command = None
                            self.current_command.start()
                time.sleep(0.0001)

            except KeyboardInterrupt:
                print("Ctrl-C pressed. Landing the drones and shutting down.")
                # Stop current command
                if self.current_command:
                    self.current_command.stop_event.set()
                    self.current_command.join()

                # Stop collision avoidance
                if self.avoidance_thread:
                    self.avoidance_thread.stop_event.set()
                    self.avoidance_thread.join()
                self.drone.land()

                return

drone = dronekit.connect(CONNECT_STRING, vehicle_class=Drone)

# Temporily placing this here - attempts to set EKF origin
msg = drone.message_factory.command_long_encode(
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_CMD_DO_SET_HOME, #command
        0,    #confirmation
        0,    # param 1, (1=use current location, 0=use specified location)
        0,    # param 2, unused
        0,    # param 3,unused
        0,    # param 4, unused
        38.5828, 90.6629, 0)    # param 5 ~ 7 latitude, longitude, altitude

drone.send_mavlink(msg)

fs = FlightSession(drone)
fs.next_command = Takeoff(drone, 1)
fs.loop()