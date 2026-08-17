"""
Manual region-of-interest masks for pipeline 1.

`draw_roi` opens the standardized histology image with the automatic tissue
mask overlaid and lets the user outline one or more polygons; the union is
saved as `Image Validation/ROI/<Stem>.png` on the canonical histology grid.
`load_roi` reads that mask back (resized to the current grid) if it exists.
"""

from pathlib import Path

import cv2
import numpy as np
from scipy import ndimage

from . import config
from .loading import VALIDATION_ROOT, load_gray_float, resolve_image, stem_of
from .standardize import resize_to, standardize_intensity

ROI_DIR = VALIDATION_ROOT / "ROI"


def roi_path(base_name):
    return ROI_DIR / f"{stem_of(base_name)}.png"


def load_roi(base_name, shape):
    """Boolean ROI mask on the given (h, w) grid, or None if no ROI file exists."""
    path = roi_path(base_name)
    if not path.is_file():
        return None
    mask = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if mask is None:
        return None
    if mask.shape != tuple(shape[:2]):
        mask = resize_to(mask, shape[1], shape[0], nearest=True)
    return mask > 127


def draw_roi(base_name):
    """Interactive ROI tool: click detected structures to select them and/or draw polygons.

    Returns the saved mask path, or None if nothing was selected/drawn.
    """
    import matplotlib
    import matplotlib.pyplot as plt
    from matplotlib.path import Path as MplPath
    from matplotlib.widgets import PolygonSelector

    # Other modules may have left matplotlib on a non-interactive backend (e.g. Agg);
    # switch to the first interactive backend that actually loads on this machine.
    if not matplotlib.get_backend().lower().endswith(("macosx", "qtagg", "tkagg", "qt5agg", "gtk3agg", "wxagg")):
        errors = []
        for backend in ("macosx", "QtAgg", "TkAgg", "GTK3Agg", "WXAgg"):
            try:
                plt.switch_backend(backend)
                break
            except Exception as error:  # noqa: BLE001 - try the next backend
                errors.append(f"{backend}: {error}")
        else:
            raise RuntimeError("no interactive matplotlib backend could be loaded, cannot open the ROI window:\n  "
                               + "\n  ".join(errors))

    # Matplotlib's built-in hotkeys (p = pan, k/l = log axes, c = back, s = save, ...) would
    # collide with the tool's keys; disable them for this session.
    for name in list(plt.rcParams):
        if name.startswith("keymap."):
            plt.rcParams[name] = []

    hist_path = resolve_image("histology", base_name)
    if hist_path is None:
        raise FileNotFoundError(f"no histology image with stem '{stem_of(base_name)}' in {config.DIR_HISTOLOGY}")
    gray, _ = load_gray_float(hist_path)
    hist = standardize_intensity(gray, sparse=False)
    h, w = hist.image.shape
    base_rgb = cv2.cvtColor((hist.image * 255).astype(np.uint8), cv2.COLOR_GRAY2RGB)

    # Detected structures = connected components of the automatic tissue mask.
    labeled, count = ndimage.label(hist.foreground)
    existing = load_roi(base_name, hist.image.shape)
    selected = set()
    if existing is not None and count:
        # Pre-select components that lie mostly inside a previously saved ROI.
        for label in range(1, count + 1):
            component = labeled == label
            if (component & existing).sum() > 0.5 * component.sum():
                selected.add(label)

    polygons = []  # committed free-hand polygons as (kind, vertices); kind in {"add", "subtract", "keep"}
    POLY_COLORS = {"add": "red", "subtract": "orange", "keep": "magenta"}
    state = {"selector": None, "cancelled": False, "mode": "select", "kind": "add"}

    fig, ax = plt.subplots(figsize=(12, 12 * h / w))
    image_artist = ax.imshow(base_rgb)
    ax.axis("off")

    def render():
        display = base_rgb.copy()
        unselected = hist.foreground & ~np.isin(labeled, list(selected))
        chosen = np.isin(labeled, list(selected)) if selected else np.zeros_like(hist.foreground)
        display[unselected] = (0.55 * display[unselected] + 0.45 * np.array([0, 170, 255])).astype(np.uint8)
        display[chosen] = (0.45 * display[chosen] + 0.55 * np.array([0, 255, 60])).astype(np.uint8)
        image_artist.set_data(display)
        for patch in list(ax.patches):
            patch.remove()
        for kind, poly in polygons:
            ax.fill(*zip(*poly), color=POLY_COLORS[kind], alpha=0.3)
        mode = state["mode"].upper() + (f" ({state['kind']})" if state["mode"] == "polygon" else "")
        ax.set_title(f"ROI for {stem_of(base_name)}   [{len(selected)}/{count} structures selected, "
                     f"{len(polygons)} polygon(s)]   mode: {mode}\n"
                     "SELECT: click a blue structure to select (green) / again to deselect;  a = all,  c = clear\n"
                     "p = ADD polygon (red)   x = SUBTRACT polygon (orange)   k = KEEP-ONLY polygon (magenta)   "
                     "n = next polygon, u = undo;  enter/close = save;  esc = cancel")
        fig.canvas.draw_idle()

    def current_vertices():
        selector = state["selector"]
        if selector is None:
            return []
        try:
            return [tuple(v) for v in selector.verts]
        except Exception:  # noqa: BLE001
            return []

    def stop_selector():
        if state["selector"] is not None:
            state["selector"].disconnect_events()
            state["selector"] = None

    def commit_current():
        vertices = current_vertices()
        if len(vertices) >= 3:
            polygons.append((state["kind"], np.array(vertices, dtype=np.float32)))
            print(f"  {state['kind']} polygon {len(polygons)} added ({len(vertices)} vertices)")
            # Detach the selector so a later commit (e.g. close_event after enter) cannot
            # append the same polygon twice.
            stop_selector()
            return True
        return False

    def new_selector():
        stop_selector()
        state["selector"] = PolygonSelector(ax, lambda verts: None, useblit=False,
                                            props=dict(color=POLY_COLORS[state["kind"]], linewidth=1.5))

    def on_click(event):
        if state["mode"] != "select" or event.inaxes != ax or event.xdata is None or event.button != 1:
            return
        x, y = int(round(event.xdata)), int(round(event.ydata))
        if not (0 <= x < w and 0 <= y < h):
            return
        label = int(labeled[y, x])
        if label == 0:
            # Allow slightly-off clicks: pick the nearest structure within a few pixels.
            r = max(2, int(0.005 * h))
            window = labeled[max(0, y - r):y + r + 1, max(0, x - r):x + r + 1]
            nonzero = window[window > 0]
            if nonzero.size == 0:
                return
            label = int(np.bincount(nonzero).argmax())
        if label in selected:
            selected.remove(label)
            print(f"  structure {label} deselected ({len(selected)} selected)")
        else:
            selected.add(label)
            print(f"  structure {label} selected ({len(selected)} selected)")
        render()

    def enter_polygon_mode(kind):
        if state["mode"] == "polygon" and state["kind"] == kind:
            # Same key again -> back to select mode.
            commit_current()
            stop_selector()
            state["mode"] = "select"
            print("  SELECT mode: click structures to toggle them")
        else:
            if state["mode"] == "polygon":
                commit_current()
            state["mode"] = "polygon"
            state["kind"] = kind
            new_selector()
            print(f"  POLYGON mode ({kind}): click vertices; n = next polygon, u = undo, same key = back to select")
        render()

    def on_key(event):
        if event.key == "p":
            enter_polygon_mode("add")
        elif event.key == "x":
            enter_polygon_mode("subtract")
        elif event.key == "k":
            enter_polygon_mode("keep")
        elif event.key == "a":
            selected.update(range(1, count + 1))
            print(f"  all {count} structures selected")
            render()
        elif event.key == "c":
            selected.clear()
            polygons.clear()
            if state["mode"] == "polygon":
                new_selector()
            print("  selection cleared")
            render()
        elif event.key == "n" and state["mode"] == "polygon":
            commit_current()
            new_selector()
            render()
        elif event.key == "u" and state["mode"] == "polygon":
            if current_vertices():
                new_selector()
                print("  polygon in progress discarded")
            elif polygons:
                polygons.pop()
                print(f"  last polygon removed ({len(polygons)} left)")
            render()
        elif event.key == "enter":
            commit_current()
            plt.close(fig)
        elif event.key == "escape":
            state["cancelled"] = True
            plt.close(fig)

    def on_close(event):
        if not state["cancelled"]:
            commit_current()

    fig.canvas.mpl_connect("button_press_event", on_click)
    fig.canvas.mpl_connect("key_press_event", on_key)
    fig.canvas.mpl_connect("close_event", on_close)
    print("ROI tool: click the detected (blue) structures to select them (green); a = all, c = clear.")
    print("          p = ADD polygon, x = SUBTRACT polygon, k = KEEP-ONLY polygon (crop everything to it);")
    print("          n = next polygon, u = undo; enter or close the window = save; esc = cancel.")
    render()
    plt.show()

    if state["cancelled"]:
        print("ROI cancelled (esc).")
        return None
    if not selected and not polygons:
        print("Nothing selected; nothing saved.")
        return None

    mask = np.isin(labeled, list(selected)) if selected else np.zeros((h, w), dtype=bool)
    if polygons:
        yy, xx = np.mgrid[:h, :w]
        points = np.column_stack([xx.ravel(), yy.ravel()])
        masks = {kind: np.zeros(h * w, dtype=bool) for kind in POLY_COLORS}
        for kind, poly in polygons:
            masks[kind] |= MplPath(poly).contains_points(points)
        # ROI = (structures U add-polygons) minus subtract-polygons, cropped to keep-polygons if any.
        mask |= masks["add"].reshape(h, w)
        mask &= ~masks["subtract"].reshape(h, w)
        if any(kind == "keep" for kind, _ in polygons):
            mask &= masks["keep"].reshape(h, w)
    if not mask.any():
        print("The resulting ROI is empty; nothing saved.")
        return None
    ROI_DIR.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(roi_path(base_name)), mask.astype(np.uint8) * 255)
    kinds = {kind: sum(1 for k, _ in polygons if k == kind) for kind in POLY_COLORS}
    print(f"ROI: {len(selected)} structure(s), {kinds['add']} add / {kinds['subtract']} subtract / {kinds['keep']} keep-only "
          f"polygon(s); covers {100 * mask.mean():.1f}% of the grid")
    return roi_path(base_name)
