import cv2
import matplotlib.pyplot as plt
import numpy as np
from Coordinate import Coordinates, Coordinate
from tqdm import tqdm
from scipy.spatial import cKDTree
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS, BEAM_DIAMETER

save_images = True

plt.figure(figsize=(12, 9))

def get_coordinates(edges, stiffness):
    """
    Extracts the coordinates of the detected edges.

    Returns:
        Coordinates: The extracted coordinates.

    """
    coordinates = Coordinates()
    visited = np.zeros((len(edges), len(edges[0])))
    canvas_width = 20
    canvas_height = 16
    width = len(edges)
    height = 0 if len(edges) == 0 else len(edges[0])

    for i in tqdm(range(height), desc="Getting Coordinates"):
        for j in range(width):
            if edges[j][i] == 255 and visited[j][i] == 0:
                queue = [(j, i)]
                while queue:
                    x, y = queue.pop(0)
                    if visited[x][y] == 0:
                        visited[x][y] = 1
                        # Scale x and y to fit inside width and height
                        scaled_x = (canvas_width * x) / width
                        scaled_y = (canvas_height * y) / height
                        coordinates.append(Coordinate(scaled_x, scaled_y))

                        # Define the possible offsets for neighboring pixels
                        offsets = [(-1, -1), (-1, 0), (-1, 1),
                                    (0, -1),           (0, 1),
                                    (1, -1),  (1, 0),  (1, 1)]
                        
                        neighbors = []
                        for dx, dy in offsets:
                            nx, ny = x + dx, y + dy

                            # Check if the neighbor is within bounds
                            if 0 <= nx < width - 1 and 0 <= ny < height - 1 and visited[nx][ny] == 0:
                                neighbors.append((nx, ny))

                        for neighbor in neighbors:
                            if edges[neighbor[0]][neighbor[1]] == 255:
                                queue.append(neighbor)

    center = Coordinate(12.5, 12.5)
    rotation = 0
    beam_diameter = BEAM_DIAMETER
    coordinates = ordered_by_nearest_neighbor(coordinates, beam_diameter)
    if len(coordinates) != 0:
        coordinates.normalize(center=center, rotation=rotation, stiffness=stiffness, beam_diameter_mm=beam_diameter)

    return coordinates


def ordered_by_nearest_neighbor(coordinates, beam_diameter):
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


def show(filename):
    if save_images:
        plt.show()
    else:
        plt.savefig(filename)


