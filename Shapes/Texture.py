from Coordinate import Coordinate, Coordinates


class Texture:

    def __init__(self, shape, rows, columns, is_staggered=False):
        self.shape = shape
        self.rows = rows
        self.columns = columns
        self.is_staggered = is_staggered

    def get_coordinates(self):
        coordinates = Coordinates()
        for i in range(self.rows):
            for j in range(self.columns):
                if self.is_staggered and i % 2 == 1:
                    x = i * self.shape.width
                else:
                    x = i * self.shape.width
                y = j * self.shape.height
                self.shape.center = Coordinate(x, y)
                coordinates.append(self.shape.get_coordinates())

        return coordinates
