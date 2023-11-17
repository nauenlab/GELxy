from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates


class Triangle(Shape):

    def __init__(self, width_mm, height_mm, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None, filled=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=filled)
        self.width = float(width_mm)
        self.height = float(height_mm)

    def __line_coordinates__(self, raw=False):
        coordinates = Coordinates()
        coordinates.append(Coordinate(0, 0))
        coordinates.append(Coordinate(self.width, 0))
        coordinates.append(Coordinate(self.width / 2, self.height))
        coordinates.append(Coordinate(0, 0))

        if not raw:
            coordinates.normalize(step_time=10, center=self.center, rotation=self.rotation_angle)
        return coordinates




