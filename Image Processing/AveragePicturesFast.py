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

    CREATE_GIF = False  # This should only be true for devices that have enuogh RAM (Do not set true for Raspberry Pi)

    def __init__(self, directory):
        self.directory = directory

    def average(self):
        allfiles = os.listdir(self.directory)
        imlist = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG"] and "image" in filename]
        imlist = sorted(imlist)

        result = np.zeros_like(imlist[0], dtype=np.uint8)

        # num_pics = 0
        frame_list = []
        for (i, im) in enumerate(tqdm(imlist, desc="Pictures Left", unit="image")):
            result = self.get_result(result, im)
            
            if self.CREATE_GIF:
                frame_list.append(result.copy())

            # if (i+1) % 100 == 0:
            #     num_pics += 1
            #     cv2.imwrite(f"{self.directory}/checkpoint{num_pics}.jpg", result)
            #     result = np.zeros_like(imlist[0], dtype=np.uint8)
            #     result = self.get_result(result, f"checkpoint{num_pics}.jpg")


        print("Saving Average_Fast.jpg")
        cv2.imwrite(f"{self.directory}/Average_Fast.jpg", result)

        if self.CREATE_GIF:
            # writer = imageio.get_writer(output_file, duration=2)

            # Write frames one by one
            # for (i, frame) in enumerate(tqdm(frame_list, desc="Frames Left", unit="frame")):
            #     writer.append_data(frame)
            
            frames = [Image.fromarray(np.uint8(frame)).convert('RGB') for frame in frame_list]
            print("Saving Average.gif, this may take a minute")
            # frames = [Image.open(f"{self.directory}/{image}") for image in imlist]
            output_file = os.path.join(self.directory, "Average_Fast.gif")
            frames[0].save(output_file, format="GIF", append_images=frames[1:], save_all=True, duration=10000, loop=0)

            # # Close the writer
            # writer.close()
        
            # duration = 10  # seconds
            # gif = imageio.mimread(output_file)

            # imageio.mimsave(output_file, gif, fps=int(len(frame_list) / duration))

    def get_result(self, result, filename):
        image = cv2.imread(os.path.join(self.directory, filename))
        image = image.astype(np.uint8)
        result = np.maximum(result, image)
        
        return result


if __name__ == '__main__':
    AveragePictures('2024-01-26 20;42;14').average()
    # AveragePictures('/Users/yushrajkapoor/Desktop/Atom').average()