"""
Central flight controller code meant to be run on a single drone. Takes
messages sent over the network and translates them into commands that the
drone is given.
"""

import argparse
import json
import logging
import os
import threading
import time

import coloredlogs
import dronekit
from pymavlink import mavutil
from routines import ROUTINES, NetTesting
from utils import (CollisionAvoidance, Drone, Heal, InputThread, Modes, Move,
                   NetClient, Takeoff, parse_command)

LOG_LEVEL = logging.INFO
DEFAULT_PORT = 10000
DEVICE_PATH = '/dev/serial/by-id/'

# Connection string for simulator
SIM_CONNECT = '127.0.0.1:14552'
# Gets the device path for real pixhawk
REAL_CONNECT = DEVICE_PATH + os.listdir(DEVICE_PATH)[0]


class FlightSession:
    """
    Stores all of the information for this flight, such as references to
    vehicles and commands.
    """

    def __init__(self,
                 drone,
                 net=False,
                 host=None,
                 port=DEFAULT_PORT,
                 name=None,
                 routine=None):
        coloredlogs.install(LOG_LEVEL)
        self.current_command = None  # hold the current command the drone is doing
        self.next_command = None  # holds the next command for the drone to do
        self.logger = logging.getLogger(__name__)
        self.mode = Modes.NETWORK_CONTROLLED
        self.drone = drone
        self.routine = routine
        self.lock = threading.Lock()

        self.avoidance_thread = None
        self.debug_loop = None
        self.net_client = None

        self.avoidance_thread = CollisionAvoidance(flight_session=self)
        self.avoidance_thread.start()
        if net:
            self.net_client = NetClient(
                host, port, client_name=name, flight_session=self)

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

        # Wait for Enter to continue into the flight
        res = input(
            "Press Enter to continue, or d and enter to enter debug mode...")
        if res == "d":
            self.debug_loop = InputThread(self)
            self.debug_loop.start()
        if self.net_client:
            self.net_client.start()

        try:
            if self.routine:
                routine = self.routine(self)
                routine.start()
            while True:
                # If finished with current command, set it to none
                with self.lock:
                    if self.current_command and not self.drone.doing_command:
                        self.current_command = None

                if self.net_client:
                    # Get network command
                    data = self.net_client.get_command()
                    if data:
                        with self.lock:
                            if self.current_command:
                                self.current_command.stop()
                                self.current_command.join()
                            command = parse_command(self, json.loads(data))
                            self.current_command = command
                            self.current_command.start()

                with self.lock:
                    # If there is no current command, try to give a new one
                    if not self.current_command and self.mode != Modes.OBSTACLE_AVOIDANCE:
                        if not self.next_command:
                            # hover if no other command
                            if self.drone.armed:
                                self.drone.send_velocity(0, 0, 0)  # Hover
                        else:
                            self.current_command = self.next_command
                            self.next_command = None
                            self.current_command.start()
                time.sleep(0.01)
        except KeyboardInterrupt:
            self.logger.warning(
                "Ctrl-C pressed. Landing the drones and shutting down.")
            # Stop current command
            with self.lock:
                if self.current_command:
                    self.logger.info("Stopping current command...")
                    self.current_command.stop()
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

    # def do_safety_checks(self):
    #     Drone._set_altitude(self._drone)  #sets current_altitude


def main():
    global LOG_LEVEL

    parser = argparse.ArgumentParser(description='Flight starter')
    parser.add_argument('--sim', action='store_true', help='simulation flag')
    parser.add_argument(
        '--verbose', '-v', action='store_true', help='verbose flag')
    parser.add_argument('--name', required=False, type=str)
    parser.add_argument('--host', required=False, type=str)
    parser.add_argument('--port', required=False, type=int)
    parser.add_argument('--routine', required=False, type=str)

    args = parser.parse_args()

    net = True if (args.host or args.port) and args.name else False
    connect_string = SIM_CONNECT if args.sim else REAL_CONNECT
    LOG_LEVEL = logging.DEBUG if args.verbose else logging.INFO
    routine = ROUTINES.get(args.routine)
    if routine:
        print("USING ROUTINE:", args.routine)

    drone = dronekit.connect(connect_string, vehicle_class=Drone)
    drone.airspeed = .5

    fs = FlightSession(drone, net, args.host, args.port, args.name, routine)
    fs.loop()


if __name__ == "__main__":
    main()