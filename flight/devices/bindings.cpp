#include "bindings.hpp"

BOOST_PYTHON_MODULE(cv2_cuda)
{
    Py_Initialize();
    py::scope().attr("__doc__") = "A Python binding for the realsense module.";
}
