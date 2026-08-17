# Image Validation

Quantifies how well the GELxy print pipeline reproduces a histological structure, using two
metrics from the image-quality / contouring literature:

* **Structural Similarity Index (SSIM)** — Wang, Bovik, Sheikh & Simoncelli, *Image quality
  assessment: from error visibility to structural similarity*, IEEE TIP 13(4), 2004.
  Authors' page (parameters, reference MATLAB code, downsampling advice):
  <https://www.cns.nyu.edu/~lcv/ssim/> — scikit-image example:
  <https://scikit-image.org/docs/0.25.x/auto_examples/transform/plot_ssim.html>
* **Contour deviation error** — Rogelj, Hudej & Petric, *Distance deviation measure of
  contouring variability*, Radiol Oncol 2013;47(1):86-96.
  <https://pmc.ncbi.nlm.nih.gov/articles/PMC3573839/>

Two comparisons ("pipelines") are run for a given base image name:

| Pipeline | Compares | Question answered |
|---|---|---|
| 1 `pc12` | pc12 culture image **vs.** the original histology image | Did the cells arrange themselves where the histological structures are? |
| 2 `segmentation` | image-processing segmentation **vs.** manual (human) layer segmentation | Does the automatic layer extraction match a human's? |

Both print SSIM and contour deviation (plus Dice / IoU as familiar overlap numbers) and write
standardized images, overlays and deviation heat maps for visual inspection.

---

## Quick start

```bash
# from the repository root, inside the venv
python Controller.py validate Hippocampus.png            # both pipelines
python Controller.py validate Cerebellum.png --pipeline pc12
python Controller.py validate Hippocampus.png --mm-height 10 --verbose
python Controller.py roi Hippocampus.png                 # draw the pipeline-1 region of interest
python tests/validation_sanity.py                        # synthetic-ground-truth sanity checks
```

`validate --help` lists every option.

### Folder layout

Files are matched by **stem** (extension-agnostic, case-insensitive), so `Hippocampus.png`
also finds `Hippocampus.jpg`:

```
Image Validation/
├── Histology/                      original histology images (reference for pipeline 1)
├── pc12/                           photographs of the pc12 cultures printed from them
├── Manual Segmentation/            human-painted layer maps (reference for pipeline 2)
├── Image Processing Segmentation/  layer maps produced by Shapes/HistologicalImageProcessing
├── ROI/                            optional <Stem>.png region-of-interest masks (pipeline 1)
├── Standardized/<Stem>/            outputs written by every run
└── validation/                     the python package
```

### CLI options

| Option | Default | Meaning |
|---|---|---|
| `--pipeline pc12\|segmentation\|both` | `both` | which comparison(s) to run |
| `--mm-height H` | off | physical height (mm) of the **original** reference image; adds mm units to every distance (content cropping is accounted for) |
| `--register translation\|rigid\|none` | `translation` | align the second image to the reference before measuring (see *Registration*) |
| `--roi auto\|none` | `auto` | pipeline 1: `auto` uses `ROI/<Stem>.png` if it exists, else the histology structures the cells actually reach; `none` compares every structure |
| `--alignment auto\|full-frame\|content-crop` | `auto` | pipeline 2 field-of-view handling (see *Alignment*) |
| `--verbose / -v` | off | full diagnostics instead of the compact summary |
| `--no-save` | off | do not write anything under `Standardized/` |

---

## Reading the output

### Pipeline 1 (pc12 vs. histology)

```
inputs        histology Hippocampus.jpg (2880x2048)  |  pc12 Hippocampus.jpg (2000x1538)  |  grid 1024x728 px, 0.01374 mm/px
settings      registration translation: no shift improved the overlap
ROI           manual ROI (Hippocampus.png) - excludes 84.76% of tissue region, 94.09% of cell region
SSIM          0.9580 region masks within ROI, cropped to their bounding box   (0.1170 all structures; intensity SSIM 0.0445, indicative only)
deviation     mean 10.67 px ( 0.85% of diagonal) = 0.1466 mm   |   max 147.85 px (11.77% of diagonal) = 2.0309 mm
overlap       Dice 0.865 within ROI   (0.420 whole image)   |   IoU 0.762
```

* **SSIM** — the headline number is the SSIM of the two *region masks* (tissue region of the
  histology vs. cell region of the culture), cropped to their common bounding box. Intensity SSIM
  between an H&E photograph and a phase-contrast culture image is physically meaningless (different
  modalities, different textures) and is printed only as an indicator.
