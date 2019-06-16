"""
Convert points to TS space.
"""
import cv2
import numpy as np


def binarize_mat(img):
    """
    Convert mat to binary based on threshold.

    Parameters
    ----------
    img: mat
    	OpenCV mat.

    Returns
    -------
    Mat with all values in [0, 1].
    """

    img = np.where(img > .5, 1., 0.)

    return img


def get_ts_verticies(edges, u=10., z=1.):
    """
    Convert edge coordinates to verticies of lines in TS space.

    Parameters
    ----------
    edges: mat
    	1 channel binary OpenCV mat.
    u: float
    	Scale of u axis.
    z: float
    	Z value.

    Returns
    -------
    List of pairs of 3 tuples representing verticies of lines.
    """
    rule = lambda x, y: [(-u, -y, z), (0., x, z), (0., x, z), (u, y, z)]

    verticies = []
    for index, value in np.ndenumerate(edges):
        if value == 1:
            verticies += rule(*index)

    return verticies


if __name__ == '__main__':
    edges = cv2.imread('edges.jpg', 0)

    get_ts_verticies(binarize_mat(edges))
