from matplotlib import pyplot as plt
import cv2
import numpy as np


def show(img, cmap=None):
    """
    Display an image using matplotlib.
    
    Parameters:
    img (numpy.ndarray): Image to display
    cmap (str): Colormap to use
    """
    plt.imshow(img, cmap=cmap)
    plt.axis('off')
    plt.show()

def view_layers(layers):
    # get width and height of subplot grid using number of layers
    n_layers = len(layers)
    n_cols = 3
    n_rows = (n_layers + n_cols - 1) // n_cols
    fig, axes = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(18, 12))
    fig.tight_layout()
    axes = axes.flatten()
    for i, layer in enumerate(layers):
        ax = axes[i]
        ax.imshow(layer)
        ax.axis('off')
    plt.show()

def binarize(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    binary_img = (gray > 0.6).astype(np.float32)

    return binary_img

def dilate_and_erode(img):
    kernel = np.ones((4, 4), np.uint8)

    # plt.imshow(img, cmap='gray')
    # plt.show()

    img_erosion = cv2.erode(img, kernel, iterations=1)
    # plt.imshow(img_erosion, cmap='gray')
    # plt.show()

    binary_img = (img_erosion > 0.10).astype(np.float32)
    # plt.imshow(binary_img, cmap='gray')
    # plt.show()

    kernel = np.ones((2, 2), np.uint8)
    img_dilation = cv2.dilate(binary_img, kernel, iterations=1)
    # plt.imshow(img_dilation, cmap='gray')
    # plt.show()

    return img_dilation

def downsample(img):
    scale_factor = 500 / max(img.shape[0], img.shape[1])
    scale_factor = scale_factor if scale_factor < 1 else 1
    return cv2.resize(img, (0, 0), fx=scale_factor, fy=scale_factor)


def blur(img, kernel_size):
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), 0)

def canny_edge_detection(img):
    # img = (img * 255).astype(np.uint8)
    img = img.astype(np.uint8)
    
    # Otsu's thresholding: https://en.wikipedia.org/wiki/Otsu%27s_method
    high_thresh, thresh_im = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    low_thresh = 0.5*high_thresh
    
    edges = cv2.Canny(img, low_thresh, high_thresh)
    return edges

    # kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    # curvy_edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

    # contours, _ = cv2.findContours(curvy_edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # curvy_output_image = np.zeros_like(img, dtype=np.uint8)
    # curvy_output_image = cv2.cvtColor(curvy_output_image, cv2.COLOR_GRAY2BGR)
    # cv2.drawContours(curvy_output_image, contours, -1, (0, 255, 0), 2) # Draw contours in green

    
    # plt.imshow(edges, cmap='gray')
    # plt.show()
    # gray_img = cv2.cvtColor(edges, cv2.COLOR_BGR2GRAY)

    return gray_img

def remove_noise(img):
    return cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)