box = [{
    "command": "takeoff",
    "altitude": 1.0
}, {
    "command": "move",
    "north": 1,
    "east": 0,
    "down": 0,
    "duration": 3
}, {
    "command": "move",
    "north": 0,
    "east": 1,
    "down": 0,
    "duration": 3
}, {
    "command": "move",
    "north": -1,
    "east": 0,
    "down": 0,
    "duration": 6
}, {
    "command": "move",
    "north": 0,
    "east": -1,
    "down": 0,
    "duration": 6
}, {
    "command": "move",
    "north": 1,
    "east": 0,
    "down": 0,
    "duration": 6
}, {
    "command": "move",
    "north": 0,
    "east": 1,
    "down": 0,
    "duration": 3
}, {
    "command": "move",
    "north": -1,
    "east": 0,
    "down": 0,
    "duration": 3
}, {
    "command": "land"
}]

import json
import threading
import time

from quads.utils import parse_command


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
                    command = parse_command(
                        self, box.pop(0))  #command from autonomous routine
                self.fs.current_command = command

            time.sleep(0.001)
