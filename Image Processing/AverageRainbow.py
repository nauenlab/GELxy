import os

import numpy as np
from PIL import Image
from tqdm import tqdm
from AveragePictures import AveragePictures

if os.path.exists("/home/saturn/Documents/GELxy"):
    os.chdir("/home/saturn/Documents/GELxy/Image Processing/Pictures")
elif os.path.exists("/Users/yushrajkapoor/Desktop/NauenLab/GELxy"):
    os.chdir("/Users/yushrajkapoor/Desktop/NauenLab/GELxy/Image Processing/Pictures")


class AverageRainbow:

    threshold = 150

    def __init__(self, directory):
        self.directory = directory

    def average(self):
        # Get a list of all image files in the directory
        allfiles = os.listdir(self.directory)
        image_files = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG"] and "image" in filename]
        image_files = sorted(image_files)

        valid_files = [i for i in tqdm(image_files, desc="Finding Valid Pictures", unit="image") if self.has_light_point(Image.open(os.path.join(self.directory, i)))]
        if len(valid_files) > 0:
            # Open the first image to get dimensions
            contrast_directory = self.directory + "/contrast"
            if not os.path.exists(contrast_directory):
                os.mkdir(contrast_directory)

            # Loop through each image and add pixel values
            for (i, image_file) in enumerate(tqdm(valid_files, desc="Processing images", unit="image")):
                if os.path.exists(os.path.join(contrast_directory, image_file)):
                    continue

                img = Image.open(os.path.join(self.directory, image_file))
                img = self.increase_contrast(img, float(i) / len(valid_files))
                img.save(os.path.join(contrast_directory, image_file))

            AveragePictures(contrast_directory).average()
            os.rename(os.path.join(contrast_directory, "Average.jpg"), os.path.join(self.directory, "AverageRainbow.jpg"))

            # averaged_img = Image.open(os.path.join(self.directory, "AverageRainbow.jpg"))
            # averaged_img.show()
        else:
            print("No images found in the directory.")

    def has_light_point(self, img):
        # Define the brightness threshold (adjust as needed)

        # Convert the image to grayscale for simplicity in brightness check
        img_gray = img.convert('L')

        # Get image data as a list of pixel values
        pixel_values = list(img_gray.getdata())

        # Check if any pixel is brighter than the threshold
        is_bright = any(pixel > self.threshold for pixel in pixel_values)
        return is_bright

    def increase_contrast(self, img, rainbow_fraction):
        enhanced_pixels = []
        for pixel_value in img.getdata():

            if sum(pixel_value) / 3 > self.threshold:
                enhanced_pixels.append(self.interpolate_color(rainbow_fraction))  # Adjust the multiplier for desired contrast change
            else:
                enhanced_pixels.append((0, 0, 0))

        enhanced_image = Image.new(img.mode, img.size)
        enhanced_image.putdata(enhanced_pixels)
        return enhanced_image

    @staticmethod
    def interpolate_color(step_fraction):
        print(step_fraction)
        # Rainbow colors in RGB format
        rainbow_colors = [
            (255, 0, 0),  # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
            (75, 0, 130),  # Indigo
            (128, 0, 128)  # Violet
        ]

        num_colors = len(rainbow_colors) - 1
        index = step_fraction * num_colors
        start_color_index = int(index)
        end_color_index = min(start_color_index + 1, num_colors)

        start_r, start_g, start_b = rainbow_colors[start_color_index]
        end_r, end_g, end_b = rainbow_colors[end_color_index]

        # Calculate the interpolation between colors
        fraction = index - start_color_index
        r = round((end_r - start_r) * fraction) + start_r
        g = round((end_g - start_g) * fraction) + start_g
        b = round((end_b - start_b) * fraction) + start_b

        return r, g, b


if __name__ == '__main__':
    AverageRainbow('2024-01-26 15;23;40').average()
    # RainbowAverage('/home/saturn/Pictures/2023-11-17 14;47;09').average()
    # AverageRainbow('/Users/yushrajkapoor/Desktop/SquareStar').average()
