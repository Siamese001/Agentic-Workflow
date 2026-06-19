"""Compatibility shim for the legacy L6 system-learning engine namespace.

The canonical implementations now live in focused subpackages, but several
call sites and ADG import edges still reference
``agentic_core.L6_system_learning.engine``. Keep this module as a thin
backward-compatible surface so those imports remain resolvable while the code
base migrates to the canonical paths.
"""

from __future__ import annotations

from agentic_core.L6_system_learning.arbitration.engine import ArbitrationEngine
from agentic_core.L6_system_learning.confidence.engine import HealingConfidenceScorer
from agentic_core.L6_system_learning.correlation.engine import RiskCorrelator
from agentic_core.L6_system_learning.fingerprinting.engine import FailureFingerprinter

__all__ = [
    "ArbitrationEngine",
    "HealingConfidenceScorer",
    "RiskCorrelator",
    "FailureFingerprinter",
]
