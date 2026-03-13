"""CONSOLIDATED: ContentStrategyAgent → RGStrategyExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_rg.engines.RGStrategyExecutor import RGStrategyExecutor as ContentStrategyAgent

__all__ = ["ContentStrategyAgent"]
