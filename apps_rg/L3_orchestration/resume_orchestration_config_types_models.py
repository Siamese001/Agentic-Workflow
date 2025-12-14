"""Dataclass models for resume_orchestration_config_types."""
import logging


# from .resume_orchestration_config_types_enums import *  # Star import removed

@dataclass
class WordCountConstraint:
    """Word count constraint for a section."""
    min: Optional[int] = None
    max: Optional[int] = None
    scope: str = 'total'
    unit: str = 'words'

    def validate(self, count: int) -> bool:
        """Validate word count against constraints."""
        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True

@dataclass
class CharCountConstraint:
    """Character count constraint for a section."""
    min: Optional[int] = None
    max: Optional[int] = None

    def validate(self, count: int) -> bool:
        """Validate character count against constraints."""
        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True

@dataclass
class ReasoningConfig:
    """Reasoning configuration for K-node execution."""
    temperature: float = 0.7
    rag_type: RAGType = RAGType.HYBRID
    rag_total_calls: int = 5
    rag_hops: int = 2
    claim_verification_mode: ClaimVerificationMode = ClaimVerificationMode.BALANCED
    hybrid_cot_tot: bool = True
    cot_min_paths: Optional[int] = 1
    tot_branches: Optional[int] = 3
    min_tot_depth: Optional[int] = 2
    self_consistency: int = 3
    reflexion: bool = True
    routing_tier: Optional[RoutingTier] = None

@dataclass
class ProvenanceRule:
    """Provenance rule for bullet generation."""
    verbatim: int
    transformed: int
    synthetic: int

    @property
    def total(self) -> int:
        """Total bullet count."""
        return self.verbatim + self.transformed + self.synthetic

    @property
    def pattern(self) -> str:
        """Provenance pattern string."""
        return f'{self.verbatim}V-{self.transformed}T-{self.synthetic}S'

@dataclass
class ValidationGate:
    """Validation gate configuration."""
    gate_id: str
    execution_point: str
    blocking: bool
    severity: ValidationSeverity
    checks: List[str] = field(default_factory=list)
    on_fail: str = 'HALT'
    halt_message: Optional[str] = None
