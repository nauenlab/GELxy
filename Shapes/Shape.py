import math
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm
from decimal import Decimal

class Shape:
    """
    Represents a shape in a coordinate system.

    Attributes:
        center (Coordinate): The center coordinate of the shape.
        rotation_angle_degrees (float): The rotation angle of the shape in degrees.
        beam_diameter (float): The diameter of the beam used to draw the shape.
        uses_step_coordinates (bool): Indicates whether the shape uses step coordinates.
        filled (bool): Indicates whether the shape should be filled.
        stiffness (float): The stiffness of the shape.
    """

    def __init__(self, center, rotation_angle_degrees, beam_diameter, uses_step_coordinates, filled, stiffness):
        """
        Initializes a new instance of the Shape class.

        Args:
            center (Coordinate): The center coordinate of the shape.
            rotation_angle_degrees (float): The rotation angle of the shape in degrees.
            beam_diameter (float): The diameter of the beam used to draw the shape.
            uses_step_coordinates (bool): Indicates whether the shape uses step coordinates.
            filled (bool): Indicates whether the shape should be filled.
            stiffness (float): The stiffness of the shape.
        """
        self.center = center if center else Coordinate(0, 0)
        self.rotation_angle_degrees = rotation_angle_degrees if rotation_angle_degrees else 0
        self.beam_diameter = beam_diameter if beam_diameter else 0.1
        self.uses_step_coordinates = uses_step_coordinates if uses_step_coordinates else False
        self.filled = filled if filled else False
        self.stiffness = stiffness if stiffness else 1

    def plot(self):
        """
        Plots the shape.
        """
        # subclasses must have the get_coordinates function
        coordinates = self.get_coordinates()
        coordinates.plot()

    def get_coordinates(self):
        """
        Gets the coordinates of the shape.

        Returns:
            Coordinates: The coordinates of the shape.
        
        Raises:
            Exception: If the shape does not have a line or radial coordinate function.
        """
        coordinates = None
        if "__line_coordinates__" in dir(self):
            coordinates = self.__line_coordinates__()
            if self.uses_step_coordinates:
                coordinates = coordinates.fill_line_segments()
        elif "__radial_coordinates__" in dir(self):
            coordinates = self.__radial_coordinates__()
        else:
            raise Exception("Shape does not have a line or radial coordinate function")

        if self.filled:
            coordinates = coordinates.fill(uses_step_coordinates=self.uses_step_coordinates)

        if coordinates:
            coordinates.normalize(center=self.center, rotation=self.rotation_angle_degrees, stiffness=self.stiffness, beam_diameter_mm=self.beam_diameter)
        
        return coordinates
    
