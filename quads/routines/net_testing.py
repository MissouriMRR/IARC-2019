import json
import threading
import time

from utils import Takeoff, parse_command


class NetTesting(threading.Thread):
    def __init__(self, flight_session):
        super(NetTesting, self).__init__()
        self.stop_event = threading.Event()
        self.fs = flight_session

    def run(self):
        return
