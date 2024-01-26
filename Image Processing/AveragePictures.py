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
        self.target_output = "Average.jpg"

    def average(self):
        print("Averaging Pictures...")
        allfiles = os.listdir(self.directory)
        imlist = [filename for filename in allfiles if filename[-4:] in [".jpg", ".JPG"] and "image" in filename]
        imlist = sorted(imlist)

        result = np.zeros_like(imlist[0], dtype=np.uint8)

        num_pics = 0
        frame_list = []
        for (i, im) in enumerate(tqdm(imlist, desc="Pictures Left", unit="image")):
            result = self.get_result(result, im)

            if self.CREATE_GIF:
                frame_list.append(result.copy())

            if (i+1) % 100 == 0:
                num_pics += 1
                cv2.imwrite(f"{self.directory}/checkpoint{num_pics}.jpg", result)
                result = np.zeros_like(imlist[0], dtype=np.uint8)
                result = self.get_result(result, f"checkpoint{num_pics}.jpg")
        
        # result = self.increase_contrast(result)
        # self.canny_edge_detection(result)
        result = self.upscale(result)

        print(f"Saving {self.target_output}")
        cv2.imwrite(os.path.join(self.directory, self.target_output), result)

        self.canny_edge_detection(os.path.join(self.directory, self.target_output))
        # self.fill_edges(os.path.join(self.directory, "Average2.jpg"))

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
        image = cv2.imread(os.path.join(self.directory, filename))
        image = image.astype(np.uint8)
        # print(result)
        # print(image)
        result = np.maximum(result, image)
        
        return result

    def increase_contrast(self, result):
        res = result.copy()
        mx = 0
        for (i, row) in enumerate(tqdm(result, desc="Increasing Contrast", unit="row")):
            for (j, pixel_value) in enumerate(row):
                mx = max(mx, sum(pixel_value) / 3)
                if sum(pixel_value) / 3 > 180:
                    res[i][j] = (255, 255, 255)
                else:
                    res[i][j] = (0, 0, 0)
        
        print("MAX BRIGHTNESS:", mx)
        return res
    
    def canny_edge_detection(self, filename):
        img = cv2.imread(filename)

        # Convert to graycsale
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # Blur the image for better edge detection
        img_blur = cv2.GaussianBlur(img_gray, (9, 9), 0)
        cv2.imwrite(os.path.join(self.directory, "Average_blur.jpg"), img_blur)

        # Canny Edge Detection
        edges = cv2.Canny(image=img_blur, threshold1=10, threshold2=20)  # Canny Edge Detection
        cv2.imwrite(os.path.join(self.directory, "Average2.jpg"), edges)


    def fill_edges(self, filename):
        img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        hh, ww = img.shape[:2]

        # threshold
        thresh = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)[1]

        # get the (largest) contour
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]
        big_contour = max(contours, key=cv2.contourArea)

        # draw white filled contour on black background
        result = np.zeros_like(img)
        cv2.drawContours(result, [big_contour], 0, (255,255,255), cv2.FILLED)

        # save results
        cv2.imwrite(os.path.join(self.directory, "Average3.jpg"), result)


    def separate_background2(self, img):
        mask = np.zeros(img.shape[:2],np.uint8)
        bgdModel = np.zeros((1,65),np.float64)
        fgdModel = np.zeros((1,65),np.float64)
        rect = (50,50,450,290)
        cv2.grabCut(img,mask,rect,bgdModel,fgdModel,5,cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask==2)|(mask==0),0,1).astype('uint8')
        img2 = img*mask2[:,:,np.newaxis]
        return img2

    def separate_background(self, img):

        # Blur to image to reduce noise
        myimage = cv2.GaussianBlur(img,(5,5), 0)
    
        # We bin the pixels. Result will be a value 1..5
        bins=np.array([0,51,102,153,204,255])
        img[:,:,:] = np.digitize(img[:,:,:],bins,right=True)*51
    
        # Create single channel greyscale for thresholding
        myimage_grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
        # Perform Otsu thresholding and extract the background.
        # We use Binary Threshold as we want to create an all white background
        ret,background = cv2.threshold(myimage_grey,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    
        # Convert black and white back into 3 channel greyscale
        background = cv2.cvtColor(background, cv2.COLOR_GRAY2BGR)
    
        # Perform Otsu thresholding and extract the foreground.
        # We use TOZERO_INV as we want to keep some details of the foregorund
        ret,foreground = cv2.threshold(myimage_grey,0,255,cv2.THRESH_TOZERO_INV+cv2.THRESH_OTSU)  #Currently foreground is only a mask
        foreground = cv2.bitwise_and(myimage,myimage, mask=foreground)  # Update foreground with bitwise_and to extract real foreground
    
        # Combine the background and foreground to obtain our final image
        finalimage = background+foreground
    
        return finalimage

    def upscale(self, image):
        sr = cv2.dnn_superres.DnnSuperResImpl_create()

        # Read the desired model
        model_name = "EDSR_x3.pb"
        if os.path.exists("/home/saturn/Documents/GELxy"):
            path = f"/home/saturn/Documents/GELxy/{model_name}"
        elif os.path.exists("/Users/yushrajkapoor/Desktop/NauenLab/GELxy"):
            path = f"/Users/yushrajkapoor/Desktop/NauenLab/GELxy/{model_name}"
        sr.readModel(path)

        # Set the desired model and scale to get correct pre- and post-processing
        sr.setModel("edsr", 3)

        # Upscale the image
        result = sr.upsample(image)
        
        return result


if __name__ == '__main__':
    AveragePictures('2024-01-26 15;23;40').average()
    # AveragePictures('/Users/yushrajkapoor/Desktop/Atom').average()
