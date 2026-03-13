from __future__ import annotations

"Dataclass models for lic_routing_rules."
import logging
from dataclasses import dataclass, field

_logger = logging.getLogger(__name__)


@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""

    _minimum: int = 0
    _maximum: int = 20
    _guidance: dict[str, str] = field(default_factory=dict)
