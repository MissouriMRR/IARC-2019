import threading

class SharedLock():
    """A shared lock for timing events.

    A class that follows the singleton design pattern. Allows
    any thread that imports this class to get a reference to the
    lock that is to be shared across all threads.

    Attributes
    ----------
    lock : threading.Lock
        A static variable that is shared among all threads
    """
    lock = None

    def __init__(self):
        self.lock = None

    @staticmethod
    def get_lock():
        if SharedLock.lock is None:
            SharedLock.lock = threading.Lock()

        return SharedLock.lock