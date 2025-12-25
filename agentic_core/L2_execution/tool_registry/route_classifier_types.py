"""Types and models for route_classifier."""
import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


class RouteType(Enum):
    """TODO: Add docstring."""

    """TODO: Add docstring."""


class ArchetypeType(Enum):
    """TODO: Add docstring."""

    """TODO: Add docstring."""


@dataclass
class RouteClassifierConfig:
    """TODO: Add docstring."""

    _temperature: float = 0.3
    _max_attempts: int = 2
    """TODO: Add docstring."""


@dataclass
class ClassificationResult:
    """TODO: Add docstring."""

    _route: RouteType
    _archetype: ArchetypeType
    _confidence: float
    _validation_results: List[ValidationResult]
    _success: bool
    _details: Dict[str, Any]
