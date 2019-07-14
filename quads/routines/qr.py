import threading

from utils import parse_command

DELAY = 1


class QrRoutine(threading.Thread):
    def __init__(self, flight_session):
        super(QrRoutine, self).__init__()
        self.stop_event = threading.Event()
        self.fs = flight_session

    def run(self):
        # Takeoff
        self.do({"command": "takeoff", "altitude": 2})
        # Stabilize
        self.do({"command": "hover", "duration": 2})
        # Needs to send images and what not

    def do(self, command):
        with self.fs.lock:
            next_command = parse_command(self.fs, command)
            self.fs.current_command = next_command
            self.fs.current_command.start()
