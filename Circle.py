
import math
from Shape import Shape
from Coordinate import Coordinate, Coordinates


class Circle(Shape):

    def __init__(self, diameter_mm, beam_diameter):
        super().__init__()
        self.diameter = float(diameter_mm)
        self.radius = float(diameter_mm) / 2
        self.beam_diameter = beam_diameter
        
    def get_coordinates(self):
        return self.__radial_coordinates__()
    
    def __radial_coordinates__(self):
        coordinates = Coordinates()
        x_pos1 = math.cos(math.radians(0))
        y_pos1 = math.sin(math.radians(0))
        mx = 360
        resolution = 0.1
        for i in range(0, int(mx * 1/resolution) + 1, int(resolution * 1/resolution)):
            i = float(i) / (1/resolution)
            x_pos = math.cos(math.radians(i))
            y_pos = math.sin(math.radians(i))

            x_pos2 = (x_pos - x_pos1) * self.radius
            y_pos2 = (y_pos - y_pos1) * self.radius
            c = Coordinate(x_pos2, y_pos2)
            coordinates.append_if_far_enough(c, self.beam_diameter)

        coordinates.append(Coordinate(coordinates[0].x, coordinates[0].y))
        coordinates.normalize(step_time=0.5)
        return coordinates


