from Coordinate import Coordinate, Coordinates


class Texture:

    def __init__(self, shape, spacing, is_staggered=False):
        self.shape = shape
        self.spacing = spacing
        self.is_staggered = is_staggered

    def get_coordinates(self):
        coordinates = Coordinates()
        shape_coordinates = self.shape.get_coordinates()

        le = -5
        r = 15
        u = -5
        d = 15
        resolution = self.beam_diameter



        return coordinates
