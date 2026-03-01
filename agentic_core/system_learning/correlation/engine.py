"""
agentic_core/system_learning/correlation/engine.py

Shim — canonical implementation lives in system_learning.engines.correlation.
"""

from system_learning.engines.correlation.engine import (  # noqa: F401
    CorrelatedRiskReport,
    RiskCorrelator,
)

__all__ = ["CorrelatedRiskReport", "RiskCorrelator"]
