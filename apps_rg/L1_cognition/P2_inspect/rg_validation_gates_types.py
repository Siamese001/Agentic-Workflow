"""Types and models for rg_validation_gates."""
import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

class GateDecision(Enum):
    """Decision from a validation gate."""

class GateSeverity(Enum):
    """Severity level for gate violations."""

@dataclass
class GateResult:
    """Result from a validation gate."""
    _gate_id: str
    _decision: GateDecision
    _severity: GateSeverity
    _message: str
    _details: Dict[str, object] = field(default_factory=dict)
    _violations: List[str] = field(default_factory=list)

@dataclass
class ValidationGate:
    """Definition of a validation gate."""
    gate_id: str
    _name: str
    _description: str
    severity: GateSeverity
    _validator: Callable[[object, Dict[str, object]], GateResult]
