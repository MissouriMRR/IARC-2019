# QR Code Segment Detection and Processing
This project is in the form of a pipeline, 'qr-pipeline.py', and each piece of the pipeline is in it's own folder.

## Problem
In IARC mission 8, there will be four tablets, each with a quarter of a whole QR code showing along with the same alignment crosshairs on each one. The invisible parts of the code will be physically covered. The same code will remain for 30 seconds with intermittant visual noise. 

To effectively solve this problem, we will process images assuming they were taken by drones directly above ipad w/ focused camera. We will find the edges of each section via the PCLines algorithm(hopefully or something harder), crop the image accordingly and paste the sections together to be read.

Current todo list
https://docs.google.com/document/d/1dT2ow6sCkQifk0xZS4s1N0_G-nCKfon1znZfymsH39w/edit?usp=sharing

## Pipeline
The pipeline will bein with an image of a section of qr code. This will either come from generator/, the realsense or network feed. The image will then be normalized, converted into an edge matrix and each edge will be transformed into line segments in TS Space with the code from normalize/. The list of TS Space verticies will be passed into the python wrapper of the C++-OpenGL code of the TS accumulator in accumulator/. The intersections of lines in TS Space will then be accumulated. The cpp source is located in accumulator/source/, the cpp->dll compiler is accumulator/compile.sh which generates a .so in accumulator/ and the OpenGL shaders are in shaders/. From the matrix of per pixel accumulations, a list of local maxima will be found via scipy. The locations of the local maxima in TS Space will then be used to find the slope intercept form of lines of largely contiguous edges in the original image.

## Running
```
./accumulator/compile.sh
python3 qr-pipeline.py
```
