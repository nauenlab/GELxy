from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates


class Line(Shape):

    def __init__(self, length_mm, center=None, rotation_angle=None, beam_diameter=None, is_horizontal=False, uses_step_coordinates=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates)
        self.length = float(length_mm)
        self.is_horizontal = is_horizontal

    def get_coordinates(self):
        if self.uses_step_coordinates:
            return self.__step_coordinates__()
        return self.__line_coordinates__()

    def __step_coordinates__(self):
        coordinates = Coordinates()
        mx = self.length
        resolution = 0.01
        for i in range(0, int(mx * (1 / resolution)) + 1, int(resolution * (1 / resolution))):
            i = float(i) / (1 / resolution)

            c = Coordinate(0, i)
            if self.is_horizontal:
                c = Coordinate(i, 0)

            coordinates.append_if_far_enough(c, self.beam_diameter)

        coordinates.normalize(step_time=0.5, center=self.center, rotation=self.rotation_angle)
        return coordinates

    def __line_coordinates__(self):
        coordinates = Coordinates()
        if self.is_horizontal:
            coordinates.append(Coordinate(-self.length/2, 0))
            coordinates.append(Coordinate(self.length/2, 0))
        else:
            coordinates.append(Coordinate(0, -self.length/2))
            coordinates.append(Coordinate(0, self.length/2))

        coordinates.normalize(step_time=10, center=self.center, rotation=self.rotation_angle)
        return coordinates




