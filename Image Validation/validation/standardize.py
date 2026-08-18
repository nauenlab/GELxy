"""
Preprocessing that converts every input into one of two canonical forms.

* Intensity images (histology, pc12) -> float32 grayscale in [0, 1], tissue/cells
  bright on a dark background, cropped to content, CLAHE-equalised, resized so the
  longer edge is CANONICAL_LONG_EDGE.
* Segmentation images (manual, image processing) -> a uint8 label map (0 =
  background) plus a legend, cropped to content and resized with nearest-neighbour
  interpolation so labels stay crisp.

Having both members of a comparison in the same canonical form is what makes
the downstream metrics comparable across images.
"""

from dataclasses import dataclass, field

import cv2
import numpy as np
from scipy import ndimage
from scipy.spatial.distance import cdist

from . import config


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def canonical_size(height, width):
    """(new_width, new_height) so the longer edge equals CANONICAL_LONG_EDGE."""
    scale = config.CANONICAL_LONG_EDGE / float(max(height, width))
    return max(1, int(round(width * scale))), max(1, int(round(height * scale)))


def content_bbox(mask, margin_fraction=config.CROP_MARGIN_FRACTION):
    """Bounding box (y0, y1, x0, x1) of True pixels with a small margin; None if empty."""
    rows = np.where(mask.any(axis=1))[0]
    cols = np.where(mask.any(axis=0))[0]
    if rows.size == 0 or cols.size == 0:
        return None
    y0, y1 = int(rows[0]), int(rows[-1]) + 1
    x0, x1 = int(cols[0]), int(cols[-1]) + 1
    my = int(round((y1 - y0) * margin_fraction))
    mx = int(round((x1 - x0) * margin_fraction))
    return (max(0, y0 - my), min(mask.shape[0], y1 + my), max(0, x0 - mx), min(mask.shape[1], x1 + mx))


def otsu_mask(gray_float):
    """Otsu threshold of a [0, 1] float image; returns (mask, threshold in [0, 1])."""
    as_uint8 = np.clip(gray_float * 255.0, 0, 255).astype(np.uint8)
    threshold, _ = cv2.threshold(as_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return as_uint8 > threshold, threshold / 255.0


def resize_to(image, width, height, nearest=False):
    interpolation = cv2.INTER_NEAREST if nearest else cv2.INTER_AREA
    if not nearest and (width > image.shape[1] or height > image.shape[0]):
        interpolation = cv2.INTER_LINEAR
    return cv2.resize(image, (width, height), interpolation=interpolation)


def _border_ring(array, thickness=None):
    h, w = array.shape[:2]
    t = thickness or max(2, int(round(0.01 * min(h, w))))
    return np.concatenate([
        array[:t].reshape(-1, *array.shape[2:]),
        array[-t:].reshape(-1, *array.shape[2:]),
        array[:, :t].reshape(-1, *array.shape[2:]),
        array[:, -t:].reshape(-1, *array.shape[2:]),
    ])


# ---------------------------------------------------------------------------
# Intensity images
# ---------------------------------------------------------------------------

@dataclass
class IntensityImage:
    image: np.ndarray  # float32 [0, 1], canonical grid
    foreground: np.ndarray  # bool mask of tissue/cells on the canonical grid
    inverted: bool
    crop_box: tuple
    original_shape: tuple
    density: np.ndarray = None  # cell/structure density map on the canonical grid (sparse mode)
    notes: list = field(default_factory=list)


def flatten_illumination(gray):
    """Remove slow illumination gradients from a bright-on-dark image and re-stretch to [0, 1]."""
    sigma = max(1.0, config.ILLUMINATION_SIGMA_FRACTION * gray.shape[0])
    background = cv2.GaussianBlur(gray, (0, 0), sigma)
    flat = np.clip(gray - background, 0, None)
    low, high = np.percentile(flat, [config.STRETCH_LOW_PERCENTILE, config.STRETCH_HIGH_PERCENTILE])
    if high <= low:
        return np.zeros_like(flat)
    return np.clip((flat - low) / (high - low), 0.0, 1.0).astype(np.float32)


def cell_density_map(gray_bright):
    """
    Density of small bright objects (cells) in a bright-on-dark image, in [0, 1].

    A morphological top-hat isolates objects smaller than the kernel regardless of
    the local background level, so faint cells on a light gel are detected as
    reliably as dark ones; Gaussian smoothing then turns detections into a density.
    """
    k = int(round(config.CELL_KERNEL_FRACTION * gray_bright.shape[0])) | 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (max(3, k), max(3, k)))
    tophat = cv2.morphologyEx(gray_bright, cv2.MORPH_TOPHAT, kernel)
    scale = float(np.percentile(tophat, config.STRETCH_HIGH_PERCENTILE))
    if scale <= 0:
        return np.zeros_like(gray_bright)
    response = np.clip(tophat / scale, 0.0, 1.0)
    density = cv2.GaussianBlur(response, (0, 0), max(1.0, config.CELL_REGION_SIGMA_FRACTION * gray_bright.shape[0]))
    peak = float(density.max())
    return (density / peak).astype(np.float32) if peak > 0 else density


