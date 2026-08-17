"""
Match image-processing segmentation layers to manual segmentation layers.

The two renderings use different colors, the automated pipeline may split one
manual layer across several of its own layers, and backgrounds differ. Both
inputs are therefore compared as label maps on a shared grid, and every IP
label is assigned (many-to-one, by majority pixel overlap) to the manual layer
it mostly covers - or to the manual background if that is what it mostly covers.
"""

from dataclasses import dataclass, field

import cv2
import numpy as np

from . import config
from .metrics import distance_deviation, mask_ssim, ssim_wang
from .standardize import LabelMap, cropped_to_content, render_labels, resize_to


@dataclass
class LayerComparison:
    manual_label: int
    manual_rgb: tuple
    ip_labels: list
    manual_fraction: float
    ip_fraction: float
    ssim: float
    deviation: object  # DistanceDeviation


@dataclass
class SegmentationComparison:
    grid_shape: tuple
    height_fraction: float  # share of the original manual image height covered by the grid
    alignment: str  # "full-frame" or "content-crop"
    alignment_scores: dict  # alignment mode -> boundary correlation after registration
    aspect_mismatch: float  # relative aspect ratio difference before resampling
    shift: tuple  # (dx, dy) px translation applied to IP for registration
    shift_response: float  # phase-correlation peak response (0-1)
    boundary_correlation: float  # correlation of layer-boundary maps after alignment
    mapping: dict  # ip label -> manual label (0 = background)
    overlap: np.ndarray  # rows: ip labels, cols: manual labels (pixel counts)
    layers: list  # LayerComparison per manual layer
    unmatched_manual: list  # manual layers with no IP counterpart
    spurious_ip_fraction: float  # IP layer area mapped to manual background
    unassigned_ip_fraction: float  # IP background sitting on manual layers
    composite_ssim: float  # SSIM of the two renderings in the manual palette
    pixel_accuracy: float
    mean_iou: float
    weighted_mean_deviation: float
    weighted_max_deviation: float
    manual_render: np.ndarray = field(repr=False, default=None)
    ip_render: np.ndarray = field(repr=False, default=None)
    manual_labels: np.ndarray = field(repr=False, default=None)  # manual labels on the comparison grid
    ip_aligned: np.ndarray = field(repr=False, default=None)  # IP labels (own numbering) after alignment
    ip_remapped: np.ndarray = field(repr=False, default=None)  # IP labels in manual numbering


def align_to_reference(reference: LabelMap, other: LabelMap):
    """Resample `other` onto the reference grid (nearest neighbour). Returns (labels, aspect_mismatch)."""
    ref_h, ref_w = reference.labels.shape
    oth_h, oth_w = other.labels.shape
    aspect_mismatch = abs((oth_w / oth_h) - (ref_w / ref_h)) / (ref_w / ref_h)
    labels = resize_to(other.labels, ref_w, ref_h, nearest=True)
    return labels, aspect_mismatch


def boundary_map(labels):
    """Soft map of label boundaries - independent of which colors/labels are used."""
    edges = np.zeros(labels.shape, dtype=bool)
    edges[:, 1:] |= labels[:, 1:] != labels[:, :-1]
    edges[1:, :] |= labels[1:, :] != labels[:-1, :]
    return cv2.GaussianBlur(edges.astype(np.float32), (0, 0), config.REGISTRATION_BOUNDARY_BLUR_SIGMA)


def estimate_translation(reference_labels, other_labels):
    """
    Estimate the (dx, dy) shift that best aligns other's layer boundaries onto the
    reference's, via phase correlation. Returns ((dx, dy), response).
    """
    ref = boundary_map(reference_labels)
    oth = boundary_map(other_labels)
    window = cv2.createHanningWindow((ref.shape[1], ref.shape[0]), cv2.CV_32F)
    (dx, dy), response = cv2.phaseCorrelate(oth, ref, window)
    h, w = reference_labels.shape
    if abs(dx) > config.REGISTRATION_MAX_SHIFT_FRACTION * w or abs(dy) > config.REGISTRATION_MAX_SHIFT_FRACTION * h:
        return (0.0, 0.0), float(response)
    return (float(dx), float(dy)), float(response)


def translate_labels(labels, dx, dy):
    """Shift a label map by (dx, dy) px, filling exposed pixels with background (0)."""
    matrix = np.array([[1.0, 0.0, dx], [0.0, 1.0, dy]], dtype=np.float32)
    return cv2.warpAffine(labels, matrix, (labels.shape[1], labels.shape[0]),
                          flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)


def boundary_correlation(labels_a, labels_b):
    """Pearson correlation of two boundary maps - a color-agnostic alignment score."""
    a = boundary_map(labels_a).ravel()
    b = boundary_map(labels_b).ravel()
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def _align_candidate(manual: LabelMap, ip: LabelMap, register):
    ip_labels, aspect_mismatch = align_to_reference(manual, ip)
    shift, response = (0.0, 0.0), 0.0
    score = boundary_correlation(manual.labels, ip_labels)
    if register:
        candidate, response = estimate_translation(manual.labels, ip_labels)
        if candidate != (0.0, 0.0):
            shifted = translate_labels(ip_labels, *candidate)
            shifted_score = boundary_correlation(manual.labels, shifted)
            # Keep the shift only if it actually improves the alignment.
            if shifted_score > score:
                ip_labels, shift, score = shifted, candidate, shifted_score
    return {
        "manual": manual, "ip_labels": ip_labels, "aspect_mismatch": aspect_mismatch,
        "shift": shift, "response": response, "score": score,
    }


