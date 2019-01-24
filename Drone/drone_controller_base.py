# Standard Library
import abc

class DroneControllerBase():
    """Base class for controlling the actions of a drone.

    Responsible for managing the execution of tasks, maintaining a queue of
    instructions, and responding gracefully to emergency landing events.

    Attributes
    ----------
    _id : int
        Identification number used by the swarm controller to distinguish
        between the drones.
    instruction_queue : list of InstructionBase subclass
        A priority queue holding instruction sent from the swarm controller or
        inter-drone communication.
    current_instruction : InstructionBase subclass
        The instruction currently being processed.
    task : TaskBase subclass
        The task the drone is currently working on.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self._id = None
        self._instruction_queue = []
        self._current_instruction = None
        self._task = None

    # Lets the swarm controller know that an instruction is finished
    def _notify_instruction_finished(self, instructionId):
        """Notify the swarm controller that an instruction has been completed.

        Asynchronously let the swarm controller know that the instruction with
        the given id has been completed.
        """
        #
        pass

    @abc.abstractmethod
    def _read_next_instruction(self):
        """Read the next instruction on the instruction heap.

        Discards the old instruction and updates the current instruction to
        the next instruction of highest priority. Constructs a task from the
        retrieved instruction. The instruction queue must not be empty.
        """
        pass

    @abc.abstractmethod
    def _update(self):
        """Execute one iteration of control logic.

        Checks that a land event has not been set and executes the
        next iteration of the current task, if one exists.

        Returns
        -------
        bool
            False if the update should continue to be called and false
            otherwise
        """
        pass

    # Attempts to establish a connection with the swarm controller
    def connect_to_swarm(self):
        """Connect to the swarm controller over the network."""
        pass

    @property
    def id(self):
        """Get the drone's id"""
        return self._id

    @id.setter
    def id(self, identifier):
        """Set the drone's id."""
        self._id = identifier
