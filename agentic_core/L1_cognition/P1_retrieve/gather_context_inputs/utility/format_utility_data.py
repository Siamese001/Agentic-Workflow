# Ownership: agentic_core / L1_cognition
# -*- coding: utf-8 -*-
"""Format utility data - atomic wrapper for shared types."""


from typing import Dict



def format_utility_data(data: Dict[str, object]) -> str:
    """Format utility data for output."""
    return str(data)


def format_context_summary(context: Dict[str, object]) -> str:
    """Format context data as summary string."""
    keys = list(context.keys())[:5]
    return f"Context keys: {', '.join(keys)}"
