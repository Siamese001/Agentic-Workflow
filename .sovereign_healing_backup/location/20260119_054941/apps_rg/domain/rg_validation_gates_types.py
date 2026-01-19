from __future__ import annotations
"""Types and models for rg_validation_gates."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: GateDecision → GateDecision
class GateDecision(Enum):
    """Decision from a validation gate."""


# NAMING FIXED: GateSeverity → GateSeverity
class GateSeverity(Enum):
    """Severity level for gate violations."""


@dataclass
# NAMING FIXED: GateResult → GateResult
class GateResult:
    """Result from a validation gate."""

    _gate_id: str
    _decision: GateDecision
    _severity: GateSeverity
    _message: str
    _details: Dict[str, object] = field(default_factory=dict)
    _violations: List[str] = field(default_factory=list)


@dataclass
# NAMING FIXED: ValidationGate → ValidationGate
class ValidationGate:
    """Definition of a validation gate."""

    gate_id: str
    _name: str
    _description: str
    Severity: GateSeverity
    _validator: Callable[[object, Dict[str, object]], GateResult]