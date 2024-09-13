from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from CuringCalculations import CuringCalculations


class Line(Shape):
    """
    Represents a line shape.

    Args:
        length_mm (float): The length of the line in millimeters.
        stiffness (float): The stiffness of the line.
        center (Coordinate, optional): The center coordinate of the line. Defaults to None.
        rotation_angle (float, optional): The rotation angle of the line. Defaults to None.
        beam_diameter (float, optional): The beam diameter of the line. Defaults to None.
        uses_step_coordinates (bool, optional): Indicates if the line uses step coordinates. Defaults to False.

    Attributes:
        length (float): The length of the line.
        is_horizontal (bool): Indicates if the line is horizontal.

    """

    def __init__(self, length_mm, stiffness, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=False, stiffness=stiffness)
        self.length = float(length_mm)

    def __line_coordinates__(self):
        """
        Returns the coordinates of the line.

        Returns:
            Coordinates: The coordinates of the line.

        """
        coordinates = Coordinates()        
        coordinates.append(Coordinate(0, -self.length/2))
        coordinates.append(Coordinate(0, self.length/2))

        return coordinates




