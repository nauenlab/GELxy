"""
Similarity and contour-deviation metrics.

- ssim_wang: structural similarity with the parameters of Wang, Bovik, Sheikh &
  Simoncelli, "Image quality assessment: from error visibility to structural
  similarity", IEEE TIP 13(4), 2004 (11x11 gaussian window, sigma 1.5,
  K1 = 0.01, K2 = 0.03), including the authors' recommended pre-downsampling.
- distance_deviation: the distance deviation measure of Rogelj et al.,
  "Distance deviation measure of contouring variability", Radiol Oncol
  2013;47(1):86-96. Each region is converted to a signed euclidean distance map
  (positive outside, negative inside); the deviation image is the absolute
  difference of the two maps. Reported scalars are the mean deviation over the
  union of both regions (the paper's balanced choice) and the maximum deviation
  over the disagreement region, which for two contours equals the Hausdorff
  distance.
"""

from dataclasses import dataclass, field

import cv2
import numpy as np
from scipy import ndimage
from skimage.metrics import structural_similarity

from . import config


def wang_downsample_factor(shape):
    """F = max(1, round(min(H, W) / 256)) as in the SSIM authors' reference ssim.m."""
    return max(1, int(round(min(shape[0], shape[1]) / config.SSIM_REFERENCE_HEIGHT)))


def _average_downsample(image, factor):
    if factor <= 1:
        return image
    new_size = (max(1, image.shape[1] // factor), max(1, image.shape[0] // factor))
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)


def ssim_wang(image_a, image_b, data_range=1.0, downsample=True, full=False):
    """
    Structural similarity between two equally shaped images.

    Grayscale inputs are 2-D; color inputs are (H, W, 3) and averaged over channels.
    Returns the mean SSIM (and the SSIM map when full=True).
    """
    if image_a.shape != image_b.shape:
        raise ValueError(f"SSIM inputs must share a shape, got {image_a.shape} vs {image_b.shape}")
    a = image_a.astype(np.float32)
    b = image_b.astype(np.float32)
    if downsample:
        factor = wang_downsample_factor(a.shape)
        a = _average_downsample(a, factor)
        b = _average_downsample(b, factor)
    kwargs = dict(
        data_range=data_range,
        gaussian_weights=True,
        sigma=config.SSIM_SIGMA,
        use_sample_covariance=False,
        K1=config.SSIM_K1,
        K2=config.SSIM_K2,
    )
    if a.ndim == 3:
        kwargs["channel_axis"] = 2
    # skimage needs the window (11 px) to fit inside the image.
    if min(a.shape[:2]) < 11:
        return (float("nan"), None) if full else float("nan")
    result = structural_similarity(a, b, full=full, **kwargs)
    if full:
        score, ssim_map = result
        return float(score), ssim_map
    return float(result)


def signed_distance_map(mask):
    """
    Signed euclidean distance to the region contour: >0 outside, <0 inside.

    The contour is taken to lie halfway between the last inside and the first
    outside pixel, so distances are measured to the pixel edge (a 10 px shift of
    a region yields a 10 px deviation, not 11).
    """
    mask = mask.astype(bool)
    outside = ndimage.distance_transform_edt(~mask) - 0.5
    inside = ndimage.distance_transform_edt(mask) - 0.5
    return np.where(mask, -inside, outside)


@dataclass
class DistanceDeviation:
    """Result of the Rogelj distance deviation measure (all distances in pixels)."""

    valid: bool
    reason: str = ""
    mean_union: float = float("nan")  # mean DD over union of both regions
    mean_disagreement: float = float("nan")  # mean DD over region where masks disagree
    max_disagreement: float = float("nan")  # max DD over disagreement (= Hausdorff distance)
    disagreement_fraction: float = float("nan")  # disagreement area / union area
    dice: float = float("nan")
    iou: float = float("nan")
    # Directed measures (a = reference, b = prediction):
    recall: float = float("nan")  # fraction of a covered by b
    precision: float = float("nan")  # fraction of b lying on a
    mean_over_a: float = float("nan")  # mean DD over region a only
    mean_over_b: float = float("nan")  # mean DD over region b only
    area_a: int = 0
    area_b: int = 0
    deviation_image: np.ndarray = field(default=None, repr=False)


def distance_deviation(mask_a, mask_b, keep_image=False):
    """Compute the distance deviation measure between two binary masks of equal shape."""
    if mask_a.shape != mask_b.shape:
        raise ValueError(f"Masks must share a shape, got {mask_a.shape} vs {mask_b.shape}")
    a = mask_a.astype(bool)
    b = mask_b.astype(bool)
    area_a, area_b = int(a.sum()), int(b.sum())
    if area_a == 0 and area_b == 0:
        return DistanceDeviation(valid=False, reason="both regions are empty")
    if area_a == 0 or area_b == 0:
        return DistanceDeviation(
            valid=False,
            reason="one region is empty (no contour to compare)",
            area_a=area_a,
            area_b=area_b,
            dice=0.0,
            iou=0.0,
            recall=0.0,
            precision=0.0,
            disagreement_fraction=1.0,
        )
    dd = np.abs(signed_distance_map(a) - signed_distance_map(b))
    union = a | b
    intersection = a & b
    disagreement = a ^ b
    union_area = int(union.sum())
    inter_area = int(intersection.sum())
    result = DistanceDeviation(
        valid=True,
        mean_union=float(dd[union].mean()),
        mean_disagreement=float(dd[disagreement].mean()) if disagreement.any() else 0.0,
        max_disagreement=float(dd[disagreement].max()) if disagreement.any() else 0.0,
        disagreement_fraction=float(disagreement.sum()) / union_area,
        dice=2.0 * inter_area / (area_a + area_b),
        iou=inter_area / union_area,
        recall=inter_area / area_a,
        precision=inter_area / area_b,
        mean_over_a=float(dd[a].mean()),
        mean_over_b=float(dd[b].mean()),
        area_a=area_a,
        area_b=area_b,
        deviation_image=dd if keep_image else None,
    )
    return result


def mask_ssim(mask_a, mask_b, crop=True):
    """
    SSIM between two binary masks treated as 0/1 float images.

    Windows where both masks are empty score 1.0, so on a large grid the value is
    dominated by background agreement. With crop=True (default) the comparison is
    restricted to the bounding box of the union of both masks (padded by one SSIM
    window) so the score describes the regions themselves.
    """
    a = mask_a.astype(bool)
    b = mask_b.astype(bool)
    if crop:
        union = a | b
        rows = np.where(union.any(axis=1))[0]
        cols = np.where(union.any(axis=0))[0]
        if rows.size and cols.size:
            pad = config.SSIM_WINDOW
            y0, y1 = max(0, rows[0] - pad), min(a.shape[0], rows[-1] + 1 + pad)
            x0, x1 = max(0, cols[0] - pad), min(a.shape[1], cols[-1] + 1 + pad)
            a, b = a[y0:y1, x0:x1], b[y0:y1, x0:x1]
    return ssim_wang(a.astype(np.float32), b.astype(np.float32), data_range=1.0)
