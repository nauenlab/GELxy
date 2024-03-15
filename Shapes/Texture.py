from Coordinate import Coordinate, Coordinates
import Constants
import multiprocessing
from multiprocessing import Pool
from gbl import handle_processes
from copy import copy

class Texture:

    def __init__(self, shape, rows, columns):
        self.shape = shape
        self.rows = rows
        self.columns = columns

    def get_coordinates(self):
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
                print("RAMBAUG", result)
                coordinates += result
        
        return coordinates

    def append_coordinates(self, shape):
        return shape.get_coordinates()

    