import os
import numpy
import PIL
from PIL import Image, ImageEnhance, ImageDraw
import cv2
import numpy as np
import imageio

class AveragePictures:

    def __init__(self, directory):
        self.directory = directory

    def average(self):
        allfiles = os.listdir(self.directory)
        imlist = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG"] and "image" in filename]

        result = np.zeros_like(imlist[0], dtype=np.uint8)

        frame_list = []
        for (i, im) in enumerate(imlist):
            print(len(imlist) - i, "images left         ", end='\r')
            image = cv2.imread(f"{self.directory}/{im}")
            image = image.astype(np.uint8)
            result = np.maximum(result, image)
            frame_list.append(result.copy()) 

        print("Saving Average.jpg")
        cv2.imwrite(f"{self.directory}/Average.jpg", result)
        # only if you have enough RAM, Do not run on the Raspberry pi!!!
        print("Saving Average.gif, this may take a minute")
        imageio.mimsave(f"{self.directory}/Average.gif", frame_list, duration=2) 



if __name__ == '__main__':
    AveragePictures('/home/saturn/Pictures/2023-11-02 17;11;30').average()