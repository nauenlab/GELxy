from Shapes.Shape import Shape
from Coordinate import Coordinate, Coordinates
from CuringCalculations import CuringCalculations

class Rectangle(Shape):

    def __init__(self, width_mm, height_mm, stiffness, center=None, rotation_angle=None, beam_diameter=None, uses_step_coordinates=None, filled=False):
        super().__init__(center=center, rotation_angle=rotation_angle, beam_diameter=beam_diameter, uses_step_coordinates=uses_step_coordinates, filled=filled, stiffness=stiffness)
        self.width = float(width_mm)
        self.height = float(height_mm)

    def __line_coordinates__(self, raw=False):
        coordinates = Coordinates()
        coordinates.append(Coordinate(0, 0))
        coordinates.append(Coordinate(0, self.height))
        coordinates.append(Coordinate(self.width, self.height))
        coordinates.append(Coordinate(self.width, 0))
        coordinates.append(Coordinate(0, 0))

        if not raw:
            configuration = CuringCalculations().get_configuration(self.stiffness, self.beam_diameter)
            coordinates.normalize(center=self.center, rotation=self.rotation_angle, configuration=configuration)
        return coordinates




