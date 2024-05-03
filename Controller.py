import CommonPatterns
from Shapes import Rectangle, Square, EquilateralTriangle, Triangle, Line, Oval, Circle, SineWave, Gradient, EdgeDetection, Texture
import signal
import sys
import os
from Coordinate import Coordinate, Coordinates
from Constants import *
from tqdm import tqdm
import multiprocessing
from gbl import handle_processes




if IS_VIRTUAL:
    from Simulator.VirtualManager import VirtualManager
    # Sets up a virtual simulation of the motors and LED
    manager = VirtualManager(canvas_dimensions_mm=MOTOR_MAX_TRAVEL, acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY, beam_diameter=BEAM_DIAMETER)
else:
    from Hardware.Manager import Manager
    # Sets up the actual motors and LED
    # !!! For the Lamp: In the USB number the serial number (M00...) needs to be changed to the one of the connected device.
    manager = Manager(serial_number_x="27602218", serial_number_y="27264864", lamp_serial_number=b"USB0::0x1313::0x80C8::M00607903::INSTR", acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY)


def main():
    shapes = []
    center_coordinate = Coordinate(4.38134, 11.82782)
    
    # Rectangle
    # shapes.append(Rectangle.Rectangle(width_mm=2, height_mm=3, stiffness=10, center=center_coordinate, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
    
    # Square
    # shapes.append(Square.Square(side_length_mm=2, stiffness=10, center=center_coordinate, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
    
    # Equilateral Triangle
    # shapes.append(EquilateralTriangle.EquilateralTriangle(side_length_mm=2, stiffness=10, center=center_coordinate, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
    
    # Triangle
    # shapes.append(Triangle.Triangle(width_mm=2, height_mm=2.5980762114, stiffness=10, center=center_coordinate, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False))
    
    # Line
    # shapes.append(Line.Line(length_mm=3, stiffness=10, center=center_coordinate, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True))
    
    # Oval
    # shapes.append(Oval.Oval(width_mm=2, height_mm=3, stiffness=10, center=center_coordinate, rotation_angle=0, beam_diameter=BEAM_DIAMETER, filled=False))
    
    # Circle
    # shapes.append(Circle.Circle(diameter_mm=2, stiffness=10, center=center_coordinate, beam_diameter=BEAM_DIAMETER, filled=False))
    
    # Sine Wave
    # shapes.append(SineWave.SineWave(amplitude_mm=1, cycles=5, cycles_per_mm=0.5, stiffness=10, cycle_offset=0, center=center_coordinate, rotation_angle=0, beam_diameter=BEAM_DIAMETER))
    
    # Gradient
    # shapes.append(Gradient.Gradient(min_stiffness=5, max_stiffness=10, beam_diameter=BEAM_DIAMETER, is_horizontal=False, is_reversed=True))
    
    # Custom Pattern
    # shapes.append(EdgeDetection.EdgeDetection(img_file="test_images/2.jpg", stiffness=10, center=center_coordinate, rotation_angle=0, scale_factor=0.4, beam_diameter=BEAM_DIAMETER))
    
    # Texture
    shapes.append(Texture.Texture(shape=EquilateralTriangle.EquilateralTriangle(side_length_mm=1, stiffness=10, center=None, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=False), rows=None, columns=None, spacing_mm=2, margins=10))

    coordinate_sets = multiprocessing.Manager().list()
    processes = []
    for shape in shapes:
        processes.append(multiprocessing.Process(target=append_coordinates, args=(shape, coordinate_sets)))

    handle_processes(processes)

    coordinates = Coordinates()
    for i in coordinate_sets:
        coordinates += i
    
    print("Moving Motors")
    for coordinate in tqdm(coordinates, desc="Moving Motors", unit="coordinate"):
        manager.move(coordinate)

    if IS_VIRTUAL:
        manager.lamp.canvas.draw()
        

def append_coordinates(shape, coordinates):
    coordinates.append(shape.get_coordinates())

def exit_handler(*args):
    print("Cleaning Up!")
    manager.__del__()
    os.environ["current_time"] = "0"
    sys.exit(0)


signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)


if __name__ == "__main__":
    main()
    exit_handler()
