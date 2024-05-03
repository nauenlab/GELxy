from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from CuringCalculations import CuringCalculations


class Rectangle(Shape):
    """
    Represents a rectangle shape.

    Attributes:
        width_mm (float): The width of the rectangle in millimeters.
        height_mm (float): The height of the rectangle in millimeters.
        stiffness (float): The stiffness of the rectangle.
        center (Coordinate): The center coordinate of the rectangle.
        rotation_angle (float): The rotation angle of the rectangle in degrees.
        beam_diameter (float): The beam diameter used for curing calculations.
        uses_step_coordinates (bool): Indicates whether the rectangle uses step coordinates.
        filled (bool): Indicates whether the rectangle is filled.
    """

    def __init__(self, width_mm, height_mm, stiffness, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None, filled=False):
        """
        Initializes a Rectangle object.

        Args:
            width_mm (float): The width of the rectangle in millimeters.
            height_mm (float): The height of the rectangle in millimeters.
            stiffness (float): The stiffness of the rectangle.
            center (Coordinate, optional): The center coordinate of the rectangle. Defaults to None.
            rotation_angle (float, optional): The rotation angle of the rectangle in degrees. Defaults to None.
            beam_diameter (float, optional): The beam diameter used for curing calculations. Defaults to None.
            uses_step_coordinates (bool, optional): Indicates whether the rectangle uses step coordinates. Defaults to None.
            filled (bool, optional): Indicates whether the rectangle is filled. Defaults to False.
        """
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=filled, stiffness=stiffness)
        self.width = float(width_mm)
        self.height = float(height_mm)

    def __line_coordinates__(self, raw=False):
        """
        Returns the line coordinates of the rectangle.

        Args:
            raw (bool, optional): Indicates whether to return raw coordinates or normalized coordinates. Defaults to False.

        Returns:
            Coordinates: The line coordinates of the rectangle.
        """
        coordinates = Coordinates()
        coordinates.append(Coordinate(0, 0))
        coordinates.append(Coordinate(0, self.height))
        coordinates.append(Coordinate(self.width, self.height))
        coordinates.append(Coordinate(self.width, 0))
        coordinates.append(Coordinate(0, 0))

        if not raw:
            configuration = CuringCalculations().get_configuration(self.stiffness, self.beam_diameter)
            coordinates.normalize(center=self.center, rotation=self.rotation_angle, configuration=configuration)
        return coordinates




