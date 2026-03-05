from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm
import math
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS, MINIMUM_VELOCITY
from decimal import Decimal
from CuringCalculations import curing_calculations


class GradientLine(Shape):
    """
    Represents a single line with a stiffness gradient along its length.

    The gradient is achieved by dividing the line into consecutive segments, each
    exposed at a linearly interpolated stiffness. Uses sweep-based path planning
    to minimize coordinate count by eliminating dead travel between contiguous segments
    and batching iteration passes.

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
        Generates coordinates using sweep-based path planning.

        Instead of creating N independent Line objects (each with its own normalize/velocity
        pipeline), builds full-length sweeps across all segments. Contiguous segments within
        a sweep share endpoints, eliminating zero-distance lamp-off moves. Segments needing
        multiple iterations are covered in subsequent backward/forward sweeps.

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

        # Pre-compute per-segment boundaries and curing configuration
        segments = []
        for k in tqdm(range(self.num_steps), desc="Getting Coordinates"):
            y_start = self.center.y - half_length + (step_length * k)
            y_end = y_start + step_length
            config = curing_calculations.get_resolved_configuration_from_velocities(0, MINIMUM_VELOCITY, cur_s, self.beam_diameter)
            segments.append({
                'y_start': y_start,
                'y_end': y_end,
                'current': config.current,
                'iterations': config.iterations,
            })
            cur_s += stiffness_step

        max_iterations = max(seg['iterations'] for seg in segments)
        velocity = (0, MINIMUM_VELOCITY)

        # Build sweeps: forward (0), backward (1), forward (2), ...
        for sweep_num in range(max_iterations):
            is_forward = (sweep_num % 2 == 0)
            seg_order = list(range(self.num_steps)) if is_forward else list(range(self.num_steps - 1, -1, -1))

            first_in_sweep = True
            prev_was_curing = False

            for seg_idx in seg_order:
                seg = segments[seg_idx]
                needs_curing = seg['iterations'] > sweep_num

                if is_forward:
                    y_a, y_b = seg['y_start'], seg['y_end']
                else:
                    y_a, y_b = seg['y_end'], seg['y_start']

                if needs_curing:
                    if first_in_sweep or not prev_was_curing:
                        # Start of a new curing run — move to segment start
                        c_start = Coordinate(self.center.x, y_a)
                        c_start.lp = False
                        coordinates.append(c_start)
                        first_in_sweep = False

                    # End of this segment — cure with segment's current
                    c_end = Coordinate(self.center.x, y_b)
                    c_end.v = velocity
                    c_end.a = seg['current']
                    c_end.lp = True
                    coordinates.append(c_end)

                    prev_was_curing = True
                else:
                    prev_was_curing = False

        coordinates.rotate_coordinates(self.center, self.rotation_angle_degrees)

        return coordinates
