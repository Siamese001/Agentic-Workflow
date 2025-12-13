"""Dataclass models for lic_routing_rules."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .lic_routing_rules_enums import *

@dataclass
class ToolCallBudget:
    """Tool call budget configuration."""
    minimum: int = 0
    maximum: int = 20
    guidance: Dict[str, str] = field(default_factory=dict)
