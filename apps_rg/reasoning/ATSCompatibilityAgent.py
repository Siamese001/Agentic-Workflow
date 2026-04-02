"""CONSOLIDATED: ATSCompatibilityAgent → RGValidationExecutor (2026-02-08).

DEPRECATED: This shim will be removed in a future release.
Import the canonical executor directly:
    from apps_rg.engines.RGValidationExecutor import RGValidationExecutor

This file is a backward-compatibility shim.
"""

import warnings

warnings.warn(
    "ATSCompatibilityAgent is deprecated. Use RGValidationExecutor directly.",
    DeprecationWarning,
    stacklevel=2,
)

from apps_rg.engines.RGValidationExecutor import RGValidationExecutor as ATSCompatibilityAgent

__all__ = ["ATSCompatibilityAgent"]
