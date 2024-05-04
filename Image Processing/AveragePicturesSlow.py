import os
import cv2
import numpy as np
import imageio.v2 as imageio
from tqdm import tqdm
from PIL import Image
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)) + "/Pictures")

    
class AveragePictures:
    """
    A class to calculate the average of a series of images.

    Attributes:
        directory (str): The directory containing the images.
        target_output (str): The filename of the output image.
        threshold (int): The threshold value for contrast enhancement.
    """

    CREATE_GIF = False  # This should only be true for devices that have enough RAM (Do not set true for Raspberry Pi)

    def __init__(self, directory):
        """
        Initializes the AveragePictures object.

        Args:
            directory (str): The directory containing the images.
        """
        self.directory = directory
        self.target_output = "Average_Slow.jpg"
        self.threshold = 150

    def average(self):
        """
        Calculates the average of the images in the directory.
        """
        # Get a list of all image files in the directory
        allfiles = os.listdir(self.directory)
        imlist = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG"] and "image" in filename]
        imlist = sorted(imlist)

        result = np.zeros_like(imlist[0], dtype=np.uint8)

        num_pics = 0
        frame_list = []

        contrast_directory = self.directory + "/contrast"
        if not os.path.exists(contrast_directory):
            os.mkdir(contrast_directory)

        # Loop through each image and add pixel values
        for (i, im) in enumerate(tqdm(imlist, desc="Pictures Left", unit="image")):
            if os.path.exists(os.path.join(contrast_directory, im)):
                continue

            img = Image.open(os.path.join(self.directory, im))
            img = self.increase_contrast(img)
            img.save(os.path.join(contrast_directory, im))
            result = self.get_result(result, os.path.join("contrast", im))

            if self.CREATE_GIF:
                frame_list.append(result.copy())

        print(f"Saving {self.target_output}")
        cv2.imwrite(os.path.join(self.directory, self.target_output), result)

        if self.CREATE_GIF:
            print("Saving Average.gif, this may take a minute")
            output_file = os.path.join(self.directory, "Average.gif")
            writer = imageio.get_writer(output_file, duration=2)

            # Write frames one by one
            for (i, frame) in enumerate(tqdm(frame_list, desc="Frames Left", unit="frame")):
                writer.append_data(frame)

            # Close the writer
            writer.close()

    def get_result(self, result, filename):
        """
        Adds the pixel values of an image to the result.

        Args:
            result (numpy.ndarray): The current result image.
            filename (str): The filename of the image to be added.

        Returns:
            numpy.ndarray: The updated result image.
        """
        image = cv2.imread(os.path.join(self.directory, filename))
        image = image.astype(np.uint8)
        result = np.maximum(result, image)

        return result

    def increase_contrast(self, img):
        """
        Increases the contrast of an image.

        Args:
            img (PIL.Image.Image): The input image.

        Returns:
            PIL.Image.Image: The image with increased contrast.
        """
        enhanced_pixels = []
        for pixel_value in img.getdata():
            if sum(pixel_value) / 3 > self.threshold:
                white = (255, 255, 255)
                blue = (0, 0, 255)
                enhanced_pixels.append(blue)
            else:
                enhanced_pixels.append((0, 0, 0))

        enhanced_image = Image.new(img.mode, img.size)
        enhanced_image.putdata(enhanced_pixels)
        return enhanced_image

if __name__ == '__main__':
    AveragePictures('2024-05-03 18;54;47').average()
    # AveragePictures('/Users/yushrajkapoor/Desktop/Atom').average()
