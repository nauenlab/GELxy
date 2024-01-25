import math
from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from tqdm import tqdm

class Oval(Shape):

    def __init__(self, width_mm, height_mm, center=None, rotation_angle=None, beam_diameter=None, filled=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=True, filled=filled)
        self.width = float(width_mm)
        self.height = float(height_mm)
    
    def __radial_coordinates__(self):
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
            coordinates.append_if_far_enough(c, self.beam_diameter)

        if self.filled:
            coordinates = coordinates.fill(self.beam_diameter)
        else:
            coordinates.append_if_far_enough(Coordinate(coordinates[0].x, coordinates[0].y), self.beam_diameter)

        coordinates.normalize(step_time=0.3, center=self.center, rotation=self.rotation_angle)
        return coordinates


