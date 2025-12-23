"""Dataclass models for lic_routing_rules."""
from typing import Any, Optional, Protocol, Dict, List
from dataclasses import dataclass, field


import logging

_logger = logging.getLogger(__name__)
# from .lic_routing_rules_enums import *  # Star import removed


@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""

    _minimum: int = 0
    _maximum: int = 20
    _guidance: Dict[str, str] = field(default_factory=dict)
