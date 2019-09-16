import numpy as np


def crop(image, line_eq):
    """
    Crop an image based on given line equations.

    Parameters
    ----------
    image: 2d np array
        Image to crop.
    line_eq: [(m, b), ...]
        Line equations to crop by.

    Returns
    -------
    Cropped image.
    """


def stitch(im1, im2, im3, im4):
    """
    Stitch images together.

    Parameters
    ----------
    im1: 2d np array
        Image for quartile 1.
    ...

    Returns
    -------
    Image of all images put together.
    """
    WIDTH = max(len(im1[0]), len(im3[0])) + max(len(im2[0]), len(im4[0]))
    HEIGHT = max(len(im1), len(im2)) + max(len(im4), len(im3))

    out = np.zeros(shape=(HEIGHT, WIDTH))

    """
    |-----------------|
    |        |        |
    | |------|  im1   |
    | | im2  |        |
    | |      |        |
    |-------a,b-------|
    |        | im4 |  |
    |  im3   |-----|  |
    |        |        |
    |-----------------|
    """

    a = max(len(im2[0]), len(im3[0]))
    b = max(len(im1), len(im2))

    out[b-len(im1):b, a:a+len(im1[0])] = im1
    out[b-len(im2):b, a-len(im2[0]): a] = im2

    out[b:b+len(im3), a-len(im3[0]):a] = im3
    out[b:b+len(im4), a:a+len(im4[0])] = im4

    return out


if __name__ == '__main__':
    im1 = 1 * np.ones(shape=(4, 4))
    im2 = 2 * np.ones(shape=(3, 3))
    im3 = 3 * np.ones(shape=(2, 2))
    im4 = 4 * np.ones(shape=(1, 1))

    output = stitch(im1, im2, im3, im4)

    print(output)