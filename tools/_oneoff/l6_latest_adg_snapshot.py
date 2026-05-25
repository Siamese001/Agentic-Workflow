"""Resolve latest artifacts/adg/adg_indexed_*.sqlite by mtime."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADG_DIR = REPO / "artifacts" / "adg"


def latest_indexed_snapshot() -> Path:
    candidates = sorted(ADG_DIR.glob("adg_indexed_*.sqlite"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidates:
        raise FileNotFoundError(f"No adg_indexed_*.sqlite under {ADG_DIR}")
    return candidates[0]
