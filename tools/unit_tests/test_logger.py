import parent_directory

import unittest

from pandas import read_csv
from numpy import nan
from logger import Logger


class LoggerTest(unittest.TestCase):
    expected_output = []

    def test_parse_config(self):
        """
        Should return a certain set of data
        """

        my_logger = Logger(['pitch', 'roll', 'yaw'])

        def func(x):
            return x % 5

        for i in range(10):  # main loop
            my_logger.update({
                'altitude': func(i) + .1,
                'pitch': func(i) + .2,
                'roll': func(i) + .3,
            })

        filename = my_logger.directory

        my_logger.quit()

        data = read_csv(filename)

        # Make sure yaw shows up nan
        self.assertEqual(str(data['yaw'][0]), str(nan))

        # Make sure altitude didn't get logged
        with self.assertRaises(KeyError):
            print(data['altitude'])


if __name__ == '__main__':
    unittest.main()
