"""
Sanity checks for the image validation package with synthetic ground truth.

Run from the repository root:
    .venv/bin/python tests/validation_sanity.py
(also collectable by pytest).
"""

import os
import sys
import tempfile

import numpy as np
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "Image Validation"))

from validation import config  # noqa: E402
from validation.layer_matching import compare_segmentations  # noqa: E402
from validation.loading import load_gray_float  # noqa: E402
from validation.metrics import distance_deviation, mask_ssim, ssim_wang, wang_downsample_factor  # noqa: E402
from validation.pipelines import Units  # noqa: E402
from validation.standardize import standardize_intensity, standardize_labels  # noqa: E402


def _square(shape, y0, y1, x0, x1):
    mask = np.zeros(shape, dtype=bool)
    mask[y0:y1, x0:x1] = True
    return mask


def test_identical_images_have_perfect_scores():
    rng = np.random.default_rng(0)
    image = rng.random((300, 400)).astype(np.float32)
    assert abs(ssim_wang(image, image) - 1.0) < 1e-6
    mask = _square((300, 400), 50, 200, 80, 300)
    dev = distance_deviation(mask, mask)
    assert dev.valid and dev.mean_union == 0.0 and dev.max_disagreement == 0.0 and dev.dice == 1.0


def test_shifted_square_gives_exact_deviation():
    a = _square((400, 400), 100, 300, 100, 300)
    b = _square((400, 400), 100, 300, 110, 310)  # shifted 10 px right
    dev = distance_deviation(a, b)
    assert dev.valid
    # Two edges moved by 10 px: the maximum deviation (Hausdorff) is exactly 10.
    assert abs(dev.max_disagreement - 10.0) < 1e-6, dev.max_disagreement
    # Inside the moved bands the deviation is 10 except near the top/bottom rows,
    # where the nearest contour is the horizontal edge, so the mean is just under 10.
    assert 9.5 < dev.mean_disagreement <= 10.0, dev.mean_disagreement
    assert 0 < dev.mean_union < 10.0
    expected_dice = 2 * (200 * 190) / (2 * 200 * 200)
    assert abs(dev.dice - expected_dice) < 1e-9


def test_directed_measures_expose_overshoot():
    # A thick band over a thin one: full recall, low precision, symmetric Dice in between.
    thin = _square((200, 200), 95, 105, 20, 180)
    thick = _square((200, 200), 85, 115, 20, 180)
    dev = distance_deviation(thin, thick)
    assert abs(dev.recall - 1.0) < 1e-9
    assert abs(dev.precision - 1.0 / 3.0) < 1e-9
    assert abs(dev.dice - 0.5) < 1e-9
    # Overshoot shows as a larger mean deviation over the (thicker) prediction than over the reference.
    assert dev.mean_over_b > dev.mean_over_a > 0
    swapped = distance_deviation(thick, thin)
    assert abs(swapped.recall - dev.precision) < 1e-9 and abs(swapped.precision - dev.recall) < 1e-9


def test_ssim_prefers_structure_over_brightness():
    rng = np.random.default_rng(1)
    base = np.clip(rng.random((256, 256)).astype(np.float32) * 0.5 + 0.25, 0, 1)
    brighter = np.clip(base + 0.1, 0, 1)
    noisy = np.clip(base + rng.normal(0, 0.1, base.shape).astype(np.float32), 0, 1)
    assert ssim_wang(base, brighter) > ssim_wang(base, noisy)


def test_mask_ssim_is_not_inflated_by_empty_background():
    a = _square((1024, 800), 400, 500, 300, 400)
    b = _square((1024, 800), 420, 520, 300, 400)
    cropped = mask_ssim(a, b)
    whole = mask_ssim(a, b, crop=False)
    assert cropped < whole - 0.05, (cropped, whole)
    # Padding/cropping must not change the score of identical masks.
    assert abs(mask_ssim(a, a) - 1.0) < 1e-6


def test_downsample_factor_uses_shorter_edge():
    assert wang_downsample_factor((1024, 300)) == 1
    assert wang_downsample_factor((300, 1024)) == 1
    assert wang_downsample_factor((1024, 1024)) == 4


def test_units_account_for_content_crop():
    # 10 mm original, half of it kept by the crop, resized to a 1000 px grid.
    units = Units((1000, 1000), mm_height=10.0, height_fraction=0.5)
    assert abs(units.mm_per_px - 0.005) < 1e-12
    assert Units((1000, 1000)).mm_per_px is None


