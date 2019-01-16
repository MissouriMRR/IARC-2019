import logging
import sys
import threading
from ast import literal_eval

from real_time_graphing import RealTimeGraph


class RTGCache:
    """
    Creates rtg and caches data for it.

    Meant to be run within subprocess.

    Version: python 2.7 / 3.6
    """

    def __init__(self):
        self.data = {}

        self.rtg = RealTimeGraph(get_data=self.pull)

        self.thread_stop = threading.Event()

        self.stdin_reader_thread = threading.Thread(target=self.repeating_read_stdin, args=(self.thread_stop,))

    def start(self):
        """
        Start rtg & stdin reader thread.
        """

        self.stdin_reader_thread.start()

        self.rtg.run()  # Ran in main thread

        self.thread_stop.set()

        self.stdin_reader_thread.join()

    def pull(self):
        """
        Return stored data.
        """

        return self.data

    def read_stdin(self):
        """
        Read from stdin.
        """

        try:
            received = sys.stdin.readline()  # No timeout because this should be run in subprocess

            if type(received) is str:
                data = literal_eval(received)
            elif type(received) is dict:
                data = received
            else:
                logging.warning("Cache: Input type unexpected! Type: {}, Raw: {}".format(type(received), received))

            logging.debug("Cache: Received: {}".format(data))

            self.data = data

        except EOFError as e:
            logging.warning("Cache: Data not received! {}".format(e))

    def repeating_read_stdin(self, stopper):
        """
        Continuously read stdin.
        """

        while not stopper.is_set():
            self.read_stdin()


if __name__ == '__main__':
    cache = RTGCache()
    cache.start()
