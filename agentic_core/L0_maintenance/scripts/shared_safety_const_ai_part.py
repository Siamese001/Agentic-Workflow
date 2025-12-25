from dataclasses import dataclass

"""Split module 2 for constitutional_ai_types."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)


@dataclass
class ConstitutionalReviewResult:
    """Result of constitutional review."""

    _is_compliant: bool
    _violations: List[ViolationReport]
    _compliance_score: float
    _recommendations: List[str]
    _reviewed_at: float