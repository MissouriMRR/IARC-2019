"""
Pipeline from image of qr code to sending its value.
"""
import cv2
import numpy as np
from scipy.signal import argrelextrema

from generator.QrCode import QrCode
from normalize.edges import get_edges
from normalize.ts_converter import get_ts_verticies, binarize_mat, pix_to_opengl
from accumulator.py_to_cpp import TS


## Add to pipeline
from processing.crop_n_stitch import crop, stitch
from processing.straighten import straighten
from processing.read import read


def preprocess(imgs):
    """
    Preprocess images.
    """
    for i in range(len(imgs)):
        img = imgs[i]

        img = 255 - img

        edges = get_edges(img)

        edges = cv2.GaussianBlur(edges, (3, 3), cv2.BORDER_DEFAULT)

        img = binarize_mat(edges, threshold=.98)

        img = cv2.GaussianBlur(img, (5, 5), cv2.BORDER_DEFAULT)

        img = binarize_mat(edges, threshold=.96)

        imgs[i] = img

    return imgs


def permute_ordering(im1, im2, im3, im4):
    """
    Permute every stiching ordering in hopes of finding one that pyzbar
    will read.
    
    Parameters
    ----------
    im: 4 cv2 images(np.array)
        Images of sections of qr codes.

    Returns
    -------
    Interpreted code if successful else none.
    """
    sections1 = [im1, im2, im3, im4]

    for i, image1 in enumerate(sections1):
        sections2 = sections1.copy()
        del sections2[i]

        for j, image2 in enumerate(sections2):
            sections3 = sections2.copy()
            del sections3[j]

            for k, image3 in enumerate(sections3):
                sections4 = sections3.copy()
                del sections4[k]

                image4 = sections4[0]

                full_image = stitch(image1, image2, image3, image4)

                code = read(full_image)

                if code:
                    return code

    return None


def PCLines(edges):
    """
    PC Lines algorithm for detecting lines.

    Parameters
    ----------
    edges: image
        Values to calculate line formula from.

    Returns
    -------
    Detected slope intercept parameters [(m, b), ...].

    Description
    -----------
    Convert cartesian to line segments in Twisted and Straight space.
    Straight space consists of the parralel axes x', y'.
    Twisted space consists of the parralel axes x', -y'.

       v    T          S
       |-y        |x         |y
       |          |          |
       |          |          |
    ---|----------|----------|---u
       |-d        |0         |d
       |          |          |
       |          |          |
    (T and S space attatched in the uv plane. Parralel axes separated by
    distance d along the u axis. Each parralel axis is length v.)

    The length of the axis u and v does not need to be infinite. u only
    needs to fill cover the interval [-d, d], v needs to cover the interval
    [-max(W/2, H/2), max(W/2, H/2)] (W is width of plane, H is height).

    Line formulas are calculated in slope intercept form. Local maxima
    in TS space, above a theshold, are thought to be relevant lines.

    Line formula based on space:
        ℓ: y = mx + b
        ℓS = (d, b, 1 − m),  −∞ ≤ m ≤ 0
        ℓT = (−d, −b, 1 + m),  0 ≤ m ≤ ∞.

        ℓ has one image in TS space; except when m = 0 or m = ±∞, 
        meaning, when ℓ lies in both spaces either on axis x' or y'.

        Attaching the y′ and −y′ axes results in an enclosed Mobius strip.

    Slope based on location
        ℓ is between x' & y' iff −∞ < m < 0.
        ℓ is between x' & -y' iff 0 < m < ∞.
        ℓ is on the x' axis for vertical lines m = ±∞.
        ℓ is on the y', -y' axis at m=0.
        ℓ is an ideal point, at infinity, at m=1.
    """
    N_MAXIMA = 500

    V_SCALE = 1

    IMG_WIDTH = len(edges[0])
    IMG_HEIGHT = len(edges)

    scale = 1  # width needs to be set in fragment shader also!
    TS_WIDTH = int(1024 * scale) # >=  2 * D + 10
    TS_HEIGHT = int(768 * scale) # >= max(IMG_WIDTH, IMG_HEIGHT)

    U_OFFSET = TS_WIDTH // 2
    V_OFFSET = TS_HEIGHT // 2

    D = TS_WIDTH // 2 - 1

    verticies = get_ts_verticies(edges, U_OFFSET, V_OFFSET, V_SCALE, D)

    opengl_verticies = pix_to_opengl(verticies, TS_WIDTH, TS_HEIGHT)

    space = TS(TS_WIDTH, TS_HEIGHT, opengl_verticies)
    accumulated = space.accumulate()

    accumulated = accumulated.reshape((TS_HEIGHT, TS_WIDTH))

    accumulated = accumulated[::-1]

    # cv2.imshow("img", np.where(accumulated > 0, 1, 0.))
    # cv2.waitKey(0)

    ########################
    # S Space
    # ℓ : u = d/(1-m)
    # ℓ : v = b/(1-m)

    # m = -d/u + 1
    # b = dv/u

    # T Space
    # ℓ : u = -d/(1+m)
    # ℓ : v = -b/(1+m)

    # m = -d/u - 1
    # b = dv/u

    # Parametrization
    ## y = mx + b
    ## point l* has (d, b, 1-m)

    def m(u):
        """
        Calculate slope based off u axis.
        """
        # S: + 1, T: -1
        if u == 0:
            return 0
        elif u > 0:
            return (-D / u) + 1
        else:
            return (-D / u) - 1

    def b(u, v):
        """
        Calculate y intercept based of TS space coordinates.
        """
        if u == 0:
            return 0

        return abs(D * v / u)# + IMG_HEIGHT // 2

    ################
    """
    accumulated = cv2.GaussianBlur(np.float32(accumulated), (3, 3), 0)

    cv2.imshow("", accumulated)
    cv2.waitKey(0)
    """
    ################

    maxima_keys = argrelextrema(accumulated, np.greater)

    maxima = [(maxima_keys[1][i], maxima_keys[0][i]) for i in range(len(maxima_keys[0]))]

    maxima = dict(zip(maxima, list(accumulated[maxima_keys])))

    # maxima = {1: 2, 3: 4, 4: 3, 2: 1, 0: 0}
    sorted_x = sorted(maxima.items(), key=lambda kv: kv[1])[::-1]

    maxima = [v[0] for v in sorted_x][:N_MAXIMA]
    
    ################

    # maxima = [maxima[2]]

    ################

    accumulated = np.where(accumulated > 0, 1, 0.)

    for u, v in maxima:
        accumulated = cv2.circle(accumulated, (u, v), 5, .5)

    #cv2.imshow("Accumulation w/ maxima", accumulated)
    #cv2.waitKey(0)

    print('Maxima:', maxima)

    lines = [(m(u-U_OFFSET), b(u - U_OFFSET, v - V_OFFSET)) for u, v in maxima]

    return lines


