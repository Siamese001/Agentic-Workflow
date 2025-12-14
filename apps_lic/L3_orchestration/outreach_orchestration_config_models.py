"""Dataclass models for outreach_orchestration_config."""
import logging


logger = logging.getLogger(__name__)
# from .outreach_orchestration_config_enums import *  # Star import removed

@dataclass
class CharLimitConstraint:
    """Character limit constraint for a route."""
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
class WordLimitConstraint:
    """Word limit constraint for a route."""
    min: Optional[int] = None
    max: Optional[int] = None

    def validate(self, count: int) -> bool:
        """Validate word count against constraints."""
        if self.min is not None and count < self.min:
            return False
        if self.max is not None and count > self.max:
            return False
        return True

@dataclass
class RouteConfig:
    """Configuration for a message route."""
    route: Route
    char_limit: Optional[CharLimitConstraint] = None
    word_limit: Optional[WordLimitConstraint] = None
    k_nodes_enabled: Dict[str, bool] = field(default_factory=dict)
    k_nodes_format: Dict[str, str] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    cta_word_limit: Optional[int] = None
    signature_format: str = 'standard'
    subject_line: bool = True
    attachments_allowed: bool = True

@dataclass
class ArchetypeConfig:
    """Configuration for recipient archetype."""
    archetype: Archetype
    temperature: float = 0.7
    rag_enabled: bool = True
    rag_hops: int = 2
    rag_total_calls: int = 5
    self_consistency_runs: int = 3
    tot_branches: int = 3
    message_format_template: str = 'standard'
    tone: str = 'professional'
    formality_level: str = 'moderate'

@dataclass
class ValidationRule:
    """Validation rule configuration."""
    rule_id: str
    name: str
    phase: str
    severity: ValidationSeverity
    description: str
    enforcement: str
    validation_method: str
    threshold: Optional[float] = None
