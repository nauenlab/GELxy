import math
from Shapes.Triangle import Triangle


class EquilateralTriangle(Triangle):

    def __init__(self, side_length_mm, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None):
        height = math.sqrt((side_length_mm ** 2) * 3 / 4)
        super().__init__(width_mm=side_length_mm, height_mm=height, center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates)



