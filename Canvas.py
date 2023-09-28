

class Pixel:

    def __init__(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha


class Canvas:
    
    mm_to_pixel_ratio = 10

    def __init__(self, dimensions_cm):
        self.pixels = []
        dimensions = dimensions_cm * self.mm_to_pixel_ratio * 10 # 0.1 mm is 1 pixel
        for i in range(1, dimensions):
            if i > len(self.pixels):
                self.pixels.append([])
            for j in range(1, dimensions):
                self.pixels[i].append(Pixel(0.0, 0.0, 0.0, 0.0))
