from Shape import Shape
from Coordinate import Coordinate, Coordinates


class Triangle(Shape):

    def __init__(self, width_mm, height_mm, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates)
        self.width = float(width_mm)
        self.height = float(height_mm)

    def get_coordinates(self):
        if self.uses_step_coordinates:
            return self.__step_coordinates__()
        return self.__line_coordinates__()

    def __step_coordinates__(self):
        coordinates = Coordinates()
        resolution = 0.005
        for i in range(0, int(self.height * (1 / resolution)) + 1, int(resolution * (1 / resolution))):
            i = float(i) / (1 / resolution)
            c = Coordinate(0, i)

            coordinates.append_if_far_enough(c, self.beam_diameter)

        for i in range(0, int(self.width * (1 / resolution)) + 1, int(resolution * (1 / resolution))):
            i = float(i) / (1 / resolution)
            c = Coordinate(i, self.height)

            coordinates.append_if_far_enough(c, self.beam_diameter)

        for i in range(0, int(self.height * (1 / resolution)) + 1, int(resolution * (1 / resolution))):
            i = float(i) / (1 / resolution)
            c = Coordinate(self.width, self.height - i)

            coordinates.append_if_far_enough(c, self.beam_diameter)

        for i in range(0, int(self.width * (1 / resolution)) + 1, int(resolution * (1 / resolution))):
            i = float(i) / (1 / resolution)
            c = Coordinate(self.width - i, 0)

            coordinates.append_if_far_enough(c, self.beam_diameter)

        coordinates.normalize(step_time=0.5, center=self.center, rotation=self.rotation_angle)
        return coordinates

    def __line_coordinates__(self):
        coordinates = Coordinates()
        coordinates.append(Coordinate(0, 0))
        coordinates.append(Coordinate(self.width, 0))
        coordinates.append(Coordinate(self.width / 2, self.height))
        coordinates.append(Coordinate(0, 0))

        coordinates.normalize(step_time=10, center=self.center, rotation=self.rotation_angle)
        return coordinates




