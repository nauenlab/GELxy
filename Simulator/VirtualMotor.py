import math
from Constants import *


class VirtualMotor:

    TIME_STEP = 0.01  # 0.01 seconds

    def __init__(self, serial_no=None, acceleration=None, max_velocity=None):
        self.serial_number = serial_no
        self.acceleration = acceleration if acceleration else ACCELERATION
        self.max_velocity = max_velocity if max_velocity else MAXIMUM_VELOCITY
        self.position = 0.0
        
    def __del__(self):
        pass

    def set_params(self, vmax):
        self.max_velocity = vmax

    def get_movements(self, new_position, is_lamp_off):
        movements = []
        ti = 0
        distance = new_position - self.position
        tf = self.get_movement_time(math.fabs(distance), is_lamp_off)
        while ti - self.TIME_STEP <= tf:
            new_pos = self.get_position_change_at(ti, is_lamp_off)
            change = new_pos if distance > 0 else -new_pos
            movements.append(self.position + change)
            ti += self.TIME_STEP
        self.position = new_position

        return movements

    def get_movement_time(self, d, is_lamp_off):
        v = MAXIMUM_VELOCITY if is_lamp_off or self.max_velocity == 0 else self.max_velocity
        a = ACCELERATION if is_lamp_off else self.acceleration

        max_time = v / a
        t1 = math.sqrt((2*d)/a)
        if t1 < max_time:
            return t1

        t2 = (d - ((a*(max_time**2)) / 2)) / v
        return max_time + t2

    def get_position_change_at(self, t, is_lamp_off):
        v = MAXIMUM_VELOCITY * 1000 if is_lamp_off else self.max_velocity # MAXIMUM_VELOCITY * 1000 is a hack to make the virtual motor move faster becauase is wastes computation otherwise!
        a = ACCELERATION if is_lamp_off else self.acceleration

        max_time = v / a
        if t < max_time:
            return (a * (t ** 2)) / 2

        c = (v**2 / (2 * a)) - (v * max_time)
        return (v * t) + c

    def move_absolute(self, final_position):
        original_position = self.position
        distance = final_position - self.position
        current_time = 0

        while math.fabs(self.position - original_position) < math.fabs(distance):
            current_time += self.TIME_STEP
            if current_time > 15:
                raise Exception("Virtual Motor will take too long to move")

            new_pos = self.get_position_change_at(current_time, not final_position.lp)
            self.position += new_pos if distance > 0 else -new_pos
            print(self.position)


