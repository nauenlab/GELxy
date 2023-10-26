from Shapes.Oval import Oval


class Circle(Oval):

    def __init__(self, diameter_mm, center=None, beam_diameter=None):
        super().__init__(width_mm=diameter_mm, height_mm=diameter_mm, center=center, rotation_angle=None, beam_diameter=beam_diameter)
