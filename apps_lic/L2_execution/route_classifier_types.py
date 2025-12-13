"""Types and models for route_classifier."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

class RouteType(Enum):
    INMAIL = 'INMAIL'
    CONNECTION_REQ = 'CONNECTION_REQ'
    SHORT_NEW = 'SHORT_NEW'
    FOLLOW_UP = 'FOLLOW_UP'

class ArchetypeType(Enum):
    C_LEVEL = 'C_LEVEL'
    VP_LEVEL = 'VP_LEVEL'
    DIRECTOR = 'DIRECTOR'
    MANAGER = 'MANAGER'
    RECRUITER = 'RECRUITER'
    UNKNOWN = 'UNKNOWN'

@dataclass
class RouteClassifierConfig:
    temperature: float = 0.3
    max_attempts: int = 2

@dataclass
class ClassificationResult:
    route: RouteType
    archetype: ArchetypeType
    confidence: float
    validation_results: List[ValidationResult]
    success: bool
    details: Dict[str, Any]
