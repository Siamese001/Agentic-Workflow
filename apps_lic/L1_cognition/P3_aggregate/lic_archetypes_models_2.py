"""Dataclass models for lic_archetypes."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from .lic_archetypes_enums import *

@dataclass
class SignatureTemplate:
    """Template for message signature."""
    template: str
    use_for: List[str]
    line_count: int

@dataclass
class GreetingTemplate:
    """Template for message greeting."""
    template: str
    note: str

