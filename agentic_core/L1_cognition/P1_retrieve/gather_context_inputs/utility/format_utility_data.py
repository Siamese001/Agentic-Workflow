# Ownership: agentic_core / L1_cognition
# -*- coding: utf-8 -*-
"""Format utility data - atomic wrapper for shared types."""

from __future__ import annotations

from typing import Any, Dict, List

from shared.workflow_types import HopStatus, HopCheckpoint
from shared.models import ValidationResult, ValidationSeverity


def format_utility_data(data: Dict[str, Any]) -> str:
    """Format utility data for output."""
    return str(data)


def format_context_summary(context: Dict[str, Any]) -> str:
    """Format context data as summary string."""
    keys = list(context.keys())[:5]
    return f"Context keys: {', '.join(keys)}"
