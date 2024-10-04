import CommonPatterns
from Shapes import *
import signal
import sys
import os
from Coordinate import Coordinate, Coordinates
from Constants import *
from tqdm import tqdm
from Multiprocessor import Multiprocessor
from EstimatedCompletionTime import EstimatedCompletionTime

### INSTRUCTIONS
### STEP 1: Connect the motors and LED to the computer using USB cables.

### STEP 2: Change the IS_VIRTUAL value to True if you want to run the motors in a virtual simulation. Change the IS_VIRTUAL value to False if you want to run the motors in real life.
###         It is recommended to run the motors in a virtual simulation first to see how the motors will move before running the motors in real life.
### STEP 3: Change the center_coordinate value in the main function. The center coordinate will be used to determine the center of each shape, texture, or pattern.
### STEP 4: Choose which shapes, textures, or patterns to draw and uncomment the desired shape, texture, or pattern from the list in the main function.
### STEP 5: Run the program. The motors will move to draw the shapes, textures, or patterns.

IS_VIRTUAL = True

X_MOTOR_SERIAL_NUMBER = "27602218"
Y_MOTOR_SERIAL_NUMBER = "27264864"
LAMP_SERIAL_NUMBER = b"USB0::0x1313::0x80C8::M00607903::INSTR"

class Controller:

    def main(self):
        shapes = []
        center_coordinate = Coordinate(4.38134, 11.82782)
        
        # Rectangle
        shapes.append(Rectangle(width_mm=5, height_mm=3, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False, filled=False))
        
        # Square
        # shapes.append(Square(side_length_mm=2, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
        
        # Equilateral Triangle
        # shapes.append(EquilateralTriangle(side_length_mm=2, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
        
        # Triangle
        # shapes.append(Triangle(width_mm=2, height_mm=2.5980762114, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False, filled=True))
        
        # Line
        # shapes.append(Line(length_mm=5, stiffness=20000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True))
        
        # Oval
        # shapes.append(Oval(width_mm=2, height_mm=3, stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, filled=True))
        
        # Circle
        # shapes.append(Circle(diameter_mm=2, stiffness=10000, center=center_coordinate, beam_diameter=BEAM_DIAMETER, filled=False))
        
        # Sine Wave
        # shapes.append(SineWave(amplitude_mm=1, cycles=5, cycles_per_mm=0.5, stiffness=10000, cycle_offset=0, center=center_coordinate, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER))
        
        # Gradient
        # shapes.append(Gradient(min_stiffness=5000, max_stiffness=50000, width_mm=3, height_mm=4, center=center_coordinate, beam_diameter=BEAM_DIAMETER, rotation_angle_degrees=0, is_reversed=True))
        
        # Custom Pattern
        # shapes.append(EdgeDetection(img_file="test_images/2.jpg", stiffness=10000, center=center_coordinate, rotation_angle_degrees=0, scale_factor=0.4, beam_diameter=BEAM_DIAMETER))
        
        # Texture
        # texture_shape = EquilateralTriangle(side_length_mm=1, stiffness=10000, center=None, rotation_angle_degrees=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False, filled=False)
        # shapes.append(Texture(shape=texture_shape, center=center_coordinate, rows=None, columns=None, spacing_mm=1.5, margins=11))

        # Common Patterns
        # shapes.extend(CommonPatterns.atom(width_mm=5, height_mm=2, center=center_coordinate, stiffness=10000))
        # shapes.extend(CommonPatterns.deathly_hallows(size_mm=5, center=center_coordinate, stiffness=10000))

        coordinate_sets = Multiprocessor().get_coordinate_sets(shapes)

        coordinates = Coordinates()
        for i in coordinate_sets:
            coordinates += i
        
        # Estimated Completion Time
        completion_time = EstimatedCompletionTime(coordinates).get_completion_time()
        print(f"Estimated Completion Time: {int(completion_time // 3600)} hours {int((completion_time % 3600) // 60)} minutes {int(completion_time % 60)} seconds")

        if IS_VIRTUAL:
            from Simulator.VirtualManager import VirtualManager
            # Sets up a virtual simulation of the motors and LED
            self.manager = VirtualManager(canvas_dimensions_mm=MOTOR_MAX_TRAVEL, acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY, beam_diameter=BEAM_DIAMETER)
        else:
            from Hardware.Manager import Manager
            # Sets up the actual motors and LED
            self.manager = Manager(serial_number_x=X_MOTOR_SERIAL_NUMBER, serial_number_y=Y_MOTOR_SERIAL_NUMBER, lamp_serial_number=LAMP_SERIAL_NUMBER, acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY)
        
        if not IS_VIRTUAL:
            print("Going to first Coordinate")
            self.manager.move(coordinates[0])
            print("First coordinate reached. Please adjust stage as needed.")
            lamp_on = input("Would you like to turn the lamp on to 1 mA for calibration? (y/n): ")
            if lamp_on == "y":
                self.manager.lamp.turn_on(0.001)
            
            input("Press any key to continue.")

        for coordinate in tqdm(coordinates, desc="Moving Motors", unit="coordinate"):
            self.manager.move(coordinate)

        if IS_VIRTUAL:
            self.manager.lamp.canvas.draw()
    
    def __del__(self):
        """
        Cleans up the resources used by the Controller instance.
        """
        try:
            self.manager.__del__()
        except:
            pass


controller = Controller()

def exit_handler(*args):
    print("Cleaning Up!")
    controller.__del__()
    os.environ["current_time"] = "0"
    sys.exit(0)


signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)


if __name__ == "__main__":
    controller.main()
    exit_handler()