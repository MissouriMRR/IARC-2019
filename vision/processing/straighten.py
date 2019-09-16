"""
Make a cropped piece of an image square
"""
import numpy as np
import cv2


def straighten(img, pts):
    """
    Straighten a section of an image

    https://stackoverflow.com/questions/41995916/opencv-straighten-an-image-with-python

    Parameters
    ----------
    img: cv2 img(np.array)
        Base image.
    pts: list of 4 x, y coordinates
        Points that make up bounding box of image to be straightened.

    Returns
    -------
    Straightened version of the image within given coordinates.
    """

    HEIGHT = 552
    WIDTH = 77

    CHANNELS = 3

    #---- 4 corner points of the bounding box
    pts_src = np.array([[17, 0], [77, 5], [0, 552], [53, 552]])

    #---- 4 corner points of the black image you want to impose it on
    pts_dst = np.array([[0, 0], [WIDTH, 0], [0, HEIGHT], [WIDTH, HEIGHT]])

    #---- forming the black image of specific size
    im_dst = np.zeros((HEIGHT, WIDTH, CHANNELS) if CHANNELS > 1 else (HEIGHT, WIDTH), np.uint8)

    #---- Framing the homography matrix
    h, _ = cv2.findHomography(pts_src, pts_dst)

    #---- transforming the image bound in the rectangle to straighten
    out = cv2.warpPerspective(img, h, (im_dst.shape[1], im_dst.shape[0]))

    return out


if __name__ == '__main__':
    output = straighten()

    cv2.imshow("", output)
