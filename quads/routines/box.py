box = [{
    "command": "takeoff",
    "altitude": 1.0
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "move",
    "north": 1,
    "east": 0,
    "down": 0,
    "duration": 3
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "move",
    "north": 0,
    "east": 1,
    "down": 0,
    "duration": 3
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "move",
    "north": -1,
    "east": 0,
    "down": 0,
    "duration": 6
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "move",
    "north": 0,
    "east": -1,
    "down": 0,
    "duration": 6
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "move",
    "north": 1,
    "east": 0,
    "down": 0,
    "duration": 6
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "move",
    "north": 0,
    "east": 1,
    "down": 0,
    "duration": 3
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "move",
    "north": -1,
    "east": 0,
    "down": 0,
    "duration": 3
}, {
    "command": "hover",
    "duration": 2
}, {
    "command": "land"
}]

import json
import threading
import time

from utils import parse_command

DELAY = 1


class Box(threading.Thread):
    def __init__(self, flight_session):
        super(Box, self).__init__()
        self.stop_event = threading.Event()
        self.fs = flight_session

    def run(self):
        while True:
            if not box:
                return
            with self.fs.lock:
                if not self.fs.drone.doing_command:
                    command = parse_command(self.fs, box.pop(0))
                    print("BOX GAVE:", command)
                    if command:
                        self.fs.current_command = command
                        self.fs.current_command.start()
            time.sleep(DELAY)
