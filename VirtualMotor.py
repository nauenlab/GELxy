



class VirtualMotor:
    def __init__(self, sleep_time, serial_no=None, acceleration=None, max_velocity=None, min_velocity=None):
        self.sleep_time = sleep_time
        self.serial_number = serial_no
        self.acceleration = acceleration if acceleration else 4.0
        self.max_velocity = max_velocity if max_velocity else 2.6
        self.min_velocity = min_velocity if min_velocity else 2.6


    def move_absolute(self, position):
        print()


