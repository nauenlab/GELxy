from Rectangle import Rectangle


class Square(Rectangle):

    def __init__(self, width_mm, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None):
        super().__init__(width_mm=width_mm, height_mm=width_mm, center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates)
        height = width_mm ** 2 * 3 / 4

