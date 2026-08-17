"""Named constants controlling image standardization and metric computation."""

# --- Directory layout (relative to the "Image Validation" folder) ---
DIR_HISTOLOGY = "Histology"
DIR_PC12 = "pc12"
DIR_MANUAL = "Manual Segmentation"
DIR_IP = "Image Processing Segmentation"
DIR_STANDARDIZED = "Standardized"

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp")

# --- Canonical grid ---
# Every standardized image is resized so its longer edge equals this many pixels.
CANONICAL_LONG_EDGE = 1024

# --- Intensity standardization (pipeline 1) ---
# Percentile stretch used for high-bit-depth (uint16) microscopy images.
STRETCH_LOW_PERCENTILE = 0.5
STRETCH_HIGH_PERCENTILE = 99.5
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID = (8, 8)
MEDIAN_KERNEL = 3
# Margin (fraction of the bounding box size) added around detected content when cropping.
CROP_MARGIN_FRACTION = 0.02
# Gaussian smoothing (fraction of image height) applied before thresholding regions.
CELL_DENSITY_SIGMA_FRACTION = 0.01
# --- Sparse cell images (pc12) ---
# Cells are detected by local contrast (morphological top-hat) with a kernel of this
# fraction of the image height (slightly larger than a cell), then converted to a
# density map with the sigma below. The region threshold is Otsu * (1 - CELL_SENSITIVITY);
# the sensitivity is fixed (1.0 = most inclusive: any appreciable cell density counts).
CELL_KERNEL_FRACTION = 0.008
CELL_REGION_SIGMA_FRACTION = 0.015
CELL_SENSITIVITY = 1.0
# Illumination flattening: background estimated with a blur of this fraction of the height.
ILLUMINATION_SIGMA_FRACTION = 0.05
# Below this foreground fraction the image is treated as empty / mis-scaled.
MIN_FOREGROUND_FRACTION = 0.005
# Pipeline 1 region of interest: histology structures count only if the cell region
# comes within this fraction of the image height of them.
ROI_TOUCH_MARGIN_FRACTION = 0.01
# Aspect-ratio mismatch above which a warning is printed.
ASPECT_WARN_FRACTION = 0.02

# --- Label standardization (pipeline 2) ---
# Colors are first histogrammed on a coarse RGB grid (this many levels per channel)
# so that JPEG noise does not fragment the palette.
PALETTE_QUANT_LEVELS = 8
# Colors closer than this (euclidean RGB distance) are merged into one palette entry.
PALETTE_MERGE_RADIUS = 60.0
# Palette candidates must cover at least this fraction of pixels before merging.
PALETTE_MIN_FRACTION = 0.002
# A color is "achromatic" (grey/black/white) if its channel spread is below this.
ACHROMATIC_SPREAD = 40
# Achromatic clusters covering at least this fraction of the image are background.
BACKGROUND_MIN_FRACTION = 0.10
# Minor achromatic clusters are outline strokes (absorbed into neighbours) only when
# they are thin: 95th-percentile stroke thickness at native resolution <= this many px.
OUTLINE_MAX_THICKNESS_PX = 4.0
# Connected components smaller than this fraction of the image are absorbed into neighbours.
MIN_ISLAND_FRACTION = 0.0005

# --- Layer mapping (pipeline 2) ---
# An IP layer whose majority lies on the manual background is still assigned to a
# manual layer if at least this share of its pixels lies on that layer.
MAPPING_MIN_LAYER_SHARE = 0.20

# --- Registration (pipeline 2) ---
# Translation between the two segmentations is estimated by phase correlation of
# their (color-agnostic) layer-boundary maps. Shifts above this fraction of the grid
# are considered spurious and ignored.
REGISTRATION_MAX_SHIFT_FRACTION = 0.25
REGISTRATION_BOUNDARY_BLUR_SIGMA = 3.0

# --- Rigid registration (pipeline 1, --register rigid) ---
# Exhaustive rotation search (translation by phase correlation) on a grid reduced
# to this width, refined around the best candidate, accepted only if it improves
# the Dice overlap of the two regions. Scale search is off by default: an
# overlap-maximising scale can inflate a region onto the wrong structure.
RIGID_SEARCH_WIDTH = 256
RIGID_SEARCH_SCALE = False
RIGID_SCALE_RANGE = (0.8, 1.25)
RIGID_SCALE_STEP = 0.05
RIGID_MAX_ROTATION_DEG = 30.0
RIGID_ROTATION_STEP = 5.0

# --- SSIM (Wang, Bovik, Sheikh, Simoncelli 2004) ---
SSIM_K1 = 0.01
SSIM_K2 = 0.03
SSIM_SIGMA = 1.5  # 11x11 gaussian window
SSIM_WINDOW = 11
# The authors recommend averaging/downsampling by F = max(1, round(min(H, W) / 256)) first.
SSIM_REFERENCE_HEIGHT = 256
