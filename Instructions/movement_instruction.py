from collections import deque

# Ours
from ..Tasks.movement_task import MovementTask
from instruction_base import InstructionBase
from ..Utilities.constants import Directions

class MovementInstruction(InstructionBase):

    def __init__(self, data):
        super(MovementInstruction, self).__init__()
        # The data here will eventually be the raw binary data that
        # has traveled over the network. The decoding may be more
        # involved than what is shown here.
        self.x, self.y, self.z = data

        self.movement_task = None

    def get_task(self, drone):
        queue = deque()

        direction_map = {
            'x':  (Directions.FORWARD, Directions.BACKWARD),
            'y': (Directions.LEFT, Directions.RIGHT),
            'z': (Directions.UP, Directions.DOWN)
        }

        positive_vector_index = 0
        negative_vector_index = 1
        for direction, vectors in direction_map.items():
            value = getattr(self, direction)
            if value != 0:
                queue.append(
                    (vectors[positive_vector_index if value > 0
                        else negative_vector_index], abs(value)))

        self.movement_task = MovementTask(drone, queue)

        return self.movement_task
