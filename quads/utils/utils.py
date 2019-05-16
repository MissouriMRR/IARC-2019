import json

from utils import Heal, Move, Takeoff


def parse_command(fs, data):
    command = data.get("command")
    if command == "move":
        north = data.get("north")
        east = data.get("east")
        down = data.get("down")
        duration = data.get("duration")
        return Move(fs.drone, north, east, down, duration)
    elif command == "land":
        fs.drone.land()
    elif command == "takeoff":
        altitude = data.get("altitude")
        return Takeoff(fs.drone, altitude)
    elif command == "heal":
        return Heal(fs.drone)
