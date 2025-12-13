"""Implementation for data_models."""

from typing import Any, Dict, List, Optional
from .data_models_types import *

class FactualGapError(Exception):
    """
    v13.0: Raised by HOP-7 GateDecisionAgent when a FACTUAL failure is detected.
    This signals the HOPOrchestrator to trigger the S6->S2 "Slow Factual Loop"
    for a full re-planning and re-research cycle.
    """
    pass

class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is OPEN"""
    pass

