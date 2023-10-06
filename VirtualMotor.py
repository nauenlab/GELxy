import math


class VirtualMotor:

    TIME_STEP = 0.01  # 0.01 s
    VELOCITY_LIMIT = 2.6
    ACCELERATION_LIMIT = 4.0

    def __init__(self, serial_no=None, acceleration=None, max_velocity=None, min_velocity=None):
        self.serial_number = serial_no
        self.acceleration = acceleration if acceleration else self.ACCELERATION_LIMIT
        self.max_velocity = max_velocity if max_velocity else self.VELOCITY_LIMIT
        self.min_velocity = min_velocity if min_velocity else self.VELOCITY_LIMIT
        self.position = 0.0
        
    def __del__(self):
        pass

    def set_params(self, vmax):
        self.min_velocity = vmax
        self.max_velocity = vmax

    def get_movements(self, new_position, is_first_move):
        movements = []
        ti = 0
        distance = new_position - self.position
        tf = self.get_movement_time(math.fabs(distance), is_first_move)
        while ti - self.TIME_STEP <= tf:
            new_pos = self.get_position_change_at(ti, is_first_move)
            change = new_pos if distance > 0 else -new_pos
            movements.append(self.position + change)
            ti += self.TIME_STEP
        self.position = new_position

        return movements

    def get_movement_time(self, d, is_first_move):
        v = self.VELOCITY_LIMIT if is_first_move or self.max_velocity == 0 else self.max_velocity
        a = self.ACCELERATION_LIMIT if is_first_move else self.acceleration

        max_time = v / a
        t1 = math.sqrt((2*d)/a)
        if t1 < max_time:
            return t1

        t2 = (d - ((a*(max_time**2)) / 2)) / v
        return max_time + t2

    def get_position_change_at(self, t, is_first_move):
        v = self.VELOCITY_LIMIT if is_first_move else self.max_velocity
        a = self.ACCELERATION_LIMIT if is_first_move else self.acceleration

        max_time = v / a
        if t < max_time:
            return (a * (t ** 2)) / 2

        c = (v**2 / (2 * a)) - (v * max_time)
        return (v * t) + c

    def move_absolute(self, final_position, timeout, is_first_move):
        original_position = self.position
        distance = final_position - self.position
        current_time = 0

        while math.fabs(self.position - original_position) < math.fabs(distance):
            current_time += self.TIME_STEP
            if current_time > timeout / 1000:
                raise Exception("Virtual Motor will take too long to move")

            new_pos = self.get_position_change_at(current_time, is_first_move)
            self.position += new_pos if distance > 0 else -new_pos
            print(self.position)


