from Motor import Motor
from Lamp import Lamp
import threading


class Manager:

    def __init__(self, led_ampere, serial_number_x, serial_number_y, acceleration=None, max_velocity=None):
        self.x = Motor(serial_no=serial_number_x, acceleration=acceleration, max_velocity=max_velocity)
        self.y = Motor(serial_no=serial_number_y, acceleration=acceleration, max_velocity=max_velocity)
        home_threads = []
        for i in [self.x, self.y]:
            t = threading.Thread(target=i.home)
            home_threads.append(t)
            t.start()
        
        for t in home_threads:
            t.join()

        self.lamp = Lamp(led_ampere=led_ampere)

    def motors(self):
        return self.x, self.y

    def move(self, position):
        x_thread_target = self.x.jog_to
        y_thread_target = self.y.jog_to
        
        if position.lp:
            # turn on light and set movement speed
            if position.v[0] != 0:
                self.x.set_params(position.v[0])
            if position.v[1] != 0:
                self.y.set_params(position.v[1])
            self.lamp.turn_on()
        else:
            # set movement speed
            self.x.set_params(self.x.max_velocity)
            self.y.set_params(self.y.max_velocity)
            x_thread_target = self.x.move_absolute
            y_thread_target = self.y.move_absolute

        xt = threading.Thread(target=x_thread_target, args=(position.x,))
        yt = threading.Thread(target=y_thread_target, args=(position.y,))

        for thread in [xt, yt]:
            thread.start()

        for thread in [xt, yt]:
            thread.join()

        if position.lp:
            # turn on light
            self.lamp.turn_off()

    def __del__(self):
        try:
            self.x.__del__()
        except:
            pass
        try:
            self.y.__del__()
        except:
            pass
        try:
            self.lamp.__del__()
        except:
            pass
