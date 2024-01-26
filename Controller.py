import CommonPatterns
from Shapes import Rectangle, Square, EquilateralTriangle, Triangle, Line, Oval, Circle, SineWave, Gradient, EdgeDetection
import signal
import sys
import os
from Coordinate import Coordinate
from Constants import *
import math



if IS_VIRTUAL:
    from VirtualManager import VirtualManager
    # Sets up a virtual simulation of the motors and LED
    manager = VirtualManager(canvas_dimensions_mm=15, led_ampere=0.0001, acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY)
else:
    from Manager import Manager
    # Sets up the actual motors and LED
    manager = Manager(led_ampere=0.01, serial_number_x="27602218", serial_number_y="27264864", acceleration=ACCELERATION, max_velocity=MAXIMUM_VELOCITY)


def main():
    shapes = []
    center_coordinate = Coordinate(8.32135, 7.88237)
    # shapes = CommonPatterns.audi(size_mm=2, center=center_coordinate)
    # shapes = CommonPatterns.atom(width_mm=2, height_mm=1, center=center_coordinate)
    # shapes = CommonPatterns.ovals(width1_mm=3, height1_mm=2, width2_mm=2, height2_mm=1, center=center_coordinate)
    # shapes = CommonPatterns.deathly_hallows(size_mm=2, center=center_coordinate)
    # shapes = CommonPatterns.square_star(size_mm=2, center=Coordinate(10.956, 7.557))
    # shapes = CommonPatterns.star_of_david(size_mm=2, center=Coordinate(11.139, 7.573))
    # shapes = [Shapes.Square.Square(side_length_mm=2, center=Coordinate(10.956, 7.557), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True)]
    # shapes = [Circle.Circle(diameter_mm=2, center=Coordinate(10.956, 7.557), beam_diameter=BEAM_DIAMETER)]
    # shapes = [Shapes.EquilateralTriangle.EquilateralTriangle(side_length_mm=2, center=Coordinate(10.956, 7.557), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False)]
    # shapes = [Circle.Circle(diameter_mm=2, center=center_coordinate, beam_diameter=BEAM_DIAMETER)]
    # shapes = [SineWave.SineWave(amplitude_mm=1, cycles=5, cycles_per_mm=0.5, center=Coordinate(10.956, 7.557), cycle_offset=0)]
    # shapes = [Oval.Oval(width_mm=3, height_mm=1, center=center_coordinate, rotation_angle=math.pi, beam_diameter=BEAM_DIAMETER)]
    # shapes = [Oval.Oval(width_mm=1, height_mm=1, center=center_coordinate, rotation_angle=math.pi, beam_diameter=BEAM_DIAMETER)]
    # from Shapes import SineWave
    # shapes.append(SineWave.SineWave(amplitude_mm=1, cycles=5, cycles_per_mm=0.5, center=Coordinate(1, 2), cycle_offset=0))
    # shapes.append(Circle.Circle(diameter_mm=2, center=center_coordinate, beam_diameter=BEAM_DIAMETER))
    # shapes.append(Oval(width_mm=4, height_mm=2, center=Coordinate(4, 4), rotation_angle=3.14/4.0, beam_diameter=BEAM_DIAMETER))
    # shapes.append(Oval(width_mm=4, height_mm=2, center=Coordinate(4, 4)))
    # shapes.append(Oval(width_mm=2, height_mm=4, center=Coordinate(4, 4), rotation_angle=0, beam_diameter=BEAM_DIAMETER))
    # shapes.append(Oval(width_mm=4, height_mm=2, center=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER))
    # shapes.append(Triangle.Triangle(width_mm=7, height_mm=2.5980762114, center=Coordinate(2, 2), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True))
    # shapes.append(Rectangle.Rectangle(width_mm=4, height_mm=2, center=Coordinate(5, 5), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=True))
    # shapes.append(Triangle.Triangle(width_mm=4, height_mm=2, center=Coordinate(5, 5), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True, filled=True))
    # shapes.append(Circle.Circle(diameter_mm=2, center=Coordinate(5, 5), beam_diameter=BEAM_DIAMETER, filled=True))
    # shapes.append(Triangle(width_mm=3, height_mm=2.5980762114, center=Coordinate(2, 2), rotation_angle=3.14/4.0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Rectangle.Rectangle(width_mm=2, height_mm=3, center=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Rectangle.Rectangle(width_mm=2, height_mm=3, center=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True))
    # shapes.append(Line(length_mm=3, center=Coordinate(2, 2), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Line(length_mm=3, center=Coordinate(2, 2), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Line(length_mm=3, center=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER, is_horizontal=True, uses_step_coordinates=False))
    # shapes.append(Line(length_mm=3, center=Coordinate(8, 8), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, is_horizontal=True, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=5, height_mm=10, center=Coordinate(0, 0), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=5, height_mm=10, center=Coordinate(0, 0), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Triangle(width_mm=5, height_mm=5, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Gradient.Gradient(min_velocity=0.1, max_velocity=1.5, beam_diameter=BEAM_DIAMETER, is_horizontal=False, is_reversed=True))
    shapes.append(EdgeDetection.EdgeDetection(img_file="2.jpg", center=center_coordinate, scale_factor=0.4, beam_diameter=BEAM_DIAMETER))
    
    coordinate_sets = []

    for shape in shapes:
        # shape.plot()
        print(shape)
        coordinate_sets.append(shape.get_coordinates())

    for coordinate_set in coordinate_sets:
        move(coordinate_set)
    
    if IS_VIRTUAL:
        manager.lamp.canvas.draw()


def move(coordinates):
    print("Moving Motors")
    for (i, coordinate) in enumerate(coordinates):
        print(f"{i}/{len(coordinates)} complete", end='\r')
        manager.move(coordinate)


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
