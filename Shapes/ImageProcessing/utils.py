from matplotlib import pyplot as plt
import cv2
import numpy as np
from sklearn.cluster import KMeans
from PIL import Image
import tempfile
import atexit
import os


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


import numpy as np
import cv2
from skimage.metrics import structural_similarity as ssim
from scipy.ndimage import binary_dilation

def merge_similar_edges(layers, threshold=0.5, dilation_iter=2):
    """
    Detects and morphs similar edges from multiple grayscale intensity layers based on a normalized similarity score.
    
    Parameters:
    - layers: list of binary edge maps (numpy arrays) for each layer.
    - threshold: similarity score threshold for merging edges.
    - dilation_iter: number of iterations for binary dilation to handle slight mismatches.
    
    Returns:
    - morphed_edges: single edge map with similar edges morphed into one.
    """

    # Convert all layers to grayscale
    layers = [cv2.cvtColor(layer, cv2.COLOR_BGR2GRAY) if len(layer.shape) == 3 else layer for layer in layers]

    # Initialize the output morphed edge map as a copy of the first layer
    morphed_edges = np.copy(layers[0])
    
    for i in range(1, len(layers)):
        # Dilate edges to increase the overlap area for similarity comparison
        dilated_morphed = binary_dilation(morphed_edges, iterations=dilation_iter).astype(np.uint8)
        dilated_layer = binary_dilation(layers[i], iterations=dilation_iter).astype(np.uint8)
        
        # Compute structural similarity (SSIM) to measure edge similarity
        score, _ = ssim(dilated_morphed, dilated_layer, full=True)
        if score >= threshold:
            # Combine layers based on detected similarity
            morphed_edges = cv2.bitwise_or(morphed_edges, layers[i])
    
    return morphed_edges


def texture_segmentation(img, num_clusters):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Define Gabor filter parameters
    ksize = 31  # Filter size
    sigma = 4.0  # Standard deviation of the Gaussian function
    theta_values = [0, np.pi/4, np.pi/2, 3*np.pi/4]  # Orientation of the Gabor filters
    lamda = 10.0  # Wavelength of the sinusoidal factor
    gamma = 0.5  # Spatial aspect ratio
    psi = 0  # Phase offset
    
    # Apply Gabor filters at different orientations
    gabor_features = []
    for theta in theta_values:
        gabor_kernel = cv2.getGaborKernel((ksize, ksize), sigma, theta, lamda, gamma, psi, ktype=cv2.CV_32F)
        filtered_image = cv2.filter2D(img, cv2.CV_8UC3, gabor_kernel)
        gabor_features.append(filtered_image)

    # Stack Gabor features into a feature matrix
    gabor_features = np.array(gabor_features)
    feature_vector = gabor_features.transpose(1, 2, 0).reshape(-1, len(theta_values))

    # Apply K-means clustering on the feature vector
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    labels = kmeans.fit_predict(feature_vector)

    # Reshape the labels back to the image shape
    segmented_image = labels.reshape(img.shape)
    
    # Normalize and scale the segmented image for visualization
    segmented_image = (segmented_image * (255 / (num_clusters - 1))).astype(np.uint8)
    plt.imshow(segmented_image, cmap='viridis')
    plt.axis('off')
    plt.show()
    
    # Apply a colormap to the segmented image for better visualization
    color_segmented_image = cv2.normalize(segmented_image, None, 0, 255, cv2.NORM_MINMAX)
    
    return color_segmented_image


from skimage.feature import local_binary_pattern
from scipy.spatial.distance import cdist

