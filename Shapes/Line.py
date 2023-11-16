from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates


class Line(Shape):

    def __init__(self, length_mm, center=None, rotation_angle=None, beam_diameter=None, is_horizontal=False, uses_step_coordinates=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates)
        self.length = float(length_mm)
        self.is_horizontal = is_horizontal

    def __line_coordinates__(self, raw=False):
        coordinates = Coordinates()
        if self.is_horizontal:
            coordinates.append(Coordinate(-self.length/2, 0))
            coordinates.append(Coordinate(self.length/2, 0))
        else:
            coordinates.append(Coordinate(0, -self.length/2))
            coordinates.append(Coordinate(0, self.length/2))

        if not raw:
            coordinates.normalize(step_time=10, center=self.center, rotation=self.rotation_angle)
        return coordinates




