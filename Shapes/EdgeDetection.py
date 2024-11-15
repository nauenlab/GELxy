import cv2
from Coordinate import Coordinate, Coordinates
import numpy as np
from tqdm import tqdm
from .ImageProcessing import *
from scipy.spatial import cKDTree
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS, MOTOR_MAX_TRAVEL
import matplotlib.pyplot as plt


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
        self.img = plt.imread(self.img_file)
        self.center = center
        self.rotation = rotation_angle_degrees
        self.scale_factor = scale_factor
        self.beam_diameter = beam_diameter
        self.stiffness = stiffness

        major_length = MOTOR_MAX_TRAVEL * scale_factor
        image_shape = self.img.shape[:2]
        minor_length = ((MOTOR_MAX_TRAVEL / max(image_shape)) * min(image_shape)) * scale_factor
        self.dimensions = (minor_length, major_length) if image_shape[0] > image_shape[1] else (major_length, minor_length)


    def get_coordinates(self):
        og_img = downsample(self.img)
        segmented_images = segment_images(og_img)

        stiffness = [50000, 30000, 25000, 20000, 15000, 10000]
        stiffness = [30000, 30000, 30000, 30000, 30000, 30000]
        coordinates = Coordinates()
        coordinate_layers = []
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255), (0, 0, 0), (128, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128)]

        layers = []
        for (i, (_, image)) in enumerate(segmented_images.items()):
            gray_img = image
            if len(image.shape) == 3:
                gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            # plt.imshow(gray_img, cmap='gray')
            # plt.show()
            medianBlurred = cv2.medianBlur(gray_img, 3)
            
            # whitelist = [0, 1, 2, 3, 5]
            # if i not in whitelist:
            #     continue
            
            binary_img = (medianBlurred > 0.6).astype(np.float32)
            blurred = blur(binary_img, 5)
            reduced_noise_img = dilate_and_erode(blurred)
            binary_img2 = (reduced_noise_img < 0.05).astype(np.float32)
        
            # plt.imshow(binary_img2, cmap='gray')
            # plt.show()
            # filled_img = test_fill(binary_img2)
            # plt.imshow(filled_img, cmap='gray')
            # plt.show()
            
            # blurred_heavy = blur(filled_img, 5)
            # plt.imshow(blurred_heavy, cmap='gray')
            # plt.show()
            
            edge_detection_img = canny_edge_detection(binary_img2)
            # plt.imshow(edge_detection_img, cmap='gray')
            # plt.show()

            labeled_image, num_islands, island_sizes, thicknesses, island_mask = detect_islands(edge_detection_img)

            cleaned_image = remove_islands(edge_detection_img, island_mask)
    
            # Visualize results
            # visualize_results(edge_detection_img, labeled_image, cleaned_image, num_islands, thicknesses)
            
            opened_edges_colored = np.zeros_like(og_img)
            opened_edges_colored[cleaned_image > 0] = colors[0]
            
            # get the associated color from the og_img
            colored_img = np.zeros_like(og_img)
            colored_img[image > 0] = og_img[image > 0]
            
            colored_img = blur(colored_img, 21)
            opened_edges_colored_overlayed = combine_images(opened_edges_colored, colored_img)

            filled_shape = fill_shape(opened_edges_colored_overlayed, colors[i])

            layers.append(filled_shape)

            filled_shape_gray = cv2.cvtColor(filled_shape, cv2.COLOR_BGR2GRAY)
            binary_img3 = (filled_shape_gray > 0.6).astype(np.float32) * 255
            filled_shape_flip = [np.flip(row, 0) for row in binary_img3]
            coordinates_layer = self.convert_pixels_to_coordinates(filled_shape_flip, stiffness[i])
            coordinate_layers.append(coordinates_layer)
            coordinates += coordinates_layer

        if len(coordinates) != 0:
            coordinates.normalize(center=self.center, rotation=self.rotation, stiffness=0, beam_diameter_mm=self.beam_diameter, is_layer=False, is_multiple_layers=True)
        
        # self.view_layers(layers)
        # self.plot_merged_layers(layers)
        # self.plot_spatial_layers(coordinate_layers)

        return coordinates
    
    def plot_spatial_layers(self, layers):
        cs = ["green", "red", "blue", "yellow", "cyan", "magenta", "white", "black", "gray", "maroon", "green", "navy", "olive", "purple", "teal"]
        for i, layer in enumerate(layers):
            plt.plot(layer.x, layer.y, 'ro', color=cs[i])
        plt.show()

    def plot_merged_layers(self, layers):
        combined_image = merge_layers(layers)
        plt.imshow(combined_image, cmap='gray')
        plt.show()

    def view_layers(self, layers):
        # get width and height of subplot grid using number of layers
        n_layers = len(layers)
        n_cols = 3
        n_rows = (n_layers + n_cols - 1) // n_cols
        fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(18, 12))
        fig.tight_layout()
        axes = axes.flatten()
        for i, layer in enumerate(layers):
            ax = axes[i]
            ax.imshow(layer)
            ax.axis('off')
        plt.show()
    
    def convert_pixels_to_coordinates(self, pixels, stiffness):
        """
        Extracts the coordinates of the detected edges.

        Returns:
            Coordinates: The extracted coordinates.

        """
        coordinates = Coordinates()
        pixels = np.flip(pixels, axis=1)
        visited = np.zeros((len(pixels), len(pixels[0])))
        
        canvas_width = self.dimensions[0]
        canvas_height = self.dimensions[1]

        width = 0 if len(pixels) == 0 else len(pixels[0])
        height = len(pixels)

        for row in tqdm(range(height), desc="Getting Coordinates"):
            for col in range(width):
                if pixels[row][col] == 255 and visited[row][col] == 0:
                    queue = [(row, col)]
                    while queue:
                        y, x = queue.pop(0)
                        if visited[y][x] == 0:
                            visited[y][x] = 1
                            # Scale x and y to fit inside width and height
                            scaled_x = (canvas_width * x) / width
                            scaled_y = (canvas_height * (height - y)) / height
                            coordinates.append(Coordinate(scaled_x, scaled_y))

                            # Define the possible offsets for neighboring pixels
                            offsets = [(-1, -1), (-1, 0), (-1, 1),
                                        (0, -1),           (0, 1),
                                        (1, -1),  (1, 0),  (1, 1)]
                            
                            neighbors = []
                            for dx, dy in offsets:
                                nx, ny = x + dx, y + dy

                                # Check if the neighbor is within bounds
                                if 0 <= nx < width - 1 and 0 <= ny < height - 1 and visited[ny][nx] == 0:
                                    neighbors.append((ny, nx))

                            for neighbor in neighbors:
                                if pixels[neighbor[0]][neighbor[1]] == 255:
                                    queue.append(neighbor)

        coordinates = self.ordered_by_nearest_neighbor(coordinates, self.beam_diameter)

        if len(coordinates) != 0:
            coordinates.normalize(center=self.center, rotation=self.rotation, stiffness=stiffness, beam_diameter_mm=self.beam_diameter, is_layer=True, is_multiple_layers=False)

        # coordinates.plot(plot_lines=False, plot_points=True)

        return coordinates

    def ordered_by_nearest_neighbor(self, coordinates, beam_diameter):
        min_distance = float(MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS)
        
        # Convert the Coordinates object into a list of tuples for easier calculation
        points = [(coord.x, coord.y) for coord in coordinates]
        
        # Initialize the path with the first point
        path = Coordinates()
        path.append(coordinates[0])
        blacklist = set()
        blacklist.add(0)
        
        # Build a k-d tree for efficient nearest neighbor search
        tree = cKDTree(points)

        while True:
            current_coord = path[-1]
            current_point = (current_coord.x, current_coord.y)

            distances, indices = tree.query(current_point, k=len(points), distance_upper_bound=np.inf)        
            next_point_found = False
            for dist, idx in zip(distances, indices):
                # idx == tree.n when there are no more neighbors
                if idx != tree.n and dist >= min_distance and idx not in blacklist:
                    # Add the next valid coordinate to the path
                    if dist > beam_diameter:
                        coordinates[idx].lp = False
                    path.append(coordinates[idx])
                    
                    # Blacklist all points within distance `m` of the new point
                    nearby_indices = tree.query_ball_point(points[idx], min_distance)
                    blacklist.update(nearby_indices)

                    next_point_found = True
                    break

            # If no valid next point is found, break the loop
            if not next_point_found:
                break

        return path