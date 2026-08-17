"""
The two validation pipelines and their CLI report.

Pipeline 1 ("pc12"):        pc12 culture image      vs. original histology image
Pipeline 2 ("segmentation"): image-processing segmentation vs. manual segmentation

Both are keyed by a base file name (e.g. "Hippocampus.png") that is matched,
extension-agnostically, against each data directory under "Image Validation".
"""

import math
from pathlib import Path

import cv2
import numpy as np

from . import config
from .layer_matching import compare_segmentations, estimate_translation, translate_labels
from .registration import apply_rigid, estimate_rigid
from .roi import draw_roi, load_roi, roi_path
from .loading import load_gray_float, load_rgb_uint8, resolve_image, standardized_dir, stem_of
from .metrics import distance_deviation, mask_ssim, ssim_wang
from .standardize import render_labels, resize_to, standardize_intensity, standardize_labels

PIPELINES = ("pc12", "segmentation")
VERBOSE = False


def detail(*args, **kwargs):
    """Diagnostic output, shown only with --verbose."""
    if VERBOSE:
        print(*args, **kwargs)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

class Units:
    """Converts pixel distances into the reported unit strings."""

    def __init__(self, grid_shape, mm_height=None, height_fraction=1.0):
        """
        grid_shape: (h, w) of the comparison grid.
        mm_height: physical height of the *original* reference image in mm.
        height_fraction: share of the original image height that the grid covers
            (< 1 when the image was cropped to content before resizing).
        """
        h, w = grid_shape
        self.diagonal = math.hypot(h, w)
        self.mm_per_px = (mm_height * height_fraction / h) if mm_height else None

    def fmt(self, pixels):
        if pixels is None or (isinstance(pixels, float) and math.isnan(pixels)):
            return "n/a"
        text = f"{pixels:8.2f} px ({100.0 * pixels / self.diagonal:5.2f}% of diagonal)"
        if self.mm_per_px:
            text += f" = {pixels * self.mm_per_px:.4f} mm"
        return text


def _pct(value):
    return "n/a" if value is None or math.isnan(value) else f"{100.0 * value:.2f}%"


def _score(value):
    return "n/a" if value is None or math.isnan(value) else f"{value:.4f}"


def _print_header(title):
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def _save_png(path, array):
    path.parent.mkdir(parents=True, exist_ok=True)
    array = np.asarray(array)
    if array.dtype == bool:
        array = array.astype(np.uint8) * 255
    elif np.issubdtype(array.dtype, np.floating):
        array = np.clip(array * 255.0, 0, 255).astype(np.uint8)
    if array.ndim == 3:
        array = cv2.cvtColor(array, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(path), array)


def _save_heatmap(path, deviation_image, union_mask):
    """Deviation image rendered as a heat map, masked to the union region."""
    if deviation_image is None:
        return
    scale = float(np.percentile(deviation_image[union_mask], 99)) if union_mask.any() else 1.0
    scaled = np.clip(deviation_image / max(scale, 1e-6), 0, 1)
    colored = cv2.applyColorMap((scaled * 255).astype(np.uint8), cv2.COLORMAP_INFERNO)
    colored[~union_mask] = 0
    path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(path), colored)


def _dice(mask_a, mask_b):
    total = int(mask_a.sum()) + int(mask_b.sum())
    return 2.0 * int((mask_a & mask_b).sum()) / total if total else 0.0


def _interactive():
    """True when a human is at the terminal (so a window can be opened)."""
    import sys
    try:
        return sys.stdin.isatty() and sys.stdout.isatty()
    except Exception:  # noqa: BLE001
        return False


def _fraction_inside(mask, roi):
    total = int(mask.sum())
    return int((mask & roi).sum()) / total if total else 1.0


