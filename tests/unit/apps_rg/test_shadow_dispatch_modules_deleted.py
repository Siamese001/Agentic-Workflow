"""Retired ``apps_rg.runtime.dispatch.*_dispatch`` paths must not exist."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
DISPATCH_DIR = REPO / "apps_rg" / "runtime" / "dispatch"

RETIRED = (
    "executive_summary_dispatch.py",
    "competencies_dispatch.py",
    "unify_bullets_dispatch.py",
    "unify_narrative_dispatch.py",
    "ibm_bullets_dispatch.py",
    "ibm_narrative_dispatch.py",
    "headline_dispatch.py",
)


@pytest.mark.parametrize("filename", RETIRED)
def test_dispatch_shadow_file_absent(filename: str) -> None:
    assert not (DISPATCH_DIR / filename).is_file(), filename


def test_only_apps_rg_dispatch_bridge_remains() -> None:
    remaining = sorted(p.name for p in DISPATCH_DIR.glob("*_dispatch.py"))
    assert remaining == ["apps_rg_dispatch.py"], remaining
