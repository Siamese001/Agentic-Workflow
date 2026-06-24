"""Governed apps_rg C0 section evidence room (C0.1–C0.7)."""

from __future__ import annotations

from typing import Any

__all__ = ["run_section_c0_evidence_room"]


def __getattr__(name: str) -> Any:
    if name == "run_section_c0_evidence_room":
        from apps_rg.runtime.c0.evidence_room import run_section_c0_evidence_room

        return run_section_c0_evidence_room
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
