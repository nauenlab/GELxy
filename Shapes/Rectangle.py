from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates


class Rectangle(Shape):

    def __init__(self, width_mm, height_mm, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates)
        self.width = float(width_mm)
        self.height = float(height_mm)

    def __line_coordinates__(self):
        coordinates = Coordinates()
        coordinates.append(Coordinate(0, 0))
        coordinates.append(Coordinate(0, self.height))
        coordinates.append(Coordinate(self.width, self.height))
        coordinates.append(Coordinate(self.width, 0))
        coordinates.append(Coordinate(0, 0))

        coordinates.normalize(step_time=10, center=self.center, rotation=self.rotation_angle)
        return coordinates




