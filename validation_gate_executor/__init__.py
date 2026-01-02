"""Validation Gate Executor - Core Types and Base Class.

Provides the execution engine types for ValidationGate and ValidationRule
objects used in orchestration config files.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class ValidationStatus(str, Enum):
    """Validation result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    BLOCK = "BLOCK"  # Critical failure - halt immediately


class ValidationAction(str, Enum):
    """Action to take on validation failure."""
    REGENERATE = "REGENERATE"
    HALT = "HALT"
    SOFT_REJECT = "SOFT_REJECT"
    WARN = "WARN"
    PROCEED = "PROCEED"


@dataclass
class RuleFailure:
    """Details of a failed validation rule."""
    rule_id: str
    rule_name: str
    severity: str
    message: str
    actual: Any
    expected: Any
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """Result of validation gate execution."""
    status: ValidationStatus
    gate_id: str
    execution_point: str
    failures: List[RuleFailure] = field(default_factory=list)
    action: ValidationAction = ValidationAction.PROCEED
    score: float = 1.0  # 0.0-1.0, for reversion policy
    message: Optional[str] = None
    
    @property
    def passed(self) -> bool:
        """Check if validation passed."""
        return self.status == ValidationStatus.PASS


class ValidationGateExecutor:
    """Base validation gate executor.
    
    Subclass this for domain-specific validation (e.g., OutreachValidationExecutorAgent).
    """
    
    def __init__(
        self,
        validation_gates: List[Any] = None,
        word_count_constraints: Dict[str, Any] = None,
        **kwargs
    ):
        """Initialize validation gate executor.
        
        Args:
            validation_gates: List of ValidationGate objects from config
            word_count_constraints: Word count constraints from config
        """
        self.validation_gates = validation_gates or []
        self.word_count_constraints = word_count_constraints or {}


__all__ = [
    "ValidationStatus",
    "ValidationAction",
    "RuleFailure",
    "ValidationResult",
    "ValidationGateExecutor",
]
