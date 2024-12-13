import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import cv2

def get_blob_thickness(binary_blob):
    """
    Calculate the maximum thickness (width/height) of a blob using distance transform.
    
    Parameters:
    binary_blob (numpy.ndarray): Binary image containing a single blob
    
    Returns:
    float: Maximum thickness of the blob
    """
    # Compute distance transform
    dist_transform = cv2.distanceTransform(binary_blob.astype(np.uint8), cv2.DIST_L2, 5)
    
    # The maximum value in the distance transform * 2 gives us the maximum thickness
    max_thickness = np.max(dist_transform) * 2
    
    return max_thickness


def detect_islands(image):
    """
    Detect and visualize small isolated regions (islands) in a Canny edge detection output image.
    
    Parameters:
    image (numpy.ndarray): Grayscale image (output from Canny edge detection)
    min_thickness (int): Minimum width/height of blobs to detect
    min_size (int): Minimum size of islands to detect (in pixels)
    max_size (int): Maximum size of islands to detect (in pixels)
    
    Returns:
    tuple: (labeled_image, number_of_islands, sizes_of_islands, thicknesses)
    """
    min_thickness = 3
    min_size = 15
    max_size = 1000
    # Ensure image is binary
    binary_image = (image > 0).astype(np.uint8)
    
    # Fill holes in the edges to create solid regions
    filled_binary = ndimage.binary_fill_holes(binary_image)
    
    # Label connected components
    labeled_array, num_features = ndimage.label(filled_binary)
    
    # Calculate sizes of all regions
    sizes = ndimage.sum(filled_binary, labeled_array, range(1, num_features + 1))
    
    # Create mask for islands within size range
    mask_size = (sizes >= min_size) & (sizes <= max_size)
    valid_labels = np.arange(1, num_features + 1)[mask_size]
    
    # Check thickness of each valid region
    valid_labels_thickness = []
    thicknesses = []
    
    for label in valid_labels:
        # Extract single blob
        blob_mask = (labeled_array == label).astype(np.uint8)
        thickness = get_blob_thickness(blob_mask)
        area = np.sum(blob_mask)
        
        if thickness >= min_thickness and area < 80:
            valid_labels_thickness.append(label)
            thicknesses.append(thickness)
    
    # Create new image with only valid islands
    island_mask = np.in1d(labeled_array, valid_labels_thickness).reshape(labeled_array.shape)
    final_labeled, final_num_features = ndimage.label(island_mask)
    
    # Calculate sizes of final islands
    final_sizes = ndimage.sum(island_mask, final_labeled, range(1, final_num_features + 1))
    
    return final_labeled, final_num_features, final_sizes, thicknesses, island_mask


def remove_islands(original_image, island_mask):
    """
    Remove detected islands from the original image.
    
    Parameters:
    original_image (numpy.ndarray): Original image
    island_mask (numpy.ndarray): Binary mask of detected islands
    
    Returns:
    numpy.ndarray: Image with islands removed
    """
    # Create copy of original image
    result = original_image.copy()
    
    # Set pixels in island regions to 0 (black)
    result[island_mask] = 0
    
    return result

def visualize_results(original_image, labeled_image, cleaned_image, num_islands, thicknesses=None):
    """
    Visualize original image, detected islands, and cleaned image.
    
    Parameters:
    original_image (numpy.ndarray): Original image
    labeled_image (numpy.ndarray): Labeled image from detect_islands
    cleaned_image (numpy.ndarray): Image with islands removed
    num_islands (int): Number of islands detected
    thicknesses (list): List of island thicknesses
    """
    # Create RGB image for visualization of islands
    height, width = original_image.shape
    vis_image = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Generate random colors for each island
    colors = np.random.randint(0, 255, (num_islands + 1, 3))
    colors[0] = [0, 0, 0]  # Background color
    
    # Color each island
    for i in range(num_islands + 1):
        vis_image[labeled_image == i] = colors[i]
    
    # Display results
    plt.figure(figsize=(20, 5))
    
    plt.subplot(141)
    plt.title('Original Image')
    plt.imshow(original_image, cmap='gray')
    plt.axis('off')
    
    plt.subplot(142)
    plt.title(f'Detected Islands ({num_islands})')
    plt.imshow(vis_image)
    plt.axis('off')
    
    plt.subplot(143)
    plt.title('Labeled Islands')
    plt.imshow(labeled_image, cmap='nipy_spectral')
    plt.axis('off')
    
    plt.subplot(144)
    plt.title('Cleaned Image')
    plt.imshow(cleaned_image, cmap='gray')
    plt.axis('off')
    
    if thicknesses:
        plt.suptitle(f'Maximum thicknesses: {[round(t, 1) for t in thicknesses]}')
    
    plt.tight_layout()
    plt.show()