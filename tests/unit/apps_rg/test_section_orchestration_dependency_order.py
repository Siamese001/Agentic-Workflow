"""Section orchestration redesign — dependency-ordered execution, composite-judge defaults,
non-retryable upstream-block early-exit, and attempts clamp.

Covers the 2026-06-06 redesign:
  * GENERATED_LANES serial order = dependency order
    (competencies -> unify_bullets -> ibm_bullets -> unify_narrative -> ibm_narrative
     -> executive_summary -> headline)
  * Phase-1 wave DAG mirrors the dependency order (bullets before narratives before
    exec_summary before headline) and passes the wave-order validator.
  * ibm_bullets default X1D = ONE composite judge (anthropic_claude); unify already uses one.
  * Upstream-block runtime statuses are non-retryable (early-exit failure-class set).
  * Per-lane judge resolution callable threads through LaneExecutionContext.
"""
from __future__ import annotations

import apps_rg.runtime.internal.generated_lane_rollup as glr
from apps_rg.runtime.orchestration.section_lane_concurrency import (
    assert_section_dag_wave_order,
    build_phase1_waves,
    load_section_dag_manifest,
)
from apps_rg.runtime.orchestration.section_lane_executor import LaneExecutionContext
from apps_rg.runtime.section_cli_defaults import (
    resolve_cli_x1d_judges,
    summarize_section_x1d_minimization_policy,
)
from apps_rg.runtime.validators.companion_bullet_finalization import (
    UPSTREAM_BLOCKED_RUNTIME_STATUSES,
    is_upstream_blocked_runtime_status,
)

_EXPECTED_ORDER = (
    "competencies",
    "unify_bullets",
    "ibm_bullets",
    "unify_narrative",
    "ibm_narrative",
    "executive_summary",
    "headline",
)


# ----------------------------------------------------------------------------- execution order
def test_generated_lanes_is_dependency_order() -> None:
    assert glr.GENERATED_LANES == _EXPECTED_ORDER


def test_generated_lanes_has_exactly_seven_content_sections() -> None:
    assert len(glr.GENERATED_LANES) == 7
    assert set(glr.GENERATED_LANES) == set(_EXPECTED_ORDER)


def test_bullets_precede_their_narratives_in_serial_order() -> None:
    order = list(glr.GENERATED_LANES)
    assert order.index("unify_bullets") < order.index("unify_narrative")
    assert order.index("ibm_bullets") < order.index("ibm_narrative")


def test_executive_summary_after_all_bullets_and_narratives() -> None:
    order = list(glr.GENERATED_LANES)
    es = order.index("executive_summary")
    for upstream in ("competencies", "unify_bullets", "ibm_bullets", "unify_narrative", "ibm_narrative"):
        assert order.index(upstream) < es, f"{upstream} must precede executive_summary"


def test_headline_runs_last() -> None:
    assert glr.GENERATED_LANES[-1] == "headline"
    order = list(glr.GENERATED_LANES)
    assert order.index("executive_summary") < order.index("headline")


# ----------------------------------------------------------------------------- wave DAG order
def test_wave_dag_passes_order_validator() -> None:
    manifest = load_section_dag_manifest()
    # Raises if any depends_on edge points to a same/later wave.
    assert_section_dag_wave_order(manifest)


def test_wave_dag_bullets_before_narratives_before_exec_before_headline() -> None:
    waves = build_phase1_waves()
    lane_wave = {lane: w.wave_id for w in waves for lane in w.lanes}
    assert lane_wave["competencies"] < lane_wave["unify_narrative"]
    assert lane_wave["unify_bullets"] < lane_wave["unify_narrative"]
    assert lane_wave["ibm_bullets"] < lane_wave["ibm_narrative"]
    assert lane_wave["unify_narrative"] < lane_wave["executive_summary"]
    assert lane_wave["ibm_narrative"] < lane_wave["executive_summary"]
    assert lane_wave["executive_summary"] < lane_wave["headline"]


def test_wave_dag_covers_all_seven_lanes() -> None:
    waves = build_phase1_waves()
    covered = {lane for w in waves for lane in w.lanes}
    assert covered == set(_EXPECTED_ORDER)


# ----------------------------------------------------------------- composite-judge defaults
def test_ibm_bullets_defaults_to_single_composite_judge(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)
    assert resolve_cli_x1d_judges(None, section_id="ibm_bullets") == "anthropic_claude"


def test_competencies_defaults_to_single_advisory_judge(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)
    assert resolve_cli_x1d_judges(None, section_id="competencies") == "gemini_pro"


