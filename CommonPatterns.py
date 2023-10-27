import math
from Shapes.Circle import Circle
from Shapes.Line import Line
from Shapes.EquilateralTriangle import EquilateralTriangle
from Shapes.Square import Square
from Coordinate import Coordinate


def deathly_hallows(size_mm=5, center=Coordinate(5, 5)):
    shapes = []
    shapes.append(Line(length_mm=size_mm, center=center, is_horizontal=False, uses_step_coordinates=True))
    shape_offset = 5 + size_mm*1/6
    center.y = shape_offset
    shapes.append(Circle(diameter_mm=5 * (2 / 3), center=center))
    tri_len = math.sqrt((size_mm**2) * 4 / 3.0)
    shapes.append(EquilateralTriangle(side_length_mm=tri_len, center=center, rotation_angle=math.pi))

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
