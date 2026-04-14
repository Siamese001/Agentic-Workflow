"""Utility package for apps_shared.

Avoid eager imports here so standalone tests and partial environments can import
specific utility modules without dragging in the full agentic_core stack.
"""

from __future__ import annotations

__all__: list[str] = []
