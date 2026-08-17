"""Locate validation images by base name and load them into predictable numpy formats."""

from pathlib import Path

import numpy as np
from PIL import Image

from . import config

# Path of the "Image Validation" folder that contains this package.
VALIDATION_ROOT = Path(__file__).resolve().parent.parent

DIRECTORIES = {
    "histology": config.DIR_HISTOLOGY,
    "pc12": config.DIR_PC12,
    "manual": config.DIR_MANUAL,
    "ip": config.DIR_IP,
}


def stem_of(base_name):
    """Return the extension-free stem of a base name such as 'Hippocampus.png'."""
    return Path(base_name).stem


def resolve_image(dir_key, base_name):
    """
    Find the image in the given directory whose stem matches the base name.

    Matching is extension-agnostic and case-insensitive so that 'Hippocampus.png'
    also matches 'Hippocampus.jpg'. Returns a Path or None.
    """
    directory = VALIDATION_ROOT / DIRECTORIES[dir_key]
    if not directory.is_dir():
        return None
    target = stem_of(base_name).lower()
    candidates = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() in config.IMAGE_EXTENSIONS and path.stem.lower() == target:
            candidates.append(path)
    if not candidates:
        return None
    # Prefer an exact (case-sensitive) name match, then PNG, then anything else.
    candidates.sort(key=lambda p: (p.name != base_name, p.suffix.lower() != ".png"))
    return candidates[0]


def standardized_dir(base_name):
    """Directory where standardized outputs for this base name are written."""
    return VALIDATION_ROOT / config.DIR_STANDARDIZED / stem_of(base_name)


def _percentile_stretch(array):
    """Linearly rescale an array to [0, 1] between its low/high percentiles."""
    array = array.astype(np.float32)
    low = np.percentile(array, config.STRETCH_LOW_PERCENTILE)
    high = np.percentile(array, config.STRETCH_HIGH_PERCENTILE)
    if high <= low:
        low, high = float(array.min()), float(array.max())
    if high <= low:
        return np.zeros_like(array, dtype=np.float32)
    return np.clip((array - low) / (high - low), 0.0, 1.0)


def load_gray_float(path):
    """
    Load an image as float32 grayscale in [0, 1].

    8-bit images are divided by 255. Higher bit-depth images (e.g. 16-bit
    microscopy PNGs) are percentile-stretched, because their nominal range is
    rarely used and a naive /65535 conversion produces a near-black or,
    after 8-bit conversion, a blown-out white image.
    """
    with Image.open(path) as image:
        info = {"mode": image.mode, "size": image.size}
        if image.mode in ("I;16", "I;16B", "I;16L", "I", "F"):
            array = np.array(image).astype(np.float32)
            gray = _percentile_stretch(array)
            info["stretched"] = True
            info["raw_range"] = (float(array.min()), float(array.max()))
            return gray, info
        rgb = np.array(image.convert("RGB")).astype(np.float32)
    # ITU-R 601 luminance, same weights as OpenCV / skimage rgb2gray.
    gray = (0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]) / 255.0
    info["stretched"] = False
    return gray.astype(np.float32), info


def load_rgb_uint8(path):
    """
    Load an image as uint8 RGB (H, W, 3).

    High bit-depth grayscale images are percentile-stretched to 8 bits and
    replicated across channels; alpha channels are dropped.
    """
    with Image.open(path) as image:
        info = {"mode": image.mode, "size": image.size}
        if image.mode in ("I;16", "I;16B", "I;16L", "I", "F"):
            gray = (_percentile_stretch(np.array(image)) * 255.0).round().astype(np.uint8)
            return np.stack([gray] * 3, axis=-1), info
        rgb = np.array(image.convert("RGB"))
    return rgb, info
