import cv2
from Coordinate import Coordinate, Coordinates

dimensions = 15  # 15 mm * 100 mm_to_pixel_ratio


class EdgeDetection:

    def __init__(self, img_file, center=Coordinate(0, 0), rotation_angle=0, scale_factor=1, beam_diameter=0.1):
        self.img_file = img_file
        self.center = center
        self.rotation = rotation_angle
        self.scale_factor = scale_factor
        self.beam_diameter = beam_diameter
        self.edges = []
        self.canny_edge_detection()

        max_dimension = max(self.height, self.width)
        self.factor = (dimensions / max_dimension) * self.scale_factor

    @property
    def height(self):
        if len(self.edges) == 0:
            return 0
        return len(self.edges[0])

    @property
    def width(self):
        return len(self.edges)

    def canny_edge_detection(self):
        img = cv2.imread(self.img_file)

        # Convert to graycsale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur the image for better edge detection
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

        # Canny Edge Detection
        self.edges = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)  # Canny Edge Detection

    def get_coordinates(self):
        coordinates = Coordinates()
        visited = []

        for i in range(self.height):
            for j in range(self.width):
                if self.edges[j][i] == 255 and (i, j) not in visited:
                    queue = [(i, j)]
                    while queue:
                        x, y = queue.pop(0)
                        if (x, y) not in visited:
                            c = Coordinate(x * self.factor, y * self.factor)
                            # lp = False
                            # if len(visited) != 0:
                            #     neigh_last_visited = self.get_neighbors(visited[-1])
                            #     if (x, y) in neigh_last_visited:
                            #         lp = True
                            # c.lp = lp

                            visited.append((x, y))

                            coordinates.append(c)
                            neighbors = self.get_neighbors((x, y))
                            for neighbor in neighbors:
                                if self.edges[neighbor[1]][neighbor[0]] == 255 and neighbor not in visited:
                                    queue.append(neighbor)

        coordinates = self.ordered_by_nearest_neighbor(coordinates)
        coordinates.normalize(step_time=0.5, center=self.center, rotation=self.rotation)
        print(len(coordinates))
        coordinates.plot(plot_lines=True, plot_points=True)
        return coordinates
    
    def ordered_by_nearest_neighbor(self, coordinates):
    # Start at the first point
        current_point = coordinates[0]
        path = Coordinates()
        path.append(current_point)
        unvisited = set(coordinates[1:])

        while unvisited:
            nearest_point = min(unvisited, key=lambda x: Coordinates.distance(current_point, x))
            path.append_if_far_enough(nearest_point, self.beam_diameter)

            dist = Coordinates.distance(current_point, nearest_point)
            if dist > self.beam_diameter:
                nearest_point.lp = False
            
            unvisited.remove(nearest_point)
            current_point = nearest_point

        return path

    def get_neighbors(self, coord):
        x, y = coord
        neighbors = []

        # Define the possible offsets for neighboring pixels
        offsets = [(-1, -1), (-1, 0), (-1, 1),
                   (0, -1),           (0, 1),
                   (1, -1),  (1, 0),  (1, 1)]

        for dx, dy in offsets:
            nx, ny = x + dx, y + dy

            # Check if the neighbor is within bounds
            if 0 <= nx < self.height - 1 and 0 <= ny < self.width - 1:
                neighbors.append((nx, ny))

        return neighbors

