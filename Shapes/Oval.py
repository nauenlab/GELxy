import math
from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm

class Oval(Shape):
    """
    Represents an oval shape.

    Attributes:
        width_mm (float): The width of the oval in millimeters.
        height_mm (float): The height of the oval in millimeters.
        stiffness (float): The stiffness of the oval.
        center (Coordinate, optional): The center coordinate of the oval. Defaults to None.
        rotation_angle_degrees (float, optional): The rotation angle of the oval in degrees. Defaults to None.
        beam_diameter (float, optional): The beam diameter. Defaults to None.
        filled (bool, optional): Whether the oval is filled or not. Defaults to False.
    """

    def __init__(self, width_mm, height_mm, stiffness, center=None, rotation_angle_degrees=None, beam_diameter=None, filled=False):
        """
        Initializes a new instance of the Oval class.

        Args:
            width_mm (float): The width of the oval in millimeters.
            height_mm (float): The height of the oval in millimeters.
            stiffness (float): The stiffness of the oval.
            center (Coordinate, optional): The center coordinate of the oval. Defaults to None.
            rotation_angle_degrees (float, optional): The rotation angle of the oval in degrees. Defaults to None.
            beam_diameter (float, optional): The beam diameter. Defaults to None.
            filled (bool, optional): Whether the oval is filled or not. Defaults to False.
        """
        super().__init__(center=center, rotation_angle_degrees=rotation_angle_degrees, beam_diameter=beam_diameter, uses_step_coordinates=True, filled=filled, stiffness=stiffness)
        self.width = float(width_mm)
        self.height = float(height_mm)
    
    def __radial_coordinates__(self):
        """
        Calculates the radial coordinates of the oval.

        Returns:
            Coordinates: The calculated radial coordinates.
        """
        coordinates = Coordinates()
        x_pos1 = math.cos(math.radians(0))
        y_pos1 = math.sin(math.radians(0))
        mx = 360
        resolution = 0.1
        for i in tqdm(range(0, int(mx * 1/resolution) + 1, int(resolution * 1/resolution)), desc="Getting Coordinates"):
            i = float(i) / (1/resolution)
            x_pos = math.cos(math.radians(i))
            y_pos = math.sin(math.radians(i))

            x_pos2 = (x_pos - x_pos1) * self.width/2
            y_pos2 = (y_pos - y_pos1) * self.height/2
            c = Coordinate(x_pos2, y_pos2)
            coordinates.append_if_far_enough(c)

        return coordinates


