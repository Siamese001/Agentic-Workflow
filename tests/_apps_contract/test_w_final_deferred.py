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


def test_exec_positioning_judge_exports_core_contract():
    from agentic_core.runtime.judges.resume_judges.executive_positioning import (
        ExecutivePositioningJudge,
    )

    assert ExecutivePositioningJudge.IS_STUB is False
    assert ExecutivePositioningJudge.GRADER_REF == "rg::executive_positioning_judge::v1"


def test_exec_positioning_judge_builds_prompt_from_context():
    from agentic_core.runtime.judges.resume_judges.executive_positioning import (
        ExecutivePositioningJudge,
    )

    judge = ExecutivePositioningJudge()
    prompt = judge.build_prompt(
        candidate_text="Led a 300-person org and delivered 15% revenue growth.",
        context_metadata={
            "target_role": "VP Engineering",
            "target_level": "executive",
            "target_company": "Acme",
        },
    )
    assert "VP Engineering" in prompt.user_prompt
    assert "Acme" in prompt.user_prompt
    assert "Led a 300-person org" in prompt.user_prompt
    assert prompt.system_prompt.strip()


def test_exec_positioning_judge_parse_response_handles_empty_output():
    from agentic_core.runtime.judges.resume_judges.executive_positioning import (
        ExecutivePositioningJudge,
    )

    judge = ExecutivePositioningJudge()
    result = judge.parse_response("")
    assert result.score == 0.0
    assert result.confidence == 0.0
    assert result.parse_error is not None


def test_exec_positioning_judge_parse_response_bounds_scores():
    from agentic_core.runtime.judges.resume_judges.executive_positioning import (
        ExecutivePositioningJudge,
    )

    judge = ExecutivePositioningJudge()
    result = judge.parse_response(
        json.dumps(
            {
                "score": 1.4,
                "confidence": -0.3,
                "reasoning": "Signals are strong.",
                "signal_breakdown": {
                    "scope_signals_count": 2,
                    "ownership_language_count": 3,
                    "quantified_outcomes_count": 1,
                    "executive_summary_quality": "strong",
                },
            }
        )
    )
    assert 0.0 <= result.score <= 1.0
    assert 0.0 <= result.confidence <= 1.0
    assert result.reasoning == "Signals are strong."
    assert result.signal_breakdown["executive_summary_quality"] == "strong"


def test_exec_positioning_judge_parse_response_extracts_valid_payload():
    from agentic_core.runtime.judges.resume_judges.executive_positioning import (
        ExecutivePositioningJudge,
    )

    judge = ExecutivePositioningJudge()
    result = judge.parse_response(
        json.dumps(
            {
                "score": 0.87,
                "confidence": 0.91,
                "reasoning": "Executive positioning is strong.",
                "signal_breakdown": {
                    "scope_signals_count": 3,
                    "ownership_language_count": 2,
                    "quantified_outcomes_count": 4,
                    "executive_summary_quality": "strong",
                },
            }
        )
    )
    assert result.score == 0.87
    assert result.confidence == 0.91
    assert result.signal_breakdown["scope_signals_count"] == 3


def test_judge_registry_reports_promoted_count_at_least_one():
    # Module-import side effects in tests can affect this. Force re-resolve.
    import importlib
    from apps_shared import judge_registry as mod

    importlib.reload(mod)
    assert mod.promoted_count() >= 1


# ----- W3: synthetic dev fixtures -------------------------------------------


DEV_FIXTURE_ROOT = REPO_ROOT / "apps_eval" / "fixtures" / "dev"
DEV_FIXTURE_APPS = tuple(
    sorted(p.name for p in DEV_FIXTURE_ROOT.iterdir() if p.is_dir())
) if DEV_FIXTURE_ROOT.is_dir() else ()


@pytest.mark.parametrize("app_id", DEV_FIXTURE_APPS)
def test_seed_fixture_bundle_exists_for_app(app_id: str):
    app_root = DEV_FIXTURE_ROOT / app_id
    assert app_root.is_dir(), f"missing dev fixture root: {app_root}"

    scenario_dirs = sorted(p for p in app_root.iterdir() if p.is_dir())
    assert scenario_dirs, f"no dev fixture scenarios found for {app_id}"

    for scenario_dir in scenario_dirs:
        for rel_path in (
            "scenario.yaml",
            "input/request.json",
            "expected/expectations.json",
            "snapshots/app_output_snapshot.json",
        ):
            assert (scenario_dir / rel_path).is_file(), f"missing {rel_path} in {scenario_dir}"


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
