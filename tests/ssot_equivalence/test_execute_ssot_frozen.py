"""Phase 0 — Freeze contract: both legacy SSOT files carry the FROZEN header."""

from __future__ import annotations

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

FROZEN_HEADER = "# FROZEN — superseded by l0_execute.py (Guardian→Dispatcher→Healer pipeline)."

LEGACY_FILES = [
    REPO_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot.py",
    REPO_ROOT / "agentic_core" / "L0_maintenance" / "scripts" / "execute_ssot_entrypoint.py",
]


def test_frozen_header_present():
    """Both legacy files must contain the exact FROZEN header string."""
    for fpath in LEGACY_FILES:
        assert fpath.exists(), f"Legacy file not found: {fpath}"
        content = fpath.read_text(encoding="utf-8")
        assert FROZEN_HEADER in content, (
            f"FROZEN header missing in {fpath.name}. Expected line: {FROZEN_HEADER!r}"
        )


def test_frozen_header_is_early():
    """FROZEN header must appear within the first 5 non-empty lines."""
    for fpath in LEGACY_FILES:
        lines = fpath.read_text(encoding="utf-8").splitlines()
        non_empty = [ln for ln in lines[:10] if ln.strip()]
        found = any(FROZEN_HEADER in ln for ln in non_empty[:5])
        assert found, f"FROZEN header not in first 5 non-empty lines of {fpath.name}"
