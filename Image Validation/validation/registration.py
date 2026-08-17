"""
Rigid (scale + rotation + translation) registration between two binary regions.

Used by pipeline 1 to bring the pc12 cell region onto the histology tissue region
when the two photographs were taken at different magnification / orientation.
The search is exhaustive over a coarse grid at reduced resolution, refined
around the best candidate, and scored by Dice overlap - so it can only ever be
accepted when it demonstrably improves the agreement.
"""

from dataclasses import dataclass

import cv2
import numpy as np

from . import config


@dataclass
class RigidTransform:
    scale: float = 1.0
    rotation_deg: float = 0.0
    dx: float = 0.0
    dy: float = 0.0
    dice_before: float = 0.0
    dice_after: float = 0.0

    @property
    def is_identity(self):
        return self.scale == 1.0 and self.rotation_deg == 0.0 and self.dx == 0.0 and self.dy == 0.0

    @property
    def at_search_limit(self):
        """True if the solution sits on the edge of the search range (likely a degenerate fit)."""
        lo, hi = config.RIGID_SCALE_RANGE
        scale_limit = config.RIGID_SEARCH_SCALE and (self.scale <= lo + 1e-6 or self.scale >= hi - 1e-6)
        return scale_limit or abs(self.rotation_deg) >= config.RIGID_MAX_ROTATION_DEG - 1e-6

    def matrix(self, shape):
        """2x3 affine matrix (rotation/scale about the image centre, then translation)."""
        h, w = shape[:2]
        matrix = cv2.getRotationMatrix2D((w / 2.0, h / 2.0), self.rotation_deg, self.scale)
        matrix[0, 2] += self.dx
        matrix[1, 2] += self.dy
        return matrix.astype(np.float32)

    def scaled(self, factor):
        """Same transform expressed on a grid `factor` times larger."""
        return RigidTransform(self.scale, self.rotation_deg, self.dx * factor, self.dy * factor,
                              self.dice_before, self.dice_after)


def dice(mask_a, mask_b):
    total = int(mask_a.sum()) + int(mask_b.sum())
    return 2.0 * int((mask_a & mask_b).sum()) / total if total else 0.0


def apply_rigid(image, transform, shape, nearest=False):
    """Warp an image (mask or intensity) with the transform onto a grid of the given shape."""
    h, w = shape[:2]
    flags = cv2.INTER_NEAREST if nearest else cv2.INTER_LINEAR
    src = image.astype(np.uint8) if image.dtype == bool else image
    warped = cv2.warpAffine(src, transform.matrix(shape), (w, h), flags=flags,
                            borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    return warped > 0 if image.dtype == bool else warped


def _translation_for(reference_blur, moving_mask, window):
    moving_blur = cv2.GaussianBlur(moving_mask.astype(np.float32), (0, 0), config.REGISTRATION_BOUNDARY_BLUR_SIGMA)
    (dx, dy), _ = cv2.phaseCorrelate(moving_blur, reference_blur, window)
    h, w = moving_mask.shape
    if abs(dx) > config.REGISTRATION_MAX_SHIFT_FRACTION * w or abs(dy) > config.REGISTRATION_MAX_SHIFT_FRACTION * h:
        return 0.0, 0.0
    return float(dx), float(dy)


def _search(reference, moving, scales, rotations, best):
    h, w = reference.shape
    reference_blur = cv2.GaussianBlur(reference.astype(np.float32), (0, 0), config.REGISTRATION_BOUNDARY_BLUR_SIGMA)
    window = cv2.createHanningWindow((w, h), cv2.CV_32F)
    for scale in scales:
        for rotation in rotations:
            candidate = RigidTransform(float(scale), float(rotation))
            warped = apply_rigid(moving, candidate, reference.shape, nearest=True)
            if not warped.any():
                continue
            candidate.dx, candidate.dy = _translation_for(reference_blur, warped, window)
            score = dice(reference, apply_rigid(moving, candidate, reference.shape, nearest=True))
            if score > best.dice_after:
                candidate.dice_after = score
                best = candidate
    return best


def estimate_rigid(reference_mask, moving_mask):
    """
    Find the rigid transform of `moving_mask` that maximises Dice with `reference_mask`.

    Returns a RigidTransform on the reference grid; if nothing beats the identity,
    the identity is returned (dice_after == dice_before).
    """
    reference = reference_mask.astype(bool)
    moving = moving_mask.astype(bool)
    baseline = dice(reference, moving)

    # Coarse search on a reduced grid for speed.
    factor = max(1.0, reference.shape[1] / float(config.RIGID_SEARCH_WIDTH))
    small = (max(8, int(round(reference.shape[1] / factor))), max(8, int(round(reference.shape[0] / factor))))
    ref_small = cv2.resize(reference.astype(np.uint8), small, interpolation=cv2.INTER_NEAREST) > 0
    mov_small = cv2.resize(moving.astype(np.uint8), small, interpolation=cv2.INTER_NEAREST) > 0

    identity = RigidTransform(dice_before=dice(ref_small, mov_small), dice_after=dice(ref_small, mov_small))
    if config.RIGID_SEARCH_SCALE:
        scales = np.arange(config.RIGID_SCALE_RANGE[0], config.RIGID_SCALE_RANGE[1] + 1e-9, config.RIGID_SCALE_STEP)
    else:
        scales = np.array([1.0])
    rotations = np.arange(-config.RIGID_MAX_ROTATION_DEG, config.RIGID_MAX_ROTATION_DEG + 1e-9, config.RIGID_ROTATION_STEP)
    best = _search(ref_small, mov_small, scales, rotations, identity)
    if not best.is_identity:
        if config.RIGID_SEARCH_SCALE:
            fine_scales = np.arange(best.scale - config.RIGID_SCALE_STEP, best.scale + config.RIGID_SCALE_STEP + 1e-9,
                                    config.RIGID_SCALE_STEP / 5.0)
        else:
            fine_scales = np.array([1.0])
        fine_rotations = np.arange(best.rotation_deg - config.RIGID_ROTATION_STEP,
                                   best.rotation_deg + config.RIGID_ROTATION_STEP + 1e-9, 1.0)
        fine_rotations = fine_rotations[np.abs(fine_rotations) <= config.RIGID_MAX_ROTATION_DEG + 1e-9]
        best = _search(ref_small, mov_small, fine_scales, fine_rotations, best)

    # Re-score at full resolution.
    full = best.scaled(factor)
    full.dice_before = baseline
    full.dice_after = dice(reference, apply_rigid(moving, full, reference.shape, nearest=True))
    if full.dice_after <= baseline:
        return RigidTransform(dice_before=baseline, dice_after=baseline)
    return full
