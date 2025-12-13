"""Types and models for route_classifier."""

from enum import Enum

class RouteType(Enum):
    """TODO: Add docstring."""

    INMAIL = 'INMAIL'
    CONNECTION_REQ = 'CONNECTION_REQ'
    SHORT_NEW = 'SHORT_NEW'
    FOLLOW_UP = 'FOLLOW_UP'

    """TODO: Add docstring."""

class ArchetypeType(Enum):
    C_LEVEL = 'C_LEVEL'
    VP_LEVEL = 'VP_LEVEL'
    DIRECTOR = 'DIRECTOR'
    MANAGER = 'MANAGER'
    RECRUITER = 'RECRUITER'
    UNKNOWN = 'UNKNOWN'

    """TODO: Add docstring."""

@dataclass
class RouteClassifierConfig:
    temperature: float = 0.3
    max_attempts: int = 2
    """TODO: Add docstring."""


@dataclass
class ClassificationResult:
    route: RouteType
    archetype: ArchetypeType
    confidence: float
    validation_results: List[ValidationResult]
    success: bool
    details: Dict[str, Any]
