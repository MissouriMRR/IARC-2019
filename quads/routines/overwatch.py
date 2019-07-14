"""
Routine for the overwatch drone. Note that the following actions will probably negatively
affect the performance of this routine:

    1) Issuing horizontal movement commands to the drone
    2) Yawing the drone
"""

import threading
import time

from utils.commands import Land, Takeoff

OVERWATCH_HEIGHT = 2  # in meters

# Number of scans with which to average reading to determine distance to walls
NUM_SCAN_SAMPLES = 10
# How often to get next sample in get_distances_to_walls()
SAMPLE_INTERVAL = 0.5

# For clarifying indices of list which contains distances to walls
FRONT = 0
RIGHT = 1
BEHIND = 2
LEFT = 3

DRIFT_THRESHOLD = 2


class Overwatch(threading.Thread):
    def __init__(self, flight_session):
        super(Overwatch, self).__init__()
        self.stop_event = threading.Event()
        self.fs = flight_session

    def run(self):
        # Take off the drone
        drone = self.fs.drone

        self.fs.next_command = Takeoff(drone, OVERWATCH_HEIGHT)

        # Wait for takeoff to complete
        while self.fs.next_command != None and self.fs.current_command != None:
            time.sleep(1)

        # Original distances to each of four walls
        original_distances = self.get_distances_to_walls()

        # Continue hovering and monitoring if the drone is getting too close to one of the walls
        while True:
            current_distances = self.get_distances_to_walls()

            for dist_pair in zip(current_distances, original_distances):
                if abs(dist_pair[0] - dist_pair[1]) > DRIFT_THRESHOLD:
                    self.fs.next_command = Land(drone)
                    return  # drifted too far - land and end routine

            # do other stuff (send image stream? send commands to Ricky/other drones?)

    def get_distances_to_walls(self):
        """
        Returns the distances to walls in front, right, behind, and left of
        the drone by taking averages of a series of samples.

        Returns:
        --------
        list:
            [dist_front, dist_right, dist_behind, dist_left] where all distances
            are in meters.

        Note:
        -----
        This function will block for NUM_SCAN_SAMPLES * 0.5 seconds. If this needs
        to be changed, make it the target of a thread. 
        """

        # These values will change as averages are taken
        distances_to_walls = [0, 0, 0, 0]
        sector_counts = [0, 0, 0, 0]

        # Get distance to walls/barriers (take average 10 scans)
        for _ in range(NUM_SCAN_SAMPLES):
            samples = self.fs.avoidance_thread.get_previous_samples()
            # Find samples in front, right, behind, and left of drone
            for s in samples:
                s_angle = int(s.angle / 1000)

                # Notes: the following angle ranges assume the lidar is
                # mounted such that angle 0 is directly in front of the drone

                # in front
                if s_angle >= 345 and s_angle <= 15:
                    distances_to_walls[FRONT] += s.distance
                    sector_counts[FRONT] += 1

                # right
                if s_angle >= 75 and s_angle <= 105:
                    distances_to_walls[RIGHT] += s.distance
                    sector_counts[RIGHT] += 1

                # behind
                if s_angle >= 165 and s_angle <= 195:
                    distances_to_walls[BEHIND] += s.distance
                    sector_counts[BEHIND] += 1

                # left
                if s_angle >= 255 and s_angle <= 285:
                    distances_to_walls[LEFT] += s.distance
                    sector_counts[LEFT] += 1

                time.sleep(SAMPLE_INTERVAL)  # Sleep half a second, then inspect next samples

        # Take averages
        distances_to_walls = [n[0]/n[1]
                              for n in zip(distances_to_walls, sector_counts)]

        return distances_to_walls
