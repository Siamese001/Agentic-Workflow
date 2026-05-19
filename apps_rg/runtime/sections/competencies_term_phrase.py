"""Competency term display normalization (shared by dispatch repair and X2 diagnostics)."""

from __future__ import annotations

from typing import Any


def term_phrase(raw: Any) -> str:
    """Normalize a competency term to display text (string or structured object)."""
    if isinstance(raw, dict):
        return str(raw.get("text") or raw.get("phrase") or raw.get("term") or "").strip()
    return str(raw).strip()
