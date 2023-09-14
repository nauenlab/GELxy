
import math
from Shape import Shape
from Coordinate import Coordinate, Coordinates


class Circle(Shape):

    def __init__(self, diameter):
        super().__init__()
        self.diameter = float(diameter)
        self.radius = float(diameter) / 2

    def get_coordinates(self):
        diameter_factor = self.diameter / 2
        coordinates = Coordinates()
        x_pos1 = math.cos(math.radians(0))
        y_pos1 = math.sin(math.radians(0))
        for i in [0, 90, 180, 270, 360]:
            x_pos = math.cos(math.radians(i))
            y_pos = math.sin(math.radians(i))

            x_pos2 = (x_pos - x_pos1) * diameter_factor
            y_pos2 = (y_pos - y_pos1) * diameter_factor
            c = Coordinate(x_pos2, y_pos2)
            coordinates.append(c)

        coordinates.normalize()
        return coordinates


