import cv2
from Coordinate import Coordinate, Coordinates
import numpy as np
from tqdm import tqdm
from CuringCalculations import curing_calculations

dimensions = 15  # 15 mm * 100 mm_to_pixel_ratio


class EdgeDetection:
    """
    A class that performs edge detection on an image and extracts coordinates of the detected edges.

    Args:
        img_file (str): The path to the input image file.
        stiffness (float): The stiffness of the material.
        center (Coordinate, optional): The center coordinate of the image. Defaults to Coordinate(0, 0).
        rotation_angle_degrees (float, optional): The rotation angle of the image in degrees. Defaults to 0.
        scale_factor (float, optional): The scale factor of the image. Defaults to 1.
        beam_diameter (float, optional): The diameter of the beam. Defaults to 0.1.

    Attributes:
        img_file (str): The path to the input image file.
        center (Coordinate): The center coordinate of the image.
        rotation (float): The rotation angle of the image in degrees.
        scale_factor (float): The scale factor of the image.
        beam_diameter (float): The diameter of the beam.
        stiffness (float): The stiffness of the material.
        edges (list): The list of detected edges.
        factor (float): The scaling factor based on the dimensions and maximum dimension of the image.
    """

    def __init__(self, img_file, stiffness, center=Coordinate(0, 0), rotation_angle_degrees=0, scale_factor=1, beam_diameter=0.1):
        """
        Initialize the EdgeDetection object.

        Parameters:
        - img_file (str): The path to the image file.
        - stiffness (float): The stiffness value.
        - center (Coordinate, optional): The center coordinate of the image. Defaults to (0, 0).
        - rotation_angle_degrees (float, optional): The rotation angle of the image in degrees. Defaults to 0.
        - scale_factor (float, optional): The scale factor of the image. Defaults to 1.
        - beam_diameter (float, optional): The beam diameter. Defaults to 0.1.
        """
        self.img_file = img_file
        self.center = center
        self.rotation = rotation_angle_degrees
        self.scale_factor = scale_factor
        self.beam_diameter = beam_diameter
        self.stiffness = stiffness
        self.edges = []
        self.canny_edge_detection()

        max_dimension = max(self.height, self.width)
        self.factor = (dimensions / max_dimension) * self.scale_factor

    @property
    def height(self):
        """
        The height of the image.

        Returns:
            int: The height of the image.

        """
        if len(self.edges) == 0:
            return 0
        return len(self.edges[0])

    @property
    def width(self):
        """
        The width of the image.

        Returns:
            int: The width of the image.

        """
        return len(self.edges)

    def canny_edge_detection(self):
        """
        Performs Canny edge detection on the input image.

        """
        img = cv2.imread(self.img_file)

        # Convert to grayscale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur the image for better edge detection
        img_blur = cv2.GaussianBlur(img_gray, (3, 3), 0)

        # Canny Edge Detection
        edge_detection = cv2.Canny(image=img_blur, threshold1=100, threshold2=200)  # Canny Edge Detection

        self.edges = [np.flip(row, 0) for row in edge_detection]

    def get_coordinates(self):
        """
        Extracts the coordinates of the detected edges.

        Returns:
            Coordinates: The extracted coordinates.

        """
        coordinates = Coordinates()
        visited = []

        for i in tqdm(range(self.height), desc="Getting Coordinates"):
            for j in range(self.width):
                if self.edges[j][i] == 255 and (i, j) not in visited:
                    queue = [(i, j)]
                    while queue:
                        x, y = queue.pop(0)
                        if (x, y) not in visited:
                            c = Coordinate(x * self.factor, y * self.factor)

                            visited.append((x, y))

                            coordinates.append(c)
                            neighbors = self.get_neighbors((x, y))
                            for neighbor in neighbors:
                                if self.edges[neighbor[1]][neighbor[0]] == 255 and neighbor not in visited:
                                    queue.append(neighbor)

        coordinates = self.ordered_by_nearest_neighbor(coordinates)
        coordinates.normalize(center=self.center, rotation=self.rotation, stiffness=self.stiffness, beam_diameter_mm=self.beam_diameter)
        return coordinates
    
    def ordered_by_nearest_neighbor(self, coordinates):
        """
        Orders the coordinates by nearest neighbor.

        Args:
            coordinates (Coordinates): The input coordinates.

        Returns:
            Coordinates: The ordered coordinates.

        """
        # Start at the first point
        current_point = coordinates[0]
        path = Coordinates()
        path.append(current_point)
        unvisited = set(coordinates[1:])

        while unvisited:
            nearest_point = min(unvisited, key=lambda x: Coordinates.distance(current_point, x))
            path.append_if_far_enough(nearest_point)

            dist = Coordinates.distance(current_point, nearest_point)
            if dist > self.beam_diameter:
                nearest_point.lp = False
            
            unvisited.remove(nearest_point)
            current_point = nearest_point

        return path

    def get_neighbors(self, coord):
        """
        Gets the neighboring coordinates of a given coordinate.

        Args:
            coord (tuple): The input coordinate.

        Returns:
            list: The neighboring coordinates.

        """
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

