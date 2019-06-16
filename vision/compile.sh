#!/bin/bash
g++ -c -fPIC accumulator/main.cpp -o accumulator/qr.o
g++ -c -fPIC accumulator/shader_loader.cpp -o accumulator/shader_loader.o
g++ -shared -Wl,-soname,qr.so -o qr.so accumulator/qr.o accumulator/shader_loader.o -std=c++17 -Wall -ggdb -g -lglfw -lGL -lGLEW -lopencv_core -lopencv_highgui -lopencv_imgproc
rm accumulator/qr.o accumulator/shader_loader.o
python3 py_to_cpp.py

