import math
import matplotlib.pyplot as plt
from tqdm import tqdm
import copy
from Constants import MOTOR_MAX_TRAVEL
from CuringCalculations import MIN_VELOCITY, MAX_VELOCITY

class Coordinate:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = None
        self.a = None
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
            pvf = MAX_VELOCITY

        return max(pvf, MIN_VELOCITY)

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
    
    def plot(self, plot_lines=True, plot_points=False, show=True):
        if plot_lines:
            plt.plot(self.get_x_coordinates(), self.get_y_coordinates())
        if plot_points:
            plt.plot(self.get_x_coordinates(), self.get_y_coordinates(), '.', color='black')
        
        plt.axis('square')
        if show:
            plt.show()
        
        return plt
        
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

    def update_with_configuration(self, configuration):
        prev = None
        for (i, v) in tqdm(enumerate(self), desc="Updating Coordinates with configuration"):
            if not prev:
                prev = self.coordinates[i]
                continue
            
            distance = self.distance(prev, self.coordinates[i])
            step_time = distance / configuration.velocity
            vmax = prev.get_vmax(to=self.coordinates[i], time=step_time)
            self.v.append(vmax)
            prev = self.coordinates[i]
            prev.v = vmax
            prev.a = configuration.current


    def normalize(self, center, rotation, configuration):
        original_coordinates = self.coordinates.copy()
        while configuration.iterations > 1:
            self.coordinates += original_coordinates
            configuration.iterations -= 1

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

        self.coordinates = self.fix_coordinates_with_corrected_slope()
        if len(self.coordinates) == 0:
            raise Exception("No coordinates to plot, check the shape dimensions and bounds.")
        
        self.update_with_configuration(configuration)
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
        c_cpy = copy.copy(self.coordinates)

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

        # filled_shape.plot()

        return filled_shape
    

    @staticmethod
    def calculate_intersection_with_slope(p1, p2, border):
        c_to_return = copy.deepcopy(p2)
        # Handle vertical lines
        if p1.x == p2.x:
            c_to_return.x = p1.x
            c_to_return.y = 0 if border == 'bottom' else MOTOR_MAX_TRAVEL
            return c_to_return
        # Handle horizontal lines
        elif p1.y == p2.y:
            c_to_return.x = 0 if border == 'left' else MOTOR_MAX_TRAVEL
            c_to_return.y = p1.y
            return c_to_return
        
        # Calculate slope
        m = (p2.y - p1.y) / (p2.x - p1.x)
        # Calculate y-intercept
        b = p1.y - m * p1.x

        
        if border in ['left', 'right']:
            x = 0 if border == 'left' else MOTOR_MAX_TRAVEL
            y = m * x + b
            c_to_return.x = x
            c_to_return.y = y
            return c_to_return
        else:  # 'top' or 'bottom'
            y = MOTOR_MAX_TRAVEL if border == 'top' else 0
            x = (y - b) / m
            c_to_return.x = x
            c_to_return.y = y
            return c_to_return

    def fix_coordinates_with_corrected_slope(self):
        fixed_coords = Coordinates()
        borders = {'left': 0, 'right': MOTOR_MAX_TRAVEL, 'top': MOTOR_MAX_TRAVEL, 'bottom': 0}
        for i in range(len(self.coordinates)):
            if i == 0:  # Add the first point if within bounds
                if 0 <= self.coordinates[i].x <= MOTOR_MAX_TRAVEL and 0 <= self.coordinates[i].y <= MOTOR_MAX_TRAVEL:
                    fixed_coords.append(self.coordinates[i])
                continue
            
            prev_coordinate = self.coordinates[i-1]
            current_coordinate = self.coordinates[i]
            
            # Check if the segment crosses any border
            for border, value in borders.items():
                if border in ['left', 'right']:
                    if (prev_coordinate.x < value < current_coordinate.x) or (current_coordinate.x < value < prev_coordinate.x):
                        intersection = self.calculate_intersection_with_slope(prev_coordinate, current_coordinate, border)
                        if 0 <= intersection.y <= MOTOR_MAX_TRAVEL:
                            fixed_coords.append(intersection)
                else:
                    if (prev_coordinate.y < value < current_coordinate.y) or (current_coordinate.y < value < prev_coordinate.y):
                        intersection = self.calculate_intersection_with_slope(prev_coordinate, current_coordinate, border)
                        if 0 <= intersection.x <= MOTOR_MAX_TRAVEL:
                            fixed_coords.append(intersection)
            
            # Add the second point if it's within bounds and no segment was added
            if 0 <= current_coordinate.x <= MOTOR_MAX_TRAVEL and 0 <= current_coordinate.y <= MOTOR_MAX_TRAVEL:
                fixed_coords.append(current_coordinate)
        
        return fixed_coords
