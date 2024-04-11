from Shapes.Rectangle import Rectangle


class Square(Rectangle):

    def __init__(self, side_length_mm, stiffness, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None, filled=False):
        super().__init__(width_mm=side_length_mm, height_mm=side_length_mm, center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=filled, stiffness=stiffness)

