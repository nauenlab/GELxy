import os
import cv2
import numpy as np
import imageio.v2 as imageio
from tqdm import tqdm
from PIL import Image

if os.path.exists("/home/saturn/Documents/GELxy"):
    os.chdir("/home/saturn/Documents/GELxy/Image Processing/Pictures")
elif os.path.exists("/Users/yushrajkapoor/Desktop/NauenLab/GELxy"):
    os.chdir("/Users/yushrajkapoor/Desktop/NauenLab/GELxy/Image Processing/Pictures")


class AveragePictures:
    """
    A class that calculates the average picture from a directory of images.

    Args:
        directory (str): The directory path containing the images.

    Attributes:
        directory (str): The directory path containing the images.
        CREATE_GIF (bool): Flag indicating whether to create a GIF or not. This should only be true for devices that have enough RAM (Do not set true for Raspberry Pi).

    Methods:
        average(): Calculates the average picture and saves it to a file.
        get_result(result, filename): Helper method to calculate the result image.

    """

    CREATE_GIF = False  # This should only be true for devices that have enough RAM (Do not set true for Raspberry Pi)

    def __init__(self, directory):
        self.directory = directory

    def average(self):
        """
        Calculates the average picture from the images in the directory and saves it to a file.

        Returns:
            None

        """
        allfiles = os.listdir(self.directory)
        imlist = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG"] and "image" in filename]
        imlist = sorted(imlist)

        result = np.zeros_like(imlist[0], dtype=np.uint8)

        frame_list = []
        for (i, im) in enumerate(tqdm(imlist, desc="Pictures Left", unit="image")):
            result = self.get_result(result, im)
            
            if self.CREATE_GIF:
                frame_list.append(result.copy())

        print("Saving Average_Fast.jpg")
        cv2.imwrite(f"{self.directory}/Average_Fast.jpg", result)

        if self.CREATE_GIF:
            frames = [Image.fromarray(np.uint8(frame)).convert('RGB') for frame in frame_list]
            print("Saving Average.gif, this may take a minute")
            output_file = os.path.join(self.directory, "Average_Fast.gif")
            frames[0].save(output_file, format="GIF", append_images=frames[1:], save_all=True, duration=10000, loop=0)

    def get_result(self, result, filename):
        """
        Helper method to calculate the result image.

        Args:
            result (numpy.ndarray): The current result image.
            filename (str): The filename of the image to be processed.

        Returns:
            numpy.ndarray: The updated result image.

        """
        image = cv2.imread(os.path.join(self.directory, filename))
        image = image.astype(np.uint8)
        result = np.maximum(result, image)
        
        return result


if __name__ == '__main__':
    AveragePictures('2024-01-26 20;42;14').average()
    # AveragePictures('/Users/yushrajkapoor/Desktop/Atom').average()