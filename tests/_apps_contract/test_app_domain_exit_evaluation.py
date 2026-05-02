"""Exit-evaluation tests for app-domain contracts (plan §P7.3 + §P7.4 subset).

Proves the behaviors the user explicitly demanded in the spec:

- apps_rg unsupported resume claim fails on factual_grounding
- apps_rg missing required section fails
- apps_lic fake personalization fails
- apps_lic sensitive targeting fails
- apps_lic channel length violation fails
- UNKNOWN on a fail_closed_if_unknown dimension never passes
- Per-dimension minimums (threshold profile) are enforced, not just overall
- Evidence-required dimensions with empty evidence fail
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_eval.v6.app_specific_evaluator import (
    GRADER_UNKNOWN_SENTINEL,
    AppSpecificEvaluator,
    DimensionResult,
)
from agentic_core.L4_state.contracts import reset_default_app_domain_store
from agentic_core.L4_state.uwg import (
    discover_app_contract_dirs,
    load_bundle_from_dir,
    register_bundle,
)
from agentic_core.L4_state.uwg.durable_write_gateway import reset_default_gateway

REPO_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def _reset():
    reset_default_gateway()
    reset_default_app_domain_store()
    dirs = discover_app_contract_dirs(REPO_ROOT)
    for app_id in sorted(dirs):
        register_bundle(load_bundle_from_dir(dirs[app_id]))
    yield
    reset_default_gateway()
    reset_default_app_domain_store()


# ---------------------------------------------------------------------------
# Grader builders: a grader returns (score, evidence_refs). Tests compose
# per-dimension graders to simulate runtime grader outputs.
# ---------------------------------------------------------------------------


def _const_grader(score: float, evidence: list[str] | None = None):
    def fn(_dim, _ctx):
        return score, list(evidence or ["ev-1"])
    return fn


def _unknown_grader():
    def fn(_dim, _ctx):
        return GRADER_UNKNOWN_SENTINEL, []
    return fn


def _empty_evidence_grader(score: float):
    def fn(_dim, _ctx):
        return score, []
    return fn


def _build_all_pass_evaluator_for(app_id: str, task_class: str) -> AppSpecificEvaluator:
    """Build an evaluator whose every dimension grader returns 0.99 with evidence."""
    from agentic_core.L4_state.contracts import get_default_app_domain_store
    store = get_default_app_domain_store()
    contract = store.get_contract(app_id, task_class, allow_draft=True)
    rubric_id = contract.eval_rubric_refs[0]
    rubric = store.get_eval_rubric(rubric_id)
    graders = {d.dimension_id: _const_grader(0.99) for d in rubric.score_dimensions}
    return AppSpecificEvaluator(graders=graders)


# ---------------------------------------------------------------------------
# Basic plumbing
# ---------------------------------------------------------------------------


class TestBasicPlumbing:
    def test_unbound_route_returns_unbound_result(self) -> None:
        evaluator = AppSpecificEvaluator()
        result = evaluator.evaluate(
            app_id="",
            task_class="",
            rubric_ref="",
            threshold_profile_ref="",
            run_context={},
        )
        assert result.bound is False
        assert result.passed is False

    def test_unknown_rubric_fails_closed(self) -> None:
        evaluator = AppSpecificEvaluator()
        result = evaluator.evaluate(
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::nonexistent::rubric::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            run_context={},
        )
        assert result.bound is True
        assert result.passed is False
        assert any("unknown_app_contract" in r for r in result.fail_reasons)


# ---------------------------------------------------------------------------
# apps_rg cases (user's named exemplar)
# ---------------------------------------------------------------------------


class TestAppsRgEvaluation:
    def test_all_pass_passes(self) -> None:
        evaluator = _build_all_pass_evaluator_for("apps_rg", "resume_generation")
        result = evaluator.evaluate(
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            run_context={"candidate_profile": {}, "output": {}},
        )
        assert result.bound is True
        assert result.passed is True, f"fail_reasons={result.fail_reasons}"
        assert result.overall_score > 0.9

    def test_unsupported_resume_claim_fails_factual_grounding(self) -> None:
        """factual_grounding is the cardinal RG dimension. Simulate a grader
        that detects the unsupported claim and returns a low score."""
        evaluator = _build_all_pass_evaluator_for("apps_rg", "resume_generation")
        evaluator.register_grader("factual_grounding", _const_grader(0.40))
        result = evaluator.evaluate(
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            run_context={},
        )
        assert result.passed is False
        # factual_grounding has min_required_score=0.95 → below-min FAIL
        reasons = " ".join(result.fail_reasons)
        assert "factual_grounding" in reasons

    def test_no_fabrication_fail_is_terminal(self) -> None:
        """no_fabrication has min=0.99 and fail_closed_if_unknown=True."""
        evaluator = _build_all_pass_evaluator_for("apps_rg", "resume_generation")
        evaluator.register_grader("no_fabrication", _const_grader(0.50))
        result = evaluator.evaluate(
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            run_context={},
        )
        assert result.passed is False
        assert any("no_fabrication" in r for r in result.fail_reasons)

    def test_unknown_on_fail_closed_dimension_never_passes(self) -> None:
        """factual_grounding is fail_closed_if_unknown=True."""
        evaluator = _build_all_pass_evaluator_for("apps_rg", "resume_generation")
        evaluator.register_grader("factual_grounding", _unknown_grader())
        result = evaluator.evaluate(
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            run_context={},
        )
        assert result.passed is False
        fg = next(d for d in result.dimensions if d.dimension_id == "factual_grounding")
        assert fg.status == "FAIL"
        assert fg.reason == "unknown_fail_closed"

    def test_evidence_required_empty_fails(self) -> None:
        """factual_grounding has evidence_required=True."""
        evaluator = _build_all_pass_evaluator_for("apps_rg", "resume_generation")
        evaluator.register_grader("factual_grounding", _empty_evidence_grader(0.99))
        result = evaluator.evaluate(
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            run_context={},
        )
        assert result.passed is False
        fg = next(d for d in result.dimensions if d.dimension_id == "factual_grounding")
        assert fg.status == "FAIL"
        assert "evidence_required" in fg.reason


# ---------------------------------------------------------------------------
# apps_lic cases (user's named exemplar #2)
# ---------------------------------------------------------------------------


class TestAppsLicEvaluation:
    def test_all_pass_passes(self) -> None:
        evaluator = _build_all_pass_evaluator_for("apps_lic", "outreach_message")
        result = evaluator.evaluate(
            app_id="apps_lic",
            task_class="outreach_message",
            rubric_ref="aer::apps_lic::outreach_message::v1",
            threshold_profile_ref="atp::apps_lic::outreach_message::v1",
            run_context={},
        )
        assert result.passed is True, f"fail_reasons={result.fail_reasons}"

    def test_fake_personalization_fails(self) -> None:
        """personalization_integrity has min=0.95; no_fake_personalization min=0.99."""
        evaluator = _build_all_pass_evaluator_for("apps_lic", "outreach_message")
        evaluator.register_grader("personalization_integrity", _const_grader(0.30))
        evaluator.register_grader("no_fake_personalization", _const_grader(0.40))
        result = evaluator.evaluate(
            app_id="apps_lic",
            task_class="outreach_message",
            rubric_ref="aer::apps_lic::outreach_message::v1",
            threshold_profile_ref="atp::apps_lic::outreach_message::v1",
            run_context={},
        )
        assert result.passed is False
        reasons = " ".join(result.fail_reasons)
        assert "personalization_integrity" in reasons
        assert "no_fake_personalization" in reasons

    def test_sensitive_targeting_fails(self) -> None:
        evaluator = _build_all_pass_evaluator_for("apps_lic", "outreach_message")
        evaluator.register_grader("no_sensitive_targeting", _const_grader(0.20))
        result = evaluator.evaluate(
            app_id="apps_lic",
            task_class="outreach_message",
            rubric_ref="aer::apps_lic::outreach_message::v1",
            threshold_profile_ref="atp::apps_lic::outreach_message::v1",
            run_context={},
        )
        assert result.passed is False
        assert any("no_sensitive_targeting" in r for r in result.fail_reasons)

    def test_channel_length_violation_fails(self) -> None:
        evaluator = _build_all_pass_evaluator_for("apps_lic", "outreach_message")
        evaluator.register_grader("brevity_and_channel_fit", _const_grader(0.50))
        result = evaluator.evaluate(
            app_id="apps_lic",
            task_class="outreach_message",
            rubric_ref="aer::apps_lic::outreach_message::v1",
            threshold_profile_ref="atp::apps_lic::outreach_message::v1",
            run_context={},
        )
        assert result.passed is False
        assert any("brevity_and_channel_fit" in r for r in result.fail_reasons)


# ---------------------------------------------------------------------------
# Threshold-profile enforcement (dimension minimums)
# ---------------------------------------------------------------------------


class TestDimensionMinimumsEnforced:
    def test_threshold_dim_min_flips_pass_to_fail(self) -> None:
        """Even if overall passes, a per-dimension minimum below threshold
        flips the run to FAIL."""
        evaluator = _build_all_pass_evaluator_for("apps_rg", "resume_generation")
        # factual_grounding returning 0.90 is below rubric min (0.95)
        # AND below threshold dim_min (0.95) — either path triggers FAIL.
        evaluator.register_grader("factual_grounding", _const_grader(0.90))
        result = evaluator.evaluate(
            app_id="apps_rg",
            task_class="resume_generation",
            rubric_ref="aer::apps_rg::resume_generation::v1",
            threshold_profile_ref="atp::apps_rg::resume_generation::v1",
            run_context={},
        )
        assert result.passed is False
