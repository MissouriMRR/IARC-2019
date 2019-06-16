"""
Python code to interact with dll.
"""
import numpy as np
import cv2

from ctypes import cdll
import ctypes
lib = cdll.LoadLibrary('./qr.so')


class Allocator:
    """
    Allocate contiguous memory.
    """
    CFUNCTYPE = ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_int, ctypes.POINTER(ctypes.c_int))

    def __init__(self):
        self._data = None

    def __call__(self, dims, shape):
        """
        Allocate data.

        Parameters
        ----------
        dims: int
            Number of dimensions.
        shape: tuple of int
            Size of each dimension.
        """
        self._data = np.empty(shape[:dims], np.dtype('uint32'))
        return self._data.ctypes.data_as(ctypes.c_void_p).value

    @property
    def cfunc(self):
        """
        __call__ c function type.
        """
        return self.CFUNCTYPE(self)

    @property
    def data(self):
        """
        Allocated data.
        """
        return self._data


class TS(object):
    """
    TS Space, bindings to accumulator in c++.

    Parameters
    ----------
    width: int
        Width of image.
    height: int
        Height of image.
    v_count: int
        Number of verticies in verticies, each vertex is a 3 tuple.
        Must be even.
    verticies: numpy array
        List of verticies, each vertex is a 3 tuple. Every 2 verticies is a line.
    """
    def __init__(self, width, height, v_count=None, verticies=None):
        self.obj = lib.parameterized_init_ts(width, height, v_count, verticies) \
            if v_count and verticies else lib.init_ts()

    def accumulate(self):
        """
        Accumulate line overlaps in TS space.
        """
        lib.accumulate(self.obj)

        img = Allocator()

        lib.convert_output(self.obj, img.cfunc)

        return img.data


if __name__ == '__main__':
    # 0, 0 is in the middle of opengl, 1,1 is top right
    # https://www.khronos.org/registry/OpenGL-Refpages/gl4/html/gl_FragCoord.xhtml
    # Width in fragment_accumulator as magic number
    # opengl window is opposite of np

    VCOUNT = 10
    verticies = np.array([
        -1.0, -1.0, 0.0,
        1.0, 1.0, 0.0,
        -1.0, 1.0, 0.0,
        1.0, -1.0, 0.0,
        -1.0, 0.5, 0.0,
        1.0, 0.5, 0.0,

        0.0, 1.0, 0.0,
        0.0, -1.0, 0.0,
        0.0, 1.0, 0.0,
        0.0, -1.0, 0.0,
        ], dtype=np.float32)

    space = TS(1024, 768, VCOUNT, verticies.ctypes.data)
    img = space.accumulate()

    print(dict(zip(np.unique(img), np.bincount(img.flatten()))))
    print(dict(zip(*np.where(img >= 3))))

    img = np.where(img > 0, .2, 0.)

    cv2.imshow("img", img)
    cv2.waitKey(0)
