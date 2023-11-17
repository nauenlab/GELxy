import math
from Coordinate import Coordinate, Coordinates


class Shape:

    def __init__(self, center, rotation_angle, beam_diameter, uses_step_coordinates, filled):
        self.center = center if center else Coordinate(0, 0)
        self.rotation_angle = rotation_angle if rotation_angle else 0
        self.beam_diameter = beam_diameter if beam_diameter else 0.1
        self.uses_step_coordinates = uses_step_coordinates if uses_step_coordinates else False
        self.filled = filled if filled else False

    def plot(self):
        # subclasses must have the get_coordinates function
        coordinates = self.get_coordinates()
        coordinates.plot()

    def get_coordinates(self):
        if "__line_coordinates__" in dir(self):
            if "uses_step_coordinates" in dir(self) and self.uses_step_coordinates:
                return self.__step_coordinates__()
            return self.__line_coordinates__()
        elif "__radial_coordinates__" in dir(self):
            return self.__radial_coordinates__()
        else:
            raise Exception("Shape does not have a line or radial coordinate function")
    
    def __step_coordinates__(self):
        coordinates = Coordinates()
        resolution = 0.005
        line_coordinates = self.__line_coordinates__(raw=True)

        # Fill in the space between the coordinates linearly
        for i in range(len(line_coordinates) - 1):
            start_point = line_coordinates[i]
            end_point = line_coordinates[i + 1]
            num_points = int(self.distance(start_point.x, start_point.y, end_point.x, end_point.y) * (1 / resolution)) + 1
            for j in range(1, num_points):
                t = j / (num_points - 1)
                x = start_point.x + t * (end_point.x - start_point.x)
                y = start_point.y + t * (end_point.y - start_point.y)
                new_coord = Coordinate(x, y)
                if abs(new_coord.x - end_point.x) < resolution and abs(new_coord.y - end_point.y) < resolution:
                    coordinates.append_if_no_duplicate(end_point, self.beam_diameter)
                    continue

                coordinates.append_if_far_enough(new_coord, self.beam_diameter)
        
        if self.filled:
            coordinates = coordinates.fill(self.beam_diameter)

        coordinates.normalize(step_time=10, center=self.center, rotation=self.rotation_angle)
        return coordinates

    @staticmethod
    def distance(x1, y1, x2, y2):
        xd = x2 - x1
        yd = y2 - y1
        return math.sqrt(xd ** 2 + yd ** 2)

