import logging
import threading
import time

import coloredlogs
from utils.commands import Heal, Land, Move, Takeoff

LOG_LEVEL = logging.INFO


class InputThread(threading.Thread):
    def __init__(self, flight_session):
        super(InputThread, self).__init__()
        self.fs = flight_session
        self.stop_event = threading.Event()
        self.logger = logging.getLogger(__name__)

    def run(self):
        drone = self.fs.drone
        while not self.stop_event.is_set():
            print('>')  # prompt
            c = input().split()
            if self.can_add_command():
                if len(c) == 1:
                    if c[0] == 't':
                        self.logger.info("Next command set to takeoff.")
                        self.fs.next_command = Takeoff(drone, 1)  # takeoff 1 m
                    elif c[0] == 'l':
                        self.logger.info("Next command set to land.")
                        with self.fs.lock:
                            if self.fs.current_command:
                                self.fs.current_command.stop()
                                self.fs.current_command.join()
                        self.fs.next_command = Land(drone)
                    elif c[0] == 'y':
                        self.logger.info("Next command set to yaw.")
                        self.fs.next_command = Heal(
                            drone)  # default laser routine
                    else:
                        self.logger.info("Invalid option.")
                elif len(c) == 5:
                    # it's a move command
                    c = c[1:]
                    for x in range(4):
                        try:
                            c[x] = float(c[x])
                        except:
                            self.logger.info("Arguments not floats.")
                            continue
                        self.fs.next_command = Move(
                            drone,
                            float(c[0]),  # north
                            float(c[1]),  # east
                            float(c[2]),  # down
                            float(c[3]))  # duration
                else:
                    self.logger.info("Invalid option.")
            
            else:
                self.logger.info("Drone already has next command.")
            time.sleep(0.1)

    def can_add_command(self):
        return self.fs.next_command is None
