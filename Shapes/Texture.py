from Coordinate import Coordinate, Coordinates
import Constants

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
        for i in range(self.rows):
            for j in range(self.columns):
                x = x_dist * (i) + x_dist
                y = y_dist * (j) + y_dist
                self.shape.center = Coordinate(x, y)
                coordinates += self.shape.get_coordinates()

        return coordinates