if __name__ == '__main__':

    #####################
    """
    value = '1234'

    generator = QrCode(value)

    images = [generator.img]  
    # [getattr(generator, section) for section in ['top_left_corner', 'top_right_corner',
    'bottom_left_corner', 'bottom_right_corner']]

    # images = [getattr(generator, 'top_right_corner')]

    row, col = images[0].shape[:2]
    bottom = images[0][row-2:row, 0:col]
    mean = cv2.mean(bottom)[0]

    bordersize=30
    images = [cv2.copyMakeBorder(images[0], top=bordersize, bottom=bordersize, left=bordersize,
    right=bordersize, borderType= cv2.BORDER_CONSTANT, value=mean)]
    """
    #####################
    """
    image = np.zeros(shape=(200, 200))

    theta = 3.1415/4

    for x1, y1, slope in [
        (100, 10, np.tan(theta)),
        (10, 100, np.tan(theta)),
        (10, 100, -np.tan(theta)),
        (100, 190, -np.tan(theta))]:

        dx = 90

        print(f'Real slope: {slope:.2f}')

        x2 = x1 + dx
        y2 = y1 + int(slope * dx)
        cv2.line(image, (x1, y1), (x2, y2), 1., 2)


        image = image#[::-1]

        images = [image]
    """
    ####################

    image = np.zeros(shape=(100, 100))

    theta = 3.1415/4
    slope = np.tan(theta)

    x1 = 10
    y1 = 10

    dx = 80

    print(f'Real slope: {slope:.2f}')

    x2 = x1 + dx
    y2 = y1 + int(slope * dx)
    cv2.line(image, (x1, y1), (x2, y2), 1., 2)


    image = image#[::-1]

    images = [image]

    e_images = [binarize_mat(get_edges(img), threshold=.5) for img in images]

    ####################
    """
    ## Solve preprocessing w/ this
    images = [cv2.imread('img/22.jpg')]

    images = [cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) for image in images]
    
    e_images = preprocess(images)
    """

    for edges in e_images:

        # cv2.imshow("edges", edges)
        # cv2.waitKey(0)

        lines = PCLines(edges)

        print("(m, b):", lines)

        x = lines

        x = sorted(x, key=lambda t: t[0])

        lines = x[:len(x) // 8] + x[len(x) // 8 * 7:]

        print("(m, b):", lines)

        def line_generator(i, x):
            return (x, lines[i][0]*x + lines[i][1])

        points = [line_generator(i, x) for i in range(len(lines)) for x in [0, 1000]]

        pts = np.array(points, np.int32)
        pts = pts.reshape((-1, 1, 2))

        line_edges = cv2.polylines(edges, [pts], True, .5, 1)

        cv2.imshow("", line_edges)
        cv2.waitKey(0)


        ###############

        #img = crop(image, lines)

        #cv2.imshow("Cropped image", img)
        #cv2.waitKey(0)
 

"""
if __name__ == '__main__':
    value = '1234'

    generator = QrCode(value)

    images = [getattr(generator, section) for section in ['top_left_corner', 'top_right_corner', 'bottom_left_corner', 'bottom_right_corner']]

    im1, im2, im3, im4 = images

    print(permute_ordering(im1, im3, im3, im4))
"""
