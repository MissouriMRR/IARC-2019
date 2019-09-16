"""
Convert points to TS space.
"""
import cv2
import numpy as np


def binarize_mat(img, threshold=.5):
    """
    Convert mat to binary based on threshold.

    Parameters
    ----------
    img: mat
    	OpenCV mat.
    threshold: float
        Threshold value.

    Returns
    -------
    Mat with all values in [0, 1].
    """

    img = np.where(img > threshold, 1., 0.)

    return img


def pix_to_opengl(values, window_width, window_height):
    """
    Because the location of 1.0 in opengl varies by the number of pixels
    in the window.

    Formula
    -------
    https://stackoverflow.com/questions/30242385/convert-pixel-length-to-opengl-coordinates

    Parameters
    ----------
    Values: np array
        Array of values [x, y, z, ...] to convert.

    window_width: int
        Width of window to be displayed in.

    window_height: int
        Height of window to be displayed in.
 
    Returns
    -------
    np array of verticies that opengl can work with.
    """
    out = []

    for i in range(0, len(values), 3):
        old_x = values[i]
        old_y = values[i+1]
        old_z = values[i+2]

        new_x = (2.0 * old_x + 1.0) / window_width - 1.0
        new_y = (2.0 * old_y + 1.0) / window_height - 1.0
        new_z = old_z

        out += [new_x, new_y, new_z]

    return np.array(out, dtype=np.float32)


def get_ts_verticies(edges, u_offset, v_offset, v_scale, d, z=0.):
    """
    Convert edge coordinates to two-segment polyline defined by
    three points: (−d, −y),(0, x),(d, y), for TS space.

    Parameters
    ----------
    edges: mat
    	1 channel binary OpenCV mat.
    d: float
    	Spacing between axis along u.
    z: float
    	Z value.

    Returns
    -------
    Numpy array[float32] of pairs of 3 representing verticies of lines.
    """
    z = float(z)

    rule = lambda x, y: [
        0. + u_offset, x * v_scale + v_offset, z, 
        -d + u_offset, -y * v_scale + v_offset, z,
        0. + u_offset, x * v_scale + v_offset, z, 
        d + u_offset, y * v_scale + v_offset, z]

    verticies = []
    for index, value in np.ndenumerate(edges):
        if value == 1:
            verticies += rule(*map(float, index))

    return np.array(verticies, dtype=np.float32)


if __name__ == '__main__':
    edges = cv2.imread('edges.jpg', 0)

    get_ts_verticies(binarize_mat(edges))
