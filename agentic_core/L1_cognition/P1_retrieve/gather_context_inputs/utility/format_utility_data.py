# Ownership: agentic_core / L1_cognition
# -*- coding: utf-8 -*-
"""Format function data - atomic execution layer for shared types."""


from typing import Dict



def format_utility_data(data: Dict[str, object]) -> str:
    """Format function data for output."""
    return str(data)


def format_context_summary(context: Dict[str, object]) -> str:
    """Format context data as summary string."""
    keys = list(context.keys())[:5]
    return f"Context keys: {', '.join(keys)}"
