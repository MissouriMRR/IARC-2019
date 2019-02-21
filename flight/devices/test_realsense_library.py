import mrrdt_pyrealsense as pyrealsense
import cv2
import numpy as np
realsense = pyrealsense.Realsense()
realsense.begin()

blank_screen = np.zeros((640, 480, 3), dtype=np.uint8)

while True:
    colorized_depth = realsense.color()

    # Display the resulting frame
    if colorized_depth is not None:
        cv2.imshow('realsense-test', colorized_depth)
    else:
        cv2.imshow('realsense-test', blank_screen)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
