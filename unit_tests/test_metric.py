import unittest

import simple_imports
simple_imports.import_distributor()

from rtg.metric import metric


class MetricTest(unittest.TestCase):
    def test_function_interpreting(self):
        """
        Should return a certain set of data
        """

        test = metric.Metric(None, func="x * 5", x_stream="yaw")

        self.assertEqual(test.raw_func, "x * 5")

        self.assertEqual(test.func(5), 25)


if __name__ == '__main__':
    unittest.main()
