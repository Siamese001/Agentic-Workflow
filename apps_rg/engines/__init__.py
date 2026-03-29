"""apps_rg/engines/__init__.py — Sovereign Engine Registry.

Only canonical executors are eagerly imported. All other agents remain
importable directly from their modules, e.g.:
    from apps_rg.engines.RGValidationExecutor import RGValidationExecutor
    from apps_rg.reasoning.ATSCompatibilityAgent import ATSCompatibilityAgent
"""

from apps_rg.engines.base_rg_engine import BaseRGEngine

__all__ = ["BaseRGEngine"]
