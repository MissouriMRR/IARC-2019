"""
Contains the control object for the laser mounted on the drones
"""
from RPi import GPIO

class Laser:
"""
This class is a controller for the laser on the drone 
and will manipulate different variables of the laser

Parameters
----------
    laser_pin : int
        Pass the pin number that the laser is plugged into

Attributes
----------
    _laser_pin : int
        The pin number where the laser is attached
"""
    def __init__(self, laser_pin):
        self._laser_pin = laser_pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._laser_pin, GPIO.OUT) #Sets the given pin as output

    def on(self):
        """
        Turns on the laser mounted on the drone
        """
        GPIO.output(self._laser_pin, GPIO.HIGH)

    def off(self):
        """
        Turns off the laser mounted on the drone
        """
        GPIO.output(self._laser_pin, GPIO.LOW)