import math
from Shapes.Triangle import Triangle


class EquilateralTriangle(Triangle):
    """
    Represents an equilateral triangle shape.

    Args:
        side_length_mm (float): The length of the sides of the triangle in millimeters.
        stiffness (float): The stiffness of the triangle.
        center (tuple, optional): The center coordinates of the triangle. Defaults to None.
        rotation_angle_degrees (float, optional): The rotation angle of the triangle in degrees. Defaults to None.
        beam_diameter (float, optional): The diameter of the beam used for the triangle. Defaults to None.
        uses_step_coordinates (bool, optional): Indicates whether the triangle uses step coordinates. Defaults to None.
        filled (bool, optional): Indicates whether the triangle is filled. Defaults to False.

    Attributes:
        width_mm (float): The width of the triangle in millimeters.
        height_mm (float): The height of the triangle in millimeters.

    """

    def __init__(self, side_length_mm, stiffness, center=None, rotation_angle_degrees=None, beam_diameter=None, uses_step_coordinates=None, filled=False):
        height = math.sqrt((side_length_mm ** 2) * 3 / 4)
        super().__init__(width_mm=side_length_mm, height_mm=height, center=center, rotation_angle_degrees=rotation_angle_degrees, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=filled, stiffness=stiffness)
