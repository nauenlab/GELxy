from PIL import Image, ImageDraw
from tqdm import tqdm


def points_in_circle(center, radius, mm_to_pixel_ratio):
    """
    Generate a list of points within a circle.

    Args:
        center (tuple): The center coordinate of the circle.
        radius (float): The radius of the circle.
        mm_to_pixel_ratio (float): The conversion ratio from millimeters to pixels.

    Returns:
        list: A list of points within the circle, represented as tuples of (x, y) coordinates.
    """
    x0_pixel = int(round(center[0] * mm_to_pixel_ratio))
    y0_pixel = int(round(center[1] * mm_to_pixel_ratio))
    pixel_radius = int(round(radius * mm_to_pixel_ratio))

    points = []

    x = 0
    y = pixel_radius
    d = 1 - pixel_radius

    while x <= y:
        # For each pixel from x to y, draw horizontal lines across the circle
        for yi in range(x, y + 1):
            # Exploit symmetry by drawing lines across each octant
            points.extend([
                (x0_pixel + x, y0_pixel + yi),
                (x0_pixel - x, y0_pixel + yi),
                (x0_pixel + x, y0_pixel - yi),
                (x0_pixel - x, y0_pixel - yi),
                (x0_pixel + yi, y0_pixel + x),
                (x0_pixel - yi, y0_pixel + x),
                (x0_pixel + yi, y0_pixel - x),
                (x0_pixel - yi, y0_pixel - x),
            ])
        if d < 0:
            d += 2 * x + 3
        else:
            d += 2 * (x - y) + 5
            y -= 1
        x += 1

    # Remove duplicates if any
    points = list(set(points))

    return points


class Pixel:
    MAX_ALPHA = 256

    def __init__(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def tuple(self):
        return self.red, self.green, self.blue, self.alpha

    def inc(self, v):
        if self.alpha + v <= self.MAX_ALPHA:
            self.alpha += v


class Canvas:
    """
    A class representing a canvas for drawing and curing pixels.

    Attributes:
        mm_to_pixel_ratio (int): The ratio of millimeters to pixels.
        pixels (List[List[Pixel]]): A 2D list representing the pixels on the canvas.
        dimensions (int): The dimensions of the canvas in pixels.

    Methods:
        __init__(self, dimensions_mm: int): Initializes a new instance of the Canvas class.
        cure(self, x: int, y: int, diameter: int, cure_per_step: int): Cures the pixels within a given circle.
        draw(self): Draws the pixels on the canvas.
    """

    mm_to_pixel_ratio = 100

    def __init__(self, dimensions_mm: int):
        """
        Initializes a new instance of the Canvas class.

        Args:
            dimensions_mm (int): The dimensions of the canvas in millimeters.
        """
        self.pixels = []
        self.dimensions = dimensions_mm * self.mm_to_pixel_ratio  # 0.1 mm is 1 pixel
        for i in range(self.dimensions + 1):
            if i + 1 > len(self.pixels):
                self.pixels.append([])
            for j in range(1, self.dimensions + 1):
                self.pixels[i].append(Pixel(0, 0, 0, 0))

    def cure(self, x: int, y: int, diameter: int, cure_per_step: int):
        """
        Cures the pixels within a given circle beam.

        Args:
            x (int): The x-coordinate of the center of the circle beam.
            y (int): The y-coordinate of the center of the circle beam.
            diameter (int): The diameter of the circle beam.
            cure_per_step (int): The amount to cure each pixel per step.
        """
        radius = diameter / 2.0
        points = points_in_circle((x, y), radius, self.mm_to_pixel_ratio)

        for point in points:
            x_pos, y_pos = point
            if 0 < x_pos < len(self.pixels) - 1 and 0 < y_pos < len(self.pixels[x_pos]) - 1:
                self.pixels[x_pos][y_pos].inc(cure_per_step)

    def draw(self, binarized=False):
        """
        Draws the pixels on the canvas.
        """
        new = Image.new(mode="RGBA", size=(len(self.pixels), len(self.pixels)), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(new)
        for x in tqdm(range(len(self.pixels) - 1), desc="Drawing on Canvas"):
            for y in range(len(self.pixels) - 1):
                pixel_color = self.pixels[x][y]
                red = 0
                if pixel_color.alpha > 0:
                    red = 256
                draw.point((x, len(self.pixels)-y), fill=(red, 0, 0, 256 if binarized else int(pixel_color.alpha)))

        new.show()
