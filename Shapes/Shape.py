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
            coordinates = self.__step_coordinates__() if "uses_step_coordinates" in dir(self) and self.uses_step_coordinates else self.__line_coordinates__()
        elif "__radial_coordinates__" in dir(self):
            coordinates = self.__radial_coordinates__()
        else:
            raise Exception("Shape does not have a line or radial coordinate function")

        if self.filled:
            coordinates = coordinates.fill()

        if coordinates:
            coordinates.normalize(center=self.center, rotation=self.rotation_angle_degrees, stiffness=self.stiffness, beam_diameter_mm=self.beam_diameter)
        
        return coordinates
    
    def __step_coordinates__(self):
        """
        Gets the step coordinates of the shape.

        Returns:
            Coordinates: The step coordinates of the shape.
        """
        coordinates = Coordinates()
        resolution = 0.005
        line_coordinates = self.__line_coordinates__()

        # Fill in the space between the coordinates linearly
        for i in tqdm(range(len(line_coordinates) - 1), desc="Getting Coordinates"):
            start_point = line_coordinates[i]
            end_point = line_coordinates[i + 1]
            num_points = int(self.distance(start_point.x, start_point.y, end_point.x, end_point.y) * (1 / resolution)) + 1
            for j in range(1, num_points):
                t = Decimal(j / (num_points - 1))
                x = start_point.x + t * (end_point.x - start_point.x)
                y = start_point.y + t * (end_point.y - start_point.y)
                new_coord = Coordinate(x, y)
                if abs(new_coord.x - end_point.x) < resolution and abs(new_coord.y - end_point.y) < resolution:
                    coordinates.append_if_no_duplicate(end_point)
                    continue

                coordinates.append_if_far_enough(new_coord)

        return coordinates

    @staticmethod
    def distance(x1, y1, x2, y2):
        """
        Calculates the distance between two points.

        Args:
            x1 (float): The x-coordinate of the first point.
            y1 (float): The y-coordinate of the first point.
            x2 (float): The x-coordinate of the second point.
            y2 (float): The y-coordinate of the second point.

        Returns:
            float: The distance between the two points.
        """
        xd = x2 - x1
        yd = y2 - y1
        return math.sqrt(xd ** 2 + yd ** 2)

