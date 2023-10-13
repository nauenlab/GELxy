from Circle import Circle
from Line import Line
from Rectangle import Rectangle
from Triangle import Triangle
from Coordinate import Coordinate
import signal
import sys
import os

IS_VIRTUAL = True
BEAM_DIAMETER = 0.1

motor_thread_sleep = 0.4
acceleration = 4.0  # mm/s
max_velocity = 2.0
min_velocity = 2.0


if IS_VIRTUAL:
    from VirtualManager import VirtualManager
    # Sets up a virtual simulation of the motors and LED
    manager = VirtualManager(canvas_dimensions_mm=15, led_ampere=0.01, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
else:
    from Manager import Manager
    # Sets up the actual motors and LED
    manager = Manager(led_ampere=0.01, serial_number_x="27602218", serial_number_y="27264864", motor_thread_sleep=motor_thread_sleep, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)


def main():
    shapes = []
    # shapes.append(Circle(diameter_mm=10, beam_diameter=BEAM_DIAMETER))
    shapes.append(Line(length_mm=2, offset=Coordinate(8, 8), rotation_angle=0, beam_diameter=BEAM_DIAMETER, is_horizontal=True, uses_step_coordinates=False))
    shapes.append(Line(length_mm=2, offset=Coordinate(8, 8), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, is_horizontal=True, uses_step_coordinates=False))
    shapes.append(Line(length_mm=2, offset=Coordinate(4, 4), rotation_angle=0, beam_diameter=BEAM_DIAMETER, is_horizontal=False, uses_step_coordinates=False))
    shapes.append(Line(length_mm=2, offset=Coordinate(4, 4), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, is_horizontal=False, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=5, height_mm=10, offset=Coordinate(0, 0), rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Rectangle(width_mm=5, height_mm=10, offset=Coordinate(0, 0), rotation_angle=0.45, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    # shapes.append(Triangle(width_mm=5, height_mm=5, rotation_angle=0, beam_diameter=BEAM_DIAMETER, uses_step_coordinates=False))
    for shape in shapes:
        coordinates = shape.get_coordinates()
        move(coordinates)
    manager.lamp.canvas.draw()


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
