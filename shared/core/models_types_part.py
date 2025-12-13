"""Split module 1 for models_types."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class ValidationSeverity(Enum):
    """Severity levels for validation results."""
    INFO = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()

class Provider(str, Enum):
    """Available LLM providers."""
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    GOOGLE = 'google'
    MISTRAL = 'mistral'
    COHERE = 'cohere'
    GROQ = 'groq'
    TOGETHER = 'together'
    FIREWORKS = 'fireworks'

class APICallStatus(Enum):
    """Status of API calls."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    TIMEOUT = auto()
    RATE_LIMITED = auto()

@dataclass
class ValidationResult:
    """Result of a validation rule execution."""
    rule_id: str
    passed: bool
    severity: ValidationSeverity
    message: str
    details: Dict[str, object] = field(default_factory=dict)

@dataclass
class ThematicAnalysis:
    """Thematic analysis results from content inspection."""
    primary_theme: Dict[str, object] = field(default_factory=dict)
    secondary_themes: List[Dict[str, object]] = field(default_factory=list)
    role_classification: Dict[str, object] = field(default_factory=dict)
    positioning_directives: Dict[str, object] = field(default_factory=dict)
    authenticity_patterns: Dict[str, object] = field(default_factory=dict)
    competitive_intelligence: object = None
    problem_solution_narratives: Optional[Dict[str, object]] = None
    signal_quality_score: float = 0.0
    retrieval_method: str = 'UNKNOWN'
    retrieval_sources: List[Any] = field(default_factory=list)
    weighting_formula: Optional[Dict[str, object]] = None

