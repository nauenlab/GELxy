from Shapes.Shape import Shape
from Shapes.Line import Line
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm
import math
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS
from decimal import Decimal


class GradientLine(Shape):
    """
    Represents a single line with a stiffness gradient along its length.

    The gradient is achieved by dividing the line into consecutive segments, each
    exposed once at a linearly interpolated stiffness. This follows the same pattern
    as the Gradient (rectangle) shape but in one dimension.

    Args:
        length_mm (float): The total length of the line in millimeters.
        min_stiffness (float): The minimum stiffness value.
        max_stiffness (float): The maximum stiffness value.
        center (Coordinate): The center coordinate of the line.
        beam_diameter (float): The diameter of the beam.
        rotation_angle_degrees (float, optional): The rotation angle in degrees. Defaults to 0.
        is_reversed (bool, optional): If True, reverses the gradient direction. Defaults to False.
        num_steps (int, optional): The number of segments. Defaults to length / min beam spacing.
    """

    def __init__(self, length_mm, min_stiffness, max_stiffness, center, beam_diameter, rotation_angle_degrees=None, is_reversed=False, num_steps=None):
        super().__init__(center=center, rotation_angle_degrees=rotation_angle_degrees, beam_diameter=beam_diameter, uses_step_coordinates=False, filled=False, stiffness=0)
        self.length = float(length_mm)
        self.min_stiffness = min_stiffness
        self.max_stiffness = max_stiffness
        self.is_reversed = is_reversed
        self.num_steps = num_steps if num_steps else max(2, math.floor(length_mm / MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS))

    def get_coordinates(self):
        """
        Generates coordinates by creating consecutive line segments, each at a
        linearly interpolated stiffness.

        Returns:
            Coordinates: The generated coordinates.
        """
        coordinates = Coordinates()
        step_length = Decimal(self.length) / Decimal(self.num_steps)
        half_length = Decimal(self.length) / Decimal(2)

        if self.num_steps == 1:
            stiffness_step = 0
        else:
            stiffness_step = float(self.max_stiffness - self.min_stiffness) / float(self.num_steps - 1)

        cur_s = self.min_stiffness
        if self.is_reversed:
            stiffness_step *= -1
            cur_s = self.max_stiffness

        for k in tqdm(range(self.num_steps), desc="Getting Coordinates"):
            segment_center_y = self.center.y - half_length + (step_length * k) + (step_length / 2)

            temp_coords = Line(
                float(step_length),
                cur_s,
                center=Coordinate(self.center.x, segment_center_y),
                rotation_angle_degrees=0,
                beam_diameter=self.beam_diameter
            ).get_coordinates()
            temp_coords[0].lp = False
            coordinates += temp_coords
            cur_s += stiffness_step

        coordinates.rotate_coordinates(self.center, self.rotation_angle_degrees)

        return coordinates
