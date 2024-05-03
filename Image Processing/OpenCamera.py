import cv2
from picamera2 import Picamera2
import time
import enum


class VisualType(enum.Enum):
    show = 0
    save = 1


def open_camera(visual_type):
    """
    Opens the camera and displays the video feed.

    This function initializes the camera, configures the preview settings,
    sets the exposure time, analogue gain, and color gains, and continuously
    captures frames from the camera and displays them in a window. Pressing
    the 'q' key will quit the video feed.

    Returns:
        None
    """
    piCam = Picamera2()
    piCam.preview_configuration.main.size = (1280, 720)
    piCam.preview_configuration.main.format = "RGB888"
    piCam.configure("preview")
    piCam.start()

    controls = {"ExposureTime": 10000, "AnalogueGain": 1.0, "ColourGains": (3.76, 1.5)}
    piCam.set_controls(controls)

    if visual_type == VisualType.save:
        sleep_time = 0.4
        while True:
            piCam.capture_file(f"preview.jpg")
            time.sleep(sleep_time)
    elif visual_type == VisualType.show:
        while True:
            frame = piCam.capture_array()
            cv2.imshow("piCam", frame)
            if cv2.waitKey(1) == ord('q'):
                break
        cv2.destroyAllWindows()

open_camera(visual_type=VisualType.save)