def _touched_components(reference_mask, other_mask):
    """
    Keep only the connected components of `reference_mask` that the `other_mask`
    reaches (allowing a small margin for misalignment). Returns (roi_mask,
    fraction of the reference area that was excluded).
    """
    from scipy import ndimage
    labeled, count = ndimage.label(reference_mask)
    if count == 0:
        return reference_mask, 0.0
    margin = max(1, int(round(config.ROI_TOUCH_MARGIN_FRACTION * reference_mask.shape[0])))
    reach = ndimage.binary_dilation(other_mask, iterations=margin)
    touched = np.unique(labeled[reach])
    touched = touched[touched != 0]
    roi = np.isin(labeled, touched)
    total = int(reference_mask.sum())
    excluded = 1.0 - int(roi.sum()) / total if total else 0.0
    return roi, excluded


def _print_deviation(dev, units, indent="    "):
    if not dev.valid:
        detail(f"{indent}contour deviation: n/a ({dev.reason})")
        return
    detail(f"{indent}mean deviation (union):        {units.fmt(dev.mean_union)}")
    detail(f"{indent}mean deviation (disagreement): {units.fmt(dev.mean_disagreement)}")
    detail(f"{indent}max deviation (Hausdorff):     {units.fmt(dev.max_disagreement)}")
    detail(f"{indent}disagreement area / union:     {_pct(dev.disagreement_fraction)}")
    detail(f"{indent}Dice: {dev.dice:.4f}   IoU: {dev.iou:.4f}")


# ---------------------------------------------------------------------------
# Pipeline 1: pc12 vs histology
# ---------------------------------------------------------------------------

