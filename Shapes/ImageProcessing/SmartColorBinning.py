import cv2
import numpy as np
from scipy.signal import find_peaks
from scipy.ndimage import gaussian_filter1d
import matplotlib.pyplot as plt

def top_colors(img):
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = image.reshape(-1, 3) * 256

    # Define the number of bins per channel
    bins = 8  # You can adjust this number

    # Quantize the colors by reducing color depth
    quantized_pixels = (pixels // (256 // bins)) * (256 // bins)

    # Convert to integer type
    quantized_pixels = quantized_pixels.astype(np.uint8)

    # Get unique colors and their counts
    colors, counts = np.unique(quantized_pixels, axis=0, return_counts=True)
    # Sort by frequency
    sorted_indices = np.argsort(-counts)
    colors = colors[sorted_indices]
    counts = counts[sorted_indices]

    top_n = 5

    return colors[:top_n], counts[:top_n]


def color_images(img, num_colors):
    image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pixels = image.reshape(-1, 3) * 256

    # Define the number of bins per channel
    bins = 6 # You can adjust this number

    # Quantize the colors by reducing color depth
    quantized_pixels = (pixels // (256 // bins)) * (256 // bins)

    # Convert to integer type
    quantized_pixels = quantized_pixels.astype(np.uint8)

    # Get unique colors and their counts
    colors, counts = np.unique(quantized_pixels, axis=0, return_counts=True)
    # Sort by frequency
    sorted_indices = np.argsort(-counts)
    colors = colors[sorted_indices]
    counts = counts[sorted_indices]

    color_images = {}
    for color in colors[:num_colors]:
        mask = np.all(quantized_pixels == color, axis=1).reshape(image.shape[:2])
        color_images[tuple(color)] = np.zeros_like(image)
        color_images[tuple(color)][mask] = color / 255

    return color_images

def sma(data, window_size):
    sma_values = np.convolve(data, np.ones(window_size) / window_size, mode='valid')
    pad_width = (len(data) - len(sma_values)) // 2
    sma_values = np.pad(sma_values, (pad_width, len(data) - len(sma_values) - pad_width), mode='edge')
    return sma_values


def detect_bins_from_histogram(pixels):
    """
    Function to detect peaks, valleys, and start/end points of rapid changes in a grayscale image histogram.
    Args:
    - image: Grayscale image array
    - min_valley_depth: The minimum prominence of valleys to detect
    - min_peak_prominence: The minimum prominence of peaks to detect
    - sigma: Smoothing factor for Gaussian filtering
    - gradient_threshold: The threshold for detecting rapid changes in the gradient of the histogram
    """
    
    # Create the histogram
    hist, bin_edges = np.histogram(pixels, bins=256)
    
    # normalize the histogram
    hist = hist / np.max(np.abs(hist))
    hist_sma = sma(hist, 5)
    
    # Apply Gaussian smoothing to the histogram
    sigma=0.02
    smooth_hist = gaussian_filter1d(hist_sma, sigma=sigma)

    # Compute the first derivative (gradient) to detect rapid changes
    gradient = np.gradient(smooth_hist)

    # Find regions where the gradient exceeds the threshold (both positive and negative)
    gradient = gradient / np.max(np.abs(gradient))

    # Find start and end points where the histogram values cross a threshold of 0.01
    low_change_start_end = []
    start_point = 0
    for i in range(1, len(hist)):
        if hist[i] >= 0.01 and hist[i - 1] < 0.01:
            start_point = i
        elif hist[i] < 0.01 and hist[i - 1] >= 0.01:
            end_point = i
            low_change_start_end.append((start_point, end_point))
    low_change_start_end.append((start_point, len(hist) - 1))

    # find points in the gradient that cross a certain threshold using absolute value
    gradient_threshold = 0.05
    rapid_change_regions = np.where(np.abs(gradient) > gradient_threshold)[0]

    # Detect start and end points of rapid changes by identifying boundaries of the regions
    rapid_change_start_end = []
    if len(rapid_change_regions) > 0:
        start_point = rapid_change_regions[0]
        for i in range(1, len(rapid_change_regions)):
            # Check if this point is not continuous with the previous point
            if rapid_change_regions[i] != rapid_change_regions[i - 1] + 1:
                end_point = rapid_change_regions[i - 1]
                rapid_change_start_end.append((start_point, end_point))
                start_point = rapid_change_regions[i]
        # Append the last region
        rapid_change_start_end.append((start_point, rapid_change_regions[-1]))
    
    # Find valleys (local minima) by negating the smoothed histogram and finding peaks
    min_valley_depth = 0.01
    valleys, _ = find_peaks(-smooth_hist, prominence=min_valley_depth)

    # Get the bin edges for the valleys and start/end of rapid changes
    custom_bins = list(bin_edges[valleys].astype(int))  # Add valleys as bin boundaries
    for start, end in rapid_change_start_end + low_change_start_end:
        custom_bins.append(bin_edges[start])
        custom_bins.append(bin_edges[end])
    custom_bins = np.array(custom_bins).astype(int)
    custom_bins = [0] + maximize_distances(custom_bins) + [255]
    custom_bins = list(sorted(set(custom_bins)))

    # print("Bins:", custom_bins)
    # plot_histogram(bin_edges, hist_sma, smooth_hist, valleys, custom_bins, gradient)

    return np.array(custom_bins)

def plot_histogram(bin_edges, hist_sma, smooth_hist, valleys, custom_bins, gradient):
    plt.figure(figsize=(10, 6))

    plt.plot(custom_bins, np.zeros_like(custom_bins), "|", markersize=20, label="Bins", color="purple")
    plt.plot(bin_edges[:-1], gradient, label="Gradient (1st Derivative)", color='brown')
    plt.plot(bin_edges[:-1], hist_sma, label="SMA Histogram", color='blue')

    plt.xlabel("Pixel Value")
    plt.ylabel("Normalized Frequency")
    plt.title("Histogram of Grayscale Image")
    plt.legend()

    plt.show()

def maximize_distances(numbers, min_distance=15):
    """
    Remove elements from a sorted list such that the minimum distance between
    any two remaining elements is at least min_distance units.
    
    Args:
        numbers (list): List of numbers to process
        min_distance (int): Minimum required distance between elements
        
    Returns:
        list: Processed list with elements removed to maximize distances
    """
    if len(numbers) == 0:
        return []
    
    # Sort the input list
    sorted_nums = sorted(numbers)
    
    # Initialize result with the first number
    result = [sorted_nums[0]]
    
    # Iterate through the sorted list
    for num in sorted_nums[1:]:
        # Check if current number is far enough from the last kept number
        if num - result[-1] >= min_distance:
            result.append(num)
    
    return result

def segment_images(img):
    # Check if the image is already grayscale or convert it if necessary
    # assert len(img.shape) == 2 or img.shape[2] == 1, "Image must be grayscale"
    images = {}
    grayscale = True
    
    if grayscale:
        max_val = np.max(img)
        scale = 255 / max_val
        if len(img.shape) == 3:
            gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            pixels = ((gray_img.flatten() * scale) * 100).astype(int) / 100
        else:
            pixels = ((img.flatten() * scale) * 100).astype(int) / 100
        bin_ranges = detect_bins_from_histogram(pixels)
        
        pixel_colors = []
        for i in range(len(bin_ranges) - 1):
            average_pixel = int((bin_ranges[i] + bin_ranges[i + 1]) / 2)
            mask = (pixels >= bin_ranges[i]) & (pixels < bin_ranges[i + 1] + 1)
            pixel_colors.append((average_pixel, mask))
        
        # Sort by frequency
        sorted_pixel_colors = sorted(pixel_colors, key=lambda x: np.sum(x[1]), reverse=True)
        for color, mask in sorted_pixel_colors:
            images[color] = np.zeros_like(img)
            images[color][mask.reshape(img.shape[:2])] = color
            # plt.imshow(images[color])
            # plt.show()
    else:
        image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        max_val = np.max(img)
        scale = 255 / max_val
        pixels = image.reshape(-1, 3) * scale
        
        rgb = [img[:, :, 0], img[:, :, 1], img[:, :, 2]]
        pixel_colors = [[], [], []]
        for (i, pixel_array) in enumerate(rgb):
            pixels = ((pixel_array * 256) * 100).astype(int) / 100
            bin_ranges = detect_bins_from_histogram(pixels)
            
            for j in range(len(bin_ranges) - 1):
                average_pixel = int((bin_ranges[j] + bin_ranges[j + 1]) / 2)
                mask = (pixels >= bin_ranges[j]) & (pixels < bin_ranges[j + 1] + 1)
                pixel_colors[i].append((average_pixel, mask))

        
        for i in range(len(pixel_colors[0])):
            color = (pixel_colors[0][i][0], pixel_colors[1][i][0], pixel_colors[2][i][0])
            mask = pixel_colors[0][i][1] & pixel_colors[1][i][1] & pixel_colors[2][i][1]
            images[color] = np.zeros_like(img, dtype=np.uint8)
            images[color][mask.reshape(img.shape[:2])] = color
            # plt.imshow(images[color])
            # plt.show()

    return images