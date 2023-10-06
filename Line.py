from Shape import Shape
from Coordinate import Coordinate, Coordinates


class Line(Shape):

    def __init__(self, length_mm, beam_diameter, is_horizontal=False, uses_step_coordinates=False):
        super().__init__()
        self.length = float(length_mm)
        self.beam_diameter = beam_diameter
        self.is_horizontal = is_horizontal
        self.uses_step_coordinates = uses_step_coordinates

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

        coordinates.normalize(step_time=0.24)
        return coordinates

    def __line_coordinates__(self):
        coordinates = Coordinates()
        if self.is_horizontal:
            coordinates.append(Coordinate(0, 0))
            coordinates.append(Coordinate(0, self.length))
        else:
            coordinates.append(Coordinate(0, 0))
            coordinates.append(Coordinate(0, self.length))

        coordinates.normalize(step_time=10)
        return coordinates




