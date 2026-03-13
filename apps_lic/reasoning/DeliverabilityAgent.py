"""CONSOLIDATED: DeliverabilityAgent → LICValidationExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from apps_lic.engines.LICValidationExecutor import LICValidationExecutor as DeliverabilityAgent

__all__ = ["DeliverabilityAgent"]
