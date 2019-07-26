import threading

from utils import parse_command

#takes last 4 samples to insure it gets a sample for each wall
NUM_SCAN_SAMPLES = 4 
'''Not sure what exactly is in a sample
or how samples are recorded and returned. 
ould use clarification -Ben'''
#confidence needed to confirm a nearby wall
CONFIDENCE_REQ = 110
# HAS to be set BEFORE running.
DISTANCE_BETWEEN_WALLS = 0
# For clarifying indices of list which contains distances to walls
FRONT = 0
RIGHT = 1
BEHIND = 2
LEFT = 3

class QrRoutine(threading.Thread):
    def __init__(self, flight_session):
        super(QrRoutine, self).__init__()
        self.stop_event = threading.Event()
        self.fs = flight_session

    def run(self):
        distance = [0,0] #direction of travel and distance
        distance = get_distance()

        if distance[0] == RIGHT:
            self.do({"command": "move",
                     "north": 0,
                     "east": distance[1],
                     "down": 0,
                     "duration": (distance[1] * 2)
                     })
        if distance[0] == LEFT:
            self.do({"command": "move",
                     "north": 0,
                     "east": -distance[1],
                     "down": 0,
                     "duration": (distance[1] * 2)
                     })
        return 

    def get_distance(self):
        distance_move = [0,0] #returned direction of travel and distance
        nearest_wall = 0 #nearest wall
        distances = [0,0,0,0] #distances of all walls
        confidences = [0,0,0,0] #confidences of all walls
        for _ in range(NUM_SCAN_SAMPLES):
            samples = self.fs.avoidance_thread.get_previous_samples()

            for s in samples:
                s_angle = int(s.angle / 1000)

                if s_angle >= 345 and s_angle <= 15:
                    distances_to_walls[FRONT] = s.distance
                    confidences[FRONT] = s.signal_strength
                
                if s_angle >= 75 and s_angle <= 105:
                    distances_to_walls[RIGHT] = s.distance
                    confidences[RIGHT] = s.signal_strength

                if s_angle >= 165 and s_angle <= 195:
                    distances_to_walls[BEHIND] = s.distance
                    confidences[BEHIND] = s.signal_strength
                
                if s_angle >= 255 and s_angle <= 285:
                    distances_to_walls[LEFT] = s.distance
                    confidences[LEFT] = s.signal_strength

        if confidences[LEFT] > confidences[RIGHT]:
            distance_move[0] = RIGHT
            nearest_wall = [LEFT]
        else:
            distance_move[0] = LEFT
            nearest_wall = [RIGHT]
        distance_move[1] = (DISTANCE_BETWEEN_WALLS - (distances[nearest_wall] * 2))
        if confidences[nearest_wall] < CONFIDENCE_REQ or distance_move[1] < 0:
            distance_move[1] = 0
            print('cannot determine distance')

        return distance_move

    def do(self, command):
        with self.fs.lock:
            next_command = parse_command(self.fs, command)
            self.fs.current_command = next_command
            self.fs.current_command.start()
