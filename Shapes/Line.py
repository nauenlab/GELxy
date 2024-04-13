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
        is_horizontal (bool, optional): Indicates if the line is horizontal. Defaults to False.
        uses_step_coordinates (bool, optional): Indicates if the line uses step coordinates. Defaults to False.

    Attributes:
        length (float): The length of the line.
        is_horizontal (bool): Indicates if the line is horizontal.

    Methods:
        __line_coordinates__(raw=False): Returns the coordinates of the line.

    """

    def __init__(self, length_mm, stiffness, center=None, rotation_angle=None, beam_diameter=None, is_horizontal=False, uses_step_coordinates=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=False, stiffness=stiffness)
        self.length = float(length_mm)
        self.is_horizontal = is_horizontal

    def __line_coordinates__(self, raw=False):
        """
        Returns the coordinates of the line.

        Args:
            raw (bool, optional): Indicates if the coordinates should be returned in raw form. Defaults to False.

        Returns:
            Coordinates: The coordinates of the line.

        """
        coordinates = Coordinates()
        if self.is_horizontal:
            coordinates.append(Coordinate(-self.length/2, 0))
            coordinates.append(Coordinate(self.length/2, 0))
        else:
            coordinates.append(Coordinate(0, -self.length/2))
            coordinates.append(Coordinate(0, self.length/2))

        if not raw:
            configuration = CuringCalculations().get_configuration(self.stiffness, self.beam_diameter)
            coordinates.normalize(center=self.center, rotation=self.rotation_angle, configuration=configuration)
        return coordinates




