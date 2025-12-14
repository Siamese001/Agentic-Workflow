"""Types and models for route_classifier."""
import logging



class RouteType(Enum):
    """TODO: Add docstring."""


    """TODO: Add docstring."""

class ArchetypeType(Enum):
    """TODO: Add docstring."""

    """TODO: Add docstring."""

@dataclass
class RouteClassifierConfig:
    """TODO: Add docstring."""
    temperature: float = 0.3
    max_attempts: int = 2
    """TODO: Add docstring."""


@dataclass
class ClassificationResult:
    """TODO: Add docstring."""
    route: RouteType
    archetype: ArchetypeType
    confidence: float
    validation_results: List[ValidationResult]
    success: bool
    details: Dict[str, Any]
