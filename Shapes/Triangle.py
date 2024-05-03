from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from CuringCalculations import CuringCalculations


class Triangle(Shape):
    """
    Represents a triangle shape.

    Args:
        width_mm (float): The width of the triangle in millimeters.
        height_mm (float): The height of the triangle in millimeters.
        stiffness (float): The stiffness of the triangle.
        center (Coordinate, optional): The center coordinate of the triangle. Defaults to None.
        rotation_angle (float, optional): The rotation angle of the triangle in degrees. Defaults to None.
        beam_diameter (float, optional): The beam diameter of the triangle. Defaults to None.
        uses_step_coordinates (bool, optional): Indicates whether the triangle uses step coordinates. Defaults to None.
        filled (bool, optional): Indicates whether the triangle is filled. Defaults to False.

    Attributes:
        width (float): The width of the triangle in millimeters.
        height (float): The height of the triangle in millimeters.

    Methods:
        __line_coordinates__(raw=False): Returns the line coordinates of the triangle.

    """

    def __init__(self, width_mm, height_mm, stiffness, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None, filled=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=filled, stiffness=stiffness)
        self.width = float(width_mm)
        self.height = float(height_mm)

    def __line_coordinates__(self, raw=False):
        """
        Returns the line coordinates of the triangle.

        Args:
            raw (bool, optional): Indicates whether to return the raw line coordinates. Defaults to False.

        Returns:
            Coordinates: The line coordinates of the triangle.

        """
        coordinates = Coordinates()
        coordinates.append(Coordinate(0, 0))
        coordinates.append(Coordinate(self.width, 0))
        coordinates.append(Coordinate(self.width / 2, self.height))
        coordinates.append(Coordinate(0, 0))

        if not raw:
            configuration = CuringCalculations().get_configuration(self.stiffness, self.beam_diameter)
            coordinates.normalize(center=self.center, rotation=self.rotation_angle, configuration=configuration)
        return coordinates




