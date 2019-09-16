"""
Unit test for normalizing image.
"""
import unittest

import cv2
import numpy as np
import matplotlib.pyplot as plt

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from normalize.ts_converter import binarize_mat


class TestNormalizer(unittest.TestCase):
    """
    Image normalizer tester.
    """

    def test_binarize(self):
        """
        Test image binarizer.
        """
        SIZE = 512

        # joint gaussian
        x, y = np.meshgrid(np.linspace(-1, 1, SIZE), np.linspace(-1, 1, SIZE))
        d = np.sqrt(x**2 + y**2)
        sigma, mu = 1.0, 0.0
        gaussian = np.exp(-((d - mu)**2 / (2.0 * sigma**2)))

        img = binarize_mat(gaussian)

        self.assertEqual(len(np.unique(img)), 2)

    def visualize_ts(self, img):
        """
        Visualize the ts space representation of an image, points with a 
        value of 1 will be converted to ts space.

        Parameters
        ----------
        img: opencv mat
            Image to be converted to ts space.
        """
        verticies = get_ts_verticies(img, u=20, z=0.)

        X = []
        Y = []
        for i in range(len(verticies), 3):  # update
            X.append(verticies[i])
            Y.append(verticies[i+1])

        plt.plot(X, Y)
        plt.show()


if __name__ == '__main__':
    unittest.main()
