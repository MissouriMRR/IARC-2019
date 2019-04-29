import json
import threading
import time


class AutonomyTest(threading.Thread):
    def __init__(self, messages=None, group=None, target=None, name=None):
        super().__init__(group=group, target=target, name=name)
        self.messages = messages

    def add_message(self, command):
        self.messages.append(json.loads(command))

    def run(self):
        self.add_message({"command": "takeoff", "altitude": 1.0})  # takeoff
        time.sleep(4)
        self.add_message({
            "command": "move",
            "north": 1,
            "east": 0,
            "down": 0,
            "duration": 4
        })  # move forward
        time.sleep(7)
        self.add_message({
            "command": "move",
            "north": -1,
            "east": 0,
            "down": 0,
            "duration": 4
        })  # move backward
        time.sleep(7)
        self.add_message({
            "command": "move",
            "north": 0,
            "east": 1,
            "down": 0,
            "duration": 2
        })  # move right
        time.sleep(5)
        self.add_message({
            "command": "move",
            "north": 0,
            "east": -1,
            "down": 0,
            "duration": 2
        })  # move left
        time.sleep(5)
        self.add_message({"command": "heal"})  # heal
        time.sleep(7)
        self.add_message({"command": "land"})  # land