* **deviation** — Rogelj distance deviation between the two region contours: *mean* over the union
  of both regions and *max* over the disagreement region (= Hausdorff distance).
* **overlap** — Dice / IoU of the two regions, within the ROI and for the whole image.

### Pipeline 2 (IP vs. manual segmentation)

```
layer map     IP 1 rgb(0, 254, 1) -> manual 1 rgb(0, 255, 0);  IP 2 rgb(255, 0, 0) -> manual 2 rgb(255, 0, 0);  ...
SSIM          0.7646 layer-mean mask SSIM (each layer cropped to its bounding box)   (0.7720 composite, whole image)
deviation     mean 26.34 px ( 2.03% of diagonal)   |   max 173.32 px (13.36% of diagonal)   (area-weighted over manual layers)
overlap       mean Dice 0.8282   |   pixel agreement 77.20%   |   spurious 0.00%   |   missed 18.92%
  layer 1 rgb(0, 255, 0)     IP 1      Dice 0.830   mean dev    32.6 px   max   192.2 px   mask SSIM 0.621
```

* **layer map** — which IP colour was matched to which manual colour (many-to-one; an IP layer
  that mostly sits on manual background maps to `background` = spurious).
* **SSIM** — mean of the per-layer mask SSIMs, and the SSIM of the two renderings recoloured in the
  manual palette ("composite").
* **deviation** — per-layer distance deviation, area-weighted over the manual layers.
* **overlap** — mean Dice over manual layers (a layer the IP missed counts as 0), pixel agreement,
  *spurious* (IP layer area on manual background), *missed* (IP background on manual layers).
  Note: if the manual painting has **no background** (every pixel is a layer), any IP background is
  necessarily "missed".

### Files written to `Standardized/<Stem>/`

