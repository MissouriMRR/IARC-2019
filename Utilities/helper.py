""" Helper functions used across multiple directories"""

import threading

def current_thread_name():
    """Get the name of the current thread."""
    return threading.current_thread().name