def compare_segmentations(manual_full: LabelMap, ip_full: LabelMap, register=True, alignment="auto"):
    """
    Full comparison of an IP label map against a manual label map.

    alignment: "full-frame" (both images cover the same field of view),
    "content-crop" (compare bounding boxes of the segmented content), or "auto"
    (evaluate both and keep the one whose layer boundaries correlate best).
    """
    candidates = {}
    if alignment in ("auto", "full-frame"):
        candidates["full-frame"] = _align_candidate(manual_full, ip_full, register)
    if alignment in ("auto", "content-crop"):
        candidates["content-crop"] = _align_candidate(cropped_to_content(manual_full), cropped_to_content(ip_full), register)
    if not candidates:
        raise ValueError(f"alignment must be 'auto', 'full-frame' or 'content-crop', got {alignment!r}")
    chosen = max(candidates, key=lambda k: candidates[k]["score"])
    best = candidates[chosen]
    manual = best["manual"]
    manual_labels = manual.labels
    ip_labels = best["ip_labels"]
    ip = ip_full
    aspect_mismatch, shift, response = best["aspect_mismatch"], best["shift"], best["response"]
    n_ip = int(max(ip_labels.max(), max(ip.legend, default=0))) + 1
    n_manual = int(max(manual_labels.max(), max(manual.legend, default=0))) + 1

    combined = ip_labels.astype(np.int64) * n_manual + manual_labels.astype(np.int64)
    overlap = np.bincount(combined.ravel(), minlength=n_ip * n_manual).reshape(n_ip, n_manual)

    # IP background stays background. Every other IP label goes to the manual layer it
    # overlaps most - unless that is the background and a meaningful share of the label
    # still lies on some manual layer (thin manual structures would otherwise always lose
    # the vote to the surrounding background).
    mapping = {0: 0}
    for label in range(1, n_ip):
        row = overlap[label]
        total = row.sum()
        if total == 0:
            continue
        target = int(np.argmax(row))
        if target == 0 and n_manual > 1:
            best_layer = 1 + int(np.argmax(row[1:]))
            if row[best_layer] / total >= config.MAPPING_MIN_LAYER_SHARE:
                target = best_layer
        mapping[label] = target

    remapped = np.zeros_like(manual_labels)
    for ip_label, manual_label in mapping.items():
        remapped[ip_labels == ip_label] = manual_label

    total = float(manual_labels.size)
    layers = []
    unmatched = []
    ious = []
    weighted_mean = 0.0
    weighted_max = 0.0
    weight_total = 0.0
    for manual_label in manual.layer_labels:
        manual_mask = manual_labels == manual_label
        matched_ip = sorted(l for l, m in mapping.items() if m == manual_label and l != 0)
        ip_mask = remapped == manual_label
        deviation = distance_deviation(manual_mask, ip_mask)
        similarity = mask_ssim(manual_mask, ip_mask)
        comparison = LayerComparison(
            manual_label=manual_label,
            manual_rgb=manual.legend[manual_label]["rgb"],
            ip_labels=matched_ip,
            manual_fraction=float(manual_mask.mean()),
            ip_fraction=float(ip_mask.mean()),
            ssim=similarity,
            deviation=deviation,
        )
        layers.append(comparison)
        if not matched_ip:
            unmatched.append(manual_label)
        if deviation.valid:
            weight = float(manual_mask.sum())
            weighted_mean += deviation.mean_union * weight
            weighted_max += deviation.max_disagreement * weight
            weight_total += weight
            ious.append(deviation.iou)
        else:
            ious.append(0.0)

    spurious = float(sum(overlap[l].sum() for l, m in mapping.items() if l != 0 and m == 0)) / total
    unassigned = float(overlap[0, 1:].sum()) / total if n_manual > 1 else 0.0

    manual_render = render_labels(manual_labels, manual.legend)
    ip_render = render_labels(remapped, manual.legend)
    composite = ssim_wang(manual_render, ip_render, data_range=255.0)

    return SegmentationComparison(
        grid_shape=manual_labels.shape,
        height_fraction=manual.height_fraction,
        alignment=chosen,
        alignment_scores={k: v["score"] for k, v in candidates.items()},
        aspect_mismatch=aspect_mismatch,
        shift=shift,
        shift_response=response,
        boundary_correlation=best["score"],
        mapping=mapping,
        overlap=overlap,
        layers=layers,
        unmatched_manual=unmatched,
        spurious_ip_fraction=spurious,
        unassigned_ip_fraction=unassigned,
        composite_ssim=composite,
        pixel_accuracy=float((remapped == manual_labels).mean()),
        mean_iou=float(np.mean(ious)) if ious else float("nan"),
        weighted_mean_deviation=weighted_mean / weight_total if weight_total else float("nan"),
        weighted_max_deviation=weighted_max / weight_total if weight_total else float("nan"),
        manual_render=manual_render,
        ip_render=ip_render,
        manual_labels=manual_labels,
        ip_aligned=ip_labels,
        ip_remapped=remapped,
    )
