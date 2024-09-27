# We keep the acceleration at the maximum value so  that our stiffness patterns are as uniform as can be
ACCELERATION = 4.0 # mm/s^2

# This is a changable constant based on the beam diameter
BEAM_DIAMETER = 0.5 # mm

# This is the physical bounds that the motor actuators can travel
MOTOR_MAX_TRAVEL = 25 # mm

# The wavelength of light outputted by the lamp
LIGHT_WAVELENGTH = 445 # nm

# According to Thorlabs, this is the lower bound for the velocity of the motors
MINIMUM_VELOCITY = 0.05 # mm/s

# Using Thorlabs documentation, this is the maximum valocity of the motors before the speed becomes unpredictable
MAXIMUM_VELOCITY = 0.5 # mm/s

# This is the physical lower bound of the lamp
MINIMUM_CURRENT = 0.1 # mA

# Although the maximum current the lamp can output is 9000 mA, we decided to keep it lower
MAXIMUM_CURRENT = 8000 # mA

# This is an arbitrary value that holds no significance, but must be within the bounds of the minimum and maximum current
DEFAULT_CURRENT = 100 # mA

# This value represents the minimum distance that the centers of 2 light beams can be separated. 
# See this desmos graph for more information on how this constant is calculated: https://www.desmos.com/calculator/1bskxyy722
import math
MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS = (BEAM_DIAMETER / 2) * (1 - math.cos(2)) # mm

# Change this value to increase the quality of the canvas drawings. Enter a value between 0.1 and 10. A higher quality will increase the time it takes to render the canvas.
CANVAS_QUALITY = 2