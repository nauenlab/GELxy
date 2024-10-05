import math
import matplotlib.pyplot as plt
from tqdm import tqdm
import copy
from shapely.geometry import Polygon
from shapely.geometry.polygon import orient
from Constants import MOTOR_MAX_TRAVEL, MINIMUM_VELOCITY, MAXIMUM_VELOCITY, ACCELERATION, MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS
from CuringCalculations import curing_calculations, Configuration
from decimal import Decimal, getcontext, InvalidOperation

getcontext().prec = 15

class Coordinate:
    """
    Represents a coordinate point in a 2D space.
    """

    def __init__(self, x, y):
        """
        Initializes a Coordinate object with the given x and y values.

        Args:
            x (float): The x-coordinate value.
            y (float): The y-coordinate value.
        """
        self.x = Decimal(x)
        self.y = Decimal(y)
        self.v = None
        self.a = None
        self.lp = True

    def get_velocity(self, to, time):
        """
        Calculates the maximum velocity for a movement from this coordinate to another coordinate within a given time.

        Args:
            to (Coordinate): The destination coordinate.
            time (Decimal): The time duration for the movement.

        Returns:
            tuple: A tuple containing the maximum velocity in the x-direction and y-direction.
        """
        xi, yi = self.x, self.y
        xf, yf = to.x, to.y
        return float(self.__calculate_velocity__(xi, xf, time).__round__(10)), float(self.__calculate_velocity__(yi, yf, time).__round__(10))
    
    @staticmethod
    def __calculate_velocity__(i, f, t):
        """
        Calculates the maximum velocity for a movement from a starting position to a final position within a given time.

        Args:
            i (Decimal): The initial position.
            f (Decimal): The final position.
            t (Decimal): The time duration for the movement.

        Returns:
            float: The maximum velocity.
        """
        d = (f - i).__abs__()
        a = Decimal(ACCELERATION)
        try:
            pvf = a * t - a * (t ** 2 - ((2 * d) / a)).sqrt()
        except InvalidOperation:
            pvf = Decimal(MAXIMUM_VELOCITY)
        
        return pvf
    
    def movement_time(self, to):
        """
        Calculates the time required to move from this coordinate to another coordinate with a given velocity.

        Args:
            _from (Coordinate): The starting coordinate.
            to (Coordinate): The destination coordinate.

        Returns:
            float: The time duration for the movement.
        """
        x_velocity, y_velocity = to.v if to.v else (MAXIMUM_VELOCITY, MAXIMUM_VELOCITY)
        xi, yi = self.x, self.y
        xf, yf = to.x, to.y
        
        v = 0
        if x_velocity != 0:
            d = math.fabs(xf - xi)
            v = x_velocity
        if y_velocity != 0:
            d = math.fabs(yf - yi) 
            v = y_velocity
            
        return float(self.__calculate_movement_time__(Decimal(v), Decimal(d)))
    
    @staticmethod
    def __calculate_movement_time__(v, d):
        """
        Calculates the time required to move a distance with a given velocity.
        
        Args:
            v (Decimal): The velocity.
            d (Decimal): The distance to move.
            
        Returns:
            Decimal: The time required to move the distance.
        """
        if d <= v**2/(2*v):
            return (2*d/Decimal(ACCELERATION)).sqrt()
        else:
            return (d/v) + (v/(2*Decimal(ACCELERATION)))

    def __str__(self):
        """
        Returns a string representation of the Coordinate object.

        Returns:
            str: The string representation of the Coordinate object.
        """
        return f"\nx: {self.x}\ny: {self.y}\nv: {self.v}\nl: {self.lp}\na: {self.a}\n"

    def __repr__(self):
        """
        Returns a string representation of the Coordinate object.

        Returns:
            str: The string representation of the Coordinate object.
        """
        return self.__str__()

    def same_location_as(self, coord):
        """
        Checks if this Coordinate object has the same location as another Coordinate object.

        Args:
            coord (Coordinate): The other Coordinate object to compare with.

        Returns:
            bool: True if the coordinates are the same, False otherwise.
        """
        return self.x == coord.x and self.y == coord.y


