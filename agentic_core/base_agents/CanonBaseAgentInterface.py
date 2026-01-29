"""
CanonBaseAgentInterface - Protocol for CanonBaseAgent compatibility.

Provides interface definition for agents that need to interact with CanonBaseAgent.
Core interface protocol for sovereign agent architecture.
"""

from __future__ import annotations

from typing import Any, Protocol


class CanonBaseAgentInterface(Protocol):
    """Protocol for CanonBaseAgent interface compatibility."""

    ctx: Any
    name: str
    python_files: list[str]

    def smart_fix(self, file_path: str, violation_key: int) -> bool: ...
