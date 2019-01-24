# Standard Library
import abc

class InstructionBase():
    """An instruction that a drone can follow.

    Responsible for decoding data sent over the network and
    using that data to create tasks.

    Notes
    -----
    This class will be important once we start sendind messages over the
    network, but is currently in a simplified state.
    """
    __metaclass__ = abc.ABCMeta

    # Subclasses of this class should define an init function

    @abc.abstractmethod
    def get_task(self):
        """Get a task that the drone can execute.

        Decodes the raw instruction data into the appropriate instance
        of a Task object, which should be fully configured and ready
        for the perform() function to be called. The instruction must be
        properly initialized before calling this function.

        Returns
        -------
        TaskBase subclass
            The task for the drone to perform.
        """
        pass
