import math
from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm

class SineWave(Shape):
    """
    Represents a sine wave shape.

    Args:
        amplitude_mm (float): The amplitude of the sine wave in millimeters.
        cycles (float): The number of cycles of the sine wave.
        cycles_per_mm (float): The number of cycles per millimeter.
        stiffness (float): The stiffness of the shape.
        cycle_offset (float, optional): The offset of the cycle in degrees. Defaults to 0.
        center (Coordinate, optional): The center coordinate of the shape. Defaults to None.
        rotation_angle_degrees (float, optional): The rotation angle of the shape in degrees. Defaults to None.
        beam_diameter (float, optional): The diameter of the beam. Defaults to None.

    Attributes:
        amplitude (float): The amplitude of the sine wave in millimeters.
        cycles (float): The number of cycles of the sine wave.
        frequency (float): The frequency of the sine wave in degrees.
        cycle_offset (float): The offset of the cycle in degrees.

    Inherits from:
        Shape

    Uses:
        Coordinate, Coordinates, tqdm, CuringCalculations
    """

    def __init__(self, amplitude_mm, cycles, cycles_per_mm, stiffness, cycle_offset=0, center=None, rotation_angle_degrees=None, beam_diameter=None):
        super().__init__(center=center, rotation_angle_degrees=rotation_angle_degrees, beam_diameter=beam_diameter, uses_step_coordinates=True, filled=False, stiffness=stiffness)
        self.amplitude = float(amplitude_mm)
        self.cycles = abs(float(cycles))
        self.frequency = abs(float(cycles_per_mm * 360))
        self.cycle_offset = float(cycle_offset)
    
    def __radial_coordinates__(self):
        """
        Generates the radial coordinates of the sine wave.

        Returns:
            Coordinates: The generated radial coordinates.
        """
        coordinates = Coordinates()

        mx = self.cycles * 360
        resolution = 0.1
        for i in tqdm(range(0, int(mx * 1/resolution) + 1, int(resolution * 1/resolution)), desc="Getting Coordinates"):
            i = float(i) / (1/resolution) + (self.cycle_offset * 360)

            x_pos = i
            y_pos = math.sin(math.radians(i))

            x_pos2 = x_pos / self.frequency
            y_pos2 = y_pos * self.amplitude 
            c = Coordinate(x_pos2, y_pos2)
            coordinates.append_if_far_enough(c)

        return coordinates


