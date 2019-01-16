import logging
from time import sleep, time

from interprocess_communication import IPC
from logger import Logger


class DataSplitter:
    """
    Send data to this and it will send to both the logger & IPC(RTG)

    Version: python 2.7

    Parameters
    ----------
    logger_desired_headers: list, default=[]
        Headers for logger to log data for. Logger object not created if no headers given.

    use_rtg: bool, default=True
        Whether to use the real time grapher or not.
    """

    def __init__(self, logger_desired_headers=[], use_rtg=True):

        # Enable or disable each tool based on parameter choice

        if not logger_desired_headers:
            logging.critical("Splitter: Logger disabled.")
            self.logger = None
        else:
            self.logger = Logger(logger_desired_headers)

        if not use_rtg:
            logging.warning("Splitter: RTG Disabled.")
            self.ipc = None
        else:
            self.ipc = IPC()

    @property
    def active_tools(self):
        """
        Returns all active tool objects.
        """

        tools_active = []

        if self.logger:
            tools_active.append(self.logger)

        if self.ipc:
            tools_active.append(self.ipc)

        return tools_active

    def exit(self):
        """
        Safely close all created tools.
        """

        logging.warning("Splitter: Exiting all tools...")

        for tool in self.active_tools:
            tool.quit()

        logging.warning("Splitter: Successfully exited.")

    def send(self, data):
        """
        Send data everywhere.

        Parameters
        ----------
        data: dict {header: value}
            Data to dispatch.
        """

        if self.logger:
            self.logger.update(data)

        if self.ipc:
            if self.ipc.alive:
                self.ipc.send(data)
            else:
                logging.critical("Splitter: IPC Dead! Removing.")
                self.ipc.quit()
                self.ipc = None
