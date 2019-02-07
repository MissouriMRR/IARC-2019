import unittest

from ..flight.utils.priority_queue import PriorityQueue
from ..flight.constants import Priorities

class TestPriorityQueue(unittest.TestCase):
    def test_insertion(self):
        """Test that items are able to be inserted an removed."""
        queue = PriorityQueue()
        sample_item = 5
        queue.push(Priorities.MEDIUM, sample_item)
        returned_item = queue.pop()
        self.assertEqual(sample_item, returned_item, "Not inserting and \
        removing items correctly.")

    def test_proper_order(self):
        """Test that a mixed-bag of priorities comes out in the right order."""
        queue = PriorityQueue()
        items = [1, 2, 3]
        priorities = [Priorities.LOW, Priorities.MEDIUM, Priorities.HIGH]
        for item, priority in zip(items, priorities):
            queue.push(priority, item)

        items.reverse()
        for item in items:
            self.assertEqual(item, queue.pop(), "Not returning items with \
            higher priority first.")

    def test_pop_empty_queue(self):
        """Test that popping an empty queue does not throw an error."""
        queue = PriorityQueue()

        item = queue.pop()
        self.assertEqual(item, None)

    def test_empty_function(self):
        """Test that empty returns false when item are in the queue."""
        queue = PriorityQueue()
        self.assertTrue(queue.empty(), "Empty queue claiming it is not empty")


        queue.push(Priorities.LOW, "Sample string")
        self.assertFalse(queue.empty(), "Non-empty queue claiming it is \
        empty.")

if __name__ == '__main__':
    unittest.main()
