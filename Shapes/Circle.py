from Shapes.Oval import Oval


class Circle(Oval):
    """
    A class representing a circle shape.

    Attributes:
        diameter_mm (float): The diameter of the circle in millimeters.
        stiffness (float): The stiffness of the circle.
        center (tuple, optional): The center coordinates of the circle. Defaults to None.
        beam_diameter (float, optional): The beam diameter of the circle. Defaults to None.
        filled (bool, optional): Whether the circle is filled or not. Defaults to False.
    """

    def __init__(self, diameter_mm, stiffness, center=None, beam_diameter=None, filled=False):
        """
        Initializes a Circle object.

        Args:
            diameter_mm (float): The diameter of the circle in millimeters.
            stiffness (float): The stiffness of the circle.
            center (tuple, optional): The center coordinates of the circle. Defaults to None.
            beam_diameter (float, optional): The beam diameter of the circle. Defaults to None.
            filled (bool, optional): Whether the circle is filled or not. Defaults to False.
        """
        super().__init__(width_mm=diameter_mm, height_mm=diameter_mm, center=center, rotation_angle=None, beam_diameter=beam_diameter, filled=filled, stiffness=stiffness)
