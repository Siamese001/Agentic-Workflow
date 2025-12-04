"""Simple reflexion scoring helpers."""
from __future__ import annotations


def apply_feedback(draft: str, insight: str) -> str:
    if not insight:
        return draft
    return f"{draft}\n\nReflexion: {insight}"
