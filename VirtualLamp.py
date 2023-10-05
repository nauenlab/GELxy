from threading import Thread


class VirtualLamp:

    RADIUS = 0.1  # 100 microns = 0.1 mm
    TIME_STEP = 0.01  # 0.01 s
    CURING_RATE = 0.5  # 0.5 alpha / second

    def __init__(self, led_ampere, canvas):
        self.led_ampere = led_ampere
        self.canvas = canvas
        self.is_on = False

    def __del__(self):
        pass

    def turn_on(self):
        self.is_on = True

    def cure(self, x, y):
        cure_per_step = self.CURING_RATE * self.TIME_STEP
        x_pos = int(x * self.canvas.mm_to_pixel_ratio)
        y_pos = int(y * self.canvas.mm_to_pixel_ratio)
        self.canvas.pixels[x_pos][y_pos].alpha += cure_per_step

    def turn_off(self):
        self.is_on = False

