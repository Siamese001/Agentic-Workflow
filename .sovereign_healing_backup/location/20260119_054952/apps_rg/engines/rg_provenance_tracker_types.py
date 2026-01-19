from __future__ import annotations
"""Types and models for rg_provenance_tracker."""
import datetime
import logging
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


# NAMING FIXED: ProvenanceType → ProvenanceType
class ProvenanceType(Enum):
    """Type of provenance source."""


# NAMING FIXED: BulletCategory → BulletCategory
class BulletCategory(Enum):
    """Category of bullet point."""


@dataclass
# NAMING FIXED: ProvenanceSource → ProvenanceSource
class ProvenanceSource:
    """Source information for provenance tracking."""

    _source_type: ProvenanceType
    _source_id: str
    _source_text: str
    _confidence: float = 1.0
    _timestamp: Optional[datetime] = None


@dataclass
# NAMING FIXED: BulletProvenance → BulletProvenance
class BulletProvenance:
    """Provenance information for a bullet point."""

    _bullet_id: str
    _bullet_text: str
    _category: BulletCategory
    _sources: List[ProvenanceSource] = field(default_factory=list)
    _transformation_log: List[str] = field(default_factory=list)
    _confidence_score: float = 1.0
    _created_at: datetime = field(default_factory=datetime.now)


@dataclass
# NAMING FIXED: ProvenanceMap → ProvenanceMap
class ProvenanceMap:
    """Map of provenance requirements by company/section."""

    _company: str
    _pattern: str
    _value_count: int = 0
    _technical_count: int = 0
    _soft_count: int = 0
    _achievement_count: int = 0