"""Split module 2 for constitutional_ai_types."""


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""
    is_compliant: bool
    violations: List[ViolationReport]
    compliance_score: float
    recommendations: List[str]
    reviewed_at: float
