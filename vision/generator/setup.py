"""
setup.py
"""
from setuptools import setup

setup(name='easy_qr',
      version='1.0',
      description='Library for generating QR codes.',
      author="Christopher O'Toole",
      author_email='cdocq9@mst.edu',
      packages=['easy_qr'],
      install_requires=['qrcode', 'opencv-python', 'numpy']
     )