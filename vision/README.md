# QR Code Segment Detection and Processing
In IARC mission 8, there will be four tablets, each with a quarter of a whole QR code showing along with the same alignment crosshairs on each one. The invisible parts of the code will be physically covered. The same code will remain for 30 seconds with intermittant visual noise. 

To effectively solve this problem, we will process images assuming they were taken by drones directly above ipad w/ focused camera. 
Current todo list
https://docs.google.com/document/d/1dT2ow6sCkQifk0xZS4s1N0_G-nCKfon1znZfymsH39w/edit?usp=sharing


## File Descriptions
fragment_accumulator.glsl
Fragment per point overlap counter, count stored in image.

qrmain.cpp
Cpp functionality of qr code processing.

shader_loader.h/.cpp
Functionality to create program object containing loaded shaders.

vertex.glsl
Standard vertex shader with no transformations.
