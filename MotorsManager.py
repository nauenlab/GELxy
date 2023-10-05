from Motor import Motor
import threading


class MotorsManager:

    def __init__(self, serial_number_x, serial_number_y, motor_thread_sleep, acceleration=None, max_velocity=None, min_velocity=None):
        self.x = Motor(sleep_time=motor_thread_sleep, serial_no=serial_number_x, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
        self.y = Motor(sleep_time=motor_thread_sleep, serial_no=serial_number_y, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)

    def motors(self):
        return self.x, self.y

    def move(self, position, timeout, is_first_move):
        print(position.x, position.y)
        xt = threading.Thread(target=self.x.move_absolute, args=(position.x, timeout, is_first_move))
        yt = threading.Thread(target=self.y.move_absolute, args=(position.y, timeout, is_first_move))

        for thread in [xt, yt]:
            thread.start()

        for thread in [xt, yt]:
            thread.join()

    def __del__(self):
        self.x.__del__()
        self.y.__del__()