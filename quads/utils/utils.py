import json
from utils.commands import Move, Takeoff, Heal


def parse_command(fs, data):
    parsed = json.loads(data)
    command = parsed.get("command")
    if command == "move":
        north = parsed.get("north")
        east = parsed.get("east")
        down = parsed.get("down")
        duration = parsed.get("duration")
        return Move(fs.drone, north, east, down, duration)
    elif command == "land":
        fs.drone.land()
    elif command == "takeoff":
        altitude = parsed.get("altitude")
        return Takeoff(fs.drone, altitude)
    elif command == "heal":
        return Heal(fs.drone)