class Coordinates:
    """
    Represents a collection of Coordinate objects.
    """

    def __init__(self):
        """
        Initializes an empty Coordinates object.
        """
        self.x = []
        self.y = []
        self.coordinates = []
        self.v = []

    def __str__(self):
        """
        Returns a string representation of the Coordinates object.

        Returns:
            str: The string representation of the Coordinates object.
        """
        return '\n'.join([str(coord) for coord in self.coordinates])

    def __repr__(self):
        """
        Returns a string representation of the Coordinates object.

        Returns:
            str: The string representation of the Coordinates object.
        """
        return self.__str__()
    
    def __iter__(self):
        """
        Returns an iterator object for iterating over the Coordinates object.

        Returns:
            iterator: An iterator object.
        """
        self.n = 0
        return self

    def __next__(self):
        """
        Returns the next Coordinate object in the iteration.

        Returns:
            Coordinate: The next Coordinate object.

        Raises:
            StopIteration: If there are no more Coordinate objects to iterate over.
        """
        if self.n < len(self.coordinates):
            next = self.coordinates[self.n]
            self.n += 1
            return next
        else:
            raise StopIteration
    
    def __len__(self):
        """
        Returns the number of Coordinate objects in the Coordinates object.

        Returns:
            int: The number of Coordinate objects.
        """
        return len(self.coordinates)

    def __getitem__(self, item):
        """
        Returns the Coordinate object at the specified index.

        Args:
            item (int): The index of the Coordinate object.

        Returns:
            Coordinate: The Coordinate object at the specified index.
        """
        return self.coordinates[item]
    
    def __add__(self, rhs):
        """
        Concatenates two Coordinates objects.

        Args:
            rhs (Coordinates): The Coordinates object to concatenate with.

        Returns:
            Coordinates: A new Coordinates object that is the concatenation of the two Coordinates objects.
        """
        new_coords = self
        new_coords.x += rhs.x
        new_coords.y += rhs.y
        new_coords.coordinates += rhs.coordinates
        return new_coords
    
    def remove(self, index):
        """
        Removes the Coordinate object at the specified index.

        Args:
            index (int): The index of the Coordinate object to remove.
        """
        self.x.pop(index)
        self.y.pop(index)
        self.coordinates.pop(index)
        self.v.pop(index)
    
    def clear(self):
        """
        Clears the Coordinates object.
        """
        self.x = []
        self.y = []
        self.coordinates = []
        self.v = []
    
    def plot(self, plot_lines=True, plot_points=False, show=True):
        """
        Plots the coordinates on a 2D graph.

        Args:
            plot_lines (bool, optional): Whether to plot lines connecting the coordinates. Defaults to True.
            plot_points (bool, optional): Whether to plot points at the coordinates. Defaults to False.
            show (bool, optional): Whether to display the plot. Defaults to True.

        Returns:
            matplotlib.pyplot: The plot object.
        """
        if plot_lines:
            plt.plot(self.get_x_coordinates(), self.get_y_coordinates())
        if plot_points:
            plt.plot(self.get_x_coordinates(), self.get_y_coordinates(), '.', color='black')
        
        plt.axis('square')
        if show:
            plt.show()
        
        return plt
        
    def append(self, coordinate):
        """
        Appends a Coordinate object to the Coordinates object.

        Args:
            coordinate (Coordinate): The Coordinate object to append.
        """
        self.x.append(coordinate.x)
        self.y.append(coordinate.y)
        self.v.append(coordinate.v)
        self.coordinates.append(coordinate)

    def append_if_far_enough(self, coord):
        """
        Appends a Coordinate object to the Coordinates object if it is far enough from the previous coordinate.

        Args:
            coord (Coordinate): The Coordinate object to append.
        """
        if len(self) != 0:
            prev = self[-1]
            if self.distance(coord, prev) >= MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS:
                self.append(coord)
        else:
            self.append(coord)
    
    def append_if_far_enough_field(self, coord):
        """
        Appends a Coordinate object to the Coordinates object if it is far enough from all existing coordinates.

        Args:
            coord (Coordinate): The Coordinate object to append.
        """
        if len(self) != 0:
            for i in self:
                if self.distance(coord, i) < MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS:
                    return
            self.append(coord)
        else:
            self.append(coord)
    
    def append_if_no_duplicate(self, coord):
        """
        Appends a Coordinate object to the Coordinates object if it is not a duplicate and is close enough to the previous coordinate.

        Args:
            coord (Coordinate): The Coordinate object to append.
        """
        if len(self) != 0:
            prev = self[-1]
            if not prev.same_location_as(coord):
                if self.distance(coord, prev) < MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS / 2:
                    self.coordinates[-1] = coord
                else:
                    self.append(coord)
        else:
            self.append(coord)

    def get_x_coordinates(self):
        """
        Returns a list of x-coordinates of the Coordinate objects.

        Returns:
            list: A list of x-coordinates.
        """
        return self.x

    def get_y_coordinates(self):
        """
        Returns a list of y-coordinates of the Coordinate objects.

        Returns:
            list: A list of y-coordinates.
        """
        return self.y
    
    def add_velocity_and_current_to_coordinates(self, stiffness, coordinates, beam_diameter_mm):
        """
        Adds velocity and current values to the Coordinate objects.

        Args:
            stiffness (float): The stiffness in Pascals of the shape.
            coordinates (Coordinates): The Coordinate objects to add velocity and current values to.
            beam_diameter_mm (float): The diameter of the beam.
        """
        resolved_coordinates = Coordinates()
        resolved_coordinates.append(coordinates[0])
        
        # get the resolved configuration for each coordinate
        configuration = [Configuration(beam_diameter=beam_diameter_mm)]
        velocities = [None]
        prev = coordinates[0]
        for curr in coordinates[1:]:
            vx, vy = -1, -1
            while not ((MINIMUM_VELOCITY <= vx <= MAXIMUM_VELOCITY or vx == 0.0) and (MINIMUM_VELOCITY <= vy <= MAXIMUM_VELOCITY or vy == 0.0)):
                if vy >= MAXIMUM_VELOCITY:
                    curr.x = prev.x
                elif vx >= MAXIMUM_VELOCITY:
                    curr.y = prev.y

                min_distance = min([i for i in [(prev.x - curr.x).__abs__(), (prev.y - curr.y).__abs__()] if i != 0])
                step_time = Coordinate.__calculate_movement_time__(Decimal(MINIMUM_VELOCITY), min_distance)
                vx, vy = prev.get_velocity(to=curr, time=step_time)

            configuration.append(curing_calculations.get_resolved_configuration_from_velocities(vx, vy, stiffness, beam_diameter_mm))

            velocities.append((vx, vy))
            resolved_coordinates.append(curr)
            prev = copy.deepcopy(curr)

        # The value of iterations that all configurations have in common
        base_iterations = min([i.iterations for i in configuration[1:]])

        # Add velocity and current values to the coordinates and resolve the iterations
        for i in range(len(resolved_coordinates)):
            resolved_coordinates[i].v = velocities[i]
            resolved_coordinates[i].a = configuration[i].current
            configuration[i].iterations -= base_iterations

        # Copy the coordinates based on the base_iterations
        original_coordinates = copy.deepcopy(resolved_coordinates)
        for i in range(base_iterations - 1):
            copy_to_add = copy.deepcopy(original_coordinates)
            copy_to_add[0].lp = False
            if copy_to_add[0].same_location_as(resolved_coordinates[-1]):
                copy_to_add.remove(0)

            resolved_coordinates += copy_to_add

        # Resolve the remaining iterations
        last = copy.deepcopy(original_coordinates[0])
        for i in range(1, len(original_coordinates)):
            if configuration[i].iterations > 0 and not last.same_location_as(original_coordinates[i]):
                resolved_coordinates.append(copy.deepcopy(original_coordinates[i]))
                resolved_coordinates[-1].lp = False

            while configuration[i].iterations > 0:
                prev = copy.deepcopy(original_coordinates[i - 1])
                curr = copy.deepcopy(original_coordinates[i])

                if configuration[i].iterations == 1:
                    prev.lp = False
                    configuration[i].iterations -= 1
                else:
                    prev.a = curr.a
                    prev.v = curr.v
                    prev.lp = curr.lp
                    configuration[i].iterations -= 2

                resolved_coordinates.append(prev)
                resolved_coordinates.append(curr)
                
                last = curr
        
        self.clear()
        for c in resolved_coordinates:
            self.append(c)

    def normalize(self, center, rotation, stiffness, beam_diameter_mm):
        """
        Normalizes the Coordinate objects by translating and rotating them.

        Args:
            center (Coordinate): The center coordinate for normalization.
            rotation (float): The rotation angle in radians.
            stiffness (float): The stiffness in Pascals of the shape.
        """

        min_x = min(self.get_x_coordinates())
        min_y = min(self.get_y_coordinates())
        factor_x = 0 if min_x > 0 else abs(min_x)
        factor_y = 0 if min_y > 0 else abs(min_y)

        for (i, v) in tqdm(enumerate(self), desc="Normalizing"):
            self.x[i] = v.x + factor_x
            self.y[i] = v.y + factor_y
            self.coordinates[i].x = self.x[i]
            self.coordinates[i].y = self.y[i]
        
        self.rotate_coordinates(center, rotation)

        self.coordinates = self.fix_coordinates_with_corrected_slope()
        if len(self.coordinates) == 0:
            raise Exception("No coordinates to plot, check the shape dimensions and bounds.")
        
        self.add_velocity_and_current_to_coordinates(stiffness=stiffness, coordinates=self.coordinates, beam_diameter_mm=beam_diameter_mm)
        self.coordinates[0].lp = False

    def rotate_coordinates(self, center, rotation):
        centroid = self.get_centroid()
        for (i, v) in tqdm(enumerate(self), desc="Calculating Transformations"):
            r_transformation = self.rotation_transformation(v, rotation, centroid)
            self.x[i] = v.x + (center.x - centroid.x) + r_transformation.x
            self.y[i] = v.y + (center.y - centroid.y) + r_transformation.y
            self.coordinates[i].x = self.x[i]
            self.coordinates[i].y = self.y[i]

    @staticmethod
    def rotation_transformation(c, rotation, centroid):
        """
        Applies a rotation transformation to a Coordinate object.

        Args:
            c (Coordinate): The Coordinate object to transform.
            rotation (float): The rotation angle in radians.
            centroid (Coordinate): The centroid coordinate.

        Returns:
            Coordinate: The transformed Coordinate object.
        """
        delta_x = c.x - centroid.x
        delta_y = c.y - centroid.y
        rotation = math.radians(rotation)
        cos_theta = Decimal(math.cos(rotation))
        sin_theta = Decimal(math.sin(rotation))

        new_x = delta_x * cos_theta - delta_y * sin_theta + centroid.x
        new_y = delta_x * sin_theta + delta_y * cos_theta + centroid.y

        return Coordinate(new_x - c.x, new_y - c.y)

    def get_centroid(self):
        """
        Calculates the centroid of the Coordinate objects.

        Returns:
            Coordinate: The centroid coordinate.
        """
        sum_x = 0
        sum_y = 0
        closed = False

        if self[0].x == self[-1].x and self[0].y == self[-1].y:
            closed = True

        l_coords = len(self)
        for (i, c) in enumerate(self):
            if not c.lp or (i + 1 == l_coords and closed):
                l_coords -= 1
                continue
            sum_x += c.x
            sum_y += c.y

        return Coordinate(sum_x / l_coords, sum_y / l_coords)

    @staticmethod
    def distance(c1, c2):
        """
        Calculates the Euclidean distance between two Coordinate objects.

        Args:
            c1 (Coordinate): The first Coordinate object.
            c2 (Coordinate): The second Coordinate object.

        Returns:
            float: The Euclidean distance between the two Coordinate objects.
        """
        delta_x = c2.x - c1.x
        delta_y = c2.y - c1.y

        return (delta_x ** 2 + delta_y ** 2).sqrt()
    
    def is_inside_polygon(self, point):
        """
        Checks if a point is inside the polygon defined by the Coordinate objects.

        Args:
            point (Coordinate): The point to check.

        Returns:
            bool: True if the point is inside the polygon, False otherwise.
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
        """
        Checks if a point is inside the shape defined by the Coordinate objects using the ray-casting algorithm.

        Args:
            p (Coordinate): The point to check.

        Returns:
            bool: True if the point is inside the shape, False otherwise.
        """
        num_coords = len(self.coordinates)
        inside = False

        for i in range(num_coords):
            j = (i + 1) % num_coords
            if ((self.coordinates[i].y > p.y) != (self.coordinates[j].y > p.y) and
                p.x < (self.coordinates[j].x - self.coordinates[i].x) * (p.y - self.coordinates[i].y) /
                (self.coordinates[j].y - self.coordinates[i].y) + self.coordinates[i].x):
                inside = not inside

        return inside

    def fill(self, uses_step_coordinates=False):
        """
        Fills the shape defined by the Coordinate objects with points.

        Returns:
            Coordinates: An array of Coordinate objects representing the filled shape.
        """
        # Convert shape's coordinates to a shapely Polygon
        coordinates = [(coord.x, coord.y) for coord in self.coordinates]

        original_polygon = Polygon(coordinates)
        original_polygon = orient(original_polygon, sign=1.0)  # Ensure consistent orientation

        # Initialize variables
        distance = 0
        offset_polygons = []

        # Generate inward offsets until the polygon disappears
        while True:
            offset_polygon = original_polygon.buffer(-distance)
            if offset_polygon.is_empty:
                break
            if offset_polygon.geom_type == 'MultiPolygon':
                # Handle cases where the offset results in multiple polygons
                offset_polygon = max(offset_polygon.geoms, key=lambda p: p.area)
            offset_polygons.append(offset_polygon)
            distance += MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS

        # Collect points from all offset polygons
        points = Coordinates()
        for poly in offset_polygons:
            x, y = poly.exterior.coords.xy
            for i, (xi, yi) in enumerate(zip(x, y)):
                c = Coordinate(xi, yi)
                c.lp = (i != 0)
                points.append(c)
        
        if uses_step_coordinates:
            points = points.fill_line_segments()

        return points
    
    def fill_line_segments(self):
        """
        Fills the shape defined by the Coordinate objects with points using step coordinates.

        Returns:
            Coordinates: An array of Coordinate objects representing the filled line segments.
        """
        filled_coords = Coordinates()
        resolution = 0.005

        for i in range(len(self) - 1):
            start_point = self[i]
            end_point = self[i + 1]
            num_points = int(self.distance(start_point, end_point) * Decimal(1 / resolution)) + 1
            for j in range(1, num_points):
                t = Decimal(j / (num_points - 1))
                x = start_point.x + t * (end_point.x - start_point.x)
                y = start_point.y + t * (end_point.y - start_point.y)
                new_coord = Coordinate(x, y)
                new_coord.lp = end_point.lp
                if abs(new_coord.x - end_point.x) < resolution and abs(new_coord.y - end_point.y) < resolution:
                    filled_coords.append_if_no_duplicate(end_point)
                    continue

                filled_coords.append_if_far_enough(new_coord)
        
        return filled_coords

    @staticmethod
    def calculate_intersection_with_slope(p1, p2, border):
        """
        Calculates the intersection point between a line segment defined by two points (p1 and p2)
        and a border (left, right, top, or bottom) of a rectangular region.

        Parameters:
        - p1 (Point): The first point of the line segment.
        - p2 (Point): The second point of the line segment.
        - border (str): The border of the rectangular region where the intersection point is calculated.
                                        Possible values: 'left', 'right', 'top', 'bottom'.

        Returns:
        - c_to_return (Point): The intersection point.

        Notes:
        - If the line segment is vertical, the intersection point will have the same x-coordinate as p1.x
            and the y-coordinate will be 0 if border is 'bottom', or MOTOR_MAX_TRAVEL if border is 'top'.
        - If the line segment is horizontal, the intersection point will have the same y-coordinate as p1.y
            and the x-coordinate will be 0 if border is 'left', or MOTOR_MAX_TRAVEL if border is 'right'.
        - If the line segment is neither vertical nor horizontal, the intersection point will be calculated
            using the slope-intercept form of a line equation: y = mx + b, where m is the slope and b is the y-intercept.
            The x-coordinate of the intersection point will be 0 if border is 'left', or MOTOR_MAX_TRAVEL if border is 'right'.
            The y-coordinate of the intersection point will be 0 if border is 'bottom', or MOTOR_MAX_TRAVEL if border is 'top'.

        """
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
        """
        Fixes the coordinates that are out of bounds by adding intersection points with the borders based on the corrected slope.
        
        Returns:
            fixed_coords (Coordinates): The fixed coordinates with added intersection points.
        """
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
