from picamera2 import Picamera2
import time
import datetime
import os
from AveragePicturesSlow import AveragePictures
import signal
import sys



"""
Continuously captures images using a camera and saves them to a specified directory.

The images are captured at a specified exposure time and with specified color gains.

Pressing Ctrl + C will break the loop and trigger the AveragePictures function to run.

Returns:
    None
"""

if os.path.exists("/home/saturn/Documents/GELxy"):
    DIRECTORY = '/home/saturn/Documents/GELxy/Image Processing/Pictures'
elif os.path.exists("/Users/yushrajkapoor/Desktop"):
    DIRECTORY = '/Users/yushrajkapoor/Desktop'

# Initialize the camera
picam2 = Picamera2()
config = picam2.create_still_configuration({"size": (507, 380)})
picam2.configure(config)
picam2.exposure_mode = "off"
picam2.awb_mode = "off"
picam2.start()

controls = {"ExposureTime": 10000, "AnalogueGain": 1.0, "ColourGains": (3.76, 1.5)}

picam2.set_controls(controls)

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
    # The first few pictures should be disregarded because the exposure control is still setting for come reason
    if i > 3:
        # Press Ctrl + C to break the loop, the Average Pictures function will then run
        picam2.capture_file(f"{DIRECTORY}/{dt}/image{i:04}.jpg")
    time.sleep(sleep_time)
    i += 1






