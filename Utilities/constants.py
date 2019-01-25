"""
All of the constant values used across all of the scripts are located here.
"""

from enum import Enum

class Drones(Enum):
    LEONARDO_SIM = "Leonardo_Sim"
    LEONARDO = "Leonardo"


DRONES = {
        Drones.LEONARDO_SIM : 'tcp:127.0.0.1:5762',
        Drones.LEONARDO: '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'
        }
"""Drone connection strings.

Notes
-----
See http://python.dronekit.io/guide/connecting_vehicle.html
and http://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html.
"""

# Safety
DEFAULT_SPEED = 0.50
SPEED_THRESHOLD = 2
MINIMUM_ALLOWED_ALTITUDE = 0.5
MAXIMUM_ALLOWED_ALTITUDE = 4.0
RANGEFINDER_MIN = 0.29
RANGEFINDER_EPSILON = 0.03
DEFAULT_ARM_TIMEOUT = 60

# DroneKit Vehicle Modes
class Modes(Enum)  :
    GUIDED = "GUIDED"
    LAND = "LAND"
    FLOW_HOLD = "FLOW_HOLD"
    FOLLOW = "FOLLOW"

class Directions(Enum):
    UP = (0, 0, 1)
    DOWN = (0, 0, -1)
    LEFT = (0, 1, 0)
    RIGHT = (0, -1, 0)
    FORWARD = (1, 0, 0)
    BACKWARD = (-1, 0, 0)

class DronekitBitmasks(Enum):
    SEND_VELOCITY_BITMASK = 0b0000111111000111
    SET_ATTITUDE_BITMASK = 0b00000000

# Movement
DEFAULT_TAKEOFF_THRUST = 0.7
SMOOTH_TAKEOFF_THRUST = 0.6
PERCENT_TARGET_ALTITUDE = 0.95
PERCENT_ALTITUDE_THRUST_ADJUSTMENT_THRESHOLD = 0.6
SIMULATION_MULTIPLIER = 1 # Divide 1 by your average real-time factor

# Durations
SHORT_INTERVAL = 0.01
ARM_RETRY_DELAY = 1
MAV_ATTITUDE_MSG_RESEND_DELAY = 0.25
MAV_VELOCITY_MSG_RESEND_DELAY = 1
MAV_HOVER_MSG_RESEND_DELAY = 1
DEFAULT_TAKEOFF_TIMEOUT = 10
DEFAULT_HOVER_DURATION = 480
HEARTBEAT_TIMEOUT = 60
