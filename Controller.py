import CommonPatterns
from Shapes import Rectangle, Square, EquilateralTriangle, Triangle, Line, Oval, Circle, SineWave
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
    center_coordinate = Coordinate(10.88336, 6.13018)
    shapes = CommonPatterns.ovals(size1_mm=3, size2_mm=2, center=center_coordinate)
    # shapes = CommonPatterns.deathly_hallows(size_mm=2, center=Coordinate(10.956, 7.557))
    # shapes = CommonPatterns.square_star(size_mm=2, center=Coordinate(10.956, 7.557))
    # shapes = CommonPatterns.star_of_david(size_mm=2, center=Coordinate(11.139, 7.573))
    # shapes = [Shapes.Square.Square(side_length_mm=2, center=Coordinate(10.956, 7.557), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=True)]
    # shapes = [Circle.Circle(diameter_mm=2, center=Coordinate(10.956, 7.557), beam_diameter=BEAM_DIAMETER)]
    # shapes = [Shapes.EquilateralTriangle.EquilateralTriangle(side_length_mm=2, center=Coordinate(10.956, 7.557), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False)]
    
    # shapes = [SineWave.SineWave(amplitude_mm=1, cycles=5, cycles_per_mm=0.5, center=Coordinate(10.956, 7.557), cycle_offset=0)]
    # shapes = [Oval.Oval(width_mm=3, height_mm=1, center=center_coordinate, rotation_angle=math.pi, beam_diameter=BEAM_DIAMETER)]
    # shapes = [Oval.Oval(width_mm=1, height_mm=1, center=center_coordinate, rotation_angle=math.pi, beam_diameter=BEAM_DIAMETER)]
    # from Shapes import SineWave
    # shapes.append(SineWave.SineWave(amplitude_mm=1, cycles=5, cycles_per_mm=0.5, center=Coordinate(1, 2), cycle_offset=0))
    # shapes.append(Circle(diameter_mm=10, center=Coordinate(1, 1), beam_diameter=BEAM_DIAMETER))
    # shapes.append(Oval(width_mm=4, height_mm=2, center=Coordinate(4, 4), rotation_angle=3.14/4.0, beam_diameter=BEAM_DIAMETER))
    # shapes.append(Oval(width_mm=4, height_mm=2, center=Coordinate(4, 4)))
    # shapes.append(Oval(width_mm=2, height_mm=4, center=Coordinate(4, 4), rotation_angle=0, beam_diameter=BEAM_DIAMETER))
    # shapes.append(Oval(width_mm=4, height_mm=2, center=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER))
    # shapes.append(Triangle(width_mm=3, height_mm=2.5980762114, center=Coordinate(2, 2), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Triangle(width_mm=3, height_mm=2.5980762114, center=Coordinate(2, 2), rotation_angle=3.14/4.0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=3, height_mm=3, center=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=3, height_mm=3, center=Coordinate(8, 8), rotation_angle=3.14/4.0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Line(length_mm=3, center=Coordinate(2, 2), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Line(length_mm=3, center=Coordinate(2, 2), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Line(length_mm=3, center=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER, is_horizontal=True, uses_step_coordinates=False))
    # shapes.append(Line(length_mm=3, center=Coordinate(8, 8), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, is_horizontal=True, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=5, height_mm=10, center=Coordinate(0, 0), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=5, height_mm=10, center=Coordinate(0, 0), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Triangle(width_mm=5, height_mm=5, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    for shape in shapes:
        coordinates = shape.get_coordinates()
        move(coordinates)
    # manager.lamp.canvas.draw()


def move(coordinates, timeout=10000, is_first_move=False):
    if len(coordinates) > 1:
        move(coordinates=[coordinates[0]], timeout=30000, is_first_move=True)
        coordinates = coordinates[1:]

    for i in coordinates:
        manager.move(i, timeout, is_first_move)


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
