

class Pixel:

    def __init__(self, red, green, blue, alpha):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = alpha


class Canvas:

    def __init__(self, dimensions):
        self.pixels = []
        for i in range(1, dimensions):
            if i > len(self.pixels):
                self.pixels.append([])
            for j in range(1, dimensions):
                self.pixels[i].append(Pixel(0.0, 0.0, 0.0, 0.0))
