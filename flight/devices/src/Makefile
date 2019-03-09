# compiler executable macros
CXX=g++
NVCC=nvcc

# name of the library to be built
TARGET_NAME=mrrdt_pyrealsense

VPATH=numpy/:realsense/

# library source dependencies
_OBJECTS = bindings.o \
		  conversion.o \
		  realsense.o
		  
OBJECTS = $(patsubst %, bin/%, $(_OBJECTS))

# OS specific macros
PYTHON_OS_NAME_LINUX=x86_64-linux-gnu
BOOST_OS_NAME_LINUX=x86_64-linux-gnu
PYTHON_LIB_FOLDER=/usr/lib
BOOST_LIB_FOLDER=/usr/lib

# Python compilation flags
PYTHON_VERSION_MAJOR=3
PYTHON_VERSION_MINOR=6
PYTHON_VERSION=$(PYTHON_VERSION_MAJOR).$(PYTHON_VERSION_MINOR)
PYTHON_VERSION_RAW=$(PYTHON_VERSION_MAJOR)$(PYTHON_VERSION_MINOR)
PYTHON_INTERPRETER=python$(PYTHON_VERSION_MAJOR)
PYTHON_LIB=$(shell pkg-config --libs $(PYTHON_INTERPRETER))
PYTHON_LIB_DIR=$(PYTHON_LIB_FOLDER)/python$(PYTHON_VERSION)/config-$(PYTHON_VERSION)m-$(PYTHON_OS_NAME_LINUX)/
PYTHON_INCLUDE=$(shell pkg-config --cflags $(PYTHON_INTERPRETER))

# OpenCV compilation flags
OPENCV_FLAGS=$(shell pkg-config --cflags opencv)
OPENCV_LIB=$(shell pkg-config --libs opencv)

# Boost compilation flags
BOOST_PYTHON_DEPS+=-lboost_system -lboost_filesystem
BOOST_LIB=$(BOOST_LIB_FOLDER)/$(BOOST_OS_NAME_LINUX)
BOOST_PYTHON_FLAGS+=-L$(BOOST_LIB) -L$(PYTHON_LIB_DIR) -lpython$(PYTHON_VERSION) 
BOOST_PYTHON_FLAGS+=-lboost_python-py$(PYTHON_VERSION_RAW) $(BOOST_PYTHON_DEPS)

# general compilation flags
CXXFLAGS+= -std=c++14 -O3 -g -ggdb $(PYTHON_INCLUDE) $(OPENCV_FLAGS) -fPIC
LDFLAGS+= $(OPENCV_LIB) $(BOOST_PYTHON_FLAGS) -lrealsense2

# add .cpp and .cu (CUDA kernel) to the known suffices
.SUFFIXES: .cpp

.PHONY: clean

# rule for compiling .cpp files into .o files
.cpp.o: $<
	$(CXX) -c $(CXXFLAGS) $< -o bin/$@

# define the primary build task.
default: all
all: $(TARGET_NAME).so

# build the shared library file.
$(TARGET_NAME).so: $(_OBJECTS)
	$(CXX) -shared $(OBJECTS) $(LDFLAGS) -o bin/$@

# remove zero or more .o and .so files on clean
clean:
	rm -rf bin
	mkdir bin

# library dependencies and their prerequisites
bindings.o:      bindings.cpp conversion.o realsense.o
conversion.o:    conversion.cpp conversion.hpp
realsense.o: 	 realsense.cpp realsense.hpp
