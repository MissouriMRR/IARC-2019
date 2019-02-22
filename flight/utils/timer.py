""""A class that allows for the execution of arbitrary code at set intervals."""

from time import sleep
from timeit import default_timer as timer
import threading

class Timer():
    """ Runs code as specified intervals. """
    def __init__(self):
        self._event_threads = []
        self._stop_event_map = {}
        self._thread_map = {}
        self._lock = threading.Lock()
        self._num_threads_lock = threading.Lock()

        self.reset()

    def _create_event_thread(self, closure, name):
        stop_event = threading.Event()
        self._stop_event_map[name] = stop_event
        thread = threading.Thread(target=closure, args=(stop_event,))
        thread.daemon = True
        self._thread_map[name] = thread
        self._event_threads.append(thread)
        thread.start()

    @property
    def num_threads(self):
        with self._num_threads_lock:
            return len(self._event_threads)

    def add_callback(self, name, when_to_call, callback, recurring=False):
        """ Add a block of code that is called every when_to_call seconds. """
        if name in self._stop_event_map:
            raise ValueError('The `name` parameter cannot be assigned the \
                duplicate name: "{}"!'.format(name))

        if when_to_call <= self.elapsed:
            callback()
            return

        def handle_event(stop_event):
            while recurring and not stop_event.is_set():
                sleep(max(when_to_call-self.elapsed, 0))
                event_handled = False
                while (((not event_handled) or recurring) and
                    not stop_event.is_set()):
                    if when_to_call <= self.elapsed:
                        callback()
                        event_handled = True
                        break

                    sleep(1e-3)

                if self.num_threads == 1 and recurring:
                    self.reset()

        self._create_event_thread(handle_event, name)

    def stop_callback(self, name):
        self._stop_event_map[name].set()

    def shutdown(self):
        for name, stop_event in self._stop_event_map.items():
            stop_event.set()
            self._thread_map[name].join()

    @property
    def elapsed(self):
        with self._lock as lock:
            return timer() - self._start

    def reset(self):
        with self._lock:
            self._start = timer()
