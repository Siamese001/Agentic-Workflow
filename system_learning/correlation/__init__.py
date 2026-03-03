"""Risk correlation module for deterministic multi-signal correlation."""

from .engine import RiskCorrelator
from .types import CorrelatedRiskReport, CorrelatedRow, DriftEvent

__all__ = [
    "RiskCorrelator",
    "CorrelatedRiskReport",
    "CorrelatedRow",
    "DriftEvent",
]
