"""Types and models for rg_validation_gates."""


class GateDecision(Enum):
    """Decision from a validation gate."""
    PASS = 'PASS'
    FAIL = 'FAIL'
    WARN = 'WARN'
    SKIP = 'SKIP'

class GateSeverity(Enum):
    """Severity level for gate violations."""
    CRITICAL = 'CRITICAL'
    HIGH = 'HIGH'
    MEDIUM = 'MEDIUM'
    LOW = 'LOW'
    INFO = 'INFO'

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
