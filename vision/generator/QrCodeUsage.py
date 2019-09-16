"""
#-----------------------------------------------------------------------------
# Description:
# Demonstrates usage of a utility class which generates QR codes and auxiliary
# data neccessary for IARC mission 8.
#
# Author: Christopher O'Toole
# Published: 12/2/2018
#-----------------------------------------------------------------------------
"""

import cv2
from QrCode import QrCode

from argparse import ArgumentParser


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument("-q", type=str, dest="code",
                        help="String to encode.")

    options = parser.parse_args()

    DEFAULT_CODE = '1003'

    # It's not necessary for this to be a string here, it should work with any value
    # that has a valid strign representation.
    qr_code = QrCode(options.code if options.code else DEFAULT_CODE)
    # Shows the QR code
    qr_code.show()
    # Saves the QR code with its 4 segments separated out to an image in the current
    # directory
    qr_code.save()
    # Waits indefinitely until a key is pressed.
    cv2.waitKey(0)
    # Clean up any windows left over by OpenCV tasks.
    cv2.destroyAllWindows()
