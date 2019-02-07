"""
All of the constant values used across all of the scripts are located here.
"""

from enum import Enum

###################################
# Enum Classes
###################################

class Drones(Enum):
    LEONARDO_SIM = "Leonardo_Sim"
    LEONARDO = "Leonardo"

class Priorities(Enum):
    """Constants for differentiating the priority of items.

    Notes
    -----
    Values are based on heapq, with is a min-heap.
    """
    LOW = 3
    MEDIUM = 2
    HIGH = 1

# DroneKit Vehicle Modes
class Modes(Enum)  :
    """The various modes of flight."""
    GUIDED = "GUIDED"
    LAND = "LAND"
    FLOW_HOLD = "FLOW_HOLD"
    FOLLOW = "FOLLOW"

# Directions along x, y, and z axes.
class Directions(Enum):
    """Directions along each axis.

    Notes
    -----
    RIGHT => positive x
    LEFT => negative x
    FORWARD => positive y
    BACKWARD => negative y
    """
    UP = (0, 0, 1)
    DOWN = (0, 0, -1)
    LEFT = (0, 1, 0)
    RIGHT = (0, -1, 0)
    FORWARD = (-1, 0, 0)
    BACKWARD = (1, 0, 0)

class MavBitmasks(Enum):
    """Bitmasks that enable or disable the various field of a mavlink message.

    Values
    ------
    SET_POSITION_TARGET:
        https://mavlink.io/en/messages/common.html#SET_POSITION_TARGET_GLOBAL_INT
    SET_ATTITUDE_TARGET:
        https://mavlink.io/en/messages/common.html#SET_ATTITUDE_TARGET

    Notes
    -----
    0 means enabled, 1 means ignored. The first bit is the least significant
    bit.
    """
    SET_POSITION_TARGET = 0b0000111111000111
    SET_ATTITUDE_TARGET = 0b00000000

# Drone enum types mapped to connection strings
# See http://python.dronekit.io/guide/connecting_vehicle.html
# and http://ardupilot.org/dev/docs/learning-ardupilot-the-example-sketches.html.
CONNECTION_STR_DICT = {
        Drones.LEONARDO_SIM : 'tcp:127.0.0.1:5762',
        Drones.LEONARDO: '/dev/serial/by-id/usb-3D_Robotics_PX4_FMU_v2.x_0-if00'
        }

# How often to run safety checks
SAFETY_CHECKS_DELAY = 0.5

# How often to run main control loop
DELAY_INTERVAL = 0.1

# How often to retry arming during arm function
ARM_RETRY_DELAY = 1

# How long to wait before timing out a connection attempt
CONNECT_TIMEOUT = 60

# How long to hover when the controller runs out of tasks to do
DEFAULT_HOVER_DURATION = 480

# The mavlink identifier for optical flow
# See https://mavlink.io/en/messages/common.html#OPTICAL_FLOW
OPTICAL_FLOW_MESSAGE = 'OPTICAL_FLOW'
