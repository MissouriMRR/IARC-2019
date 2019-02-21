
#define INIT_NUMPY_ARRAY_CPP

#include "conversion.hpp"

NumpyAllocator g_numpyAllocator;

// https://stackoverflow.com/questions/47026900/pyarray-check-gives-segmentation-fault-with-cython-c
int init_numpy(){
    // add support for C++ interaction with numpy arrays
     import_array();
     return 0;
}

const static int numpy_initialized =  init_numpy();