def _threshold_density(density, sensitivity):
    """Region mask from a density map: Otsu threshold lowered by `sensitivity` (0..1)."""
    as_uint8 = np.clip(density * 255.0, 0, 255).astype(np.uint8)
    otsu, _ = cv2.threshold(as_uint8, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    threshold = otsu * (1.0 - float(np.clip(sensitivity, 0.0, 0.95)))
    return as_uint8 > threshold


def standardize_intensity(gray, sparse=False, sensitivity=config.CELL_SENSITIVITY, crop=True):
    """
    Convert a [0, 1] float grayscale image to the canonical intensity form.

    sparse=True is for cell-culture images whose foreground is a set of small
    objects: illumination is flattened, cells are detected by local contrast, and
    the foreground is the region of high cell density. `sensitivity` (0..1) lowers
    the density threshold below Otsu's value (0 = Otsu, higher = more inclusive).
    crop=False keeps the full frame instead of cropping to the detected content.
    """
    notes = []
    gray = gray.astype(np.float32)
    original_shape = gray.shape

    # Polarity: the structures of interest (cell-dense layers in H&E histology, cells
    # in a culture image) are the sparser intensity class. We want them bright on a
    # dark background, so invert when the bright Otsu class is the majority.
    polarity_sigma = max(1.0, config.CELL_DENSITY_SIGMA_FRACTION * gray.shape[0])
    bright_class, _ = otsu_mask(cv2.GaussianBlur(gray, (0, 0), polarity_sigma))
    inverted = float(bright_class.mean()) > 0.5
    if inverted:
        gray = 1.0 - gray
        notes.append("intensities inverted so the sparse (cell-dense) structures are bright on dark")

    if sparse:
        gray = flatten_illumination(gray)
        notes.append("illumination flattened; cells detected by local contrast (top-hat)")

    # Crop to content on a rough region estimate.
    if sparse:
        rough_mask = _threshold_density(cell_density_map(gray), sensitivity)
    else:
        smooth = cv2.GaussianBlur(gray, (0, 0), max(1.0, 0.005 * gray.shape[0]))
        rough_mask, _ = otsu_mask(smooth)
    rough_mask = ndimage.binary_opening(rough_mask, iterations=2)
    box = content_bbox(rough_mask) if crop else None
    if box is None:
        box = (0, gray.shape[0], 0, gray.shape[1])
        if crop:
            notes.append("no content detected; using full frame")
    y0, y1, x0, x1 = box
    gray = gray[y0:y1, x0:x1]

    # Canonical grid.
    width, height = canonical_size(*gray.shape)
    gray = resize_to(gray, width, height)

    # Contrast normalisation + denoise.
    as_uint8 = np.clip(gray * 255.0, 0, 255).astype(np.uint8)
    clahe = cv2.createCLAHE(clipLimit=config.CLAHE_CLIP_LIMIT, tileGridSize=config.CLAHE_TILE_GRID)
    as_uint8 = clahe.apply(as_uint8)
    as_uint8 = cv2.medianBlur(as_uint8, config.MEDIAN_KERNEL)
    image = as_uint8.astype(np.float32) / 255.0

    # Foreground region: follows the tissue / cell distribution rather than
    # individual nuclei or cells.
    if sparse:
        density = cell_density_map(gray)
        foreground = _threshold_density(density, sensitivity)
    else:
        sigma = max(1.0, config.CELL_DENSITY_SIGMA_FRACTION * image.shape[0])
        density = cv2.GaussianBlur(image, (0, 0), sigma)
        foreground, _ = otsu_mask(density)
    foreground = ndimage.binary_opening(foreground, iterations=2)
    foreground = ndimage.binary_closing(foreground, iterations=2)

    return IntensityImage(
        image=image,
        foreground=foreground,
        inverted=inverted,
        crop_box=box,
        original_shape=original_shape,
        density=density,
        notes=notes,
    )


# ---------------------------------------------------------------------------
# Segmentation images -> label maps
# ---------------------------------------------------------------------------

@dataclass
class LabelMap:
    labels: np.ndarray  # uint8, canonical grid, 0 = background
    legend: dict  # label -> {"rgb": (r, g, b), "fraction": float}
    has_background: bool
    crop_box: tuple
    original_shape: tuple
    notes: list = field(default_factory=list)
    height_fraction: float = 1.0  # share of the original image height covered by `labels`

    @property
    def layer_labels(self):
        return sorted(label for label in self.legend if label != 0)

    def mask(self, label):
        return self.labels == label


def _cluster_palette(rgb):
    """
    Group image colors into a small palette.

    Returns (assignment [H, W] of palette indices, palette [K, 3] uint8, counts).
    Colors are histogrammed on a coarse RGB grid; frequent bins seed the palette
    (any bin within PALETTE_MERGE_RADIUS of an existing seed is merged into it),
    then every exact color is assigned to its nearest seed. This absorbs JPEG
    noise and anti-aliasing while keeping genuinely distinct colors apart.
    """
    flat = rgb.reshape(-1, 3)
    unique, inverse, counts = np.unique(flat, axis=0, return_inverse=True, return_counts=True)
    inverse = inverse.reshape(-1)
    total = flat.shape[0]

    step = 256.0 / config.PALETTE_QUANT_LEVELS
    bins = np.floor(unique.astype(np.float32) / step).astype(np.int64)
    bin_ids = bins[:, 0] * config.PALETTE_QUANT_LEVELS ** 2 + bins[:, 1] * config.PALETTE_QUANT_LEVELS + bins[:, 2]
    bin_counts = np.bincount(bin_ids, weights=counts, minlength=config.PALETTE_QUANT_LEVELS ** 3)
    # Mean color per bin (weighted by pixel count).
    bin_sum = np.zeros((config.PALETTE_QUANT_LEVELS ** 3, 3), dtype=np.float64)
    np.add.at(bin_sum, bin_ids, unique.astype(np.float64) * counts[:, None])
    order = np.argsort(-bin_counts)

    seeds = []
    for bin_id in order:
        if bin_counts[bin_id] <= 0:
            break
        if bin_counts[bin_id] < config.PALETTE_MIN_FRACTION * total and seeds:
            break
        color = (bin_sum[bin_id] / bin_counts[bin_id]).astype(np.float32)
        if seeds and np.min(np.linalg.norm(np.array(seeds) - color, axis=1)) < config.PALETTE_MERGE_RADIUS:
            continue
        seeds.append(color)
    seeds = np.array(seeds, dtype=np.float32)

    nearest = np.argmin(cdist(unique.astype(np.float32), seeds), axis=1)
    assignment = nearest[inverse].reshape(rgb.shape[:2])
    palette_counts = np.bincount(assignment.ravel(), minlength=len(seeds))

    # Represent each cluster by the mean color of its members (weighted).
    palette = np.zeros((len(seeds), 3), dtype=np.float64)
    for k in range(len(seeds)):
        members = nearest == k
        weights = counts[members].astype(np.float64)
        palette[k] = (unique[members].astype(np.float64) * weights[:, None]).sum(axis=0) / max(1.0, weights.sum())
    return assignment, palette.round().astype(np.uint8), palette_counts


def _stroke_thickness(mask):
    """Approximate 95th-percentile thickness (px) of the True regions in a mask."""
    if not mask.any():
        return 0.0
    edt = ndimage.distance_transform_edt(mask)
    return 2.0 * float(np.percentile(edt[mask], 95))


def _fill_unknown(labels, unknown):
    """Replace 'unknown' pixels with the label of the nearest known pixel."""
    if not unknown.any():
        return labels
    if unknown.all():
        return labels
    _, (iy, ix) = ndimage.distance_transform_edt(unknown, return_indices=True)
    return labels[iy, ix]


def _absorb_small_islands(labels, min_pixels):
    """Mark connected components smaller than min_pixels as unknown and fill them."""
    unknown = np.zeros(labels.shape, dtype=bool)
    for label in np.unique(labels):
        components, count = ndimage.label(labels == label)
        if count == 0:
            continue
        sizes = ndimage.sum(np.ones_like(components), components, index=np.arange(1, count + 1))
        small = np.where(sizes < min_pixels)[0] + 1
        if small.size:
            unknown |= np.isin(components, small)
    return _fill_unknown(labels, unknown), int(unknown.sum())


def standardize_labels(rgb):
    """Convert an RGB segmentation rendering into the canonical LabelMap form."""
    notes = []
    original_shape = rgb.shape[:2]
    assignment, palette, counts = _cluster_palette(rgb)
    total = float(assignment.size)
    spread = palette.astype(int).max(axis=1) - palette.astype(int).min(axis=1)

    background_clusters = [
        k for k in range(len(palette))
        if spread[k] < config.ACHROMATIC_SPREAD and counts[k] / total >= config.BACKGROUND_MIN_FRACTION
    ]
    # Minor achromatic clusters are drawn outline strokes only if they are thin;
    # thick grey/white regions are genuine layers.
    outline_clusters = [
        k for k in range(len(palette))
        if spread[k] < config.ACHROMATIC_SPREAD and k not in background_clusters
        and _stroke_thickness(assignment == k) <= config.OUTLINE_MAX_THICKNESS_PX
    ]
    layer_clusters = [k for k in range(len(palette)) if k not in background_clusters and k not in outline_clusters]

    if not layer_clusters:
        # Nothing chromatic: treat every non-background cluster as a layer.
        layer_clusters, outline_clusters = outline_clusters, []
        notes.append("no chromatic layers found; grey clusters treated as layers")

    labels = np.zeros(assignment.shape, dtype=np.uint8)
    legend = {}
    if background_clusters:
        legend[0] = {"rgb": tuple(int(v) for v in palette[background_clusters[0]]), "fraction": 0.0}
        notes.append(
            "background = " + ", ".join(f"rgb{tuple(int(v) for v in palette[k])}" for k in background_clusters)
        )
    else:
        notes.append("no background detected (fully painted image)")

    for new_label, k in enumerate(layer_clusters, start=1):
        labels[assignment == k] = new_label
        legend[new_label] = {"rgb": tuple(int(v) for v in palette[k]), "fraction": 0.0}

    unknown = np.isin(assignment, outline_clusters)
    if outline_clusters:
        notes.append(f"{100.0 * unknown.mean():.2f}% outline/anti-alias pixels absorbed into neighbours")
    labels = _fill_unknown(labels, unknown)

    labels, absorbed = _absorb_small_islands(labels, config.MIN_ISLAND_FRACTION * total)
    if absorbed:
        notes.append(f"{100.0 * absorbed / total:.2f}% small-island pixels absorbed into neighbours")

    has_background = bool(background_clusters)
    width, height = canonical_size(*labels.shape)
    labels = resize_to(labels, width, height, nearest=True)
    label_map = LabelMap(
        labels=labels,
        legend=legend,
        has_background=has_background,
        crop_box=(0, labels.shape[0], 0, labels.shape[1]),
        original_shape=original_shape,
        notes=notes,
    )
    _refresh_legend(label_map)
    return label_map


def _refresh_legend(label_map):
    for label in label_map.legend:
        label_map.legend[label]["fraction"] = float((label_map.labels == label).mean())
    for label in [l for l in label_map.legend if l != 0 and label_map.legend[l]["fraction"] == 0.0]:
        del label_map.legend[label]


def cropped_to_content(label_map):
    """
    A copy of the label map cropped to the bounding box of its non-background
    pixels and resized back to the canonical grid. Images without a background
    are returned unchanged (their content already fills the frame).
    """
    if not label_map.has_background:
        return label_map
    box = content_bbox(label_map.labels != 0, margin_fraction=0.0)
    if box is None:
        return label_map
    y0, y1, x0, x1 = box
    labels = label_map.labels[y0:y1, x0:x1]
    width, height = canonical_size(*labels.shape)
    labels = resize_to(labels, width, height, nearest=True)
    cropped = LabelMap(
        labels=labels,
        legend={k: dict(v) for k, v in label_map.legend.items()},
        has_background=label_map.has_background,
        crop_box=box,
        original_shape=label_map.original_shape,
        notes=list(label_map.notes),
        height_fraction=label_map.height_fraction * (y1 - y0) / label_map.labels.shape[0],
    )
    _refresh_legend(cropped)
    return cropped


def render_labels(labels, legend, background_rgb=(0, 0, 0)):
    """Render a label map back to RGB using a legend {label: {"rgb": ...}}."""
    out = np.zeros(labels.shape + (3,), dtype=np.uint8)
    out[...] = background_rgb
    for label, entry in legend.items():
        if label == 0:
            continue
        out[labels == label] = entry["rgb"]
    return out
