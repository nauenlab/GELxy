from picamera2 import Picamera2
import time
import datetime
import os
from AveragePictures import AveragePictures
import signal
import sys

DIRECTORY = '/home/saturn/Pictures'

# Initialize the camera
picam2 = Picamera2()
config = picam2.create_still_configuration({"size": (507, 380)})
picam2.configure(config)
picam2.start()

# Allow camera to adjust to settings
time.sleep(1)

#creates 'for' loop which takes specified amount of images "range(#):"
dt = datetime.datetime.now().strftime("%Y-%m-%d %H;%M;%S")
print(dt)

LOOP = True
sleep_time = 0.1

def exit_handler(*args):
    global LOOP
    if LOOP:
        LOOP = False
        time.sleep(sleep_time * 2)
        print("Exit!")
        AveragePictures(f"{DIRECTORY}/{dt}").average()
    else:
        sys.exit()
    

signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)


os.mkdir(f"{DIRECTORY}/{dt}")
i = 0
while LOOP:
    # Press Ctrl + C to break the loop, the Average Piictures function will then run
    print(i)
    picam2.capture_file(f"{DIRECTORY}/{dt}/image{i:04}.jpg")
    time.sleep(sleep_time)
    i += 1



