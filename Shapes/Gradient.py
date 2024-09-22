from Shapes.Shape import Shape
from Shapes.Line import Line
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm
import math
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS

class Gradient(Shape):
    """
    Represents a gradient shape.

    Args:
        min_velocity (float): The minimum velocity of the gradient.
        max_velocity (float): The maximum velocity of the gradient.
        beam_diameter (float): The diameter of the beam.
        is_horizontal (bool, optional): Whether the gradient is horizontal. Defaults to True.
        is_reversed (bool, optional): Whether the gradient is reversed. Defaults to True.
    """

    def __init__(self, min_stiffness, max_stiffness, height_mm, width_mm, center, beam_diameter, rotation_angle_degrees=None, is_reversed=False):
        super().__init__(center=center, rotation_angle_degrees=rotation_angle_degrees, beam_diameter=beam_diameter, uses_step_coordinates=False, filled=False, stiffness=0)
        self.min_stiffness = min_stiffness
        self.max_stiffness = max_stiffness
        self.is_reversed = is_reversed
        self.height = height_mm
        self.width = width_mm

    def get_coordinates(self):
        coordinates =  self.__line_coordinates__()

        # if coordinates:
        #     configuration = CuringCalculations().get_configuration(self.stiffness, self.beam_diameter)
        #     coordinates.normalize(center=self.center, rotation=self.rotation_angle_degrees, configuration=configuration)
        
        return coordinates

    def __line_coordinates__(self):
        """
        Generates the coordinates for the gradient shape.

        Returns:
            Coordinates: The generated coordinates.
        """
        coordinates = Coordinates()
        x_bounds = (self.center.x - (self.width / 2) + (self.beam_diameter / 2), self.center.x + (self.width / 2) + (self.beam_diameter / 2))
        normalized_beam_diameter = self.beam_diameter - (self.beam_diameter - MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS)
        num_lines = math.floor((x_bounds[1] - x_bounds[0]) / normalized_beam_diameter)
        stiffness_step = float(self.max_stiffness - self.min_stiffness)/float(num_lines - 1)
        cur_s = self.min_stiffness

        if self.is_reversed:
            stiffness_step *= -1
            cur_s = self.max_stiffness
        
        i = x_bounds[0] + (self.beam_diameter / 2)
        for _ in tqdm(range(num_lines), desc="Getting Coordinates"):
            temp_coords = Line(self.height, cur_s, center=Coordinate(i, self.center.y), rotation_angle_degrees=0, beam_diameter=self.beam_diameter).get_coordinates()
            temp_coords[0].lp = False
            coordinates += temp_coords
            cur_s += stiffness_step

            i += normalized_beam_diameter
        
        coordinates.rotate_coordinates(self.center, self.rotation_angle_degrees)
        
        # if self.is_reversed:
        #     coordinates.coordinates.reverse()
        
        return coordinates
