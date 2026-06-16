"""W6 — shared proof SSOT versioning + briefing reuse + ops hardening.

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W6.1).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_lic.__main__ import _load_manual_brief_text
from apps_lic.integrations.apps_rg_proof_bridge import (
    load_apps_rg_proof_index,
    shared_proof_ssot_matches,
    shared_proof_ssot_stamp,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNBOOK = REPO_ROOT / "apps_lic" / "RUNBOOK.md"


def _require_shared_ssot():
    index = load_apps_rg_proof_index()
    if not index.available:
        pytest.skip(f"apps_rg shared proof SSOT unavailable: {index.load_error}")


def test_shared_proof_ssot_stamp_is_versioned_and_matches_apps_rg() -> None:
    _require_shared_ssot()
    stamp = shared_proof_ssot_stamp()
    assert stamp["available"] is True
    assert stamp["ssot_source"] == "apps_rg.augmented_skills_graph.v1"
    assert stamp["graph_version"] and stamp["graph_version"] != "unavailable"
    # resume (apps_rg) and outreach (apps_lic) read the SAME shared SSOT version.
    from apps_rg.fact_inventory.augmented_skills_graph import (  # noqa: PLC0415
        load_augmented_skills_graph,
    )

    assert shared_proof_ssot_matches(load_augmented_skills_graph()) is True


def test_shared_proof_ssot_drift_is_detected() -> None:
    _require_shared_ssot()
    # A divergent graph version is flagged (the no-drift guard actually guards).
    assert shared_proof_ssot_matches({"graph_metadata": {"graph_version": "DIVERGENT"}}) is False


def test_apps_lic_consumes_briefing_file_via_manual_brief(tmp_path: Path) -> None:
    # apps_lic reuses apps_rg's briefing.txt via --manual-brief: a plain-text
    # briefing path loads to its content (format-compatible).
    briefing = tmp_path / "briefing.txt"
    briefing.write_text(
        "AIG — Director, AI Platforms. Regulated insurer scaling agentic AI governance.\n",
        encoding="utf-8",
    )
    loaded = _load_manual_brief_text(str(briefing))
    assert "Director, AI Platforms" in loaded
    # inline text passes through unchanged too.
    assert _load_manual_brief_text("inline brief text") == "inline brief text"
    assert _load_manual_brief_text("") == ""


def test_runbook_documents_frontier_fail_closed_and_no_drift_ops() -> None:
    text = RUNBOOK.read_text(encoding="utf-8")
    assert "Claude Opus 4.8" in text
    assert "GPT-5.5" in text
    assert "fail-closed" in text.lower()
    assert "model_profiles.yaml" in text
    assert "cannot drift" in text  # shared SSOT ops note
    assert "never a stale default" in text  # dispositions reflect real verdicts
