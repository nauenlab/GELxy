"""
Explanatory figures for the validation metrics.

deviation_figure draws the distance deviation measure (Rogelj et al., Radiol Oncol
2013;47(1):86-96) in the form used in the manuscript: sample points spaced evenly along
the reference contour, each joined to the nearest point of the compared contour by a
measured segment labelled with its length in pixels. On the reference contour the signed
distance to that contour is zero, so these labels are the deviation measure itself
evaluated at those points, not a separate quantity.

The reported maximum is drawn apart from the rest, as the two legs joining the pixel of
greatest deviation to each contour; their lengths sum to that maximum, which is the
Hausdorff distance between the two contours.

Run standalone to regenerate the figure for any image in the validation set:

    python -m validation.figures BasisPontis.png --layer 1
"""

import numpy as np
import cv2
from scipy import ndimage

from .metrics import distance_deviation

# The two contours carry the comparison, so they take the cyan/red pair, which separates by lightness
# as well as hue and so survives protanopia and deuteranopia. Purple marks the maximum deviation and
# orange the per-point measurements. Orange and red are the one pair colour alone does not reliably
# separate under red-green deficiency, but the orange marks are short straight connectors and the red
# one is a long dashed closed curve, so shape distinguishes them. The contours are additionally
# distinguished by line style, so the figure does not rely on colour alone and survives grayscale
# printing. The sequential map below (cividis) is optimised for colour-vision deficiency and monotonic
# in lightness for the same reason, and its blue-yellow ramp does not collide with the contour colours.
COLOR_REFERENCE = "#1B9AAA"  # cyan
COLOR_COMPARED = "#DC3220"  # red
COLOR_MEASURE = "#C25100"  # orange, darkened so the thin lines and small labels stay legible on white
COLOR_WORST = "#5D3A9B"  # purple
STYLE_REFERENCE = "solid"
STYLE_COMPARED = "dashed"


def _boundary(mask):
    """Boundary pixels of a binary mask (the inner edge of the region)."""
    return mask & ~ndimage.binary_erosion(mask)


def _largest_contour(mask):
    """The longest closed contour of a mask, ordered, as an (N, 2) array of (row, col)."""
    contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return np.empty((0, 2), dtype=int)
    biggest = max(contours, key=len).reshape(-1, 2)  # (x, y)
    return biggest[:, ::-1]  # -> (row, col)


def _nearest_on(mask_boundary):
    """
    Nearest-boundary lookup for a contour.

    Returns (distance, rows, cols) arrays: for any pixel, its euclidean distance to the
    nearest boundary pixel and that pixel's coordinates.
    """
    distance, (rows, cols) = ndimage.distance_transform_edt(~mask_boundary, return_indices=True)
    return distance, rows, cols


def _sample_contour(contour, n_points):
    """`n_points` indices spaced evenly along an ordered contour."""
    if len(contour) <= n_points:
        return np.arange(len(contour))
    return np.linspace(0, len(contour), n_points, endpoint=False).astype(int)


