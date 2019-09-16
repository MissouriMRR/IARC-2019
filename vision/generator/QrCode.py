"""
(PYTHON 3 ONLY)
Objects for dealing with QR codes.
This module provides a utility class for encoding values to their QR code
representation. All objects passed should have a string representation
defined for the encoding to function as expected.

Constants
---------
- `BORDER_SIZE` -- Margins around QR code, defaults to 15px.

Classes
-------
- `QRCode` -- Generates QR code representations of objects.
"""

import qrcode
import numpy as np
import cv2
import os

BORDER_SIZE = 15

class QrCode(object):
    """A class for generating QR codes.

    Parameters
    ----------
    value : castable to string
        The value which we desire to encode as a QR code.
    """

    # Window title
    TITLE = 'QR Code'
    # OpenCV font used for image generation
    FONT = cv2.FONT_HERSHEY_SIMPLEX
    # Thickness of text
    THICKNESS = 4
    # Relative amount of space to add when splitting up QR code segments
    UPSCALE_FACTOR = 5

    def __init__(self, value='0'):
        self.encoded_value = value

    def show(self, title=TITLE):
        """
        Shows the QR code in an OpenCV window.

        Parameters
        ----------
        title : str
            Title of the window, defaults to the class constant TITLE.

        Returns
        -------
        None
        """
        cv2.imshow(title, self.img)
        cv2.waitKey(1)

    @property
    def encoded_value(self):
        """Getter for the value the QR code represents"""
        return self._encoded_value

    @property
    def img(self):
        """Getter for the QR code as an OpenCV compatible image"""
        return self._img

    @property
    def top_left_corner(self):
        """Gets the top left corner segment of the QR code."""
        return self._top_left_corner

    @property
    def top_right_corner(self):
        """Gets the top right corner segment of the QR code."""
        return self._top_right_corner

    @property
    def bottom_left_corner(self):
        """Gets the bottom left corner segment of the QR code."""
        return self._bottom_left_corner

    @property
    def bottom_right_corner(self):
        """Gets the bottom right corner segment of the QR code."""
        return self._bottom_right_corner

    def mid_y(self):
        """Gets the midpoint of the image along the y-axis"""
        return int(self.img.shape[0]/2)

    def mid_x(self):
        """Gets the midpoint of the image along the x-axis"""
        return int(self.img.shape[1]/2)

    @property
    def combined_image(self):
        """
        Gets a image with 4 QR code segments separated out to simulate IARC
        Mission 8.
        """

        # Create image and read in border mask.
        self._combined_image = (np.ones((self._corner_width*QrCode.UPSCALE_FACTOR,
            self._corner_width*QrCode.UPSCALE_FACTOR, 3))*255).astype(np.uint8)

        # border_img_path = 'border.png'
        # border = cv2.imread(border_img_path, cv2.IMREAD_GRAYSCALE)
        # assert border is not None, 'Could not read {}'.format(border_img_path)

        # Write the QR code segments onto the image
        corner_w, corner_h = self._corner_width, self._corner_height
        height, width, _ = self._combined_image.shape
        self._combined_image[BORDER_SIZE:corner_h+BORDER_SIZE,
            BORDER_SIZE:corner_w+BORDER_SIZE] = self.top_left_corner.reshape(corner_w, corner_h, -1)
        self._combined_image[BORDER_SIZE:corner_h+BORDER_SIZE,
            width-BORDER_SIZE-corner_w:width-BORDER_SIZE] = self.top_right_corner.reshape(corner_w, corner_h, -1)
        self._combined_image[height-BORDER_SIZE-corner_h:height-BORDER_SIZE,
            BORDER_SIZE:corner_w+BORDER_SIZE] = self.bottom_left_corner.reshape(corner_w, corner_h, -1)
        self._combined_image[height-BORDER_SIZE-corner_h:height-BORDER_SIZE,
            width-BORDER_SIZE-corner_w:width-BORDER_SIZE] = self.bottom_right_corner.reshape(corner_w, corner_h, -1)

        # Write the value the QR code represents in plaintext for record keeping purposes.
        text = str(self.encoded_value)
        text_size = cv2.getTextSize(text, QrCode.FONT, 4, QrCode.THICKNESS)[0]
        center = (int((width-text_size[0])/2), int((height+text_size[1])/2))
        cv2.putText(self._combined_image, text, center, QrCode.FONT, 4, (0, 0, 0),
            QrCode.THICKNESS, cv2.LINE_AA)

        # Add border
        #margin = int(BORDER_SIZE*1.5)
        #h, w = border.shape
        #ret, mask = cv2.threshold(border, 10, 255, cv2.THRESH_BINARY)
        #roi = self._combined_image[margin:margin+h, margin:margin+w]
        #self._combined_image[margin:margin+h, margin:margin+w] = cv2.bitwise_and(roi, roi, mask=mask)

        return self._combined_image

    def save(self, target=None, path=None):
        """
        Generates an image in which the 4 corners of the QR code are separated by white space in the
        image. The generated image has a label in the middle which gives the plaintext
        value that the QR code encoded.

        Parameters
        ----------
        target: mat
            Image to be saved.

        path : str
            Path to save the image to, defaults to the current directory if None.

        Returns
        -------
        str Filename of the qr code.
        """
        assert path is None or os.path.isdir(path), 'Cannot save to {}'.format(path)

        filename = '{}.png'.format(str(self.encoded_value)) if path is None else path

        cv2.imwrite(filename, target if target is not None else self.combined_image)

        return filename

    @encoded_value.setter
    def encoded_value(self, value):
        """
        Sets the value represented by the QR code and updates all fields to represent this
        change.
        """

        self._encoded_value = value
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=2,
        )

        qr.add_data(str(value))
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        self._img = np.asarray(img.getdata()).reshape(img.size[0], img.size[1]).astype(np.uint8)
        self._top_left_corner = self.img[:self.mid_y(), :self.mid_x()]
        self._bottom_left_corner = self.img[self.mid_y():, :self.mid_x()]
        self._top_right_corner = self.img[:self.mid_y(), self.mid_x():]
        self._bottom_right_corner = self.img[self.mid_y():, self.mid_x():]
        self._corner_width = self.top_left_corner.shape[1]
        self._corner_height = self.top_left_corner.shape[0]