
import math
from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm

class SineWave(Shape):

    def __init__(self, amplitude_mm, cycles, cycles_per_mm, cycle_offset=0, center=None, rotation_angle=None, beam_diameter=None):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=True, filled=False)
        self.amplitude = float(amplitude_mm)
        self.cycles = abs(float(cycles))
        self.frequency = abs(float(cycles_per_mm * 360))
        self.cycle_offset = float(cycle_offset)
    
    def __radial_coordinates__(self):
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
            coordinates.append_if_far_enough(c, self.beam_diameter)

        coordinates.normalize(step_time=0.5, center=self.center, rotation=self.rotation_angle)
        return coordinates