def test_unify_bullets_defaults_to_single_composite_judge(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)
    assert resolve_cli_x1d_judges(None, section_id="unify_bullets") == "anthropic_claude"


def test_explicit_x1d_judges_override_wins_for_ibm_adjudicator() -> None:
    # The 3-provider panel is reachable as the optional adjudicator via explicit override.
    panel = "gemini_pro,openai_chatgpt,anthropic_claude"
    assert resolve_cli_x1d_judges(panel, section_id="ibm_bullets") == panel


def test_env_x1d_judges_override_wins_for_ibm(monkeypatch) -> None:
    monkeypatch.setenv("APPS_RG_E2E_X1D_JUDGES", "gemini_pro,anthropic_claude")
    assert resolve_cli_x1d_judges(None, section_id="ibm_bullets") == "gemini_pro,anthropic_claude"


def test_non_bullet_sections_keep_standard_panel_default(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)
    panel = "gemini_pro,openai_chatgpt,anthropic_claude"
    assert resolve_cli_x1d_judges(None, section_id="headline") == panel
    assert resolve_cli_x1d_judges(None, section_id="executive_summary") == panel


def test_wave9_policy_summary_marks_compact_non_repairing_defaults(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)
    policy = summarize_section_x1d_minimization_policy()
    assert set(policy) == {
        "competencies",
        "executive_summary",
        "headline",
        "ibm_bullets",
        "ibm_narrative",
        "unify_bullets",
        "unify_narrative",
        "final_aggregate_resume",
    }
    assert policy["unify_bullets"]["default_judge_count"] == 1
    assert policy["ibm_bullets"]["default_judge_count"] == 1
    assert policy["competencies"]["default_judge_count"] == 1
    assert policy["headline"]["default_judge_count"] == 3
    assert policy["executive_summary"]["default_judge_count"] == 3
    assert all(v["repair_allowed"] is False for v in policy.values())
    assert all(v["packet_scope"] == "compact_grade_only" for v in policy.values())


# ------------------------------------------------------------ per-lane judge callable threading
def test_lane_execution_context_resolves_per_lane_callable(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_E2E_X1D_JUDGES", raising=False)
    ctx = LaneExecutionContext(
        sections_root="x",
        target_company="",
        target_role="",
        job_description_ref="",
        job_description_text="",
        manual_brief="",
        lane_provider="qwen_vllm",
        lane_x1d_judges=lambda lane: resolve_cli_x1d_judges(None, section_id=lane),
        lane_mock_judges=False,
    )
    assert ctx.x1d_judges_for_lane("ibm_bullets") == "anthropic_claude"
    assert ctx.x1d_judges_for_lane("competencies") == "gemini_pro"
    assert ctx.x1d_judges_for_lane("unify_bullets") == "anthropic_claude"
    assert ctx.x1d_judges_for_lane("headline") == "gemini_pro,openai_chatgpt,anthropic_claude"


def test_lane_execution_context_passthrough_string() -> None:
    ctx = LaneExecutionContext(
        sections_root="x",
        target_company="",
        target_role="",
        job_description_ref="",
        job_description_text="",
        manual_brief="",
        lane_provider="qwen_vllm",
        lane_x1d_judges="anthropic_claude",
        lane_mock_judges=False,
    )
    # Non-callable string is returned verbatim for every lane.
    assert ctx.x1d_judges_for_lane("ibm_bullets") == "anthropic_claude"
    assert ctx.x1d_judges_for_lane("headline") == "anthropic_claude"


# ----------------------------------------------------------- non-retryable upstream-block classes
def test_upstream_blocked_status_set_includes_all_failure_classes() -> None:
    for cls in (
        "BLOCKED_UPSTREAM_NOT_FINALIZED",
        "UPSTREAM_EVIDENCE_MISSING",
        "FEC_NOT_FINALIZED",
        "REQUIRED_PROOF_ABSENT",
        "REQUIRED_DEPENDENCY_EMPTY",
    ):
        assert cls in UPSTREAM_BLOCKED_RUNTIME_STATUSES
        assert is_upstream_blocked_runtime_status(cls) is True


def test_real_llm_is_not_upstream_blocked() -> None:
    assert is_upstream_blocked_runtime_status("REAL_LLM") is False
    assert is_upstream_blocked_runtime_status("MOCKED") is False
    assert is_upstream_blocked_runtime_status("") is False
    assert is_upstream_blocked_runtime_status(None) is False


def test_upstream_blocked_predicate_is_case_insensitive() -> None:
    assert is_upstream_blocked_runtime_status("blocked_upstream_not_finalized") is True
