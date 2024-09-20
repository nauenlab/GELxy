import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)))
from Motor import Motor
from Lamp import Lamp
import threading


class Manager:
    """
    The Manager class controls the motors and lamp in the GELxy hardware system.

    Args:
        serial_number_x (str): The serial number of the Thorlabs KDC101 motor for the x-axis.
        serial_number_y (str): The serial number of the Thorlabs KDC101 motor for the y-axis.
        acceleration (float, optional): The acceleration value for the motors. Defaults to None.
        max_velocity (float, optional): The maximum velocity value for the motors. Defaults to None.
    """

    def __init__(self, serial_number_x, serial_number_y, lamp_serial_number, acceleration=None, max_velocity=None):
        self.lamp = Lamp(lamp_serial_number)
        self.x = Motor(serial_no=serial_number_x, acceleration=acceleration, max_velocity=max_velocity)
        self.y = Motor(serial_no=serial_number_y, acceleration=acceleration, max_velocity=max_velocity)
        home_threads = []
        for i in [self.x, self.y]:
            t = threading.Thread(target=i.home)
            home_threads.append(t)
            t.start()
        
        for t in home_threads:
            t.join()

    def motors(self):
        """
        Get the motor objects for the x and y axes.

        Returns:
            tuple: A tuple containing the motor objects for the x and y axes.
        """
        return self.x, self.y

    def move(self, position):
        """
        Move the motors to the specified position.

        Args:
            position (Position): The position object containing the coordinates and movement parameters.
        """
        x_thread_target = self.x.jog_to
        y_thread_target = self.y.jog_to
        
        if position.lp:
            # turn on light and set movement speed
            if position.v[0] != 0:
                self.x.set_params(position.v[0])
            if position.v[1] != 0:
                self.y.set_params(position.v[1])
            self.lamp.turn_on(position.a)
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
            # turn off light
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
