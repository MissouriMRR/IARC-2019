import threading
import time

class CollisionAvoidance(threading.Thread):
    """
    Responsible for taking contorl of the drone when an obstacle is
    encountered. It will move the drone a short distance in the opposing 
    direciton of the obstacle.
    """
    def __init__(self, flight_session):
        super(CollisionAvoidance, self).__init__()
        self.flight_sesson = flight_session
        self.stop_event = threading.Event()

    def run(self):
        while True:
            if self.stop_event.is_set():
                # TODO: do any necessary clean up
                return
            # TODO: detect obstacles
            # if obstacle:
            #   self.flight_session.mode = Modes.OBSTACLE_AVOIDANCE
            #   if flight_session has current task:
            #     flight_session.current_task.stop()
            #     flight_session.current_task.join()
            #   move the drone away from the obstacle
            #   self.flight_session.mode = Modes.NETWORKED_COMMANDS
            time.sleep(0.0001)