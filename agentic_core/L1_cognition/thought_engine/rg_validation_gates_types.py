"""Types and models for rg_validation_gates."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: GateDecision → gate_decision
class gate_decision(Enum):
    """Decision from a validation gate."""


# NAMING FIXED: GateSeverity → gate_severity
class gate_severity(Enum):
    """Severity level for gate violations."""


@dataclass
# NAMING FIXED: GateResult → gate_result
class gate_result:
    """Result from a validation gate."""

    _gate_id: str
    _decision: GateDecision
    _severity: GateSeverity
    _message: str
    _details: Dict[str, object] = field(default_factory=dict)
    _violations: List[str] = field(default_factory=list)


@dataclass
# NAMING FIXED: ValidationGate → validation_gate
class validation_gate:
    """Definition of a validation gate."""

    gate_id: str
    _name: str
    _description: str
    severity: GateSeverity
    _validator: Callable[[object, Dict[str, object]], GateResult]
