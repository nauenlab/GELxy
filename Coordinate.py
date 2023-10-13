import math


class Coordinate:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.v = None

    def get_vmax(self, to, time):
        xi, yi = self.x, self.y
        xf, yf = to.x, to.y
        return self.__calculate_vmax__(xi, xf, time), self.__calculate_vmax__(yi, yf, time)

    @staticmethod
    def __calculate_vmax__(i, f, t):
        d = math.fabs(f - i)
        a = 4.0

        # pvf2 = a * t + a * (math.sqrt(t ** 2 - ((2 * d) / a)))
        pvf = a * t - a * (math.sqrt(t ** 2 - ((2 * d) / a)))
        return pvf


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

    def get_x_coordinates(self):
        return self.x

    def get_y_coordinates(self):
        return self.y

    def __calculate_velocities__(self, step_time):
        prev = None
        for (i, v) in enumerate(self):
            if not prev:
                prev = self.coordinates[i]
                continue

            vmax = prev.get_vmax(to=self.coordinates[i], time=step_time)
            self.v.append(vmax)
            prev = self.coordinates[i]
            prev.v = vmax

    def normalize(self, step_time, offset, rotation):
        centroid = self.__get_centroid__()

        for (i, v) in enumerate(self):
            r_transformation = self.rotation_transformation(v, rotation, centroid)
            print(r_transformation.x, r_transformation.y)
            self.x[i] = v.x + offset.x + r_transformation.x
            self.y[i] = v.y + offset.y + r_transformation.y
            self.coordinates[i].x = self.x[i]
            self.coordinates[i].y = self.y[i]

        min_x = min(self.get_x_coordinates())
        min_y = min(self.get_y_coordinates())

        factor_x = 0 if min_x > 0 else abs(min_x)
        factor_y = 0 if min_y > 0 else abs(min_y)

        for (i, v) in enumerate(self):
            r_transformation = self.rotation_transformation(v, rotation, centroid)
            print(r_transformation.x, r_transformation.y)
            self.x[i] = v.x + factor_x
            self.y[i] = v.y + factor_y
            self.coordinates[i].x = self.x[i]
            self.coordinates[i].y = self.y[i]
            # print(self.x[i], self.y[i])

        self.__calculate_velocities__(step_time)

    def rotation_transformation(self, c, rotation, centroid):
        o_over_a = 0
        if centroid.y - c.y != 0:
            o_over_a = math.fabs((centroid.x - c.x) / (centroid.y - c.y))
        t5 = math.atan(o_over_a)
        print("t5", t5)
        t2 = (math.pi - rotation) / 2
        print("t2", t2)
        t6 = (math.pi / 2) - t2 + t5
        print("t6", t6)
        d = self.distance(centroid, c)

        a = math.sqrt(2*(d**2) * (1 - math.cos(rotation)))
        print("a", a)
        si = a * math.sin(t6)
        print("m", si)
        co = a * math.cos(t6)
        print("n", co)

        if c.x - centroid.x >= 0:
            if c.y - centroid.y > 0:
                x = -co
                y = si
            else:
                x = -si
                y = -co
        else:
            if c.y - centroid.y > 0:
                x = co
                y = -si
            else:
                # g
                x = si
                y = co

        # x_dir = 1
        # y_dir = 1
        # if c.x - centroid.x > 0:
        #     x_dir = -1
        # if c.y - centroid.y > 0:
        #     y_dir = -1
        # if x_dir == y_dir:
        #     t = m
        #     m = n
        #     n = t

        # x_dir = 1 if c.x - centroid.x > 0 else -1
        # y_dir = 1 if c.y - centroid.y > 0 else -1

        cr = Coordinate(x, y)
        return cr

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






