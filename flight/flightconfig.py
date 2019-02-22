"""Values which may be configured frequently."""

# Set to true for more detailed error messages and backtraces
DEBUG = True

# How high in meters the drone will default flight
DEFAULT_ALTITUDE = 1

# How fast (in meters/s) to move by default
DEFAULT_SPEED = 0.50

# Maximum speed (in meters/s) before being considered unsafe
SPEED_THRESHOLD = 1

# Maximum altitude (in meters) before being considered unsafe
MAXIMUM_ALLOWED_ALTITUDE = 1.5

# Consider takeoff complete after reaching this percent of target takeoff
# altitude
PERCENT_TARGET_ALTITUDE = 0.3

# Expands or contracts time calculations (divide 1 by your average real-time
# factor in Gazebo simulator)
SIMULATION_MULTIPLIER = 1

# Thrust level during takeoff
DEFAULT_TAKEOFF_THRUST = 0.7