"""
Must run in python 2. Must have zbar installed for qrtools.

sudo apt install libzbar-dev
python -m pip install zbar
"""


import unittest

import os, sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'qr_gen'))

from QrCode import QrCode
import qrtools


class TestQRGen(unittest.TestCase):
    """
    QR code generator tester.
    """

    def test_generator(self):
        """
        Test the qr generator by reading multiple generated codes.
        """
        for code in ['1003', '1234']:
            qr_code = QrCode(code)

            path = qr_code.save(qr_code.img)
            print(path)
            interpreter = qrtools.QR()
            interpreter.decode(path)

            interpreted_code = interpreter.data

            self.assertEqual(code, interpreted_code)

            os.remove(path)


if __name__ == '__main__':
    unittest.main()