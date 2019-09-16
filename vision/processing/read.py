"""
sudo apt-get install libzbar0
"""
from PIL import Image
from pyzbar.pyzbar import decode


def read(image):
    """
    Read qr code.

    Parameters
    ----------
    image: np array
        Image with qr code.

    Returns
    -------
    int or None
    """
    data = decode(image)  ## Outputs 4 corner locations as well!!

    if data:
        data = int(data[0][0])

    return data


if __name__ == '__main__':
    import os, sys
    sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'generator'))

    from QrCode import QrCode

    number = '4545'

    code = QrCode(number).img

    print(f'Interpreted: {read(code)}, Real {number}')
