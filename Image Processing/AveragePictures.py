import os
import cv2
import numpy as np
import imageio.v2 as imageio
import subprocess


class AveragePictures:
    
    quality = 50  # Adjust the quality (0-100) as needed

    def __init__(self, directory):
        self.directory = directory

    def average(self):
        allfiles = os.listdir(self.directory)
        imlist = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG"] and "image" in filename]
        imlist = sorted(imlist)

        result = np.zeros_like(imlist[0], dtype=np.uint8)

        num_pics = 0
        # frame_list = []
        for (i, im) in enumerate(imlist):
            print(len(imlist) - i, "images left         ", end='\r')
            result = self.get_result(result, f"{self.directory}/{im}")
            # frame_list.append(result.copy())

            if (i+1) % 100 == 0:
                num_pics += 1
                cv2.imwrite(f"{self.directory}/checkpoint{num_pics}.jpg", result)
                result = np.zeros_like(imlist[0], dtype=np.uint8)
                result = self.get_result(result, f"{self.directory}/checkpoint{num_pics}.jpg")


        print("Saving Average.jpg")
        cv2.imwrite(f"{self.directory}/Average.jpg", result)

        # print("Saving Average.gif, this may take a minute")
        # output_file = f"{self.directory}/Average.gif"
        # writer = imageio.get_writer(output_file, duration=2)

        # # Write frames one by one
        # for (i, frame) in enumerate(frame_list):
        #     print(len(frame_list) - i, "frames left         ", end='\r')
        #     writer.append_data(frame)

        # # Close the writer
        # writer.close()


    def get_result(self, result, filename):
        image = cv2.imread(filename)
        image = image.astype(np.uint8)
        result = np.maximum(result, image)
        return result


if __name__ == '__main__':
    AveragePictures('/home/saturn/Pictures/2023-11-03 2023-11-03 14;39;51').average()
