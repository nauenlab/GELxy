import math
import matplotlib.pyplot as plt
from Coordinate import Coordinate


class Shape:

    def __init__(self, center, rotation_angle, beam_diameter, uses_step_coordinates):
        self.center = center if center else Coordinate(0, 0)
        self.rotation_angle = rotation_angle if rotation_angle else 0
        self.beam_diameter = beam_diameter if beam_diameter else 0.1
        self.uses_step_coordinates = uses_step_coordinates if uses_step_coordinates else False

    def plot(self):
        # subclasses must have the get_coordinates function
        coordinates = self.get_coordinates()
        plt.plot(coordinates.get_x_coordinates(), coordinates.get_y_coordinates())
        plt.axis('square')
        plt.show()

    @staticmethod
    def distance(x1, y1, x2, y2):
        xd = x2 - x1
        yd = y2 - y1
        return math.sqrt(xd ** 2 + yd ** 2)
