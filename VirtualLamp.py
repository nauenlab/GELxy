from threading import Thread
from CuringCalculations import MAX_CURRENT


class VirtualLamp:

    def __init__(self, canvas):
        self.canvas = canvas
        self.is_on = False

    def __del__(self):
        pass

    def turn_on(self, _):
        self.is_on = True

    def cure(self, x, y, beam_diameter, curing_rate):
        curing_percentage = (curing_rate / MAX_CURRENT) * 10
        self.canvas.cure(x, y, beam_diameter, curing_percentage)

    def turn_off(self):
        self.is_on = False

