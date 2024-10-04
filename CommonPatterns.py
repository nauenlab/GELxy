import math
from Shapes import *
from Coordinate import Coordinate


def deathly_hallows(size_mm=5, center=Coordinate(5, 5), stiffness=0.1):
    """
    Generates a list of shapes representing the Deathly Hallows symbol.

    Args:
        size_mm (float): The size of the symbol in millimeters. Default is 5.
        center (Coordinate): The center coordinate of the symbol. Default is (5, 5).

    Returns:
        list: A list of shapes representing the Deathly Hallows symbol.
    """
    shapes = []
    shapes.append(Line(length_mm=size_mm, stiffness=stiffness, center=center, uses_step_coordinates=True))
    second_center = Coordinate(center.x, center.y + (size_mm * 1/6))
    shapes.append(Circle(diameter_mm=size_mm * (2 / 3), stiffness=stiffness, center=second_center))
    tri_len = math.sqrt((size_mm**2) * 4 / 3.0)
    shapes.append(EquilateralTriangle(side_length_mm=tri_len, stiffness=stiffness, center=second_center, rotation_angle_degrees=180, uses_step_coordinates=True))

    return shapes


def square_star(size_mm=5, center=Coordinate(5, 5), stiffness=0.1):
    """
    Generates a list of shapes representing a square star.

    Args:
        size_mm (float): The size of the star in millimeters. Default is 5.
        center (Coordinate): The center coordinate of the star. Default is (5, 5).

    Returns:
        list: A list of shapes representing a square star.
    """
    shapes = []
    shapes.append(Square(side_length_mm=size_mm, stiffness=stiffness, center=center))
    shapes.append(Square(side_length_mm=size_mm, stiffness=stiffness, center=center, rotation_angle_degrees=90))

    return shapes


def star_of_david(size_mm=5, center=Coordinate(5, 5), stiffness=0.1):
    """
    Generates a list of shapes representing the Star of David.

    Args:
        size_mm (float): The size of the symbol in millimeters. Default is 5.
        center (Coordinate): The center coordinate of the symbol. Default is (5, 5).

    Returns:
        list: A list of shapes representing the Star of David.
    """
    shapes = []
    shapes.append(EquilateralTriangle(side_length_mm=size_mm, stiffness=stiffness, center=center))
    shapes.append(EquilateralTriangle(side_length_mm=size_mm, stiffness=stiffness, center=center, rotation_angle_degrees=180))

    return shapes


def ovals(width1_mm=5, height1_mm=3, width2_mm=3, height2_mm=2, center=Coordinate(5, 5), stiffness=0.1):
    """
    Generates a list of shapes representing two ovals.

    Args:
        width1_mm (float): The width of the first oval in millimeters. Default is 5.
        height1_mm (float): The height of the first oval in millimeters. Default is 3.
        width2_mm (float): The width of the second oval in millimeters. Default is 3.
        height2_mm (float): The height of the second oval in millimeters. Default is 2.
        center (Coordinate): The center coordinate of the ovals. Default is (5, 5).

    Returns:
        list: A list of shapes representing two ovals.
    """
    shapes = []
    shapes.append(Oval(width_mm=width1_mm, height_mm=height1_mm, stiffness=stiffness, center=center, rotation_angle_degrees=180))
    shapes.append(Oval(width_mm=width2_mm, height_mm=height2_mm, stiffness=stiffness, center=center, rotation_angle_degrees=180))
    
    return shapes


def atom(width_mm=5, height_mm=2, center=Coordinate(5, 5), stiffness=0.1):
    """
    Generates a list of shapes representing an atom.

    Args:
        width_mm (float): The width of the atom shape in millimeters. Default is 5.
        height_mm (float): The height of the atom shape in millimeters. Default is 2.
        center (Coordinate): The center coordinate of the atom shape. Default is (5, 5).

    Returns:
        list: A list of shapes representing an atom.
    """
    shapes = []
    shapes.append(Oval(width_mm=width_mm, height_mm=height_mm, stiffness=stiffness, center=center))
    shapes.append(Oval(width_mm=width_mm, height_mm=height_mm, stiffness=stiffness, center=center, rotation_angle_degrees=60))
    shapes.append(Oval(width_mm=width_mm, height_mm=height_mm, stiffness=stiffness, center=center, rotation_angle_degrees=120))

    return shapes


def audi(size_mm=5, center=Coordinate(5, 5), stiffness=0.1):
    """
    Generates a list of shapes representing the Audi logo.

    Args:
        size_mm (float): The size of the logo in millimeters. Default is 5.
        center (Coordinate): The center coordinate of the logo. Default is (5, 5).

    Returns:
        list: A list of shapes representing the Audi logo.
    """
    shapes = []
    radius = size_mm / 2
    offset = radius / 4
    
    shapes.append(Circle(diameter_mm=size_mm, stiffness=stiffness, center=Coordinate(center.x + radius - offset, center.y)))
    shapes.append(Circle(diameter_mm=size_mm, stiffness=stiffness, center=Coordinate(center.x + 3*(radius - offset), center.y)))
    shapes.append(Circle(diameter_mm=size_mm, stiffness=stiffness, center=Coordinate(center.x - (radius - offset), center.y)))
    shapes.append(Circle(diameter_mm=size_mm, stiffness=stiffness, center=Coordinate(center.x - 3*(radius - offset), center.y)))

    return shapes