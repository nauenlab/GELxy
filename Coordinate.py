import math
import matplotlib.pyplot as plt
from tqdm import tqdm

class Coordinate:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = None
        self.lp = True

    def get_vmax(self, to, time):
        xi, yi = self.x, self.y
        xf, yf = to.x, to.y
        return self.__calculate_vmax__(xi, xf, time), self.__calculate_vmax__(yi, yf, time)

    @staticmethod
    def __calculate_vmax__(i, f, t):
        d = math.fabs(f - i)
        a = 4.0
        try:
            pvf = a * t - a * (math.sqrt(t ** 2 - ((2 * d) / a)))
        except ValueError:
            pvf = 2.6

        # seems like 0.005 is the minimum velocity (value found by testing)
        return max(pvf, 0.005)

    def __str__(self):
        return f"\nx: {self.x}\ny: {self.y}\nv: {self.v}\nl: {self.lp}"

    def same_location_as(self, coord):
        return self.x == coord.x and self.y == coord.y


class Coordinates:

    def __init__(self):
        self.x = []
        self.y = []
        self.coordinates = []
        self.v = []
    
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
    
    def __add__(self, rhs):
        new_coords = self
        new_coords.x += rhs.x
        new_coords.y += rhs.y
        new_coords.coordinates += rhs.coordinates
        return new_coords
    
    def plot(self, plot_lines=True, plot_points=False):
        if plot_lines:
            plt.plot(self.get_x_coordinates(), self.get_y_coordinates())
        if plot_points:
            plt.plot(self.get_x_coordinates(), self.get_y_coordinates(), '.', color='black')
        
        plt.axis('square')
        plt.show()
        
    def append(self, coordinate):
        self.x.append(coordinate.x)
        self.y.append(coordinate.y)
        self.coordinates.append(coordinate)

    def append_if_far_enough(self, coord, beam_diameter):
        if len(self) != 0:
            prev = self[-1]
            if self.distance(coord, prev) >= beam_diameter:
                self.append(coord)
        else:
            self.append(coord)
    
    def append_if_far_enough_field(self, coord, beam_diameter):
        if len(self) != 0:
            for i in self:
                if self.distance(coord, i) < beam_diameter:
                    return
            self.append(coord)
        else:
            self.append(coord)
    
    def append_if_no_duplicate(self, coord, beam_diameter):
        if len(self) != 0:
            prev = self[-1]
            if not prev.same_location_as(coord):
                if self.distance(coord, prev) < beam_diameter / 4:
                    self.coordinates[-1] = coord
                else:
                    self.append(coord)
        else:
            self.append(coord)

    def get_x_coordinates(self):
        return self.x

    def get_y_coordinates(self):
        return self.y

    def __calculate_velocities__(self, step_time):
        prev = None
        for (i, v) in tqdm(enumerate(self), desc="Calculating Velocities"):
            if not prev:
                prev = self.coordinates[i]
                continue

            vmax = prev.get_vmax(to=self.coordinates[i], time=step_time)
            self.v.append(vmax)
            prev = self.coordinates[i]
            prev.v = vmax

    def normalize(self, step_time, center, rotation):
        min_x = min(self.get_x_coordinates())
        min_y = min(self.get_y_coordinates())

        factor_x = 0 if min_x > 0 else abs(min_x)
        factor_y = 0 if min_y > 0 else abs(min_y)

        for (i, v) in tqdm(enumerate(self), desc="Normalizing"):
            self.x[i] = v.x + factor_x
            self.y[i] = v.y + factor_y
            self.coordinates[i].x = self.x[i]
            self.coordinates[i].y = self.y[i]

        centroid = self.__get_centroid__()
        for (i, v) in tqdm(enumerate(self), desc="Calculating Transformations"):
            r_transformation = self.rotation_transformation(v, rotation, centroid)
            self.x[i] = v.x + (center.x - centroid.x) + r_transformation.x
            self.y[i] = v.y + (center.y - centroid.y) + r_transformation.y
            self.coordinates[i].x = self.x[i]
            self.coordinates[i].y = self.y[i]

        self.__calculate_velocities__(step_time)
        self.coordinates[0].lp = False

    @staticmethod
    def rotation_transformation(c, rotation, centroid):
        delta_x = c.x - centroid.x
        delta_y = c.y - centroid.y
        cos_theta = math.cos(rotation)
        sin_theta = math.sin(rotation)

        new_x = delta_x * cos_theta - delta_y * sin_theta + centroid.x
        new_y = delta_x * sin_theta + delta_y * cos_theta + centroid.y

        return Coordinate(new_x - c.x, new_y - c.y)

    def __get_centroid__(self):
        sum_x = 0
        sum_y = 0
        closed = False

        if self[0].x == self[-1].x and self[0].y == self[-1].y:
            closed = True

        l_coords = len(self)
        for (i, c) in enumerate(self):
            if i + 1 == l_coords and closed:
                l_coords -= 1
                continue
            sum_x += c.x
            sum_y += c.y

        return Coordinate(sum_x / l_coords, sum_y / l_coords)

    @staticmethod
    def distance(c1, c2):
        delta_x = c2.x - c1.x
        delta_y = c2.y - c1.y

        return math.sqrt(delta_x ** 2 + delta_y ** 2)
    
    def is_inside_polygon(self, point):
        """
        Returns True if the given point is inside the polygon, False otherwise.
        """
        # Check if the point is outside the bounding box of the polygon
        min_x = min(self.get_x_coordinates())
        max_x = max(self.get_x_coordinates())
        min_y = min(self.get_y_coordinates())
        max_y = max(self.get_y_coordinates())
        if point.x < min_x or point.x > max_x or point.y < min_y or point.y > max_y:
            return False

        # Count the number of intersections between the polygon and a horizontal line
        # that starts from the point and goes to the right
        count = 0
        for i in range(len(self)):
            p1 = self[i]
            p2 = self[(i + 1) % len(self)]
            if point.y < min(p1.y, p2.y) or point.y > max(p1.y, p2.y):
                continue
            if point.x >= max(p1.x, p2.x):
                continue
            if point.x < min(p1.x, p2.x):
                count += 1
                continue
            if p1.x == p2.x:
                continue
            slope = (p2.y - p1.y) / (p2.x - p1.x)
            if slope == 0:
                continue
            x_intersect = p1.x + (point.y - p1.y) / slope 
            if point.x < x_intersect:
                count += 1

        return count % 2 == 1
    
    def is_point_inside_shape(self, p):
        # Check if a point is inside a shape using ray-casting algorithm
        # Reference: https://wrf.ecse.rpi.edu/Research/Short_Notes/pnpoly.html
        num_coords = len(self.coordinates)
        inside = False

        for i in range(num_coords):
            j = (i + 1) % num_coords
            if ((self.coordinates[i].y > p.y) != (self.coordinates[j].y > p.y) and
                p.x < (self.coordinates[j].x - self.coordinates[i].x) * (p.y - self.coordinates[i].y) /
                (self.coordinates[j].y - self.coordinates[i].y) + self.coordinates[i].x):
                inside = not inside

        return inside

    def fill(self, beam_diameter):
        """
        Returns an array of Coordinate objects that represents the filled shape.
        """

        # Find the bounding box of the shape
        min_x = min(self.get_x_coordinates())
        max_x = max(self.get_x_coordinates())
        min_y = min(self.get_y_coordinates())
        max_y = max(self.get_y_coordinates())
        c_cpy = self.coordinates.copy()

        # Create a grid of points inside the bounding box
        resolution = beam_diameter / 2
        
        points = Coordinates()
        for x in range(int(min_x / resolution) - 1, int(max_x / resolution)):
            if x % 2 == 0:
                range_y = range(int(min_y / resolution) - 1, int(max_y / resolution) + 1)
            else:
                range_y = range(int(max_y / resolution), int(min_y / resolution) - 2, -1)
    
            x = float(x) * resolution
            for y in range_y:
                y = float(y) * resolution
                points.append(Coordinate(x, y))
            
        # Check which points are inside the shape
        filled_shape = Coordinates()
        for point in points:
            if self.is_point_inside_shape(point):
                filled_shape.append(point)

        c_cpy[0].lp = False
        for c in c_cpy:
            filled_shape.append(c)

        filled_shape.plot()

        return filled_shape
    
