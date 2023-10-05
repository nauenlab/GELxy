from threading import Thread


class VirtualLamp:

    DIAMETER = 0.1  # 0.1 mm
    CURING_RATE = 5

    def __init__(self, led_ampere, canvas):
        self.led_ampere = led_ampere
        self.canvas = canvas
        self.is_on = False

    def __del__(self):
        pass

    def turn_on(self):
        self.is_on = True

    def cure(self, x, y):
        self.canvas.cure(x, y, self.DIAMETER, self.CURING_RATE)

    def turn_off(self):
        self.is_on = False

