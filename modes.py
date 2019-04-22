"""
The various modes of operation for the flight controller.
"""

from enum import Enum

class Modes(Enum):
    NETWORK_CONTROLLED = 0
    OBSTACLE_AVOIDANCE = 1