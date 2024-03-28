from Coordinate import Coordinate, Coordinates
import Constants
from multiprocessing import Pool
from copy import copy

class Texture:

    def __init__(self, shape, rows=None, columns=None, spacing_mm=None, margins=None):
        self.shape = shape
        self.rows = rows
        self.columns = columns
        self.spacing = spacing_mm
        self.margins = margins

        self.is_spacing = spacing_mm is not None
        if (self.rows or self.columns) and (self.spacing or self.margins):
            raise Exception("Cannot specify spacing or margins when rows or columns are populated")
        
        if not self.margins:
            self.margins = spacing_mm

    def get_coordinates(self):
        if self.is_spacing:
            bound = Constants.MOTOR_MAX_TRAVEL
            coordinates = Coordinates()
            
            args = []
            x = 0
            y = 0
            while True:
                x_spacing = self.margins + (x * self.spacing)
                y_spacing = self.margins + (y * self.spacing)
                if x_spacing > bound - self.margins:
                    x_spacing = self.margins
                    x =  0
                    y += 1
                if y_spacing > bound - self.margins:
                    break
                
                self.shape.center = Coordinate(x_spacing, y_spacing)
                shape_copy = copy(self.shape)
                args.append(shape_copy)
                x += 1

            with Pool() as pool:
                for result in pool.map(self.append_coordinates, args):
                    coordinates += result
            
            return coordinates
        else:
            bound = Constants.MOTOR_MAX_TRAVEL
            coordinates = Coordinates()
            x_dist = (bound / self.rows) / 2
            y_dist = (bound / self.rows) / 2
            
            args = []
            for i in range(self.rows):
                for j in range(self.columns):
                    x = x_dist * (i) + x_dist
                    y = y_dist * (j) + y_dist
                    self.shape.center = Coordinate(x, y)
                    shape_copy = copy(self.shape)
                    args.append(shape_copy)

            with Pool() as pool:
                for result in pool.map(self.append_coordinates, args):
                    coordinates += result
            
            return coordinates

    def append_coordinates(self, shape):
        return shape.get_coordinates()

    