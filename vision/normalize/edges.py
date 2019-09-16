"""
Greyscale, blur and get edges of an image
"""
import cv2
import numpy as np

def get_edges(image):
    """Get the edges in an image"""
    if len(image.shape) == 3:
        # has more than one channel
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    kernel = np.ones((5, 5), np.float32)/5
    dst = cv2.filter2D(image, -1, kernel)
    lap = cv2.Laplacian(dst, cv2.CV_64F)
    return lap

if __name__ == '__main__':
    qr = cv2.imread('code.png')
    cv2.imshow('code', get_edges(qr))
    cv2.waitKey(0)
    cv2.destroyAllWindows()