def deviation_figure(reference_mask, compared_mask, out_path, n_points=14,
                     reference_name="manual segmentation", compared_name="automated segmentation",
                     title=None, mm_per_px=None, label_every=1):
    """
    Draw the contour deviation between two binary masks and save it to `out_path`.

    Args:
        reference_mask, compared_mask: equally shaped boolean arrays.
        out_path: destination PNG.
        n_points: how many sample points to place along the reference contour.
        reference_name, compared_name: legend labels.
        title: figure title; a metric summary is appended.
        mm_per_px: if given, distances are annotated in mm as well as pixels.
        label_every: label only every n-th sample point (use 2 when points crowd).

    Returns:
        The DistanceDeviation for the pair.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    reference_mask = reference_mask.astype(bool)
    compared_mask = compared_mask.astype(bool)
    deviation = distance_deviation(reference_mask, compared_mask, keep_image=True)

    ref_boundary = _boundary(reference_mask)
    cmp_boundary = _boundary(compared_mask)
    to_compared, cmp_rows, cmp_cols = _nearest_on(cmp_boundary)
    to_reference, ref_rows, ref_cols = _nearest_on(ref_boundary)

    contour = _largest_contour(reference_mask)
    samples = _sample_contour(contour, n_points)

    # The reported maximum is the largest deviation over the disagreement region. At a pixel there,
    # the two signed maps have opposite signs, so the deviation is the pixel's distance to one contour
    # plus its distance to the other - drawn below as the two legs meeting at that pixel, which is why
    # the drawn length equals `max_disagreement` exactly rather than approximating it.
    disagreement = reference_mask ^ compared_mask
    worst_at = np.unravel_index(
        np.argmax(np.where(disagreement, deviation.deviation_image, -1.0)), disagreement.shape)
    worst_legs = ((ref_rows[worst_at], ref_cols[worst_at]), (cmp_rows[worst_at], cmp_cols[worst_at]))
    worst_distance = deviation.max_disagreement

    def annotate(distance):
        text = f"{distance:.0f} px"
        return text + f"\n{distance * mm_per_px:.2f} mm" if mm_per_px else text

    figure, (left, right) = plt.subplots(1, 2, figsize=(13.5, 6.8))

    # --- Left: contours with measured deviations at the sample points ---
    left.imshow(np.ones(reference_mask.shape), cmap="gray", vmin=0, vmax=1)
    left.contourf(reference_mask.astype(float), levels=[0.5, 1.5], colors=[COLOR_REFERENCE], alpha=0.13)
    left.contourf(compared_mask.astype(float), levels=[0.5, 1.5], colors=[COLOR_COMPARED], alpha=0.13)
    left.contour(reference_mask.astype(float), levels=[0.5], colors=[COLOR_REFERENCE],
                 linewidths=1.8, linestyles=STYLE_REFERENCE)
    left.contour(compared_mask.astype(float), levels=[0.5], colors=[COLOR_COMPARED],
                 linewidths=1.8, linestyles=STYLE_COMPARED)

    for order, index in enumerate(samples):
        row, col = contour[index]
        near_row, near_col = cmp_rows[row, col], cmp_cols[row, col]
        distance = to_compared[row, col]
        left.plot([col, near_col], [row, near_row], color=COLOR_MEASURE, linewidth=1.1, zorder=3)
        left.plot([col], [row], "o", color=COLOR_REFERENCE, markersize=4.5,
                  markeredgecolor="white", markeredgewidth=0.6, zorder=4)
        if order % label_every:
            continue
        # Push the label outward from the region so it does not sit on the contour.
        centre_row, centre_col = ndimage.center_of_mass(reference_mask)
        away = np.array([row - centre_row, col - centre_col], dtype=float)
        norm = np.linalg.norm(away)
        away = away / norm * 34 if norm else np.zeros(2)
        height, width = reference_mask.shape
        margin = 26
        label_col = float(np.clip(col + away[1], margin, width - margin))
        label_row = float(np.clip(row + away[0], margin, height - margin))
        left.annotate(annotate(distance), xy=(col, row), xytext=(label_col, label_row),
                      fontsize=7.4, color=COLOR_MEASURE, ha="center", va="center", zorder=5,
                      bbox=dict(boxstyle="round,pad=0.18", facecolor="white", edgecolor="none", alpha=0.82))

    for leg in worst_legs:
        left.plot([worst_at[1], leg[1]], [worst_at[0], leg[0]], color=COLOR_WORST, linewidth=2.4, zorder=6)
    left.plot([worst_at[1]], [worst_at[0]], "*", color=COLOR_WORST, markersize=13,
              markeredgecolor="white", markeredgewidth=0.8, zorder=7)
    left.annotate(f"maximum deviation\n{annotate(worst_distance)}", xy=(worst_at[1], worst_at[0]),
                  xytext=(14, 14), textcoords="offset points", fontsize=8.2, color=COLOR_WORST,
                  fontweight="bold", zorder=8,
                  bbox=dict(boxstyle="round,pad=0.22", facecolor="white", edgecolor=COLOR_WORST, alpha=0.9))

    handles = [
        plt.Line2D([], [], color=COLOR_REFERENCE, linewidth=1.8, linestyle=STYLE_REFERENCE,
                   marker="o", markersize=5, label=reference_name),
        plt.Line2D([], [], color=COLOR_COMPARED, linewidth=1.8, linestyle=STYLE_COMPARED, label=compared_name),
        plt.Line2D([], [], color=COLOR_MEASURE, linewidth=1.1, label="deviation at sample point"),
        plt.Line2D([], [], color=COLOR_WORST, linewidth=2.4, marker="*", markersize=9,
                   label="maximum deviation (Hausdorff)"),
    ]
    left.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.09), ncol=2, fontsize=8, framealpha=0.92)
    left.set_title("Contour deviation at sample points", fontsize=11)
    left.set_xlabel("x (px)")
    left.set_ylabel("y (px)")

    # --- Right: the full deviation field the reported means are taken over ---
    union = reference_mask | compared_mask
    field = np.where(union, deviation.deviation_image, np.nan)
    image = right.imshow(field, cmap="cividis")
    for mask, colour, style in ((reference_mask, COLOR_REFERENCE, STYLE_REFERENCE),
                                (compared_mask, COLOR_COMPARED, STYLE_COMPARED)):
        # A white underlay keeps both contours legible over the dark and the bright end of the map.
        right.contour(mask.astype(float), levels=[0.5], colors=["white"], linewidths=2.4)
        right.contour(mask.astype(float), levels=[0.5], colors=[colour], linewidths=1.2, linestyles=style)
    bar = figure.colorbar(image, ax=right, fraction=0.046, pad=0.03)
    bar.set_label("deviation (px)" + (" / mm" if mm_per_px else ""), fontsize=9)
    right.set_title("Deviation over the union of both regions", fontsize=11)
    right.set_xlabel("x (px)")

    diagonal = float(np.hypot(*reference_mask.shape))
    summary = (f"Dice {deviation.dice:.3f}    "
               f"mean deviation {annotate(deviation.mean_union).replace(chr(10), ' ')} "
               f"({100 * deviation.mean_union / diagonal:.1f}% of diagonal)    "
               f"maximum {annotate(deviation.max_disagreement).replace(chr(10), ' ')} "
               f"({100 * deviation.max_disagreement / diagonal:.1f}%)")
    figure.suptitle(title or "Distance deviation between two contours", fontsize=12.5, y=0.98)
    figure.text(0.5, 0.915, summary, ha="center", fontsize=9.2, color="#333333")
    figure.tight_layout(rect=[0, 0.06, 1, 0.90])
    figure.savefig(out_path, dpi=190)
    plt.close(figure)
    return deviation


def _main(argv=None):
    import argparse
    from .layer_matching import compare_segmentations
    from .loading import load_rgb_uint8, resolve_image
    from .standardize import standardize_labels

    parser = argparse.ArgumentParser(prog="python -m validation.figures",
                                     description="Draw the contour deviation figure for one segmentation layer.")
    parser.add_argument("base_name", help="base image file name, e.g. BasisPontis.png")
    parser.add_argument("--layer", type=int, default=None, help="manual layer to draw (default: the largest)")
    parser.add_argument("--points", type=int, default=14, help="sample points along the reference contour")
    parser.add_argument("--label-every", type=int, default=1, help="label every n-th sample point")
    parser.add_argument("--mm-height", type=float, default=None, help="physical height of the reference image in mm")
    parser.add_argument("--out", default=None, help="output PNG path (default: Image Validation/figures/<stem>_contour_deviation.png)")
    args = parser.parse_args(argv)

    manual_path, ip_path = resolve_image("manual", args.base_name), resolve_image("ip", args.base_name)
    if manual_path is None or ip_path is None:
        raise SystemExit(f"no manual/IP image found for '{args.base_name}'")
    manual = standardize_labels(load_rgb_uint8(manual_path)[0])
    ip = standardize_labels(load_rgb_uint8(ip_path)[0])
    result = compare_segmentations(manual, ip)

    valid = [layer for layer in result.layers if layer.deviation.valid]
    if not valid:
        raise SystemExit("no comparable layer in this image pair")
    layer = (next(l for l in valid if l.manual_label == args.layer) if args.layer
             else max(valid, key=lambda l: l.manual_fraction))

    out_path = args.out
    if out_path is None:
        from pathlib import Path
        from .loading import VALIDATION_ROOT, stem_of
        directory = Path(VALIDATION_ROOT) / "figures"
        directory.mkdir(parents=True, exist_ok=True)
        # The layer is part of the name so figures for different layers do not overwrite one another.
        out_path = str(directory / f"{stem_of(args.base_name)}_layer{layer.manual_label}_contour_deviation.png")

    reference = result.manual_labels == layer.manual_label
    compared = result.ip_remapped == layer.manual_label
    mm_per_px = (args.mm_height * result.height_fraction / result.grid_shape[0]) if args.mm_height else None
    deviation = deviation_figure(
        reference, compared, out_path, n_points=args.points, label_every=args.label_every, mm_per_px=mm_per_px,
        title=f"Contour deviation: automated vs. manual segmentation ({args.base_name}, layer {layer.manual_label})")
    print(f"{out_path}: Dice {deviation.dice:.3f}, mean {deviation.mean_union:.2f} px, "
          f"max {deviation.max_disagreement:.2f} px")


if __name__ == "__main__":
    _main()
