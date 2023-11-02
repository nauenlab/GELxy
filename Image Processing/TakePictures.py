from picamera2 import Picamera2
import time
import datetime
import os
from AveragePictures import AveragePictures

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


os.mkdir(f"{DIRECTORY}/{dt}")
for i in range(1000):
    print(i)
    picam2.capture_file(f"{DIRECTORY}/{dt}/image{i}.jpg")
#sleep(#) creates delay in time lapse, so 1 image for every specified sleep time, runs until the range(#) function is finished
    time.sleep(.1)


AveragePictures(f"{DIRECTORY}/{dt}").average()
