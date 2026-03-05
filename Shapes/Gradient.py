from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm
import math
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS, MINIMUM_VELOCITY
from decimal import Decimal
from CuringCalculations import curing_calculations

class Gradient(Shape):
    """
    Represents a gradient shape (rectangle with varying stiffness across columns).

    Uses sweep-based zigzag (boustrophedon) path planning to minimize dead travel.
    Consecutive columns alternate vertical direction, eliminating full-height
    repositioning moves between columns.

    Args:
        min_stiffness (float): The minimum stiffness of the gradient.
        max_stiffness (float): The maximum stiffness of the gradient.
        height_mm (float): The height of the gradient rectangle.
        width_mm (float): The width of the gradient rectangle.
        center (Coordinate): The center coordinate.
        beam_diameter (float): The diameter of the beam.
        rotation_angle_degrees (float, optional): The rotation angle in degrees. Defaults to 0.
        is_reversed (bool, optional): Whether the gradient is reversed. Defaults to False.
    """

    def __init__(self, min_stiffness, max_stiffness, height_mm, width_mm, center, beam_diameter, rotation_angle_degrees=None, is_reversed=False):
        super().__init__(center=center, rotation_angle_degrees=rotation_angle_degrees, beam_diameter=beam_diameter, uses_step_coordinates=False, filled=False, stiffness=0)
        self.min_stiffness = min_stiffness
        self.max_stiffness = max_stiffness
        self.is_reversed = is_reversed
        self.height = height_mm
        self.width = width_mm

    def get_coordinates(self):
        """
        Generates coordinates using sweep-based zigzag path planning.

        Instead of creating independent vertical Lines all going bottom-to-top,
        alternates column direction (boustrophedon) to eliminate full-height dead travel.
        Iteration passes are batched: all first passes grouped, then all second passes, etc.

        Returns:
            Coordinates: The generated coordinates.
        """
        coordinates = Coordinates()
        w = Decimal(self.width)
        h = Decimal(self.height)
        b = Decimal(self.beam_diameter)
        x_bounds = (self.center.x - (w / 2) + (b / 2), self.center.x + (w / 2) + (b / 2))
        normalized_beam_diameter = Decimal(MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS)
        num_columns = math.floor((x_bounds[1] - x_bounds[0]) / normalized_beam_diameter)

        if num_columns == 0:
            return coordinates

        y_bottom = self.center.y - (h / 2)
        y_top = self.center.y + (h / 2)

        if num_columns == 1:
            stiffness_step = 0
        else:
            stiffness_step = float(self.max_stiffness - self.min_stiffness) / float(num_columns - 1)

        cur_s = self.min_stiffness
        if self.is_reversed:
            stiffness_step *= -1
            cur_s = self.max_stiffness

        # Pre-compute per-column configuration
        columns = []
        x = x_bounds[0] + (b / 2)
        for _ in tqdm(range(num_columns), desc="Getting Coordinates"):
            config = curing_calculations.get_resolved_configuration_from_velocities(0, MINIMUM_VELOCITY, cur_s, self.beam_diameter)
            columns.append({
                'x': x,
                'current': config.current,
                'iterations': config.iterations,
            })
            cur_s += stiffness_step
            x += normalized_beam_diameter

        max_iterations = max(col['iterations'] for col in columns)
        velocity = (0, MINIMUM_VELOCITY)

        # Track zigzag direction — alternates only when a column is actually cured
        going_up = True

        for sweep_num in range(max_iterations):
            is_forward = (sweep_num % 2 == 0)
            col_order = list(range(num_columns)) if is_forward else list(range(num_columns - 1, -1, -1))

            for col_idx in col_order:
                col = columns[col_idx]
                needs_curing = col['iterations'] > sweep_num

                if going_up:
                    y_a, y_b = y_bottom, y_top
                else:
                    y_a, y_b = y_top, y_bottom

                if needs_curing:
                    # Move to column start (lp=False)
                    c_start = Coordinate(col['x'], y_a)
                    c_start.lp = False
                    coordinates.append(c_start)

                    # Cure to column end
                    c_end = Coordinate(col['x'], y_b)
                    c_end.v = velocity
                    c_end.a = col['current']
                    c_end.lp = True
                    coordinates.append(c_end)

                    going_up = not going_up

        coordinates.rotate_coordinates(self.center, self.rotation_angle_degrees)

        return coordinates
