import os
import logging

import shlex
import subprocess
import threading
from time import sleep


_command_whitelist = ['python']
_filename_whitelist = ['rtg_cache.py']


class IPC:
    """
    Creates subprocess in python 2.7 that it can send and receive data from.

    Version: python 2.7

    Parameters
    ----------
    reader: bool, default=True
        Whether or not to use the shell reader.

    thread_stop: threading.Event, default=threading.Event
        The thread stop to be used by shell reader, pass in own thread stop or allow it to create its own.
    """

    command = 'python'  # Command to start python 2.7

    def __init__(self, reader=True, thread_stop=threading.Event(), target_path="rtg_cache.py"):
        self.thread_stop = thread_stop

        # Get filename

        filename = os.path.dirname(__file__)

        if filename and filename[-1] is not os.path.sep:
            filename += '/'

        filename += target_path

        # Start subprocess

        try:
            # Attempt start

            if IPC.command in _command_whitelist and target_path in _filename_whitelist:
                command_w_args = shlex.split('{} {}'.format(IPC.command, filename), posix=0)
                command_w_args = shlex.split('{} {}'.format(IPC.command, filename), posix=0)

                if reader:
                    self.subprocess = subprocess.Popen(command_w_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
                else:
                    self.subprocess = subprocess.Popen(command_w_args, stdin=subprocess.PIPE)
            else:
                raise ValueError("Command '{}' not in whitelist!".format(IPC.command))

            sleep(.1)  # Give time to start / fail to start

            # See if started

            if self.subprocess.poll():
                _, error_output = self.subprocess.communicate()
                logging.warning("IPC: Poll: {}".format(error_output))

        except Exception as e:
            raise IOError("IPC: {}".format(e))

        # Shell reader

        if reader:
            self.reader_thread = threading.Thread(target=self.continuous_shell_reader)
            self.reader_thread.start()

    def __enter__(self):
        """
        On enter with statement.
        """

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        On exit with statement.
        """

        self.quit()

    @property
    def alive(self):
        """
        If process is still alive or not.
        """

        return self.subprocess.poll() is None and not self.thread_stop.is_set()

    def quit(self):
        """
        Terminates subprocess and created thread.
        """

        logging.warning("IPC: Quitting.")
        try:
            self.subprocess.terminate()
        except OSError:
            logging.warning("Failed to terminate subprocess.")
        self.thread_stop.set()

        if self.reader_thread:
            try:
                self.reader_thread.join()
            except RuntimeError:
                pass

    def send(self, data):
        """
        Send data to subprocess.

        Parameters
        ----------
        data:
            Data in format subprocess can read.
        """

        if self.subprocess.poll() is None:
            try:
                self.subprocess.stdin.write("{}\n".format(str(data).encode()))
            except IOError as e:
                logging.warning("IPC: Failed to send data! IOError: {}".format(e))

            logging.debug("IPC: {}".format(str(data)))
        else:
            logging.error("IPC: Process is dead! Poll: {}".format(self.subprocess.poll()))

    def shell_reader(self):
        """
        Returns output from generated subprocess shell.
        """

        return self.subprocess.stdout.readline().strip()  # output w/out \n

    def continuous_shell_reader(self):
        """
        Continuously read output form subprocess shell
        """

        while not self.thread_stop.is_set():
            out = self.shell_reader()

            if not out == "":
                print("IPC: Received: {}".format(out))
