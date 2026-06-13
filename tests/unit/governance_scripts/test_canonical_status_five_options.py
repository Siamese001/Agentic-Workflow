"""Lock: the Plans-DB canonical Status set is limited to the LIVE 5 options.

Cross-checked 2026-06-08 against the live Notion Plans data source
(``ac53d31b-3068-4039-9ebe-856c12caab32``), whose Status select has exactly:
In Progress, Not Started, Completed, Retired, Archived.

"Lower Priority" and "Waiting" were never created in the live data source; writing
them would make Notion silently auto-create polluting options. So the enforcement
SSOT must (a) not list them as canonical, (b) coerce them to a live status, and
(c) forbid writing them.

This test loads the SSOT by path to avoid the rotted ``_legacy_windsurf`` import
shim used by ``test_notion_plans_status_check.py`` (pre-existing collection error).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HELPER = REPO / ".claude" / "governance" / "scripts" / "_notion_plans_status_check.py"

LIVE_FIVE = {"In Progress", "Not Started", "Completed", "Retired", "Archived"}


def _load():
    spec = importlib.util.spec_from_file_location("_nps_status_check_under_test", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_canonical_statuses_equal_live_db_five():
    m = _load()
    assert set(m.CANONICAL_STATUSES) == LIVE_FIVE


def test_lower_priority_and_waiting_are_not_canonical():
    m = _load()
    assert "Lower Priority" not in m.CANONICAL_STATUSES
    assert "Waiting" not in m.CANONICAL_STATUSES


def test_paused_blocked_family_coerces_to_a_live_status():
    m = _load()
    for stale in ("Lower Priority", "Waiting", "Deferred", "Deprioritized"):
        assert m.STALE_EQUIVALENTS.get(stale) in LIVE_FIVE, stale


def test_removed_statuses_are_forbidden_to_write():
    m = _load()
    assert "Lower Priority" in m.FORBIDDEN_PLANS_STATUSES
    assert "Waiting" in m.FORBIDDEN_PLANS_STATUSES


def test_ai_summary_enforced_set_derives_from_five():
    # PLANS_STATUSES_AI_SUMMARY_ENFORCED = canonical minus terminal Retired/Archived.
    m = _load()
    assert set(m.PLANS_STATUSES_AI_SUMMARY_ENFORCED) == {"In Progress", "Not Started", "Completed"}
