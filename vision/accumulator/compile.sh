#!/bin/bash
g++ -c -fPIC accumulator/source/main.cpp -o accumulator/qr.o
g++ -c -fPIC accumulator/source/shader_loader.cpp -o accumulator/shader_loader.o
g++ -shared -Wl,-soname,qr.so -o accumulator/qr.so accumulator/qr.o accumulator/shader_loader.o -std=c++17 -Wall -ggdb -g -lglfw -lGL -lGLEW -lopencv_core -lopencv_highgui -lopencv_imgproc
rm accumulator/qr.o accumulator/shader_loader.o
