import math
from Shapes.Circle import Circle
from Shapes.Line import Line
from EquilateralTriangle import EquilateralTriangle
from Shapes.Square import Square
from Coordinate import Coordinate


def deathly_hallows():
    shapes = []
    shapes.append(Line(length_mm=5, center=Coordinate(5, 5), is_horizontal=False, uses_step_coordinates=True))
    shape_offset = 5 + 5*1/6
    shapes.append(Circle(diameter_mm=5 * (2 / 3), center=Coordinate(5, shape_offset)))
    tri_len = math.sqrt(100.0 / 3.0)
    shapes.append(EquilateralTriangle(side_length_mm=tri_len, center=Coordinate(5, shape_offset), rotation_angle=math.pi))

    return shapes


def square_star():
    shapes = []
    shapes.append(Square(side_length_mm=5, center=Coordinate(5, 5)))
    shapes.append(Square(side_length_mm=5, center=Coordinate(5, 5), rotation_angle=math.pi/4))

    return shapes


def star_of_david():
    shapes = []
    shapes.append(EquilateralTriangle(side_length_mm=5, center=Coordinate(5, 5)))
    shapes.append(EquilateralTriangle(side_length_mm=5, center=Coordinate(5, 5), rotation_angle=math.pi))

    return shapes
