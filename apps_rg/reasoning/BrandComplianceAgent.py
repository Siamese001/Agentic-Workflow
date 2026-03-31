"""CONSOLIDATED: BrandComplianceAgent → RGValidationExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_rg.reasoning.RGValidationExecutor import RGValidationExecutor as BrandComplianceAgent

__all__ = ["BrandComplianceAgent"]
