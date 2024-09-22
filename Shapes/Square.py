from Shapes.Rectangle import Rectangle


class Square(Rectangle):
    """
    Represents a square shape.

    Args:
        side_length_mm (float): The length of the square's side in millimeters.
        stiffness (float): The stiffness of the square.
        center (tuple, optional): The coordinates of the center of the square. Defaults to None.
        rotation_angle_degrees (float, optional): The rotation angle of the square in degrees. Defaults to None.
        beam_diameter (float, optional): The diameter of the beam used to draw the square. Defaults to None.
        uses_step_coordinates (bool, optional): Indicates whether the square uses step coordinates. Defaults to None.
        filled (bool, optional): Indicates whether the square is filled. Defaults to False.
    """

    def __init__(self, side_length_mm, stiffness, center=None, rotation_angle_degrees=None, beam_diameter=None, uses_step_coordinates=None, filled=False):
        super().__init__(width_mm=side_length_mm, height_mm=side_length_mm, center=center, rotation_angle_degrees=rotation_angle_degrees, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=filled, stiffness=stiffness)
