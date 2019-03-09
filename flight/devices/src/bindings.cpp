#include "numpy/bindings.hpp"
#include "realsense/realsense.hpp"

BOOST_PYTHON_MODULE(mrrdt_pyrealsense)
{
    Py_Initialize();
    py::scope().attr("__doc__") = "A Python binding for the realsense module.";
    py::class_<Realsense>("Realsense", "", py::init<>())
        .def("begin", &Realsense::begin, "")
        .def("depth", &Realsense::depth, "")
        .def("color", &Realsense::color, "");
}
