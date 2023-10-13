from PIL import Image, ImageDraw
import numpy as np


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


def points_in_circle(center, diameter, resolution):
    points = []
    radius = diameter / 2.0

    for x in np.arange(center[0] - radius, center[0] + radius + resolution, resolution):
        for y in np.arange(center[1] - radius, center[1] + radius + resolution, resolution):
            if (x - center[0]) ** 2 + (y - center[1]) ** 2 <= radius ** 2:
                points.append((x, y))

    return points


class Canvas:

    mm_to_pixel_ratio = 100
    shape_buffer = 100  # 100 pixel buffer

    def __init__(self, dimensions_mm):
        self.pixels = []
        dimensions = dimensions_mm * self.mm_to_pixel_ratio  # 0.1 mm is 1 pixel
        for i in range(dimensions + 1):
            if i + 1 > len(self.pixels):
                self.pixels.append([])
            for j in range(1, dimensions + 1):
                self.pixels[i].append(Pixel(0, 0, 0, 0))

    def cure(self, x, y, diameter, cure_per_step):
        diameter * self.mm_to_pixel_ratio
        points = points_in_circle((x, y), diameter, 1.0 / self.mm_to_pixel_ratio)
        for point in points:
            x_pos = int(round(point[0] * self.mm_to_pixel_ratio))
            y_pos = int(round(point[1] * self.mm_to_pixel_ratio))
            # print(x_pos + self.shape_buffer, y_pos + self.shape_buffer)
            if len(self.pixels) - 1 > x_pos + self.shape_buffer >= 0 and \
                    len(self.pixels[x_pos + self.shape_buffer]) - 1 > y_pos + self.shape_buffer >= 0:
                self.pixels[x_pos + self.shape_buffer][y_pos + self.shape_buffer].inc(cure_per_step)

    def draw(self):
        new = Image.new(mode="RGBA", size=(len(self.pixels), len(self.pixels)), color=(0, 0, 0, 0))
        draw = ImageDraw.Draw(new)
        for x in range(len(self.pixels) - 1):
            for y in range(len(self.pixels) - 1):
                pixel_color = self.pixels[x][y]
                # draw.point((x, y), fill=pixel_color.tuple())
                red = 0
                if pixel_color.alpha > 0:
                    red = 256
                draw.point((x, y), fill=(red, 0, 0, pixel_color.alpha))

        # new.save("rgba_image.png")

        new.show()

