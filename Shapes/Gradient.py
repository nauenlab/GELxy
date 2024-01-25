from Coordinate import Coordinate, Coordinates
from tqdm import tqdm

class Gradient:

    def __init__(self, min_velocity, max_velocity, beam_diameter, is_horizontal=True, is_reversed=True):
        self.is_horizontal = is_horizontal
        self.min_velocity = min_velocity
        self.max_velocity = max_velocity
        self.is_reversed = is_reversed
        self.beam_diameter = beam_diameter

    def get_coordinates(self):
        coordinates = Coordinates()
        le = -5
        r = 15
        u = -5
        d = 15
        resolution = self.beam_diameter
        for i in tqdm(range(0, int(d * (1 / resolution)) + 1, int(resolution * (1 / resolution))), desc="Getting Coordinates"):
            i = float(i) / (1 / resolution)
            if self.is_horizontal:
                coordinates.append(Coordinate(i, u))
                coordinates.append(Coordinate(i, d))
            else:
                coordinates.append(Coordinate(le, i))
                coordinates.append(Coordinate(r, i))

        velocity_step = float(self.max_velocity - self.min_velocity)/len(coordinates)
        cur_v = self.min_velocity
        if self.is_reversed:
            coordinates.coordinates.reverse()
        first = True
        for coordinate in coordinates:
            if first:
                coordinate.lp = False
            first = not first
            coordinate.v = (cur_v, cur_v)
            cur_v += velocity_step

        return coordinates
