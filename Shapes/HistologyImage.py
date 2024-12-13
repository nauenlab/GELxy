import cv2
from Coordinate import Coordinate, Coordinates
import numpy as np
from tqdm import tqdm
from .HistologicalImageProcessing import *
from scipy.spatial import cKDTree
from Constants import MINIMUM_DISTANCE_BETWEEN_TWO_LIGHT_BEAMS
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('TkAgg')


class HistologyImage:
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

    def __init__(self, img_file, height_mm=None, width_mm=None, center=Coordinate(0, 0), rotation_angle_degrees=0, beam_diameter=0.1):
        """
        Initialize the HistologyImage object.

        Parameters:
        - img_file (str): The path to the image file.
        - height_mm (float, optional): The height of the image in mm. Defaults to None. 
            If height_mm is not provided, it will be calculated based on the width_mm and the aspect ratio of the image.
        - width_mm (float, optional): The width of the image in mm. Defaults to None. 
            If width_mm is not provided, it will be calculated based on the height_mm and the aspect ratio of the image.
        - center (Coordinate, optional): The center coordinate of the image. Defaults to (0, 0).
        - rotation_angle_degrees (float, optional): The rotation angle of the image in degrees. Defaults to 0.
        - beam_diameter (float, optional): The beam diameter. Defaults to 0.1.
        """
        if img_file.lower().endswith('.jpg'):
            img_file = convert_jpg_to_png(img_file)

        if not img_file.lower().endswith('.png'):
            raise ValueError("The image file must be a PNG file.")
        
        if height_mm is None and width_mm is None:
            raise ValueError("The height or width of the image in mm must be provided.")
        
        self.img_file = img_file
        self.img = plt.imread(self.img_file)
        self.center = center
        self.rotation = rotation_angle_degrees
        self.beam_diameter = beam_diameter

        self.selected_layers = []

        if height_mm and width_mm is None:
            width_mm = (height_mm / self.img.shape[0]) * self.img.shape[1]
        
        if width_mm and height_mm is None:
            height_mm = (width_mm / self.img.shape[1]) * self.img.shape[0]

        self.dimensions = (width_mm, height_mm)

    def get_coordinates(self):
        og_img = downsample(self.img)
        segmented_images = segment_images(og_img)

        coordinates = Coordinates()
        coordinate_layers = []
        colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (255, 255, 255), (0, 0, 0), (128, 128, 128), (128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128)]

        layers = []
        target_values = list(segmented_images.values())
        self.select_layers(target_values)
        selected_images = [target_values[i] for i, _ in self.selected_layers]
        stiffness = [i[1] for i in self.selected_layers]
        for (i, image) in enumerate(selected_images):
            gray_img = image
            if len(image.shape) == 3:
                gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            medianBlurred = cv2.medianBlur(gray_img, 3)
            
            binary_img = (medianBlurred > 0.6).astype(np.float32)
            blurred = blur(binary_img, 5)
            reduced_noise_img = dilate_and_erode(blurred)
            binary_img2 = (reduced_noise_img < 0.05).astype(np.float32)
            
            edge_detection_img = canny_edge_detection(binary_img2)

            labeled_image, num_islands, island_sizes, thicknesses, island_mask = detect_islands(edge_detection_img)

            cleaned_image = remove_islands(edge_detection_img, island_mask)
    
            opened_edges_colored = np.zeros_like(og_img)
            opened_edges_colored[cleaned_image > 0] = (0, 255, 0)
            
            # get the associated color from the og_img
            colored_img = np.zeros_like(og_img)
            colored_img[image > 0] = og_img[image > 0]
            
            colored_img = blur(colored_img, 21)
            opened_edges_colored_overlayed = combine_images(opened_edges_colored, colored_img)

            layer_color = colors.pop(0)
            colors.append(layer_color)
            filled_shape = fill_shape(opened_edges_colored_overlayed, layer_color)

            layers.append(filled_shape)

            filled_shape_gray = cv2.cvtColor(filled_shape, cv2.COLOR_BGR2GRAY)
            binary_img3 = (filled_shape_gray > 0.6).astype(np.float32) * 255
            filled_shape_flip = [np.flip(row, 0) for row in binary_img3]
            coordinates_layer = self.convert_pixels_to_coordinates(filled_shape_flip, stiffness[i])
            coordinate_layers.append(coordinates_layer)
            coordinates += coordinates_layer

        if len(coordinates) != 0:
            coordinates.normalize(center=self.center, rotation=self.rotation, stiffness=0, beam_diameter_mm=self.beam_diameter, is_layer=False, is_multiple_layers=True)
        
        # if len(layers) != 0:
        #     self.view_layers(layers)
        #     self.plot_merged_layers(layers)
        #     self.plot_spatial_layers(coordinate_layers, scatter=False)

        return coordinates
    
    def plot_spatial_layers(self, layers, scatter=False):
        cs = ["green", "red", "blue", "yellow", "cyan", "magenta", "white", "black", "gray", "maroon", "navy", "olive", "purple", "teal"]
        for i, layer in enumerate(layers):
            layer_color = cs.pop(0)
            cs.append(layer_color)
            if scatter:
                plt.scatter(layer.x, layer.y, color=layer_color)
            else:
                plt.plot(layer.x, layer.y, color=layer_color)
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
    
    def select_layers(self, layers):
        """
            use tkinter to create a GUI so the user can select the layer to use.
            display all the layers to the user with the ability for the image to be full screen. 
            The user should select each layer using a radio button if a layer is selected, a text box should appear for the user to enter the stiffness value
        """
        def on_select():
            selected_layers = []
            for i, var in enumerate(layer_vars):
                if var.get():
                    img_window = tk.Toplevel(root)
                    img_window.title(f"Layer {i+1}")
                    img = ImageTk.PhotoImage(Image.fromarray((layers[i]).astype(np.uint8)))
                    img_label = tk.Label(img_window, image=img)
                    img_label.image = img  # Keep a reference to avoid garbage collection
                    img_label.pack()
                    
                    tk.Label(img_window, text=f"Enter stiffness value for layer {i+1} (Pa):").pack()
                    stiffness_value_entry = tk.Entry(img_window)
                    stiffness_value_entry.pack()
                    def on_confirm(entry=stiffness_value_entry, index=i, window=img_window):
                        stiffness_value = float(entry.get())
                        window.destroy()
                        if stiffness_value is not None:
                            selected_layers.append((index, stiffness_value))
                    confirm_button = tk.Button(img_window, text="Confirm", command=on_confirm)
                    confirm_button.pack()
                    img_window.wait_window()
            root.destroy()
            self.selected_layers = selected_layers

        root = tk.Tk()
        root.title("Select Layers")

        canvas = tk.Canvas(root)
        canvas.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(canvas, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.configure(yscrollcommand=scrollbar.set)

        frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=frame, anchor='nw')
        root.geometry(f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}")
        root.focus_force() 

        layer_vars = []
        for i, layer in enumerate(layers):
            layer_array = (layer > 0.2).astype(np.float32)
            layer_array = (layer_array * 255).astype(np.uint8)
            
            img = Image.fromarray(layer_array)
            
            img = img.resize((300, 300), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            label = tk.Label(frame, image=img_tk)
            label.image = img_tk
            label.grid(row=i // 3, column=i % 3)

            var = tk.BooleanVar()
            checkbox = tk.Checkbutton(frame, text=f"Layer {i+1}", variable=var)
            checkbox.grid(row=i // 3, column=i % 3, sticky='s')
            layer_vars.append(var)

        button = tk.Button(frame, text="Select", command=on_select)
        button.grid(row=(len(layers) + 2) // 3, column=1)

        frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

        root.mainloop()

    
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