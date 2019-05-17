import json

from utils import Heal, Hover, Land, Move, Takeoff


def parse_command(fs, data):
    command = data.get("command")
    if command == "move":
        north = data.get("north")
        east = data.get("east")
        down = data.get("down")
        duration = data.get("duration")
        return Move(fs.drone, north, east, down, duration)
    elif command == "land":
        return Land(fs.drone)
    elif command == "takeoff":
        altitude = data.get("altitude")
        return Takeoff(fs.drone, altitude)
    elif command == "heal":
        return Heal(fs.drone)
    elif command == "hover":
        duration = data.get("duration")
        return Hover(fs.drone, duration)
