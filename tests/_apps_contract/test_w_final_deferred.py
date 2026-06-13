"""Tests for apps-eval-harness-final-8f3e21 W1/W2/W3/W4.

Covers grounded FEC producers, promoted exec-positioning judge,
synthetic dev fixtures, and legacy-YAML deprecation headers.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


# ----- W1: grounded FEC producers ------------------------------------------


def test_grounded_producers_registered_for_all_5_apps():
    # Force a fresh import so module-side-effect registration runs.
    from apps_shared.cert import fec_producer
    from apps_shared.cert import grounded_fec_producers

    fec_producer.clear_registry()
    grounded_fec_producers.register_all()

    ids = fec_producer.registered_app_ids()
    for app_id in grounded_fec_producers.GROUNDED_APP_IDS:
        assert app_id in ids


def test_grounded_producer_returns_empty_when_no_bundle():
    from apps_shared.cert import fec_producer
    from apps_shared.cert import grounded_fec_producers

    fec_producer.clear_registry()
    grounded_fec_producers.register_all()

    assert fec_producer.resolve_fec("apps_qna", {}) == {}
    assert fec_producer.resolve_fec("apps_qna", {"evidence_bundle": {}}) == {}


def test_grounded_producer_projects_bundle_to_fec_pass():
    from apps_shared.cert import fec_producer
    from apps_shared.cert import grounded_fec_producers

    fec_producer.clear_registry()
    grounded_fec_producers.register_all()

    ctx = {
        "evidence_bundle": {
            "support_score": 0.92,
            "cited_spans": ["s1", "s2"],
            "contract_refs": ["ref1"],
        }
    }
    fec = fec_producer.resolve_fec("apps_research", ctx)
    assert fec["c0_status"] == "PASS"
    assert fec["support_score"] == 0.92
    assert fec["cited_spans"] == ["s1", "s2"]
    assert fec["contradiction_flags"] == []


def test_grounded_producer_flags_contradictions_as_fail():
    from apps_shared.cert import fec_producer
    from apps_shared.cert import grounded_fec_producers

    fec_producer.clear_registry()
    grounded_fec_producers.register_all()

    ctx = {
        "evidence_bundle": {
            "support_score": 0.9,
            "contradiction_flags": ["conflict1"],
        }
    }
    fec = fec_producer.resolve_fec("apps_research", ctx)
    assert fec["c0_status"] == "FAIL"


def test_grounded_producer_weak_band_for_mid_support():
    from apps_shared.cert import fec_producer
    from apps_shared.cert import grounded_fec_producers

    fec_producer.clear_registry()
    grounded_fec_producers.register_all()

    ctx = {"evidence_bundle": {"support_score": 0.70}}
    fec = fec_producer.resolve_fec("apps_exec", ctx)
    assert fec["c0_status"] == "WEAK_WITH_CAVEATS"


# ----- W2: promoted exec-positioning judge ---------------------------------


def test_exec_positioning_judge_is_no_longer_stub():
    from apps_rg.engines.judges import executive_positioning_judge as mod

    assert mod.IS_STUB is False
    assert mod.GRADER_ID.endswith("::v2")


def test_exec_positioning_judge_abstains_on_empty_output():
    from apps_rg.engines.judges.executive_positioning_judge import grade
    from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
        GRADER_UNKNOWN_SENTINEL,
    )

    score, refs = grade(None, {"output": {"text": ""}})
    assert score is GRADER_UNKNOWN_SENTINEL
    assert refs == []


def test_exec_positioning_judge_scores_high_for_canonical_output():
    from apps_rg.engines.judges.executive_positioning_judge import grade

    text = (
        "The executive strategy delivered a 35% ROI improvement. "
        "We aligned stakeholders around a quarterly roadmap, prioritized "
        "the board initiative, and drove outcome KPI gains of 20%."
    )
    score, refs = grade(None, {"output": {"text": text}})
    assert isinstance(score, float)
    assert score >= 0.6
    assert len(refs) == 4
    assert all("exec_positioning::v2" in r for r in refs)


def test_exec_positioning_judge_scores_low_for_empty_signal_text():
    from apps_rg.engines.judges.executive_positioning_judge import grade

    text = "hello"  # too short + no lexicon hits
    score, refs = grade(None, {"output": {"text": text}})
    assert isinstance(score, float)
    assert score < 0.3


def test_exec_positioning_judge_output_score_bounded():
    from apps_rg.engines.judges.executive_positioning_judge import grade

    text = "strategy roadmap stakeholder quarterly kpi roi executive align prioritize board initiative outcome delivered achieved drove improved increased reduced 10% 20% 30%"
    score, _refs = grade(None, {"output": {"text": text}})
    assert 0.0 <= score <= 1.0


def test_judge_registry_reports_promoted_count_at_least_one():
    # Module-import side effects in tests can affect this. Force re-resolve.
    import importlib
    from apps_shared import judge_registry as mod

    importlib.reload(mod)
    assert mod.promoted_count() >= 1


# ----- W3: synthetic dev fixtures -------------------------------------------


@pytest.mark.parametrize(
    "app_id",
    [
        "apps_qna",
        "apps_research",
        "apps_exec",
        "apps_underwriting_ai",
        "apps_rg",
        "apps_lic",
        "apps_eval",
    ],
)
def test_seed_fixture_exists_for_app(app_id: str):
    fixture = REPO_ROOT / "apps_eval" / "fixtures" / "dev" / f"{app_id}.jsonl"
    assert fixture.is_file(), f"missing seed fixture: {fixture}"
    rows = [json.loads(line) for line in fixture.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows, f"empty fixture: {fixture}"
    assert rows[0]["app_id"] == app_id
    assert "SYNTHETIC" in rows[0].get("tags", [])


# ----- W4: legacy YAML deprecation headers ---------------------------------


LEGACY_FILES = [
    "apps_eval/config/eval_policies.yaml",
    "apps_eval/config/eval_thresholds.yaml",
    "apps_exec/config/exec_policies.yaml",
    "apps_exec/config/exec_thresholds.yaml",
    "apps_lic/config/lic_policies.yaml",
    "apps_lic/config/lic_thresholds.yaml",
    "apps_research/config/research_policies.yaml",
    "apps_research/config/research_thresholds.yaml",
    "apps_rg/config/rg_policies.yaml",
    "apps_rg/config/rg_thresholds.yaml",
    "config/routing_thresholds.yaml",
]


@pytest.mark.parametrize("rel_path", LEGACY_FILES)
def test_legacy_yaml_header_state(rel_path: str):
    """NOTE: final-8f3e21 W4 blanket-added DEPRECATED headers; terminal-3c9f81
    W5 reverted them on all 13 files because every one is actively imported
    by live Python (verified by grep audit). This test now asserts the
    post-revert state: NO DEPRECATED header in first 10 lines. True
    deprecation requires per-file downstream-consumer audit + Author-Gate
    (separate plan)."""
    path = REPO_ROOT / rel_path
    if not path.is_file():
        pytest.skip(f"file not present: {rel_path}")
    text = path.read_text(encoding="utf-8")
    head = "\n".join(text.splitlines()[:10])
    assert "DEPRECATED" not in head, (
        f"DEPRECATED header still present in {rel_path} — terminal-3c9f81 "
        f"W5 should have reverted it (file is actively imported)"
    )