def top_colors(img):
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = image.reshape(-1, 3) * 256

    # Define the number of bins per channel
    bins = 8  # You can adjust this number

    # Quantize the colors by reducing color depth
    quantized_pixels = (pixels // (256 // bins)) * (256 // bins)

    # Convert to integer type
    quantized_pixels = quantized_pixels.astype(np.uint8)

    # Get unique colors and their counts
    colors, counts = np.unique(quantized_pixels, axis=0, return_counts=True)
    # Sort by frequency
    sorted_indices = np.argsort(-counts)
    colors = colors[sorted_indices]
    counts = counts[sorted_indices]

    top_n = 5

    return colors[:top_n], counts[:top_n]


def color_images(img, num_colors):
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = image.reshape(-1, 3) * 256

    # Define the number of bins per channel
    bins = 6 # You can adjust this number

    # Quantize the colors by reducing color depth
    quantized_pixels = (pixels // (256 // bins)) * (256 // bins)

    # Convert to integer type
    quantized_pixels = quantized_pixels.astype(np.uint8)

    # Get unique colors and their counts
    colors, counts = np.unique(quantized_pixels, axis=0, return_counts=True)
    # Sort by frequency
    sorted_indices = np.argsort(-counts)
    colors = colors[sorted_indices]
    counts = counts[sorted_indices]

    color_images = {}
    for color in colors[:num_colors]:
        mask = np.all(quantized_pixels == color, axis=1).reshape(image.shape[:2])
        color_images[tuple(color)] = np.zeros_like(image)
        color_images[tuple(color)][mask] = color / 255

    return color_images

def binarize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary_img = (gray > 0.6).astype(np.float32)

    return binary_img

def dilate_and_erode(img):
    kernel = np.ones((5, 5), np.uint8)

    img_dilation = cv2.dilate(img, kernel, iterations=1)
    img_erosion = cv2.erode(img_dilation, kernel, iterations=1)

    return img_erosion


def blur(img, kernel_size):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def canny_edge_detection(img):
    img = (img * 255).astype(np.uint8)
    edges = cv2.Canny(img, 100, 200)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    curvy_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(curvy_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    curvy_output_image = np.zeros_like(img, dtype=np.uint8)
    curvy_output_image = cv2.cvtColor(curvy_output_image, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(curvy_output_image, contours, -1, (0, 255, 0), 2) # Draw contours in green

    return curvy_output_image

def remove_noise(img):
    return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

def view_layers(layers):
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    fig.tight_layout()
    axes = axes.flatten()
    for i, layer in enumerate(layers):
        ax = axes[i]
        ax.imshow(layer)
        ax.axis('off')
    plt.show()



def process2(filename):
    img = plt.imread(filename)
    blurred_img = blur(img, 5)
    num_colors = 5
    colored_images = color_images(blurred_img, num_colors)
    # colored_images[-1] = img
    stiffness = [10000, 20000, 30000, 40000, 50000]
    coordinates = Coordinates()
    for (i, (_, image)) in enumerate(colored_images.items()):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        division_blur = blur(gray, 15)
        divide = cv2.divide(gray, division_blur, scale=255)
        binary_img = (divide > 0.6).astype(np.float32) * 255
        edges = [np.flip(row, 0) for row in binary_img]
        coordinates += get_coordinates(edges, stiffness[i])
        
    coordinates.plot()
    # self.edges = [np.flip(row, 0) for row in edge_detection]
    

def process(filename):
    img = plt.imread(filename)
    blurred_img = blur(img, 5)
    num_colors = 5
    colored_images = color_images(blurred_img, num_colors)
    colored_images[-1] = img
    stiffness = [10000, 20000, 30000, 40000, 50000, 60000]
    coordinates = Coordinates()
    colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255), (0, 0, 0)]

    layers = []
    for (i, (_, image)) in enumerate(colored_images.items()):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        if i == len(colored_images) - 1:
            binary_img = (gray > 0.6).astype(np.float32)
            blurred = blur(binary_img, 5)
            reduced_noise_img = dilate_and_erode(blurred)
            binary_img2 = (reduced_noise_img < 0.95).astype(np.float32)
        else:
            division_blur = blur(gray, 15)
            divide = cv2.divide(gray, division_blur, scale=255)
            
            binary_img = (divide > 0.6).astype(np.float32)
            blurred = blur(binary_img, 5)
            reduced_noise_img = dilate_and_erode(blurred)
            binary_img2 = (reduced_noise_img < 0.05).astype(np.float32)    
        
        blurred_heavy = blur(binary_img2, 21)
        edge_detection_img = canny_edge_detection(blurred_heavy)
        
        opened_edges_colored = np.zeros_like(img)
        opened_edges_colored[edge_detection_img[:, :, 1] > 0] = colors[i]

        gray_edges = cv2.cvtColor(opened_edges_colored, cv2.COLOR_BGR2GRAY)
        binary_img3 = (gray_edges > 0.6).astype(np.float32) * 255
        edges = [np.flip(row, 0) for row in binary_img3]
        coordinates_layer = get_coordinates(edges, stiffness[i])
        # if len(coordinates_layer) == 0:
        #     coordinates_layer.normalize(center=Coordinate(0, 0), rotation=0, stiffness=stiffness[i], beam_diameter_mm=0.5)
        coordinates += coordinates_layer
        # opened_edges_colored = cv2.addWeighted(opened_edges_colored, 1, image, 1, 0)

        layers.append(opened_edges_colored)
        

    return coordinates

    # view_layers(layers)
    # combined_image = np.zeros_like(img)    
    # for layer in layers:
    #     combined_image[layer > 0] = layer[layer > 0]
    # plt.imshow(combined_image)
    # plt.show()
        


# process("test_images/7.png")
        