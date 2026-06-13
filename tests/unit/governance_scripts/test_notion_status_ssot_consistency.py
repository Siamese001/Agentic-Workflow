"""SSOT enforcement: every Notion-Plans status definition across the repo agrees on
the LIVE 5-option set, and the removed "Lower Priority"/"Waiting" survive ONLY as
stale-coercion + forbidden (never as canonical/active/valid).

SSOT = ``_notion_plans_status_check.CANONICAL_STATUSES`` (+ derived ACTIVE/TERMINAL).
Derived: ``_notion_canonical`` imports it; ``_plan_lifecycle.PlanStatus`` mirrors it.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
GOV = REPO / ".claude" / "governance" / "scripts"

LIVE_FIVE = {"In Progress", "Not Started", "Completed", "Retired", "Archived"}
ACTIVE_TWO = {"In Progress", "Not Started"}
TERMINAL_THREE = {"Completed", "Retired", "Archived"}


def _load(name: str):
    if str(GOV) not in sys.path:
        sys.path.insert(0, str(GOV))
    spec = importlib.util.spec_from_file_location(name, GOV / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_ssot_sets_are_five_two_three():
    ck = _load("_notion_plans_status_check")
    assert set(ck.CANONICAL_STATUSES) == LIVE_FIVE
    assert set(ck.ACTIVE_STATUSES) == ACTIVE_TWO
    assert set(ck.TERMINAL_STATUSES) == TERMINAL_THREE


def test_notion_canonical_module_derives_from_ssot():
    _load("_notion_plans_status_check")
    nc = _load("_notion_canonical")
    assert set(nc.STATUS_IDS.keys()) == LIVE_FIVE
    assert set(nc.STATUS_COLORS.keys()) == LIVE_FIVE
    assert nc.get_active_statuses() == ACTIVE_TWO
    assert nc.get_terminal_statuses() == TERMINAL_THREE


def test_plan_lifecycle_enum_aligns_with_ssot():
    pl = _load("_plan_lifecycle")
    assert set(pl.PlanStatus.ALL) == LIVE_FIVE
    assert set(pl.PlanStatus.ACTIVE) == ACTIVE_TWO
    assert set(pl.PlanStatus.TERMINAL) == TERMINAL_THREE
    assert set(pl.PlanStatus.BLOCKED) == set()
    transitions = str(pl.VALID_PLAN_TRANSITIONS)
    assert "Lower Priority" not in transitions
    assert "Waiting" not in transitions


def test_removed_statuses_survive_only_as_stale_and_forbidden():
    ck = _load("_notion_plans_status_check")
    for removed in ("Lower Priority", "Waiting"):
        assert removed not in ck.CANONICAL_STATUSES
        assert removed in ck.FORBIDDEN_PLANS_STATUSES
        assert ck.STALE_EQUIVALENTS.get(removed) in LIVE_FIVE
