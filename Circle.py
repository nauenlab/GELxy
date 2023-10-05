
import math
from Shape import Shape
from Coordinate import Coordinate, Coordinates


class Circle(Shape):

    def __init__(self, diameter_mm, step_size):
        super().__init__()
        self.diameter = float(diameter_mm)
        self.radius = float(diameter_mm) / 2
        self.step_size = step_size # mm
        
    def get_coordinates(self):
        return self.__radial_coordinates__()

    def __linear_coordinates__(self):
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
    
    def __radial_coordinates__(self):
       coordinates = Coordinates()
       x_pos1 = math.cos(math.radians(0))
       y_pos1 = math.sin(math.radians(0))
       for i in range(360):
           x_pos = math.cos(math.radians(i))
           y_pos = math.sin(math.radians(i))

           x_pos2 = (x_pos - x_pos1) * self.radius
           y_pos2 = (y_pos - y_pos1) * self.radius
           c = Coordinate(x_pos2, y_pos2)
           coordinates.append(c)

       coordinates.normalize()
       return coordinates

