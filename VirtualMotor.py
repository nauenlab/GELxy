import math


class VirtualMotor:

    VELOCITY_LIMIT = 2.6
    ACCELERATION_LIMIT = 4.0

    def __init__(self, timing_manager, serial_no=None, acceleration=None, max_velocity=None, min_velocity=None):
        self.timing_manager = timing_manager
        self.serial_number = serial_no
        self.acceleration = acceleration if acceleration else self.ACCELERATION_LIMIT
        self.max_velocity = max_velocity if max_velocity else self.VELOCITY_LIMIT
        self.min_velocity = min_velocity if min_velocity else self.VELOCITY_LIMIT
        self.position = 0.0
        
    def __del__(self):
        pass

    def get_position_change_at(self, t, is_first_move):
        v = self.VELOCITY_LIMIT if is_first_move else self.max_velocity
        a = self.ACCELERATION_LIMIT if is_first_move else self.acceleration

        max_time = v / a
        if t > max_time:
            c = (v**2 / (2 * a)) - (v * max_time)
            return (v * t) + c
        else:
            return (a * (t**2))/2

    def move_absolute(self, final_position, timeout, is_first_move):
        original_position = self.position
        distance = final_position - self.position
        prev_time = -1

        while math.fabs(self.position - original_position) < math.fabs(distance):
            if prev_time == self.timing_manager.current_time:
                continue

            if self.timing_manager.current_time > timeout / 1000:
                raise Exception("Virtual Motor will take too long to move")

            new_pos = self.get_position_change_at(self.timing_manager.current_time, is_first_move)
            self.position = new_pos if distance > 0 else -new_pos
            print(new_pos, final_position, self.timing_manager.current_time)
            self.timing_manager.increment(id(self))

        self.timing_manager.reset()




