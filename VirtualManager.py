from VirtualMotor import VirtualMotor
from VirtualLamp import VirtualLamp
from Canvas import Canvas


class VirtualManager:

    def __init__(self, canvas_dimensions_mm, led_ampere, acceleration=None, max_velocity=None):
        self.canvas = Canvas(dimensions_mm=canvas_dimensions_mm)
        self.x = VirtualMotor(acceleration=acceleration, max_velocity=max_velocity)
        self.y = VirtualMotor(acceleration=acceleration, max_velocity=max_velocity)
        self.lamp = VirtualLamp(led_ampere=led_ampere, canvas=self.canvas)

    def motors(self):
        return self.x, self.y

    def move(self, position):
        is_lamp_on = position.lp
        if is_lamp_on:
            self.x.set_params(position.v[0])
            self.y.set_params(position.v[1])
        x_mvts = self.x.get_movements(position.x, not is_lamp_on)
        y_mvts = self.y.get_movements(position.y, not is_lamp_on)
        print(range(max(len(x_mvts), len(y_mvts))))
        for i in range(max(len(x_mvts), len(y_mvts))):
            x_i = i if i < len(x_mvts) else len(x_mvts) - 1
            y_i = i if i < len(y_mvts) else len(y_mvts) - 1
            x_pos = x_mvts[x_i]
            y_pos = y_mvts[y_i]
            if is_lamp_on:
                self.lamp.cure(x_pos, y_pos)

    def __del__(self):
        self.x.__del__()
        self.y.__del__()
        self.lamp.__del__()
