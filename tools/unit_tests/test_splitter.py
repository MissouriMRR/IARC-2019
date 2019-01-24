import parent_directory

import unittest
from data_splitter import DataSplitter

from logger import Logger
from interprocess_communication import IPC


def execute_test(obj):
    for _ in range(10):
        obj.send({'pitch': 1, 'roll': 2, 'yaw': 3})

    tools = obj.active_tools

    obj.exit()

    return tools


class RTGTest(unittest.TestCase):
    def test_use_all(self):
        """
        Test with all tools on.
        """

        demo = DataSplitter(['pitch', 'altitude', 'roll', 'yaw', 'voltage'], use_rtg=True)

        tools_active = execute_test(demo)

        for tool in tools_active:
            self.assertTrue((tool.__class__ in (Logger, IPC)))

    def test_use_ipc(self):
        """
        Test if ipc turns on from splitter.
        """

        demo = DataSplitter([], use_rtg=True)

        tools_active = execute_test(demo)

        for tool in tools_active:
            self.assertTrue((tool.__class__ is IPC))

    def test_use_log(self):
        """
        Test if logger turns on from logger.
        """

        demo = DataSplitter(['pitch', 'altitude', 'roll', 'yaw', 'voltage'], use_rtg=False)

        tools_active = execute_test(demo)

        for tool in tools_active:
            self.assertTrue((tool.__class__ is Logger))

    def test_use_none(self):
        """
        Test splitter with no tools.
        """

        demo = DataSplitter(use_rtg=False)

        tools_active = execute_test(demo)

        self.assertTrue(tools_active == [])


if __name__ == '__main__':
    unittest.main()
