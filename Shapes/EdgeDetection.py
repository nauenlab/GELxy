import time
import cv2
from Coordinate import Coordinate, Coordinates

dimensions = 15  # 15 mm * 100 mm_to_pixel_ratio


class EdgeDetection:

    def __init__(self, img_file, beam_diameter):
        self.img_file = img_file
        self.edges = []
        self.beam_diameter = beam_diameter
        self.canny_edge_detection()

        max_dimension = max(self.height, self.width)
        self.factor = dimensions / max_dimension 

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
                            lp = False
                            if len(visited) != 0:
                                neigh_last_visited = self.get_neighbors(visited[-1])
                                if (x, y) in neigh_last_visited:
                                    lp = True
                            c.lp = lp

                            visited.append((x, y))

                            coordinates.append_if_far_enough(c, self.beam_diameter)
                            neighbors = self.get_neighbors((x, y))
                            for neighbor in neighbors:
                                if self.edges[neighbor[1]][neighbor[0]] == 255 and neighbor not in visited:
                                    queue.append(neighbor)

        coordinates.plot()
        print(len(coordinates))
        return coordinates

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





EdgeDetection("/Users/yushrajkapoor/Desktop/Network Analysis/GELxy/0.jpg", beam_diameter=0.01).get_coordinates()

