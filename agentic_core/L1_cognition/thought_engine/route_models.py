from __future__ import annotations
"""Dataclass models for lic_routing_rules."""
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Protocol

_logger = logging.getLogger(__name__)
# from agentic_core.lic_routing_rules_enums import *  # Star import removed


@dataclass
# NAMING FIXED: ToolCallBudget → ToolCallBudget
class ToolCallBudget:
    """Tool call budget configuration."""

    _minimum: int = 0
    _maximum: int = 20
    _guidance: Dict[str, str] = field(default_factory=dict)
