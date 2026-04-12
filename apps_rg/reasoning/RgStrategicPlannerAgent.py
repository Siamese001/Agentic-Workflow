"""CONSOLIDATED: RgStrategicPlannerAgent → RGStrategyExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_rg.reasoning.RGStrategyExecutor import RGStrategyExecutor as RgStrategicPlannerAgent

__all__ = ["RgStrategicPlannerAgent"]
