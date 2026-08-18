"""
The two validation pipelines and their CLI report.

Pipeline 1 ("pc12"):        pc12 culture image      vs. image-processed histology layers (the printed pattern)
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
# Pipeline 1: pc12 vs image-processed histology layers
# ---------------------------------------------------------------------------

def _align_cells_to_pattern(pc12, pattern, register):
    """Resample a standardized pc12 image onto the pattern grid and register it (if it helps)."""
    ref_h, ref_w = pattern.shape
    oth_h, oth_w = pc12.image.shape
    aspect_mismatch = abs((oth_w / oth_h) - (ref_w / ref_h)) / (ref_w / ref_h)
    image = resize_to(pc12.image, ref_w, ref_h)
    mask = resize_to(pc12.foreground.astype(np.uint8), ref_w, ref_h, nearest=True) > 0
    density = resize_to(pc12.density, ref_w, ref_h) if pc12.density is not None else None
    warnings = []
    reg_note = "disabled"
    if register == "rigid":
        transform = estimate_rigid(pattern, mask)
        if transform.is_identity:
            reg_note = "rigid: no transform improved the overlap"
        else:
            reg_note = f"rigid: rotated {transform.rotation_deg:+.0f} deg, shifted ({transform.dx:+.0f}, {transform.dy:+.0f}) px"
            mask = apply_rigid(mask, transform, (ref_h, ref_w), nearest=True)
            image = apply_rigid(image, transform, (ref_h, ref_w))
            if density is not None:
                density = apply_rigid(density, transform, (ref_h, ref_w))
            if transform.at_search_limit:
                warnings.append("the rigid fit sits at the edge of the search range - it may be matching the wrong "
                                "structure. Check pc12_region_on_layers.png; consider --register translation.")
    elif register == "translation":
        (dx, dy), _ = estimate_translation(pattern.astype(np.uint8), mask.astype(np.uint8))
        shifted = translate_labels(mask.astype(np.uint8), dx, dy) > 0
        if (dx, dy) != (0.0, 0.0) and _dice(pattern, shifted) > _dice(pattern, mask):
            reg_note = f"translation: shifted ({dx:+.0f}, {dy:+.0f}) px"
            mask = shifted
            matrix = np.array([[1.0, 0.0, dx], [0.0, 1.0, dy]], dtype=np.float32)
            image = cv2.warpAffine(image, matrix, (ref_w, ref_h), flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            if density is not None:
                density = cv2.warpAffine(density, matrix, (ref_w, ref_h), flags=cv2.INTER_LINEAR,
                                         borderMode=cv2.BORDER_CONSTANT, borderValue=0)
        else:
            reg_note = "translation: no shift improved the overlap"
    return {"image": image, "mask": mask, "density": density, "aspect_mismatch": aspect_mismatch,
            "reg_note": reg_note, "warnings": warnings, "dice": _dice(pattern, mask)}


def run_pc12_pipeline(base_name, mm_height=None, save=True, register="translation", alignment="auto"):
    _print_header(f"PIPELINE 1  pc12 culture vs. image-processed histology layers  [{stem_of(base_name)}]")
    ip_path = resolve_image("ip", base_name)
    pc12_path = resolve_image("pc12", base_name)
    missing = [name for name, p in (("Image Processing Segmentation", ip_path), ("pc12", pc12_path)) if p is None]
    if missing:
        print(f"SKIPPED: no image with stem '{stem_of(base_name)}' in: {', '.join(missing)}")
        return None

    # Reference: the image-processed layers (the printed pattern) as a label map.
    ip_rgb, ip_info = load_rgb_uint8(ip_path)
    layers = standardize_labels(ip_rgb)
    pattern = layers.labels != 0  # union of all layers = everything that was printed
    ref_h, ref_w = layers.labels.shape
    detail(f"IP layers: {ip_path.name}  {ip_info['size'][0]}x{ip_info['size'][1]} -> {ref_w}x{ref_h} canonical; "
           f"{len(layers.layer_labels)} layer(s)" + ("" if layers.has_background else "; no background"))
    for label in layers.layer_labels:
        entry = layers.legend[label]
        detail(f"      layer {label}: rgb{entry['rgb']}  {_pct(entry['fraction'])}")
    for note in layers.notes:
        detail(f"      note: {note}")

    # pc12 culture image -> cell region.
    pc12_gray, pc12_info = load_gray_float(pc12_path)
    detail(f"pc12:      {pc12_path.name}  {pc12_info['size'][0]}x{pc12_info['size'][1]} mode={pc12_info['mode']}"
           + (f"  (16-bit, raw range {pc12_info['raw_range'][0]:.0f}-{pc12_info['raw_range'][1]:.0f}, percentile-stretched)"
              if pc12_info.get("stretched") else ""))

    # Field-of-view handling: the pc12 photograph either covers the same field as the layer
    # image (full-frame) or only the printed content (content-crop). Evaluate the requested
    # candidate(s); each is registered and the one with the best overlap is kept.
    modes = ("full-frame", "content-crop") if alignment == "auto" else (alignment,)
    candidates = {}
    for mode in modes:
        pc12 = standardize_intensity(pc12_gray, sparse=True, crop=(mode == "content-crop"))
        candidates[mode] = _align_cells_to_pattern(pc12, pattern, register)
        candidates[mode]["pc12"] = pc12
        detail(f"  alignment {mode}: region Dice {candidates[mode]['dice']:.3f} ({candidates[mode]['reg_note']})")
    chosen = max(candidates, key=lambda k: candidates[k]["dice"])
    best = candidates[chosen]
    pc12, pc12_image, pc12_fg, pc12_density = best["pc12"], best["image"], best["mask"], best["density"]
    reg_note, aspect_mismatch = best["reg_note"], best["aspect_mismatch"]
    warnings = list(best["warnings"])
    for note in pc12.notes:
        detail(f"  [pc12] {note}")
    if aspect_mismatch > config.ASPECT_WARN_FRACTION:
        warnings.insert(0, f"aspect ratios differ by {100 * aspect_mismatch:.1f}% ({chosen} pc12 vs. layer image); "
                           f"pc12 is resampled anisotropically onto the layer grid")

    units = Units((ref_h, ref_w), mm_height)
    fg_fraction = float(pc12_fg.mean())
    deviation = None
    similarity = float("nan")
    per_layer = []
    if fg_fraction < config.MIN_FOREGROUND_FRACTION:
        print(f"contour deviation: SKIPPED - pc12 cell region covers only {_pct(fg_fraction)} of the grid "
              f"(image appears empty or mis-scaled)")
    else:
        similarity = mask_ssim(pattern, pc12_fg)
        deviation = distance_deviation(pattern, pc12_fg, keep_image=save)
        cells_total = int(pc12_fg.sum())
        for label in layers.layer_labels:
            layer_mask = layers.labels == label
            inter = int((layer_mask & pc12_fg).sum())
            per_layer.append({
                "label": label,
                "rgb": layers.legend[label]["rgb"],
                "fraction": float(layer_mask.mean()),
                "coverage": inter / int(layer_mask.sum()) if layer_mask.any() else float("nan"),
                "cell_share": inter / cells_total if cells_total else float("nan"),
            })

    if save:
        out = standardized_dir(base_name)
        layer_render = render_labels(layers.labels, layers.legend)
        _save_png(out / "layers_standardized.png", layer_render)
        _save_png(out / "pattern_mask.png", pattern)
        _save_png(out / "pc12_standardized.png", pc12_image)
        _save_png(out / "pc12_mask.png", pc12_fg)
        if pc12_density is not None:
            _save_png(out / "pc12_cell_density.png", pc12_density)
        overlay = (layer_render * 0.45).astype(np.uint8)
        overlay[pc12_fg] = (0.55 * overlay[pc12_fg] + 0.45 * np.array([255, 255, 255])).astype(np.uint8)
        _save_png(out / "pc12_region_on_layers.png", _contour_overlay(overlay, pc12_fg.astype(np.uint8), color=(255, 255, 255)))
        if deviation is not None and deviation.valid:
            _save_heatmap(out / "pc12_deviation_heatmap.png", deviation.deviation_image, pattern | pc12_fg)

    print(f"inputs        layers {ip_path.name} ({ip_info['size'][0]}x{ip_info['size'][1]}, {len(layers.layer_labels)} layers)  |  "
          f"pc12 {pc12_path.name} ({pc12_info['size'][0]}x{pc12_info['size'][1]})  |  grid {ref_w}x{ref_h} px"
          + (f", {units.mm_per_px:.5f} mm/px" if units.mm_per_px else ""))
    scores = ", ".join(f"{k} {v['dice']:.3f}" for k, v in candidates.items())
    print(f"settings      alignment {chosen} (Dice {scores})  |  registration {reg_note}")
    if deviation is not None and deviation.valid:
        print(f"SSIM          {_score(similarity)} region masks (printed pattern vs cell region, cropped to their bounding box)")
        print(f"deviation     mean {units.fmt(deviation.mean_union).strip()}   |   max {units.fmt(deviation.max_disagreement).strip()}")
        print(f"overlap       Dice {deviation.dice:.3f}   |   IoU {deviation.iou:.3f}   "
              f"(pattern {_pct(pattern.mean())} of grid, cells {_pct(fg_fraction)} of grid)")
        print(f"direction     recall {deviation.recall:.3f} (pattern covered by cells)   |   precision {deviation.precision:.3f} "
              f"(cells lying on the pattern)   |   mean deviation over pattern {deviation.mean_over_a:.1f} px, over cells {deviation.mean_over_b:.1f} px")
        for item in per_layer:
            print(f"  layer {item['label']} rgb{str(item['rgb']):<15} {_pct(item['fraction']):>7} of grid   "
                  f"covered by cells {_pct(item['coverage']):>7}   share of all cells {_pct(item['cell_share']):>7}")
    else:
        print("SSIM          n/a")
        print("deviation     n/a")
    if save:
        print(f"outputs       {standardized_dir(base_name)}")
    for text in warnings:
        print(f"WARNING       {text}")

    return {"ssim": similarity, "deviation": deviation, "foreground_fraction": fg_fraction, "layers": per_layer}


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
    valid_layers = [l for l in result.layers if l.deviation.valid]
    if valid_layers:
        weights = np.array([l.manual_fraction for l in valid_layers])
        weights = weights / weights.sum() if weights.sum() else weights
        w_recall = float(np.sum(weights * [l.deviation.recall for l in valid_layers]))
        w_precision = float(np.sum(weights * [l.deviation.precision for l in valid_layers]))
        print(f"direction     recall {w_recall:.3f} (manual layers covered by IP)   |   "
              f"precision {w_precision:.3f} (IP layer area lying on the matching manual layer)   (area-weighted)")
    for layer in result.layers:
        d = layer.deviation
        ip_text = ",".join(str(l) for l in layer.ip_labels) if layer.ip_labels else "none"
        if d.valid:
            print(f"  layer {layer.manual_label} rgb{str(layer.manual_rgb):<15} IP {ip_text:<6} Dice {d.dice:.3f}   "
                  f"recall {d.recall:.3f}   precision {d.precision:.3f}   "
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
                   verbose=False):
    """
    Run the requested validation pipeline(s) for a base image name.

    pipeline: "pc12", "segmentation" or "both".
    mm_height: optional physical height (mm) of the reference image, adds mm units.
    save: write standardized images / heat maps / mapping under Image Validation/Standardized/<stem>/.
    register: "rigid" (rotation+translation, pipeline 1; pipeline 2 uses translation),
              "translation" (both pipelines) or "none".
    alignment: "auto", "full-frame" or "content-crop" - field-of-view handling for both pipelines
               (auto tries both and keeps the better-fitting one).
    verbose: print the full diagnostics instead of the compact summary.
    Returns a dict with per-pipeline results (None where skipped).
    """
    if pipeline not in PIPELINES + ("both",):
        raise ValueError(f"pipeline must be one of {PIPELINES + ('both',)}, got {pipeline!r}")
    if register not in ("rigid", "translation", "none"):
        raise ValueError(f"register must be 'rigid', 'translation' or 'none', got {register!r}")
    global VERBOSE
    VERBOSE = bool(verbose)
    selected = PIPELINES if pipeline == "both" else (pipeline,)
    results = {}
    if "pc12" in selected:
        results["pc12"] = run_pc12_pipeline(base_name, mm_height=mm_height, save=save, register=register,
                                            alignment=alignment)
    if "segmentation" in selected:
        results["segmentation"] = run_segmentation_pipeline(base_name, mm_height=mm_height, save=save,
                                                            register=register, alignment=alignment)
    print()
    return results
