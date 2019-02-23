"""Provides a continuous command line prompt for testing drone capabilities."""

import argparse
import threading

from flight.drone.drone_controller import DroneController
from flight import constants as c

PROMPT_FOR_COMMAND = '> '


def main():
    parser = create_parser()
    args = parser.parse_args()

    # Make the controller object
    controller = DroneController(is_simulation=args.sim)

    # Make a thread whose target is a command line interface
    input_thread = threading.Thread(
        target=input_loop, args=(controller,))

    input_thread.daemon = True

    input_thread.start()

    controller.run()


def create_parser():
    """Returns a configured argument parser."""
    parser = argparse.ArgumentParser(description='Test flight commands.')
    parser.add_argument('--sim',
                        dest='sim',
                        action='store_true',
                        default=False,
                        help='run simulator compatible flight code')
    return parser

class ExitRequested(Exception):
    """Raised when the input loop should stop."""
    pass


class Command(object):
    """A command line argument that can be translated into a drone command.

    Attributes
    ----------
    _controller : DroneController
        Interface to adding a command to the drone.
    """

    def __init__(self, controller):
        """Initialize the given command.

        Notes
        -----
        Subclasses must assign a list to self._expected_order or else this
        class will break. The list contains the types (in expected order) that
        the given command takes.
        """
        self._controller = controller

    def matches(self, *args):
        """Validates the command line arguments.

        Notes
        -----
        This function must be called before calling __call__, because it
        populates the _parameters.
        """
        if len(args) != len(self._expected_order):
            raise TypeError('Expected {} arguments, got {}.'.format(
                len(self._expected_order), len(args)))

        for param, cast in zip(args, self._expected_order):
            self._parameters.append(cast(param))

    def __call__(self, *args):
        """Adds the command as a task on the drone controller."""
        # implement command here:
        pass


class HoverCommand(Command):
    def __init__(self, controller):
        super(HoverCommand, self).__init__(controller)
        self._expected_order = [float, float, get_priority]
        self._parameters = []

    def __call__(self, *args):
        self._controller.add_hover_task(*self._parameters)


class MoveCommand(Command):
    def __init__(self, controller):
        super(MoveCommand, self).__init__(controller)
        self._expected_order = [get_direction, float, get_priority]
        self._parameters = []

    def __call__(self, *args):
        self._controller.add_linear_movement_task(*self._parameters)


class TakeoffCommand(Command):
    def __init__(self, controller):
        super(TakeoffCommand, self).__init__(controller)
        self._expected_order = [float]
        self._parameters = []

    def __call__(self, *args):
        self._controller.add_takeoff_task(*self._parameters)


class LandCommand(Command):
    def __init__(self, controller):
        super(LandCommand, self).__init__(controller)
        self._expected_order = [get_priority]
        self._parameters = []

    def __call__(self, *args):
        self._controller.add_land_task(*self._parameters)


class ExitCommand(Command):
    def __init__(self, controller):
        super(ExitCommand, self).__init__(controller)
        self._expected_order = []

    def __call__(self, *args):
        self._controller.add_exit_task(c.Priorities.HIGH)
        raise ExitRequested


NAME_TO_COMMAND = {
    'hover': HoverCommand,
    'move': MoveCommand,
    'takeoff': TakeoffCommand,
    'land': LandCommand,
    'exit': ExitCommand
}


def input_loop(controller):
    """Simple command line interface to drone controller.

    exit: lands and terminates program
    land: land <priority>
    hover: hover <duration> <priority>
    takeoff: takeoff <altitude>
    move: move <FOWARD,BACKWARD,LEFT,RIGHT> <duration> <priority>

    Notes
    -----
    Priority is one of "high", "med", or "low".
    """
    while True:
        try:
            args = raw_input(PROMPT_FOR_COMMAND).lower().split()
            if not len(args):
                continue
            command = args[0]
            if command in NAME_TO_COMMAND:
                command_instance = NAME_TO_COMMAND[command](controller)
                command_instance.matches(*args[1:])
                command_instance()
            else:
                raise ValueError('Unknown command: {}'.format(command))
        except Exception as e:
            if isinstance(e, ExitRequested):
                print('Closing session.')
                return

            print('{}{}: {}'.format(PROMPT_FOR_COMMAND, type(e).__name__, e))


def get_priority(priority):
    """Gets priority level from a string."""
    key = priority.upper()
    if hasattr(c.Priorities, key):
        converted_form = getattr(c.Priorities, key)
    else:
        raise TypeError(
            'Expected value for type {}, got {}.'.format(
                type(c.Priorities).__name__, priority))

    return converted_form


def get_direction(direction):
    """Gets direction from a string."""
    key = direction.upper()
    if hasattr(c.Directions, key):
        converted_form = getattr(c.Directions, key)
    else:
        raise TypeError(
            'Expected value for type {}, got {}.'.format(
                type(c.Directions).__name__, direction))

    return converted_form


if __name__ == '__main__':
    main()
