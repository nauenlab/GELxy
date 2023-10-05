from threading import Thread
import os


class VirtualLamp:

    TIME_STEP = 0.01  # 0.01 s
    CURING_RATE = 0.5  # 0.5 alpha / second

    def __init__(self, led_ampere, motors_manager, canvas):
        self.led_ampere = led_ampere
        self.deviceX = motors_manager.x
        self.deviceY = motors_manager.y
        self.canvas = canvas
        self.is_on = False

    def __del__(self):
        pass

    def turn_on(self):
        self.is_on = True
        # self.cure()
        Thread(target=self.cure).start()

    def cure(self):
        cure_per_step = self.CURING_RATE * self.TIME_STEP
        time_progress = -1

        while self.is_on:
            ct = int(os.environ.get("current_time"))
            print(ct)
            if ct > time_progress:
                time_progress = ct
                x_pos = int(self.deviceX.position * self.canvas.mm_to_pixel_ratio)
                y_pos = int(self.deviceY.position * self.canvas.mm_to_pixel_ratio)
                self.canvas.pixels[x_pos][y_pos].alpha += cure_per_step
                print("curing")

    def turn_off(self):
        self.is_on = False

