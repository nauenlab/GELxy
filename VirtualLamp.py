import time
from threading import Thread


class VirtualLamp:

    TIME_STEP = 0.1
    CURING_RATE = 0.5  # 0.5 alpha / second

    def __init__(self, led_ampere, deviceX, deviceY, canvas, timing_manager):
        self.led_ampere = led_ampere
        self.deviceX = deviceX
        self.deviceY = deviceY
        self.canvas = canvas
        self.timing_manager = timing_manager
        self.is_on = False

    def __del__(self):
        pass
        
    def turn_on(self):
        self.is_on = True
        Thread(target=self.cure).start()

    def cure(self):
        cure_per_step = self.CURING_RATE * self.TIME_STEP
        time_progress = 0
        while self.is_on:
            if self.timing_manager.current_time > time_progress:
                time_progress = self.timing_manager.current_time
                xpos = int(self.deviceX.position * self.canvas.mm_to_pixel_ratio)
                ypos = int(self.deviceY.position * self.canvas.mm_to_pixel_ratio)
                self.canvas.pixels[xpos][ypos].alpha += cure_per_step
            # else:
            #     print("same time")

    def turn_off(self):
        self.is_on = False

