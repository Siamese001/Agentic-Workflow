"""CONSOLIDATED: FactCheckAgent → RGValidationExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_rg.engines.RGValidationExecutor import RGValidationExecutor as FactCheckAgent

__all__ = ["FactCheckAgent"]
