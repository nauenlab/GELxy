
import enum


class Coordinate:

    def __init__(self, x, y):
        self.x = x
        self.y = y


class Coordinates:

    def __init__(self, movement_type=None):
        self.x = []
        self.y = []
        self.coordinates = []
        self.movement_type = MovementType.absolute if not movement_type else movement_type
    
    def __iter__(self):
        self.a = 0
        return self

    def __next__(self):
        if self.a < len(self.coordinates):
            n = self.coordinates[self.a]
            self.a += 1
            return n
        else:
            raise StopIteration
    
    def __len__(self):
        return len(self.coordinates)

    def __getitem__(self, item):
         return self.coordinates[item]
    
    def __add__(lhs, rhs):
        new_coords = lhs
        new_coords.x += rhs.x
        new_coords.y += rhs.y
        new_coords.coordinates += rhs.coordinates
        return new_coords
        
    def append(self, coordinate):
        self.x.append(coordinate.x)
        self.y.append(coordinate.y)
        self.coordinates.append(coordinate)

    def get_x_coordinates(self):
        return self.x

    def get_y_coordinates(self):
        return self.y

    def normalize(self):
        min_x = min(self.get_x_coordinates())
        min_y = min(self.get_y_coordinates())

        factor_x = 0 if min_x > 0 else abs(min_x)
        factor_y = 0 if min_y > 0 else abs(min_y)

        for (i, v) in enumerate(self):
            self.x[i] = v.x + factor_x
            self.y[i] = v.y + factor_y
            self.coordinates[i].x = self.x[i]
            self.coordinates[i].y = self.y[i]

    def movements(self):
        if self.movement_type == MovementType.relative:
            prev_coordinate = Coordinate(0, 0)
            for i in self.coordinates:
                delta_x, delta_y = Coordinates.distance(prev_coordinate, i)
        elif self.movement_type == MovementType.absolute:
            print()

    @staticmethod
    def distance(c1, c2):
        delta_x = c2.x - c1.x
        delta_y = c2.y - c1.y

        return delta_x, delta_y


class MovementType(enum.Enum):
    absolute = 0
    relative = 1




