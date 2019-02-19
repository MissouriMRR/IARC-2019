# IARC 2019 Laser Class

## Usage:

### laser_class
	 Make a laser object and give it the pin number it is plugged into. Then you can 'obj.on()' and 'obj.off()' to turn it on and off (respectively).

### serial_controller_class
	Works with the sketchServoControl.ino for sending commands over serial. Make a servo_controller object and give the Serial port and the baudrate of that connection. To send a command, use numbers as strings between 0 and 180 in "obj.writeTo(string)" to set the servo to that angle in degrees.
### Notes
 Since we are using RPi.GPIO with the UpBoard you need to use this specific [kernel](https://wiki.up-community.org/RPi.GPIO).


