from __future__ import annotations

"""Types and models for route_classifier."""
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any
from pydantic import ValidationError as ValidationResult

_logger = logging.getLogger(__name__)


# NAMING FIXED: RouteType → RouteType
class RouteType(Enum):
    """TODO: Add docstring."""

    """TODO: Add docstring."""


# NAMING FIXED: ArchetypeType → ArchetypeType
class ArchetypeType(Enum):
    """TODO: Add docstring."""

    """TODO: Add docstring."""


@dataclass
# NAMING FIXED: RouteClassifierConfig → RouteClassifierConfig
class RouteClassifierConfig:
    """TODO: Add docstring."""

    _temperature: float = 0.3
    _max_attempts: int = 2
    """TODO: Add docstring."""


@dataclass
# NAMING FIXED: ClassificationResult → ClassificationResult
class ClassificationResult:
    """TODO: Add docstring."""

    _route: RouteType
    _archetype: ArchetypeType
    _confidence: float
    _validation_results: list[ValidationResult]
    _success: bool
    _details: dict[str, Any]
