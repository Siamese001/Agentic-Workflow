"""Types and models for rg_validation_gates."""
import logging



class GateDecision(Enum):
    """Decision from a validation gate."""

class GateSeverity(Enum):
    """Severity level for gate violations."""

@dataclass
class GateResult:
    """Result from a validation gate."""
    gate_id: str
    decision: GateDecision
    severity: GateSeverity
    message: str
    details: Dict[str, object] = field(default_factory=dict)
    violations: List[str] = field(default_factory=list)

@dataclass
class ValidationGate:
    """Definition of a validation gate."""
    gate_id: str
    name: str
    description: str
    severity: GateSeverity
    validator: Callable[[object, Dict[str, object]], GateResult]