def find_similar_textures(image, selected_region, radius=1, n_points=8, threshold=0.1):
    """
    Finds all regions in the image with a similar texture to the selected region.
    
    Parameters:
    - image: Input image (grayscale or color).
    - selected_region: Region selected by the user as a reference texture (numpy array).
    - radius: Radius for Local Binary Patterns (LBP) extraction (default 1).
    - n_points: Number of points for LBP extraction (default 8).
    - threshold: Similarity threshold (default 0.5), where lower is more restrictive.
    
    Returns:
    - similarity_map: Binary mask where similar textures are highlighted.
    """
    # Convert the image and selected region to grayscale if they are color images
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image
    
    if len(selected_region.shape) == 3:
        selected_gray = cv2.cvtColor(selected_region, cv2.COLOR_BGR2GRAY)
    else:
        selected_gray = selected_region

    # Compute LBP for the selected region
    selected_lbp = local_binary_pattern(selected_gray, n_points, radius, method='uniform')
    selected_hist, _ = np.histogram(selected_lbp.ravel(), bins=np.arange(0, n_points + 3), density=True)
    # plt.plot(selected_hist)
    # plt.title("Selected Texture Histogram")
    # plt.xlabel("LBP Value")
    # plt.ylabel("Normalized Frequency")
    # plt.show()
    
    # Initialize an empty similarity map
    similarity_map = np.zeros(image_gray.shape, dtype=np.uint8)

    # Slide a window across the image to compute LBP for each region
    window_size = selected_region.shape
    for i in range(0, image_gray.shape[0] - window_size[0], window_size[0] // 2):
        for j in range(0, image_gray.shape[1] - window_size[1], window_size[1] // 2):
            # Extract the window and compute LBP
            window = image_gray[i:i + window_size[0], j:j + window_size[1]]
            window_lbp = local_binary_pattern(window, n_points, radius, method='uniform')
            window_hist, _ = np.histogram(window_lbp.ravel(), bins=np.arange(0, n_points + 3), density=True)

            # Compare histograms using a similarity metric (e.g., Chi-square distance)
            distance = 0.5 * np.sum(((selected_hist - window_hist) ** 2) / (selected_hist + window_hist + 1e-10))
            if distance < threshold:
                # Mark this region as similar in the similarity map
                similarity_map[i:i + window_size[0], j:j + window_size[1]] = 255

    return similarity_map


def manual_segmentation(image, radius=1, n_points=8, threshold=0.1):
    """Allows the user to select a region and automatically highlights similar textures in the image."""
    roi = []
    is_drawing = False

    def mouse_callback(event, x, y, flags, param):
        nonlocal roi, is_drawing
        if event == cv2.EVENT_LBUTTONDOWN:
            roi = [(x, y)]
            is_drawing = True
        elif event == cv2.EVENT_LBUTTONUP:
            roi.append((x, y))
            is_drawing = False
    
    # Load and convert the image to grayscale
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    gray = gray.astype(np.uint8)
    lbp_image = local_binary_pattern(gray, n_points, radius, 'uniform')

    title = "Select Textures"

    cv2.namedWindow(title)
    cv2.setMouseCallback(title, mouse_callback)

    while True:
        display_img = image.copy()
        
        # Draw rectangle on display image for ROI selection
        if roi and len(roi) == 2:
            cv2.rectangle(display_img, roi[0], roi[1], (0, 255, 0), 2)
        
        cv2.imshow(title, display_img)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord("q"):  # Press 'q' to quit
            break
        elif key == ord("s") and len(roi) == 2:  # Press 's' to process ROI
            # Define the selected ROI
            x1, y1 = roi[0]
            x2, y2 = roi[1]
            selected_roi = display_img[min(y1, y2):max(y1, y2), min(x1, x2):max(x1, x2)]
            # mp = find_similar_textures(image, selected_roi, radius, n_points, threshold)
            # cv2.imshow("Similar Textures", mp)
            # cv2.waitKey(0)

            
            # Calculate LBP histogram for the selected ROI
            roi_hist, _ = np.histogram(selected_roi.ravel(), bins=np.arange(0, radius + 3), density=True)
            plt.bar(np.arange(0, n_points * radius + 2), roi_hist)
            plt.title("Selected Texture Histogram")
            plt.xlabel("LBP Value")
            plt.ylabel("Normalized Frequency")
            plt.show()
            
            # Create a mask to highlight similar textures
            h, w = gray.shape
            step = 2  # Define grid step size for comparing patches
            similar_texture_mask = np.zeros((h, w), dtype=np.uint8)

            # Scan the image in grid patches to find similar textures
            for y in range(0, h - step, step):
                for x in range(0, w - step, step):
                    patch = lbp_image[y:y + step, x:x + step]
                    patch_hist, _ = np.histogram(patch.ravel(), bins=np.arange(0, n_points * radius + 3), density=True)
                    distance = cdist([roi_hist], [patch_hist], metric='euclidean')[0][0]
                    
                    # Mark regions that match within threshold
                    if distance < threshold:
                        similar_texture_mask[y:y + step, x:x + step] = 255
            
            # Overlay the mask on the original image
            result = image.copy()
            result[similar_texture_mask == 255] = (0, 255, 0)  # Highlight matched textures in green
            # cv2.imshow(title, result)
            # cv2.waitKey(0)

    cv2.destroyAllWindows()


def fill_shape(image, color):
    # Convert to RGB if needed
    if len(image.shape) == 2 or image.shape[2] == 1:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    # Identify green edges ([0, 255, 0]) and create a mask for them
    green_mask = cv2.inRange(image, (0, 254, 0), (0, 256, 0))

    # Dilate the green mask to close small gaps in the edges
    kernel = np.ones((3, 3), np.uint8)
    green_mask_dilated = cv2.dilate(green_mask, kernel, iterations=2)

    # Invert the green mask to identify regions to fill
    inverted_mask = cv2.bitwise_not(green_mask_dilated)

    # Convert the image to grayscale and apply a threshold to create the background shape mask
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, background_shape = cv2.threshold(gray_image, 100, 255, cv2.THRESH_BINARY)

    # Apply a Gaussian blur to the background shape to smooth out artifacts
    blurred_background_shape = cv2.GaussianBlur(background_shape, (15, 15), 0)

    # Re-apply threshold to get a cleaner mask after blurring
    _, refined_background_shape = cv2.threshold(blurred_background_shape, 127, 255, cv2.THRESH_BINARY)

    # Resize and convert the refined mask if necessary to match inverted_mask dimensions
    if refined_background_shape.shape != inverted_mask.shape:
        refined_background_shape = cv2.resize(refined_background_shape, (inverted_mask.shape[1], inverted_mask.shape[0]))

    # Ensure both masks are of the same type
    inverted_mask = inverted_mask.astype(np.uint8)
    refined_background_shape = refined_background_shape.astype(np.uint8)


    # change the color of the background shape
    background_copy = refined_background_shape.copy()
    colored_background = cv2.cvtColor(background_copy, cv2.COLOR_GRAY2BGR)
    colored_background[refined_background_shape == 255] = color

    return colored_background


def combine_images(primary, secondary):
    if len(primary.shape) == 2:
        primary = cv2.cvtColor(primary, cv2.COLOR_GRAY2BGR)
    if len(secondary.shape) == 2:
        secondary = cv2.cvtColor(secondary, cv2.COLOR_GRAY2BGR)

    gray_edges = cv2.cvtColor(primary, cv2.COLOR_BGR2GRAY)
    _, binary_mask = cv2.threshold(gray_edges, 0, 255, cv2.THRESH_BINARY)
    secondary[binary_mask > 0] = 0

    primary_scale = 255 / np.max(primary)
    primary_scaled = (primary * primary_scale).astype('uint8')
    secondary_scale = 255 / np.max(secondary)
    secondary_scaled = (secondary * secondary_scale).astype('uint8')

    combined = cv2.addWeighted(primary_scaled, 1, secondary_scaled, 1, 0)
    return combined



def merge_layers(layers):
    """
    Merges multiple layers of binary images into a single image.
    
    Parameters:
    - layers: List of binary images (numpy arrays).
    
    Returns:
    - merged_image: Combined binary image.
    """
    merged_image = np.zeros(layers[0].shape, dtype=np.uint8)
    for layer in layers:
        merged_image = cv2.addWeighted(merged_image, 1, layer, 1, 0)
        # merged_image = cv2.bitwise_or(merged_image, layer)

    return merged_image

def convert_jpg_to_png(file_name):
    """
        Converts a JPG image to PNG format.

        Parameters:
        - file_name: Name of the JPG file to convert.

        Returns:
        - png_file_path: Path to the converted PNG file.
    """
    if file_name.lower().endswith(".jpg") or file_name.lower().endswith(".jpeg"):
        jpg_file_path = file_name
    else:
        raise ValueError("File must be a .jpg or .jpeg")
    
    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        temp_file_path = temp_file.name

    atexit.register(os.remove, temp_file_path)

    # Open the JPG file and save it as PNG to the temporary location
    with Image.open(jpg_file_path) as img:
        img.save(temp_file_path, "PNG")

    return temp_file_path
