import heapq

# Used to ensure tasks of equal priority are first-in, first_out
DEFAULT_COUNT = 900000
# Used to determine an items priority from its value
PRIORITY_MASK = 1000000
# Index into front of queue
FRONT = 0
# Priority part of stored values
PRIORITY = 0
# Item part of stored values
ITEM = 1

class PriorityQueue():
    """Custom priority queue implementation.

    This purpose of this class is to simplify the insertion and removal of
    items from the priority queue.

    Attributes
    ----------
    _queue: heapq
        The priority queue.
    """

    count = DEFAULT_COUNT

    def __init__(self):
        self._queue = []

    def push(self, priority, item):
        """Insert an item onto the priority queue.

        Parameters
        ----------
        priority : Priority.{LOW, MEDIUM, HIGH}
            The priority of the task, with higher priority causes the item to
            "cut ahead" of items of lower priority.
        item : Any
            The data being inserted into the queue.

        Notes
        -----
        If an item of equal or higher priority to the front of the queue is
        pushed, the current front will be dequed.

        """
        # Interrupt tasks of equal or lesser priority
        if len(self._queue) and (priority.value <=
                self._queue[FRONT][PRIORITY] // PRIORITY_MASK):
            self._queue.pop()

        val = int('{}{}'.format(priority.value, PriorityQueue.count))
        PriorityQueue.count += 1
        heapq.heappush(self._queue, (val, item))

    def pop(self):
        """Remove the next item from the priortiy queue.

        Returns
        -------
        An item, or None if the priority queue is empty.
        """
        if len(self):
            # Index 0 is priority, index 1 is the item.
            return heapq.heappop(self._queue)[1]
        else:
            return None

    def top(self):
        if len(self):
        # Index 0 is priority, index 1 is the item.
            return self._queue[FRONT][ITEM]
        else:
            return None

    def empty(self):
        """Check if the priority queue is empty.

        Returns
        -------
        bool
            True if the priority queue is empty, and false otherwise.
        """
        if not len(self):
            return True
        else:
            return False

    def clear(self):
        """Empty out the priority queue, deleting all the items.
        """
        self.queue = []

    def __len__(self):
        return len(self._queue)
