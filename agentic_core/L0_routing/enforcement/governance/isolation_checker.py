"""C0 G3: LAYER ISOLATION CHECK - Verify no boundary violations.

10C-REQ-112: Verify L0 routing no retrieval L1 reasoning no execution L2 execution no routing
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any


class LayerViolation(Enum):
    """Types of layer boundary violations."""
    L0_ROUTING_RETRIEVAL = auto()   # L0 performing C0 retrieval
    L1_REASONING_EXECUTION = auto() # L1 performing L2 execution
    L1_REASONING_ROUTING = auto()   # L1 performing L0 routing
    L2_EXECUTION_ROUTING = auto()   # L2 performing L0 routing
    L2_EXECUTION_WRITE = auto()     # L2 direct write (bypass UWG)
    L3_HEALING_UNBOUND = auto()     # L3 healing without context
    L6_LEARNING_MUTATION = auto()   # L6 mutating current run


@dataclass
class BoundaryCheck:
    """Result of layer isolation check."""
    is_valid: bool
    layer: str
    attempted_operation: str
    violation: LayerViolation | None = None
    reason: str = ""


class IsolationChecker:
    """C0 G3: Layer isolation checker.

    10C-REQ-112: Verify layer isolation L0 routes only L1 reasons only
    L2 executes only L3 heals only C0 retrieves only L6 observes only.
    """

    LAYER_AUTHORITY = {
        "L0": {"routing", "dispatch"},
        "L1": {"reasoning", "planning", "synthesis"},
        "L2": {"execution", "tool_invocation", "action"},
        "L3": {"healing", "remediation", "repair"},
        "L4": {"state_read", "archive"},
        "L5": {"exit_control", "safety", "policy"},
        "L6": {"observation", "evaluation", "shadow"},
        "C0": {"retrieval", "evidence_fetch"},
    }

    VIOLATION_PATTERNS = {
        ("L0", "retrieval"): LayerViolation.L0_ROUTING_RETRIEVAL,
        ("L1", "execution"): LayerViolation.L1_REASONING_EXECUTION,
        ("L1", "routing"): LayerViolation.L1_REASONING_ROUTING,
        ("L2", "routing"): LayerViolation.L2_EXECUTION_ROUTING,
        ("L2", "direct_write"): LayerViolation.L2_EXECUTION_WRITE,
    }

    def __init__(self) -> None:
        self._violation_count: int = 0

    def check(self, layer: str, operation: str, context: dict[str, Any] | None = None) -> BoundaryCheck:
        """Check if operation is allowed for layer."""
        allowed_ops = self.LAYER_AUTHORITY.get(layer, set())

        # Check if operation category is in allowed set
        op_category = self._categorize_operation(operation)

        if op_category not in allowed_ops:
            # Check for specific violation patterns
            violation = self.VIOLATION_PATTERNS.get((layer, op_category))
            self._violation_count += 1

            return BoundaryCheck(
                is_valid=False,
                layer=layer,
                attempted_operation=operation,
                violation=violation,
                reason=f"Layer {layer} cannot perform {op_category}",
            )

        return BoundaryCheck(
            is_valid=True,
            layer=layer,
            attempted_operation=operation,
        )

    def _categorize_operation(self, operation: str) -> str:
        """Categorize operation string to authority type."""
        op_lower = operation.lower()

        if any(x in op_lower for x in ["route", "dispatch", "direct"]):
            return "routing"
        elif any(x in op_lower for x in ["reason", "plan", "synthesize", "intent"]):
            return "reasoning"
        elif any(x in op_lower for x in ["execute", "tool", "invoke", "action", "run"]):
            return "execution"
        elif any(x in op_lower for x in ["heal", "repair", "remediate", "fix"]):
            return "healing"
        elif any(x in op_lower for x in ["retrieve", "fetch", "evidence", "rag", "search"]):
            return "retrieval"
        elif any(x in op_lower for x in ["write", "commit", "mutate", "persist"]):
            return "direct_write"
        elif any(x in op_lower for x in ["observe", "evaluate", "telemetry", "shadow"]):
            return "observation"
        else:
            return "unknown"

    def get_violation_count(self) -> int:
        """Get total violations detected."""
        return self._violation_count
