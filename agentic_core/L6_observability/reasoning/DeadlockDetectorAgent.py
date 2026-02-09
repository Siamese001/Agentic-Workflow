"""CONSOLIDATED: DeadlockDetectorAgent → ObservabilityProbeExecutor (2026-02-08).

This file is a backward-compatibility shim.
Import the canonical executor directly for new code.
"""

from agentic_core.L6_observability.reasoning.ObservabilityProbeExecutor import (
    ObservabilityProbeExecutor as DeadlockDetectorAgent,
)

__all__ = ["DeadlockDetectorAgent"]
