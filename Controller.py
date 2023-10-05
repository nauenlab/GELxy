from Circle import Circle
from Canvas import Canvas
import threading
import signal
import time
import sys

IS_VIRTUAL = True
motor_thread_sleep = 0.4
acceleration = 4.0  # mm/s
max_velocity = 2.0
min_velocity = 2.0


if IS_VIRTUAL:
    from VirtualMotor import VirtualMotor
    from VirtualLamp import VirtualLamp
    from VirtualMotorsManager import VirtualMotorsManager
    # Sets up a virtual simulation of the motors and LED
    motors_manager = VirtualMotorsManager(acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    # deviceX = VirtualMotor(timing_manager=timing_manager, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    # deviceY = VirtualMotor(timing_manager=timing_manager, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    canvas = Canvas(dimensions_cm=1)
    lamp = VirtualLamp(led_ampere=0.01, deviceX=deviceX, deviceY=deviceY, canvas=canvas, timing_manager=timing_manager)
else:
    from Motor import Motor
    from Lamp import Lamp
    from MotorsManager import MotorsManager
    # Sets up the actual motors and LED

    motors_manager = MotorsManager(serial_number_x="27602218", serial_number_y="27264864", motor_thread_sleep=motor_thread_sleep, acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    # deviceX, deviceY = motors_manager.motors()
    # deviceX = Motor(sleep_time=motor_thread_sleep, serial_no="27602218", acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    # deviceY = Motor(sleep_time=motor_thread_sleep, serial_no="27264864", acceleration=acceleration, max_velocity=max_velocity, min_velocity=min_velocity)
    lamp = Lamp(led_ampere=0.01)   


def main():
    shape = Circle(diameter=10, step_size=0.1)
    coordinates = shape.get_coordinates()
    move(coordinates)


def move(coordinates, timeout=10000, is_first_move=False):
    if len(coordinates) > 1:
        move(coordinates=[coordinates[0]], timeout=30000, is_first_move=True)
        coordinates = coordinates[1:]

    for i in coordinates:
        print(i.x, i.y)
        # xt = threading.Thread(target=deviceX.move_absolute, args=(i.x, timeout, is_first_move))
        # yt = threading.Thread(target=deviceY.move_absolute, args=(i.y, timeout, is_first_move))
        # yt = threading.Thread()

        if not is_first_move:
            # turn on light
            lamp.turn_on()

        motors_manager.move(i, timeout, is_first_move)

        # for thread in [xt, yt]:
        #     thread.start()
        #
        # for thread in [xt, yt]:
        #     thread.join()
            
        if not is_first_move:
            # turn on light
            lamp.turn_off()

            

def exit_handler(*args):
    print("Cleaning Up!")
    lamp.__del__()
    # deviceX.__del__()
    # deviceY.__del__()
    motors_manager.__del__()
    sys.exit(0)

signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)


if __name__ == "__main__":
    main()
    exit_handler()