def test_empty_masks_are_reported_not_crashed():
    empty = np.zeros((50, 50), dtype=bool)
    full = _square((50, 50), 10, 40, 10, 40)
    assert not distance_deviation(empty, empty).valid
    dev = distance_deviation(full, empty)
    assert not dev.valid and dev.dice == 0.0


def _render(labels, palette, background):
    rgb = np.zeros(labels.shape + (3,), dtype=np.uint8)
    rgb[...] = background
    for label, color in palette.items():
        rgb[labels == label] = color
    return rgb


def test_label_standardization_and_matching_recovers_permuted_palette():
    # Manual: white background, red disc + green rectangle, thin black outline strokes.
    shape = (300, 400)
    yy, xx = np.mgrid[:shape[0], :shape[1]]
    manual_labels = np.zeros(shape, dtype=np.uint8)
    manual_labels[(yy - 150) ** 2 + (xx - 120) ** 2 < 70 ** 2] = 1
    manual_labels[60:240, 240:360] = 2
    manual_rgb = _render(manual_labels, {1: (255, 0, 0), 2: (0, 255, 0)}, background=(255, 255, 255))
    manual_rgb[150, :] = (3, 3, 3)  # a 1 px stroke across the image
    manual_rgb[:, 200] = (3, 3, 3)

    # IP: black background, different colors, disc split across two colors, plus a
    # spurious blob on the manual background.
    ip_labels = np.zeros(shape, dtype=np.uint8)
    disc = (yy - 150) ** 2 + (xx - 120) ** 2 < 70 ** 2
    ip_labels[disc & (yy < 150)] = 1
    ip_labels[disc & (yy >= 150)] = 2
    ip_labels[60:240, 240:360] = 3
    ip_labels[260:290, 20:60] = 4
    ip_rgb = _render(ip_labels, {1: (0, 0, 255), 2: (255, 255, 0), 3: (255, 0, 255), 4: (0, 255, 255)},
                     background=(0, 0, 0))

    manual = standardize_labels(manual_rgb)
    ip = standardize_labels(ip_rgb)
    assert manual.has_background and ip.has_background
    assert len(manual.layer_labels) == 2, manual.legend
    assert len(ip.layer_labels) == 4, ip.legend

    result = compare_segmentations(manual, ip, register=True, alignment="full-frame")
    red = [l for l in manual.layer_labels if manual.legend[l]["rgb"][0] > 200][0]
    green = [l for l in manual.layer_labels if manual.legend[l]["rgb"][1] > 200][0]
    targets = sorted(result.mapping[l] for l in ip.layer_labels)
    # Two IP layers -> red disc, one -> green rectangle, one -> background (spurious).
    assert targets == sorted([red, red, green, 0]), (result.mapping, red, green)
    assert result.pixel_accuracy > 0.98, result.pixel_accuracy
    for layer in result.layers:
        assert layer.deviation.valid
        assert layer.deviation.mean_union < 2.0, layer
        assert layer.ssim > 0.9, layer
    assert 0.005 < result.spurious_ip_fraction < 0.03


def test_uint16_loader_stretches_narrow_range():
    array = np.full((64, 64), 500, dtype=np.uint16)
    array[16:48, 16:48] = 900
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "narrow.png")
        Image.fromarray(array).save(path)
        gray, info = load_gray_float(path)
    assert info["stretched"]
    assert gray.min() == 0.0 and gray.max() == 1.0
    assert gray[32, 32] == 1.0 and gray[0, 0] == 0.0


def test_intensity_standardization_normalizes_polarity_and_grid():
    # Dark tissue on a bright background (like brightfield histology).
    gray = np.ones((200, 300), dtype=np.float32)
    gray[50:150, 80:220] = 0.2
    result = standardize_intensity(gray)
    assert result.inverted
    assert max(result.image.shape) == config.CANONICAL_LONG_EDGE
    assert result.foreground.mean() > 0.3


if __name__ == "__main__":
    tests = [(name, obj) for name, obj in sorted(globals().items()) if name.startswith("test_") and callable(obj)]
    failures = 0
    for name, test in tests:
        try:
            test()
            print(f"PASS  {name}")
        except AssertionError as error:
            failures += 1
            print(f"FAIL  {name}: {error}")
        except Exception as error:  # noqa: BLE001
            failures += 1
            print(f"ERROR {name}: {type(error).__name__}: {error}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
