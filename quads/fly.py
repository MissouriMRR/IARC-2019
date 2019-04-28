"""
Central flight controller code meant to be run on a single drone. Takes
messages sent over the network and translates them into commands that the
drone is given.
"""

import argparse
import logging
import threading
import time

import coloredlogs
import dronekit
from pymavlink import mavutil
from utils import (CollisionAvoidance, Drone, InputThread, Modes, NetClient,
                   commands, parse_command)

LOG_LEVEL = logging.INFO

HOST = "192.168.2.3"
PORT = 10000
NAME = "bob"

SIM_CONNECT = '127.0.0.1:14552'
REAL_CONNECT = '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'


class FlightSession:
    """
    Stores all of the information for this flight, such as references to
    vehicles and commands.
    """

    def __init__(self, drone, debug):
        coloredlogs.install(LOG_LEVEL)
        self.current_command = None  # hold the current command the drone is doing
        self.next_command = None  # holds the next command for the drone to do
        self.logger = logging.getLogger(__name__)
        self.mode = Modes.NETWORK_CONTROLLED
        self.drone = drone

        self.avoidance_thread = CollisionAvoidance(flight_session=self)
        self.avoidance_thread.start()
        if debug:
            self.debug_loop = InputThread(self)
            self.debug_loop.start()
        else:
            self.net_client = NetClient(HOST, PORT, client_name=NAME)
            self.net_client.start()

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

        try:
            while True:
                # Get network command
                data = self.net_client.get_command()
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
            self.logger.warning(
                "Ctrl-C pressed. Landing the drones and shutting down.")
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


def main():
    global LOG_LEVEL

    parser = argparse.ArgumentParser(description='Flight starter')
    parser.add_argument('--sim', action='store_true', help='simulation flag')
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='verbose flag')
    parser.add_argument('--name', required=True, type=str)
    parser.add_argument('--host', required=False, type=str)
    parser.add_argument('--port', required=False, type=str)

    args = parser.parse_args()

    debug = False if args.host and args.port else True
    connect_string = SIM_CONNECT if args.sim else REAL_CONNECT
    LOG_LEVEL = logging.DEBUG if args.verbose else logging.INFO

    drone = dronekit.connect(connect_string, vehicle_class=Drone)

    fs = FlightSession(drone, debug)
    fs.loop()


if __name__ == "__main__":
    main()
