from Coordinate import Coordinate, Coordinates
import Constants
from multiprocessing import Pool
from copy import copy

class Texture:
    """
    Represents a texture of shapes arranged in a grid pattern.

    Attributes:
        shape (Shape): The shape to be repeated in the texture.
        rows (int): The number of rows in the texture grid.
        columns (int): The number of columns in the texture grid.
        spacing_mm (float): The spacing between shapes in millimeters.
        margins (float): The margins around the texture grid in millimeters.
        is_spacing (bool): Indicates whether spacing is used instead of rows and columns.

    Methods:
        get_coordinates(): Returns the coordinates of all shapes in the texture.
        append_coordinates(shape): Helper method to get coordinates of a single shape.
    """

    def __init__(self, shape, rows=None, columns=None, spacing_mm=None, margins=None):
        """
        Initializes a Texture object.

        Args:
            shape (Shape): The shape to be repeated in the texture.
            rows (int): The number of rows in the texture grid.
            columns (int): The number of columns in the texture grid.
            spacing_mm (float): The spacing between shapes in millimeters.
            margins (float): The margins around the texture grid in millimeters.

        Raises:
            Exception: If spacing or margins are specified when rows or columns are populated.
        """
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
        """
        Returns the coordinates of all shapes in the texture.

        Returns:
            Coordinates: The coordinates of all shapes in the texture.
        """
        if self.is_spacing:
            bound = Constants.MOTOR_MAX_TRAVEL
            coordinates = Coordinates()
            
            args = []
            x = 1
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
        """
        Helper method to get coordinates of a single shape.

        Args:
            shape (Shape): The shape to get coordinates for.

        Returns:
            Coordinates: The coordinates of the shape.
        """
        return shape.get_coordinates()

    