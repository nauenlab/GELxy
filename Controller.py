
from Motor import Motor
from Lamp import Lamp
from VirtualMotor import VirtualMotor
from VirtualLamp import VirtualLamp
from Circle import Circle
from Canvas import Canvas
import threading

IS_VIRTUAL = False
motor_thread_sleep = 0.4
acceleration = 4.0  # mm/s
max_velocity = 2.6
min_velocity = 2.6


if IS_VIRTUAL:
    # Sets up a virtual simulation of the motors and LED
    deviceX = VirtualMotor(sleep_time=motor_thread_sleep, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    deviceY = VirtualMotor(sleep_time=motor_thread_sleep, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    lamp = VirtualLamp(led_ampere=0.01)
    canvas = Canvas(dimensions=500)
else:
    # Sets up the actual motors and LED
    deviceX = Motor(sleep_time=motor_thread_sleep, serial_no="27602218", acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    deviceY = Motor(sleep_time=motor_thread_sleep, serial_no="27264864", acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    lamp = Lamp(led_ampere=0.01)


def main():
    shape = Circle(diameter=10)
    coordinates = shape.get_coordinates()
    move(coordinates)


def move(coordinates):
    for i in coordinates:
        print(i.x, i.y)
        xt = threading.Thread(target=deviceX.move_absolute, args=(i.x,))
        yt = threading.Thread(target=deviceY.move_absolute, args=(i.y,))
        for thread in [xt, yt]:
            thread.start()

        for thread in [xt, yt]:
            thread.join()
            

if __name__ == "__main__":
    main()
