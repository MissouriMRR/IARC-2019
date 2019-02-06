import os
import unittest

import simple_imports
simple_imports.import_distributor()

from rtg.file_io import file_io


class FileIOTest(unittest.TestCase):
    file0 = 'test_configs/file_io/possible_metrics.xml'
    file1 = 'test_configs/file_io/test_config1.xml'
    file2 = 'test_configs/file_io/test_config2.xml'

    expected_parse = [{'title': 'Multivariable test', 'metrics': [], 'xlabel': 'Seconds', 'ylabel': 'x', 'output': None, 'legend': None},
                          {'title': 'Test 1', 'metrics': [], 'xlabel': 'Seconds', 'ylabel': 'Pitch', 'output': None, 'legend': 'no'},
                          {'title': 'Test 2', 'metrics': [], 'xlabel': 'Seconds', 'ylabel': 'Roll', 'output': None, 'legend': None},
                          {'title': None, 'metrics': [], 'xlabel': None, 'ylabel': None, 'output': 'text', 'legend': None}]

    def test_parse_config(self):
        """
        Should return a certain set of data
        """
        self.assertEqual(file_io.parse_config(FileIOTest.file1), FileIOTest.expected_parse)

    def test_write_config(self):
        """
        The file should contain the same data as the one it pulled from
        """

        if os._exists(FileIOTest.file2): os.remove(FileIOTest.file2)

        file_io.write_config(FileIOTest.file2, file_io.parse_config(FileIOTest.file1))

        # Parsing must work for this test

        self.assertEqual(file_io.parse_config(FileIOTest.file2), FileIOTest.expected_parse)

        os.remove(FileIOTest.file2)

    def test_possible_metrics(self):
        """
        Should return list of metrics
        """
        # print(file_io.possible_metrics(FileIOTest.file0))
        self.assertEqual(file_io.possible_metrics(FileIOTest.file0),
                         {'Airspeed': [('airspeed', None, None), None],
                          'Voltage': [('voltage', None, None), None],
                          'Pitch': [('pitch', None, None), None],
                          'Yaw': [('yaw', None, None), None],
                          'Altitude': [('altitude', None, None), None],
                          'Roll': [('roll', None, None), None]})


if __name__ == '__main__':
    unittest.main()
