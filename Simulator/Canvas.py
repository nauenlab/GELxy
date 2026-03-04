from PIL import Image
import numpy as np


class Canvas:
    """
    A class representing a canvas for drawing and curing pixels.

    Attributes:
        mm_to_pixel_ratio (int): The ratio of millimeters to pixels.
        alpha (np.ndarray): A 2D numpy array representing the curing intensity of each pixel.
        dimensions (int): The dimensions of the canvas in pixels.

    Methods:
        __init__(self, dimensions_mm: int): Initializes a new instance of the Canvas class.
        cure(self, x: int, y: int, diameter: int, cure_per_step: int): Cures the pixels within a given circle.
        draw(self): Draws the pixels on the canvas.
    """

    mm_to_pixel_ratio = 100
    MAX_ALPHA = 256

    def __init__(self, dimensions_mm: int):
        """
        Initializes a new instance of the Canvas class.

        Args:
            dimensions_mm (int): The dimensions of the canvas in millimeters.
        """
        self.dimensions = dimensions_mm * self.mm_to_pixel_ratio
        self.alpha = np.zeros((self.dimensions + 1, self.dimensions + 1), dtype=np.float64)
        self._circle_mask_cache = {}

    def _get_circle_mask(self, pixel_radius):
        """
        Returns a cached circular mask for the given pixel radius.
        """
        if pixel_radius in self._circle_mask_cache:
            return self._circle_mask_cache[pixel_radius]

        diameter = 2 * pixel_radius + 1
        y_grid, x_grid = np.ogrid[-pixel_radius:pixel_radius + 1, -pixel_radius:pixel_radius + 1]
        mask = (x_grid ** 2 + y_grid ** 2) <= pixel_radius ** 2
        self._circle_mask_cache[pixel_radius] = mask
        return mask

    def cure(self, x, y, diameter, cure_per_step):
        """
        Cures the pixels within a given circle beam.

        Args:
            x: The x-coordinate of the center of the circle beam (in mm).
            y: The y-coordinate of the center of the circle beam (in mm).
            diameter: The diameter of the circle beam (in mm).
            cure_per_step: The amount to cure each pixel per step.
        """
        radius = diameter / 2.0
        x0 = int(round(float(x) * self.mm_to_pixel_ratio))
        y0 = int(round(float(y) * self.mm_to_pixel_ratio))
        pixel_radius = int(round(radius * self.mm_to_pixel_ratio))

        mask = self._get_circle_mask(pixel_radius)

        # Compute the bounding box of the circle on the canvas
        x_min = x0 - pixel_radius
        x_max = x0 + pixel_radius + 1
        y_min = y0 - pixel_radius
        y_max = y0 + pixel_radius + 1

        # Clip to canvas bounds (excluding edges at 0 and dimensions)
        canvas_x_min = max(1, x_min)
        canvas_x_max = min(self.dimensions - 1, x_max)
        canvas_y_min = max(1, y_min)
        canvas_y_max = min(self.dimensions - 1, y_max)

        if canvas_x_min >= canvas_x_max or canvas_y_min >= canvas_y_max:
            return

        # Corresponding slice of the mask
        mask_x_min = canvas_x_min - x_min
        mask_x_max = mask_x_min + (canvas_x_max - canvas_x_min)
        mask_y_min = canvas_y_min - y_min
        mask_y_max = mask_y_min + (canvas_y_max - canvas_y_min)

        region = self.alpha[canvas_x_min:canvas_x_max, canvas_y_min:canvas_y_max]
        circle_mask = mask[mask_x_min:mask_x_max, mask_y_min:mask_y_max]

        region[circle_mask] = np.minimum(region[circle_mask] + cure_per_step, self.MAX_ALPHA)

    def draw(self, binarized=False):
        """
        Draws the pixels on the canvas.
        """
        size = self.dimensions + 1

        # Build RGBA image from the alpha array
        rgba = np.zeros((size, size, 4), dtype=np.uint8)

        # Red channel: 255 wherever any curing occurred
        rgba[:, :, 0] = np.where(self.alpha > 0, 255, 0)

        # Alpha channel
        if binarized:
            rgba[:, :, 3] = np.where(self.alpha > 0, 255, 0)
        else:
            rgba[:, :, 3] = np.clip(self.alpha, 0, 255).astype(np.uint8)

        # Flip y-axis to match original coordinate system (y increases upward)
        rgba = rgba[:, ::-1, :]

        new = Image.fromarray(rgba.transpose(1, 0, 2), mode="RGBA")
        new.show()
