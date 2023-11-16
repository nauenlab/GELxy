import math
from Shapes.Circle import Circle
from Shapes.Line import Line
from Shapes.EquilateralTriangle import EquilateralTriangle
from Shapes.Square import Square
from Shapes.Oval import Oval
from Coordinate import Coordinate


def deathly_hallows(size_mm=5, center=Coordinate(5, 5)):
    shapes = []
    shapes.append(Line(length_mm=size_mm, center=center, is_horizontal=False, uses_step_coordinates=True))
    second_center = Coordinate(center.x, center.y + (size_mm * 1/6))
    shapes.append(Circle(diameter_mm=size_mm * (2 / 3), center=second_center))
    tri_len = math.sqrt((size_mm**2) * 4 / 3.0)
    shapes.append(EquilateralTriangle(side_length_mm=tri_len, center=second_center, rotation_angle=math.pi, uses_step_coordinates=True))

    return shapes


def square_star(size_mm=5, center=Coordinate(5, 5)):
    shapes = []
    shapes.append(Square(side_length_mm=size_mm, center=center))
    shapes.append(Square(side_length_mm=size_mm, center=center, rotation_angle=math.pi/4))

    return shapes


def star_of_david(size_mm=5, center=Coordinate(5, 5)):
    shapes = []
    shapes.append(EquilateralTriangle(side_length_mm=size_mm, center=center))
    shapes.append(EquilateralTriangle(side_length_mm=size_mm, center=center, rotation_angle=math.pi))

    return shapes


def ovals(size1_mm=5, size2_mm=3, center=Coordinate(5, 5)):
    shapes = []
    shapes.append(Oval(width_mm=size1_mm, height_mm=1, center=center, rotation_angle=math.pi))
    shapes.append(Oval(width_mm=size2_mm, height_mm=1, center=center, rotation_angle=math.pi))
    
    return shapes