"""Dataclass models for constitutional_ai."""

from typing import Any, Dict, List, Optional

# TODO: Replace 'from .constitutional_ai_enums import *' with explicit imports
# # from .constitutional_ai_enums import *  # Star import removed

@dataclass
class ConstitutionalPrinciple:
    """A constitutional principle for AI governance."""
    id: str
    name: str
    description: str = ''
    category: str = 'general'
    priority: int = 0
    examples: List[str] = None
    definition: Optional[str] = None
    evaluation_prompt: Optional[str] = None

    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.definition and (not self.description):
            self.description = self.definition

@dataclass
class LLMJudgment:
    """Judgment from an LLM on content compliance."""
    principle: str
    is_compliant: bool
    confidence: float
    reasoning: str
    timestamp: Optional[str] = None

    def __post_init__(self):
        if not self.timestamp:
            pass

    @property
    def principle_id(self) -> str:
        """Get principle ID (alias for principle)."""
        return self.principle

@dataclass
class ConstitutionalRule:
    """A single constitutional rule."""
    id: str
    name: str
    type: RuleType
    severity: RuleSeverity
    description: str
    pattern: Optional[str] = None
    keywords: List[str] = None
    action: RuleAction = RuleAction.WARN

    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []

@dataclass
class ViolationReport:
    """Report of a rule violation."""
    rule_id: str
    rule_name: str
    violation_type: ViolationType
    severity: RuleSeverity
    message: str
    matched_text: Optional[str] = None
    confidence: float = 0.0

@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""
    approved: bool
    violations: List[ViolationReport]
    score: float
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def has_violations(self) -> bool:
        """Check if there are any violations."""
        return len(self.violations) > 0

    @property
    def critical_violations(self) -> List[ViolationReport]:
        """Get only critical violations."""
        return [v for v in self.violations if v.severity == RuleSeverity.CRITICAL]