def run_pc12_pipeline(base_name, mm_height=None, save=True, register="translation", roi="auto"):
    _print_header(f"PIPELINE 1  pc12 culture vs. histology  [{stem_of(base_name)}]")
    hist_path = resolve_image("histology", base_name)
    pc12_path = resolve_image("pc12", base_name)
    missing = [name for name, p in (("Histology", hist_path), ("pc12", pc12_path)) if p is None]
    if missing:
        print(f"SKIPPED: no image with stem '{stem_of(base_name)}' in: {', '.join(missing)}")
        return None

    hist_gray, hist_info = load_gray_float(hist_path)
    pc12_gray, pc12_info = load_gray_float(pc12_path)
    detail(f"histology: {hist_path.name}  {hist_info['size'][0]}x{hist_info['size'][1]} mode={hist_info['mode']}")
    detail(f"pc12:      {pc12_path.name}  {pc12_info['size'][0]}x{pc12_info['size'][1]} mode={pc12_info['mode']}"
          + (f"  (16-bit, raw range {pc12_info['raw_range'][0]:.0f}-{pc12_info['raw_range'][1]:.0f}, percentile-stretched)"
             if pc12_info.get("stretched") else ""))

    hist = standardize_intensity(hist_gray, sparse=False)
    pc12 = standardize_intensity(pc12_gray, sparse=True)
    for label, item in (("histology", hist), ("pc12", pc12)):
        for note in item.notes:
            detail(f"  [{label}] {note}")

    # Bring pc12 onto the histology grid.
    ref_h, ref_w = hist.image.shape
    oth_h, oth_w = pc12.image.shape
    aspect_mismatch = abs((oth_w / oth_h) - (ref_w / ref_h)) / (ref_w / ref_h)
    warnings = []
    if aspect_mismatch > config.ASPECT_WARN_FRACTION:
        warnings.append(f"aspect ratios differ by {100 * aspect_mismatch:.1f}% after content crop; "
                        f"pc12 is resampled anisotropically onto the histology grid")
    pc12_image = resize_to(pc12.image, ref_w, ref_h)
    pc12_fg = resize_to(pc12.foreground.astype(np.uint8), ref_w, ref_h, nearest=True) > 0

    # Registration on the (modality-agnostic) region masks, accepted only if it improves overlap.
    pc12_density = resize_to(pc12.density, ref_w, ref_h) if pc12.density is not None else None
    reg_note = "disabled"
    if register == "rigid":
        transform = estimate_rigid(hist.foreground, pc12_fg)
        if transform.is_identity:
            reg_note = "rigid: no transform improved the overlap"
            detail(f"  registration (rigid): no transform improved the overlap (region Dice {transform.dice_before:.3f})")
        else:
            reg_note = f"rigid: rotated {transform.rotation_deg:+.0f} deg, shifted ({transform.dx:+.0f}, {transform.dy:+.0f}) px"
            pc12_fg = apply_rigid(pc12_fg, transform, (ref_h, ref_w), nearest=True)
            pc12_image = apply_rigid(pc12_image, transform, (ref_h, ref_w))
            if pc12_density is not None:
                pc12_density = apply_rigid(pc12_density, transform, (ref_h, ref_w))
            detail(f"  registration (rigid): pc12 rotated {transform.rotation_deg:+.0f} deg, "
                  f"shifted dx={transform.dx:+.1f}, dy={transform.dy:+.1f} px "
                  f"(region Dice {transform.dice_before:.3f} -> {transform.dice_after:.3f})")
            if transform.at_search_limit:
                warnings.append("the rigid fit sits at the edge of the search range - it may be matching the wrong "
                                "structure. Check pc12_region_on_histology.png; consider --register translation.")
    elif register == "translation":
        (dx, dy), response = estimate_translation(hist.foreground.astype(np.uint8), pc12_fg.astype(np.uint8))
        shifted_fg = translate_labels(pc12_fg.astype(np.uint8), dx, dy) > 0
        dice_before = _dice(hist.foreground, pc12_fg)
        dice_after = _dice(hist.foreground, shifted_fg)
        if (dx, dy) != (0.0, 0.0) and dice_after > dice_before:
            reg_note = f"translation: shifted ({dx:+.0f}, {dy:+.0f}) px"
            pc12_fg = shifted_fg
            matrix = np.array([[1.0, 0.0, dx], [0.0, 1.0, dy]], dtype=np.float32)
            pc12_image = cv2.warpAffine(pc12_image, matrix, (ref_w, ref_h), flags=cv2.INTER_LINEAR,
                                        borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            if pc12_density is not None:
                pc12_density = cv2.warpAffine(pc12_density, matrix, (ref_w, ref_h), flags=cv2.INTER_LINEAR,
                                              borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            detail(f"  registration (translation): pc12 shifted by dx={dx:+.1f}, dy={dy:+.1f} px "
                  f"(region Dice {dice_before:.3f} -> {dice_after:.3f}, response {response:.3f})")
        else:
            reg_note = "translation: no shift improved the overlap"
            detail(f"  registration (translation): no shift applied (candidate dx={dx:+.1f}, dy={dy:+.1f} px did not "
                  f"improve region Dice {dice_before:.3f} -> {dice_after:.3f}; response {response:.3f})")
    else:
        detail("  registration: disabled")

    # Diagnostic only: a negative value would indicate opposite polarity after standardization.
    corr = float(np.corrcoef(hist.image.ravel(), pc12_image.ravel())[0, 1])

    fg_fraction = float(pc12_fg.mean())
    y0, y1, _, _ = hist.crop_box
    units = Units(hist.image.shape, mm_height, height_fraction=(y1 - y0) / hist.original_shape[0])
    ssim_value = ssim_wang(hist.image, pc12_image, data_range=1.0)
    detail()
    detail(f"grid: {ref_w}x{ref_h} px" + (f", {units.mm_per_px:.5f} mm/px" if units.mm_per_px else ""))
    detail(f"SSIM (histology vs pc12 intensity):     {_score(ssim_value)}")
    detail(f"pixel intensity correlation:            {corr:+.4f}")

    deviation = None
    roi_hist = hist.foreground
    whole_dice = _dice(hist.foreground, pc12_fg)
    whole_mask_ssim = mask_ssim(hist.foreground, pc12_fg)
    roi_label = "none"
    roi_note = ""
    if fg_fraction < config.MIN_FOREGROUND_FRACTION:
        print(f"contour deviation: SKIPPED - pc12 foreground covers only {_pct(fg_fraction)} of the image "
              f"(image appears empty or mis-scaled)")
    else:
        detail(f"tissue region (histology): {_pct(hist.foreground.mean())} of grid; "
              f"cell region (pc12): {_pct(fg_fraction)} of grid")
        detail(f"whole-image Dice (all histology structures, all cells): {whole_dice:.4f}")
        manual_roi = load_roi(base_name, hist.image.shape) if roi != "none" else None
        if roi == "draw" or (roi == "auto" and manual_roi is None and _interactive()):
            # Open the ROI tool inside the pipeline: always for "draw", or on first use for "auto".
            print("opening ROI tool" + (" (no ROI saved yet for this image)" if manual_roi is None else "")
                  + " - select structures / draw polygons, then press enter or close the window ...")
            try:
                saved = draw_roi(base_name, cell_mask=pc12_fg)
            except Exception as error:  # noqa: BLE001 - never let the UI take the metrics down
                saved = None
                print(f"ROI tool unavailable ({error}); continuing without a manual ROI")
            manual_roi = load_roi(base_name, hist.image.shape) if saved else manual_roi
        if roi == "none":
            # No ROI: every histology structure vs. the whole cell region.
            roi_hist = hist.foreground
            roi_label = "none (all histology structures)"
            detail("region of interest: none - comparing all histology structures with the whole cell region")
        elif manual_roi is not None:
            # Manual ROI: both regions are restricted to the drawn area.
            hist_excluded = 1.0 - _fraction_inside(hist.foreground, manual_roi)
            cell_excluded = 1.0 - _fraction_inside(pc12_fg, manual_roi)
            roi_hist = hist.foreground & manual_roi
            pc12_fg = pc12_fg & manual_roi
            roi_label = f"manual ROI ({roi_path(base_name).name})"
            roi_note = f"excludes {_pct(hist_excluded)} of tissue region, {_pct(cell_excluded)} of cell region"
            detail(f"region of interest: manual ROI from {roi_path(base_name).name} covering {_pct(manual_roi.mean())} of grid - "
                  f"excludes {_pct(hist_excluded)} of the tissue region and {_pct(cell_excluded)} of the cell region")
        else:
            # Automatic ROI: only the histology structures the printed pattern actually reaches.
            roi_hist, excluded = _touched_components(hist.foreground, pc12_fg)
            roi_label = "automatic ROI (touched structures)"
            roi_note = f"excludes {_pct(excluded)} of tissue region, 0.00% of cell region"
            detail(f"region of interest: automatic (histology structures touched by the cell region) - "
                  f"{_pct(1 - excluded)} of the tissue region kept, {_pct(excluded)} never reached by the pattern (excluded). "
                  f"Use --roi draw to select one manually")
        deviation = distance_deviation(roi_hist, pc12_fg, keep_image=save)
        detail("Contour deviation within the ROI (Rogelj distance deviation, ROI histology structures vs pc12 cell region):")
        _print_deviation(deviation, units)

    if save:
        out = standardized_dir(base_name)
        _save_png(out / "histology_standardized.png", hist.image)
        _save_png(out / "pc12_standardized.png", pc12_image)
        _save_png(out / "histology_mask.png", hist.foreground)
        _save_png(out / "histology_mask_roi.png", roi_hist)
        _save_png(out / "pc12_mask.png", pc12_fg)
        if pc12_density is not None:
            _save_png(out / "pc12_cell_density.png", pc12_density)
        overlay = cv2.cvtColor((hist.image * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)
        overlay[pc12_fg] = (0.55 * overlay[pc12_fg] + 0.45 * np.array([255, 0, 0])).astype(np.uint8)
        _save_png(out / "pc12_region_on_histology.png", overlay)
        if deviation is not None and deviation.valid:
            _save_heatmap(out / "pc12_deviation_heatmap.png", deviation.deviation_image, roi_hist | pc12_fg)
        detail(f"standardized outputs written to {out}")

    detail()
    roi_mask_ssim = mask_ssim(roi_hist, pc12_fg) if deviation is not None else float("nan")
    print(f"inputs        histology {hist_path.name} ({hist_info['size'][0]}x{hist_info['size'][1]})  |  "
          f"pc12 {pc12_path.name} ({pc12_info['size'][0]}x{pc12_info['size'][1]})  |  grid {ref_w}x{ref_h} px"
          + (f", {units.mm_per_px:.5f} mm/px" if units.mm_per_px else ""))
    print(f"settings      registration {reg_note}")
    print(f"ROI           {roi_label}" + (f" - {roi_note}" if roi_note else ""))
    if deviation is not None and deviation.valid:
        print(f"SSIM          {_score(roi_mask_ssim)} region masks within ROI, cropped to their bounding box   "
              f"({_score(whole_mask_ssim)} all structures;"
              f" intensity SSIM {_score(ssim_value)}, indicative only)")
        print(f"deviation     mean {units.fmt(deviation.mean_union).strip()}   |   max {units.fmt(deviation.max_disagreement).strip()}")
        print(f"overlap       Dice {deviation.dice:.3f} within ROI   ({whole_dice:.3f} whole image)   |   IoU {deviation.iou:.3f}")
    else:
        print(f"SSIM          intensity SSIM {_score(ssim_value)} (indicative only)")
        print("deviation     n/a")
    if save:
        print(f"outputs       {standardized_dir(base_name)}")
    for text in warnings:
        print(f"WARNING       {text}")

    return {"ssim": ssim_value, "deviation": deviation, "foreground_fraction": fg_fraction}


# ---------------------------------------------------------------------------
# Pipeline 2: image-processing segmentation vs manual segmentation
# ---------------------------------------------------------------------------

def _agreement_map(manual_labels, ip_labels):
    """Colour-coded agreement image: green agree, red missed, blue spurious, yellow wrong layer."""
    h, w = manual_labels.shape
    image = np.full((h, w, 3), 30, dtype=np.uint8)
    agree = (manual_labels == ip_labels) & (manual_labels != 0)
    missed = (manual_labels != 0) & (ip_labels == 0)
    spurious = (manual_labels == 0) & (ip_labels != 0)
    wrong = (manual_labels != 0) & (ip_labels != 0) & (manual_labels != ip_labels)
    image[agree] = (0, 200, 0)
    image[missed] = (230, 0, 0)
    image[spurious] = (0, 90, 255)
    image[wrong] = (255, 220, 0)
    return image


def _contour_overlay(base_rgb, labels, color=(255, 255, 255)):
    """Draw the boundaries between label regions on top of an RGB image."""
    edges = np.zeros(labels.shape, dtype=bool)
    edges[:, 1:] |= labels[:, 1:] != labels[:, :-1]
    edges[1:, :] |= labels[1:, :] != labels[:-1, :]
    edges = cv2.dilate(edges.astype(np.uint8), np.ones((2, 2), np.uint8)) > 0
    overlay = base_rgb.copy()
    overlay[edges] = color
    return overlay


def _describe_legend(name, label_map):
    detail(f"  {name}: {label_map.original_shape[1]}x{label_map.original_shape[0]} -> "
          f"{label_map.labels.shape[1]}x{label_map.labels.shape[0]} canonical; "
          f"{len(label_map.layer_labels)} layer(s)"
          + ("" if label_map.has_background else "; no background"))
    for label in label_map.layer_labels:
        entry = label_map.legend[label]
        detail(f"      layer {label}: rgb{entry['rgb']}  {_pct(entry['fraction'])}")
    for note in label_map.notes:
        detail(f"      note: {note}")


def run_segmentation_pipeline(base_name, mm_height=None, save=True, register="translation", alignment="auto"):
    _print_header(f"PIPELINE 2  image-processing vs. manual segmentation  [{stem_of(base_name)}]")
    manual_path = resolve_image("manual", base_name)
    ip_path = resolve_image("ip", base_name)
    missing = [name for name, p in (("Manual Segmentation", manual_path),
                                    ("Image Processing Segmentation", ip_path)) if p is None]
    if missing:
        print(f"SKIPPED: no image with stem '{stem_of(base_name)}' in: {', '.join(missing)}")
        return None

    manual_rgb, _ = load_rgb_uint8(manual_path)
    ip_rgb, _ = load_rgb_uint8(ip_path)
    manual = standardize_labels(manual_rgb)
    ip = standardize_labels(ip_rgb)
    detail("Standardized label maps:")
    _describe_legend(f"manual ({manual_path.name})", manual)
    _describe_legend(f"IP     ({ip_path.name})", ip)

    result = compare_segmentations(manual, ip, register=register != "none", alignment=alignment)
    units = Units(result.grid_shape, mm_height, height_fraction=result.height_fraction)
    scores = ", ".join(f"{k}: {v:.3f}" for k, v in result.alignment_scores.items())
    detail(f"  alignment: {result.alignment} (boundary correlation {scores})")
    warnings = []
    if result.aspect_mismatch > config.ASPECT_WARN_FRACTION:
        warnings.append(f"aspect ratios differ by {100 * result.aspect_mismatch:.1f}% after content crop; "
                        f"IP is resampled anisotropically onto the manual grid")
    if register != "none":
        detail(f"  registration: IP shifted by dx={result.shift[0]:+.1f}, dy={result.shift[1]:+.1f} px "
              f"(phase-correlation response {result.shift_response:.3f})")
    else:
        detail("  registration: disabled")

    detail()
    detail("Layer mapping (IP layer -> manual layer, by majority overlap):")
    for ip_label in sorted(l for l in result.mapping if l != 0):
        target = result.mapping[ip_label]
        target_text = "background" if target == 0 else f"manual layer {target} rgb{manual.legend[target]['rgb']}"
        overlap_row = result.overlap[ip_label]
        share = overlap_row[target] / max(1, overlap_row.sum())
        detail(f"    IP layer {ip_label} rgb{ip.legend.get(ip_label, {}).get('rgb', '?')} -> {target_text}"
              f"  ({_pct(share)} of its pixels)")
    if result.unmatched_manual:
        detail("    manual layers with NO IP counterpart: "
              + ", ".join(f"{l} rgb{manual.legend[l]['rgb']}" for l in result.unmatched_manual))

    detail()
    detail(f"grid: {result.grid_shape[1]}x{result.grid_shape[0]} px"
          + (f", {units.mm_per_px:.5f} mm/px" if units.mm_per_px else ""))
    detail(f"Composite SSIM (IP recolored in manual palette): {_score(result.composite_ssim)}")
    detail(f"Pixel agreement: {_pct(result.pixel_accuracy)}    mean IoU over manual layers: {_score(result.mean_iou)}")
    detail(f"IP layer area landing on manual background (spurious): {_pct(result.spurious_ip_fraction)}")
    detail(f"IP background sitting on manual layers (missed):       {_pct(result.unassigned_ip_fraction)}")
    detail()
    detail("Per-layer contour deviation (Rogelj distance deviation):")
    for layer in result.layers:
        ip_text = ", ".join(str(l) for l in layer.ip_labels) if layer.ip_labels else "none"
        detail(f"  manual layer {layer.manual_label} rgb{layer.manual_rgb}  "
              f"(manual {_pct(layer.manual_fraction)} / IP {_pct(layer.ip_fraction)} of grid; IP layers: {ip_text})")
        detail(f"    mask SSIM: {_score(layer.ssim)}")
        _print_deviation(layer.deviation, units)
    detail()
    detail(f"Area-weighted mean deviation over layers: {units.fmt(result.weighted_mean_deviation)}")
    detail(f"Area-weighted max deviation over layers:  {units.fmt(result.weighted_max_deviation)}")

    layer_ssims = [layer.ssim for layer in result.layers if not math.isnan(layer.ssim)]
    layer_mean_ssim = float(np.mean(layer_ssims)) if layer_ssims else float("nan")
    detail()
    reg_note = ("disabled" if register == "none" else
                (f"shifted ({result.shift[0]:+.0f}, {result.shift[1]:+.0f}) px" if result.shift != (0.0, 0.0)
                 else "no shift improved the alignment"))
    print(f"inputs        manual {manual_path.name} ({manual.original_shape[1]}x{manual.original_shape[0]}, "
          f"{len(manual.layer_labels)} layers)  |  IP {ip_path.name} ({ip.original_shape[1]}x{ip.original_shape[0]}, "
          f"{len(ip.layer_labels)} layers)  |  grid {result.grid_shape[1]}x{result.grid_shape[0]} px"
          + (f", {units.mm_per_px:.5f} mm/px" if units.mm_per_px else ""))
    print(f"settings      alignment {result.alignment}  |  registration {reg_note}")
    print("layer map     " + ";  ".join(
        f"IP {l} rgb{ip.legend.get(l, {}).get('rgb', '?')} -> "
        + ("background" if result.mapping[l] == 0 else f"manual {result.mapping[l]} rgb{manual.legend[result.mapping[l]]['rgb']}")
        for l in sorted(k for k in result.mapping if k != 0)))
    if result.unmatched_manual:
        print("              manual layers with NO IP counterpart: "
              + ", ".join(f"{l} rgb{manual.legend[l]['rgb']}" for l in result.unmatched_manual))
    print(f"SSIM          {_score(layer_mean_ssim)} layer-mean mask SSIM (each layer cropped to its bounding box)   "
          f"({_score(result.composite_ssim)} composite, whole image)")
    print(f"deviation     mean {units.fmt(result.weighted_mean_deviation).strip()}   |   "
          f"max {units.fmt(result.weighted_max_deviation).strip()}   (area-weighted over manual layers)")
    # Layers the IP missed entirely count as Dice 0 (consistent with mean IoU); only
    # layers empty on both sides (nothing to compare) are left out.
    dice_values = [l.deviation.dice for l in result.layers if not math.isnan(l.deviation.dice)]
    print(f"overlap       mean Dice {_score(float(np.mean(dice_values)) if dice_values else float('nan'))}   |   "
          f"pixel agreement {_pct(result.pixel_accuracy)}   |   spurious {_pct(result.spurious_ip_fraction)}   |   "
          f"missed {_pct(result.unassigned_ip_fraction)}")
    for layer in result.layers:
        d = layer.deviation
        ip_text = ",".join(str(l) for l in layer.ip_labels) if layer.ip_labels else "none"
        if d.valid:
            print(f"  layer {layer.manual_label} rgb{str(layer.manual_rgb):<15} IP {ip_text:<6} Dice {d.dice:.3f}   "
                  f"mean dev {d.mean_union:7.1f} px   max {d.max_disagreement:7.1f} px   mask SSIM {layer.ssim:.3f}")
        else:
            print(f"  layer {layer.manual_label} rgb{str(layer.manual_rgb):<15} IP {ip_text:<6} n/a ({d.reason})")

    if save:
        out = standardized_dir(base_name)
        _save_png(out / "manual_labels.png", result.manual_render)
        _save_png(out / "ip_labels_remapped.png", result.ip_render)
        _save_png(out / "ip_labels_original_palette.png", render_labels(result.ip_aligned, ip.legend))
        side_by_side = np.concatenate([result.manual_render, result.ip_render], axis=1)
        _save_png(out / "manual_vs_ip.png", side_by_side)
        _save_png(out / "segmentation_agreement.png", _agreement_map(result.manual_labels, result.ip_remapped))
        _save_png(out / "segmentation_contours.png", _contour_overlay(result.ip_render, result.manual_labels))
        detail("overlays: segmentation_agreement.png (green = agree, red = manual layer missed by IP, "
              "blue = IP layer where manual has background, yellow = different layer), "
              "segmentation_contours.png (IP result in manual palette with manual layer boundaries in white)")
        for layer in result.layers:
            if layer.deviation.valid:
                manual_mask = result.manual_labels == layer.manual_label
                ip_mask = result.ip_remapped == layer.manual_label
                dev = distance_deviation(manual_mask, ip_mask, keep_image=True)
                _save_heatmap(out / f"layer_{layer.manual_label}_deviation_heatmap.png",
                              dev.deviation_image, manual_mask | ip_mask)
        _write_mapping(out / "mapping.txt", result, manual, ip)
        print(f"outputs       {out}")
    for text in warnings:
        print(f"WARNING       {text}")

    return result


def _write_mapping(path, result, manual, ip):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["IP label -> manual label (0 = background)"]
    for ip_label, target in sorted(result.mapping.items()):
        ip_rgb = ip.legend.get(ip_label, {}).get("rgb", "background")
        target_rgb = manual.legend.get(target, {}).get("rgb", "background") if target else "background"
        lines.append(f"{ip_label} rgb{ip_rgb} -> {target} rgb{target_rgb}")
    lines.append("")
    lines.append("overlap matrix (rows: IP labels, cols: manual labels, pixel counts)")
    for row_idx, row in enumerate(result.overlap):
        lines.append(f"{row_idx}: " + " ".join(str(int(v)) for v in row))
    path.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_validation(base_name, pipeline="both", mm_height=None, save=True, register="translation", alignment="auto",
                   roi="auto", verbose=False):
    """
    Run the requested validation pipeline(s) for a base image name.

    pipeline: "pc12", "segmentation" or "both".
    mm_height: optional physical height (mm) of the reference image, adds mm units.
    save: write standardized images / heat maps / mapping under Image Validation/Standardized/<stem>/.
    register: "rigid" (rotation+translation, pipeline 1; pipeline 2 uses translation),
              "translation" (both pipelines) or "none".
    alignment: "auto", "full-frame" or "content-crop" (pipeline 2 field-of-view handling).
    roi: "auto" (use Image Validation/ROI/<stem>.png; if none exists and a terminal is attached, open the
         ROI tool first, otherwise fall back to touched structures), "draw" (always open the ROI tool,
         pre-selecting the saved one) or "none".
    verbose: print the full diagnostics instead of the compact summary.
    Returns a dict with per-pipeline results (None where skipped).
    """
    if pipeline not in PIPELINES + ("both",):
        raise ValueError(f"pipeline must be one of {PIPELINES + ('both',)}, got {pipeline!r}")
    if register not in ("rigid", "translation", "none"):
        raise ValueError(f"register must be 'rigid', 'translation' or 'none', got {register!r}")
    if roi not in ("auto", "draw", "none"):
        raise ValueError(f"roi must be 'auto', 'draw' or 'none', got {roi!r}")
    global VERBOSE
    VERBOSE = bool(verbose)
    selected = PIPELINES if pipeline == "both" else (pipeline,)
    results = {}
    if "pc12" in selected:
        results["pc12"] = run_pc12_pipeline(base_name, mm_height=mm_height, save=save, register=register, roi=roi)
    if "segmentation" in selected:
        results["segmentation"] = run_segmentation_pipeline(base_name, mm_height=mm_height, save=save,
                                                            register=register, alignment=alignment)
    print()
    return results
