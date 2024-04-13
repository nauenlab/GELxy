import cv2
from picamera2 import Picamera2
import time
import datetime
import os
import signal
import sys

LOOP = True
cam_size = (1280,720)

#piCam sensor dimensions: 6.287mm x 4.712mm

def perform_calibration():
    """
    Perform calibration to determine the beam diameter.

    This function initializes the camera, captures an image, finds the pixel diameter of a bright dot in the image,
    and calculates the beam diameter in millimeters. It continuously performs the calibration until interrupted.
    """
    # Initialize the camera
    config = piCam.create_still_configuration({"size": cam_size})
    piCam.configure(config)
    piCam.start()

    while True:
        piCam.capture_file(f"calibration.jpg")
        pixel_diameter = find_pixel_diameter()
        if not pixel_diameter:
            print("No bright dot found in the image.", end='\r')
            continue
        # print(diameter)
        mm_diameter = (pixel_diameter / float(cam_size[0])) * 6.287
        print(f"Beam Diameter: {mm_diameter}\t", end='\r')
        time.sleep(0.25)


def find_pixel_diameter():
    """
    Find the pixel diameter of a bright dot in the image.

    This function reads the calibration image, converts it to grayscale, applies a threshold to isolate the bright dot,
    finds the contours, and determines the contour with the maximum area. It then calculates the diameter of the dot
    and returns it.
    """
    image = cv2.imread('calibration.jpg') 
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply threshold to isolate the bright dot
    _, thresh = cv2.threshold(gray_image, 150, 255, cv2.THRESH_BINARY)

    # Find contours
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Find the contour with the maximum area (assuming it represents the dot)
    if contours:
        max_contour = max(contours, key=cv2.contourArea)
        (x, y), radius = cv2.minEnclosingCircle(max_contour)
        diameter = radius * 2

        # Draw the contour and the circle around the dot
        cv2.drawContours(image, [max_contour], -1, (0, 255, 0), 2)
        cv2.circle(image, (int(x), int(y)), int(radius), (0, 0, 255), 2)

        return diameter
    else:
        return None


def exit_handler(*args):
    """
    Handle the exit signal.

    This function is called when the program receives a termination signal (SIGTERM) or an interrupt signal (SIGINT).
    It stops the camera, performs the final calibration, and exits the program.
    """
    global LOOP
    if LOOP:
        LOOP = False
        cv2.destroyAllWindows()
        piCam.stop()
        time.sleep(1)
        print("Calibrating")
        perform_calibration()
    else:
        print()
        sys.exit()


signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)

piCam = Picamera2()
piCam.preview_configuration.main.size = cam_size
piCam.preview_configuration.main.format = "RGB888"
piCam.configure("preview")
piCam.exposure_mode = "off"
piCam.awb_mode = "off"
piCam.start()
controls = {"ExposureTime": 10000, "AnalogueGain": 1.0, "ColourGains": (3.76, 1.5)}
piCam.set_controls(controls)

while LOOP:
    frame = piCam.capture_array()
    cv2.imshow("piCam", frame)
    if cv2.waitKey(1) == ord('q'):
        break




    



    
    



