"""Split module 2 for constitutional_ai_types."""
import logging
logger = logging.getLogger(__name__)
_logger = logging.getLogger(__name__)

@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""
    _is_compliant: bool
    _violations: List[ViolationReport]
    _compliance_score: float
    _recommendations: List[str]
    _reviewed_at: float
