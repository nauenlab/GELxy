"""
Image validation package for GELxy.

Provides two validation pipelines driven by a base image name:

1. pc12 culture image vs. original histology (cell response to the stiffness gradient)
2. image-processing segmentation vs. manual segmentation (pipeline vs. human input)

Both report structural similarity (SSIM, Wang et al. 2004) and contour deviation error
(distance deviation measure, Rogelj et al., Radiol Oncol 2013;47(1):86-96).
"""

from .pipelines import run_validation  # noqa: F401
