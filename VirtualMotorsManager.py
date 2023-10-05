from VirtualMotor import VirtualMotor
import threading


class MotorsManager:

    def __init__(self, acceleration=None, max_velocity=None, min_velocity=None):
        self.x = VirtualMotor(acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
        self.y = VirtualMotor(acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)

    def motors(self):
        return self.x, self.y

    def move(self, position, timeout, is_first_move):
        print(position.x, position.y)

        x_is_primary = False
        if (self.x.position - position.x) > (self.y.position - position.x):
            x_is_primary = True

        xt = threading.Thread(target=self.x.move_absolute, args=(position.x, timeout, is_first_move, x_is_primary))
        yt = threading.Thread(target=self.y.move_absolute, args=(position.y, timeout, is_first_move, not x_is_primary))

        for thread in [xt, yt]:
            thread.start()

        for thread in [xt, yt]:
            thread.join()

    def __del__(self):
        self.x.__del__()
        self.y.__del__()