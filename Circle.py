
import math
from Shape import Shape
from Coordinate import Coordinate, Coordinates


class Circle(Shape):

    def __init__(self, diameter, step_size):
        super().__init__()
        self.diameter = float(diameter)
        self.radius = float(diameter) / 2
        self.step_size = step_size # mm

    def get_coordinates(self):
        upper_coordinates = Coordinates()
        lower_coordinates = Coordinates()
        x_pos1 = math.cos(0)
        y_pos1 = math.sin(0)
        
        x_val = 0.0
        while x_val < self.diameter:
            x_pos = (x_val / self.radius) - x_pos1
            rads = math.acos(x_pos)
            y_pos = math.sin(rads)
            y_pos2 = (y_pos - y_pos1) * self.radius
            
            c = Coordinate(x_val, y_pos2)
            c2 = Coordinate(self.diameter - x_val, -y_pos2)
            upper_coordinates.append(c)
            lower_coordinates.append(c2)
            
            x_val += self.step_size
        
        coordinates = upper_coordinates + lower_coordinates
        coordinates.normalize()
        
        return coordinates

