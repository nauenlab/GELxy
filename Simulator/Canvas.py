from PIL import Image, ImageDraw
import numpy as np
from tqdm import tqdm


class Pixel:
    MAX_VALUE = 256

    def __init__(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha

    def tuple(self):
        return self.red, self.green, self.blue, self.alpha

    def inc(self, v):
        if self.alpha + v <= self.MAX_VALUE:
            self.alpha += v


def points_in_circle(center, radius, mm_to_pixel_ratio):
    resolution = 1.0 / mm_to_pixel_ratio
    points = []
    x0, y0 = center
    for x in np.arange(-radius, radius + resolution, resolution):
        for y in np.arange(-radius, radius + resolution, resolution):
            if x**2 + y**2 <= radius**2:
                points.append((int(round((x0 + x) * mm_to_pixel_ratio)), 
                                int(round((y0 + y) *  mm_to_pixel_ratio))))
    return points


class Canvas:
    mm_to_pixel_ratio = 100

    def __init__(self, dimensions_mm):
        self.pixels = []
        self.dimensions = dimensions_mm * self.mm_to_pixel_ratio  # 0.1 mm is 1 pixel
        for i in range(self.dimensions + 1):
            if i + 1 > len(self.pixels):
                self.pixels.append([])
            for j in range(1, self.dimensions + 1):
                self.pixels[i].append(Pixel(0, 0, 0, 0))

    def cure(self, x, y, diameter, cure_per_step):
        radius = diameter / 2.0
        points = points_in_circle((x, y), radius, self.mm_to_pixel_ratio)

        for point in points:
            x_pos, y_pos = point
            if 0 < x_pos < len(self.pixels) - 1 and 0 < y_pos < len(self.pixels[x_pos]) - 1:
                self.pixels[x_pos][y_pos].inc(cure_per_step)

    def draw(self):
        new = Image.new(mode="RGBA", size=(len(self.pixels), len(self.pixels)), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(new)
        for x in tqdm(range(len(self.pixels) - 1), desc="Drawing on Canvas"):
            for y in range(len(self.pixels) - 1):
                pixel_color = self.pixels[x][y]
                red = 0
                if pixel_color.alpha > 0:
                    red = 256
                draw.point((x, y), fill=(red, 0, 0, int(pixel_color.alpha)))

        new.show()