| File | Content |
|---|---|
| `histology_standardized.png`, `pc12_standardized.png` | the two intensity images after standardization, on the shared grid |
| `histology_mask.png`, `histology_mask_roi.png`, `pc12_mask.png` | tissue region, ROI-restricted tissue region, cell region |
| `pc12_cell_density.png` | cell-density map the cell region was thresholded from |
| `pc12_region_on_histology.png` | cell region (red) over the histology — check registration here |
| `pc12_deviation_heatmap.png` | Rogelj deviation image over the union region (paper's "image representation") |
| `manual_labels.png`, `ip_labels_remapped.png`, `ip_labels_original_palette.png`, `manual_vs_ip.png` | pipeline-2 label maps |
| `segmentation_agreement.png` | green agree, red missed, blue spurious, yellow wrong layer |
| `segmentation_contours.png` | IP result with manual layer boundaries in white |
| `layer_<n>_deviation_heatmap.png` | per-layer deviation image |
| `mapping.txt` | IP→manual label mapping and the full overlap matrix |

---

## What it does and why

### 1. Standardization (`validation/standardize.py`)

Metrics are only comparable if both inputs are in the same canonical form.

*Intensity images (histology, pc12)* → float32 grayscale in [0, 1], structures **bright on dark**,
cropped to content, CLAHE-equalised, resized so the longer edge is 1024 px.
Polarity is chosen automatically: the sparser Otsu class is taken to be the structure of interest
(cell-dense layers in H&E are the minority; cells in a culture image are the minority), and the
image is inverted if that class is bright. The **region mask** is derived from a smoothed density
rather than individual nuclei/cells, because the print reproduces *where tissue is*, not single
cells. For pc12 images the illumination is flattened and cells are detected by a morphological
top-hat (local contrast), so faint cells on a light gel are found as reliably as dark ones.
16-bit microscopy PNGs are percentile-stretched instead of divided by 65535 (they never use their
nominal range).

*Segmentation renderings (manual, IP)* → a uint8 **label map** (0 = background) plus a colour
legend. Colours are clustered on a coarse RGB grid to survive JPEG noise and anti-aliasing;
achromatic clusters are background (if large) or outline strokes (if thin, absorbed into their
neighbours); tiny islands are absorbed. Nearest-neighbour resizing keeps labels crisp.
Because the manual and IP renderings use different colours and the IP pipeline may split one
manual layer into several, IP labels are matched to manual labels **by majority pixel overlap**
(`layer_matching.py`), with a guard so thin manual structures are not always out-voted by the
surrounding background.

### 2. Registration and ROI

Small translations (or, with `--register rigid`, rotations) between the two photographs would
otherwise be reported as contour error. Translation is estimated by phase correlation of the
region/boundary maps and — like every alignment step here — **only accepted if it demonstrably
improves the overlap** (Dice / boundary correlation), so registration can never make the result
look worse than the raw comparison. `--register none` disables it.

Pipeline 1's histology image usually contains many structures the printed pattern never
targeted. Comparing the cell region against *all* of them mostly measures how much of the slide
was not printed. Therefore an ROI restricts the comparison: either a hand-drawn one
(`Controller.py roi <Stem>` — click detected structures, add/subtract/keep polygons; saved to
`ROI/<Stem>.png` on the canonical grid) or, automatically, only the structures the cell region
actually reaches. `--roi none` compares everything.

Pipeline 2 (`--alignment`): the manual and IP images may or may not share the same field of view.
`auto` evaluates both *full-frame* and *content-crop* (bounding box of the painted content) and
keeps whichever makes the layer boundaries correlate best.

### 3. SSIM (`validation/metrics.py::ssim_wang`)

Implemented with `skimage.metrics.structural_similarity` using the parameters of the original
paper: 11×11 Gaussian window (σ = 1.5), K1 = 0.01, K2 = 0.03, population (not sample) covariance,
and the authors' recommended pre-processing of averaging/downsampling by
`F = max(1, round(min(H, W) / 256))` so the index is evaluated at a perceptually appropriate scale
(their `ssim.m`). `data_range` is set explicitly (1.0 for float images and masks, 255 for RGB
renders), as the scikit-image example stresses.

Why SSIM on **masks** and not on raw intensities: SSIM measures structural agreement of two images
of the *same* signal. Histology and a culture photograph are different signals; two segmentation
renderings in different palettes are too. Comparing the region / layer masks measures the
structure we care about (where things are). SSIM of binary masks is 1.0 wherever both are empty,
so `mask_ssim` crops to the union bounding box (plus one window) — otherwise a large empty grid
would inflate the score toward 1.

### 4. Contour deviation (`validation/metrics.py::distance_deviation`)

Rogelj et al. argue that closest-point / Hausdorff measures are asymmetric, can miss differences
on complex shapes, and depend on one-to-one point mapping. Their **distance deviation** instead
computes a signed Euclidean distance transform for each contour (positive outside, negative
inside — eq. 1–2) and takes the absolute difference of the two distance images at *every* pixel.
This is symmetric, needs no correspondence, works for any topology, and yields absolute units
(px / mm). Following the paper we report:

* **mean deviation** over the union of both regions (their eq. 8–9, "the most balanced" summary),
* **max deviation** over the disagreement region (eq. 5–7; for two contours this equals the
  Hausdorff distance),
* the deviation image itself as a heat map (their "image representation").

Distances are measured to the pixel edge (half-pixel offset), so a region shifted by 10 px reports
exactly 10 px (checked by `tests/validation_sanity.py`). Dice and IoU are printed alongside because
they are familiar, but note the paper's point that they carry no shape/location information.

Distances are printed in px, as % of the grid diagonal (scale-free), and in mm when
`--mm-height` is given (the crop-to-content factor is applied so mm stay true to the original
image).

---

## Package layout

| Module | Role |
|---|---|
| `validation/config.py` | every tunable constant, documented |
| `validation/loading.py` | find images by stem, load as gray float / RGB uint8 |
| `validation/standardize.py` | canonical intensity images and label maps |
| `validation/registration.py` | rigid (rotation + translation) search for pipeline 1 |
| `validation/layer_matching.py` | pipeline-2 alignment, IP→manual layer mapping, per-layer metrics |
| `validation/roi.py` | interactive ROI tool and ROI loading |
| `validation/metrics.py` | `ssim_wang`, `mask_ssim`, `distance_deviation` |
| `validation/pipelines.py` | the two pipelines, reporting, output files |
| `tests/validation_sanity.py` | synthetic ground-truth checks (run standalone or with pytest) |

Dependencies: `numpy`, `scipy`, `opencv-python`, `scikit-image`, `Pillow`, `matplotlib`
(ROI tool only) — all in the repository `requirements.txt`.
