"""
Central flight controller code meant to be run on a single drone. Takes
messages sent over the network and translates them into commands that the
drone is given.
"""

import logging
import threading
import time
from commands import Laser, Move, Takeoff

import coloredlogs
import dronekit
from client import Client
# Temporary - since no virtual lidar to test with
from collision_avoidance import CollisionAvoidance
from drone import Drone
# Temporary - for debugging purposes
from input_thread import InputThread
from modes import Modes
from pymavlink import mavutil
from utils import parse_command

LOG_LEVEL = logging.INFO
<<<<<<< HEAD
HOST = "192.168.2.3"
PORT = 10000
NAME = "bob"
=======
HOST = "192.168.43.80"
PORT = 10000
>>>>>>> 46bc7ee46965fb671bd8c9def4f0b2c7825c5289

#CONNECT_STRING = '127.0.0.1:14552'
CONNECT_STRING = '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'


class FlightSession:
    """
    Stores all of the information for this flight, such as references to
    vehicles and commands.
    """

    def __init__(self, drone):
        coloredlogs.install(LOG_LEVEL)
        self.current_command = None  # hold the current command the drone is doing
        self.next_command = None  # holds the next command for the drone to do
        self.logger = logging.getLogger(__name__)
        self.mode = Modes.NETWORK_CONTROLLED
        self.drone = drone

        self.avoidance_thread = CollisionAvoidance(flight_session=self)
<<<<<<< HEAD
        self.client = Client(HOST, PORT, client_name=NAME)

        # Temporary - for debugging purposes
        self.debug_loop = InputThread(self)

    def loop(self):
        """
        Monitor and control the drones in this loop function. This should
        be customized to contain the desired behavior of the drones and
        check for the arrival of network messages from the tablet.
        """

        # Make sure drone is initialized before attempting commands
        if not isinstance(self.drone, dronekit.Vehicle):
            self.logger.info(
                "Drone not yet initialized - failed to enter main loop")

        self.avoidance_thread.start()
        self.debug_loop.start()
        self.client.start()

        while True:
            try:
                data = self.client.get_command()
                if data:
                    command = parse_command(self, data)
                    self.next_command = command

                if self.mode == Modes.NETWORK_CONTROLLED:
                    # If finished with current command, set it to none
                    if self.current_command and not self.drone.doing_command:
                        self.current_command = None

                    # If there is no current command, try to give a new one
                    if not self.current_command:
                        if not self.next_command:
                            # hover if no other command
                            if self.drone.armed:
                                self.drone.send_velocity(0, 0, 0)  # Hover
                        else:
                            # give the drone the next command
                            self.current_command = self.next_command
                            self.next_command = None
                            self.current_command.start()
                time.sleep(0.1)

            except KeyboardInterrupt:
                print("Ctrl-C pressed. Landing the drones and shutting down.")
                # Stop current command
                if self.current_command:
                    self.logger.info("Stopping current command...")
                    self.current_command.stop_event.set()
                    self.current_command.join()

                # Stop collision avoidance
                if self.avoidance_thread:
                    self.logger.info("Stopping collision avoidance...")
                    self.avoidance_thread.stop_event.set()
                    self.avoidance_thread.join()

                self.drone.land()

                # Stop debug loop
                if self.debug_loop:
                    self.logger.info("Stopping debug loop...")
                    self.debug_loop.stop_event.set()
                    self.debug_loop.join()

                return


drone = dronekit.connect(CONNECT_STRING, vehicle_class=Drone)

# Temporily placing this here - attempts to set EKF origin
msg = drone.message_factory.command_long_encode(
    0,
    0,  # target system, target component
    mavutil.mavlink.MAV_CMD_DO_SET_HOME,  #command
    0,  #confirmation
    0,  # param 1, (1=use current location, 0=use specified location)
    0,  # param 2, unused
    0,  # param 3,unused
    0,  # param 4, unused
    38.5828,
    90.6629,
    0)  # param 5 ~ 7 latitude, longitude, altitude

drone.send_mavlink(msg)

fs = FlightSession(drone)
fs.drone.arm()  # TEMPORARY - FOR TESTING ARM FUNCTION
fs.loop()
