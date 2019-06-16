"""
Unit test for grayscaling image.
"""
import cv2
import numpy as np

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ts_converter import binarize_mat


if __name__ == '__main__':
    SIZE = 512

    # joint gaussian
    x, y = np.meshgrid(np.linspace(-1, 1, SIZE), np.linspace(-1, 1, SIZE))
    d = np.sqrt(x**2 + y**2)
    sigma, mu = 1.0, 0.0
    gaussian = np.exp(-((d - mu)**2 / (2.0 * sigma**2)))

    img = binarize_mat(gaussian)

    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
