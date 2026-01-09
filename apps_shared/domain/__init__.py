"""
Apps Shared Domain - Stub module for backwards compatibility.
"""
from typing import Any, Dict, List, Optional


class Domain:
    """Base domain class."""
    def __init__(self, name: str = "Domain"):
        self.name = name


__all__ = ['Domain']
