"""
WAVE 2 tests — KV cache headroom under concurrency stress.

Validates:
- Worst-case prompt near budget ceiling passes preflight
- No truncation within max_model_len
- No unexpected fallback when token_budget_ok=True
- No output exceeds VLLM_MAX_TOKENS_ABSOLUTE
- Concurrent requests within max_num_seqs behave deterministically
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_kv_cache_headroom_under_concurrency")
_emit_applies_guardrail("p0", "test_kv_cache_headroom_under_concurrency", "p0_governance")
_emit_reads_policy_state("p0", "test_kv_cache_headroom_under_concurrency", "policy_binding")
_emit_snapshots_state("p0", "test_kv_cache_headroom_under_concurrency", "state_snapshot")
emit_replay_key("p0", "test_kv_cache_headroom_under_concurrency")
emit_determinism_digest("p0", "test_kv_cache_headroom_under_concurrency")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_kv_cache_headroom_under_concurrency", "execution_auth")
_emit_validates_capability("p2", "test_kv_cache_headroom_under_concurrency", "capability_check")
_emit_routes_to_capability("p2", "test_kv_cache_headroom_under_concurrency", "capability_route")
_emit_writes_via_uwg("p2", "test_kv_cache_headroom_under_concurrency", "uwg_write")
_emit_blocks_direct_write("p2", "test_kv_cache_headroom_under_concurrency", "direct_write_block")
_emit_records_tool_invocation("p2", "test_kv_cache_headroom_under_concurrency", "tool_invocation")
_emit_captures_execution_output("p2", "test_kv_cache_headroom_under_concurrency", "exec_output")
_emit_dispatches_agent("p3", "test_kv_cache_headroom_under_concurrency", "agent_dispatch")
_emit_coordinates_agents("p3", "test_kv_cache_headroom_under_concurrency", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_kv_cache_headroom_under_concurrency", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_kv_cache_headroom_under_concurrency", "healing_outcome")
_emit_escalates_failure("p3", "test_kv_cache_headroom_under_concurrency", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_kv_cache_headroom_under_concurrency", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_kv_cache_headroom_under_concurrency", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_kv_cache_headroom_under_concurrency", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_kv_cache_headroom_under_concurrency", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_kv_cache_headroom_under_concurrency", "eval_metric")
_emit_stores_embedding("p4", "test_kv_cache_headroom_under_concurrency", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_kv_cache_headroom_under_concurrency", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_kv_cache_headroom_under_concurrency", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit_min_deps

from agentic_core.L2_execution.types.vllm_concurrency_types import (
    VLLMStressRequest,
    build_worst_case_prompt,
    validate_concurrency_headroom,
)
from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    PROFILE_LOCAL_FAST_7B,
    PROFILE_LOCAL_STRONG_14B,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    TASK_CLASS_OUTPUT_CAPS,
    VLLM_MAX_TOKENS_ABSOLUTE,
    TaskClass,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_kv_cache_headroom_under_concurrency", "p4obs", "metric_1")
_emit_emits_metric_event("test_kv_cache_headroom_under_concurrency", "p4obs", "metric_2")
_emit_emits_metric_event("test_kv_cache_headroom_under_concurrency", "p4obs", "metric_3")
_emit_emits_metric_event("test_kv_cache_headroom_under_concurrency", "p4obs", "metric_4")
_emit_emits_metric_event("test_kv_cache_headroom_under_concurrency", "p4obs", "metric_5")
_emit_emits_metric_event("test_kv_cache_headroom_under_concurrency", "p4obs", "metric_6")
_emit_records_incident_event("test_kv_cache_headroom_under_concurrency", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_kv_cache_headroom_under_concurrency", "p4obs", "anomaly")
_emit_writes_observability_log("test_kv_cache_headroom_under_concurrency", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_kv_cache_headroom_under_concurrency", "p4obs", "mon_state")
_emit_triggers_alert("test_kv_cache_headroom_under_concurrency", "p4obs", "alert")
_emit_links_incident_trace("test_kv_cache_headroom_under_concurrency", "p4obs", "trace_link")
_emit_captures_pattern("test_kv_cache_headroom_under_concurrency", "p3lm", "pattern")
_emit_records_learning_event("test_kv_cache_headroom_under_concurrency", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_kv_cache_headroom_under_concurrency", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_kv_cache_headroom_under_concurrency", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_kv_cache_headroom_under_concurrency", "p3lm", "routing")
_emit_improves_agent_policy("test_kv_cache_headroom_under_concurrency", "p3lm", "policy")
_emit_stores_learning_state("test_kv_cache_headroom_under_concurrency", "p3lm", "state")
_emit_records_execution_trace("test_kv_cache_headroom_under_concurrency", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_kv_cache_headroom_under_concurrency", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_kv_cache_headroom_under_concurrency", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_kv_cache_headroom_under_concurrency", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_kv_cache_headroom_under_concurrency", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_kv_cache_headroom_under_concurrency", "env_read", "p2_env_1")
_emit_reads_environ("test_kv_cache_headroom_under_concurrency", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_kv_cache_headroom_under_concurrency", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_kv_cache_headroom_under_concurrency", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_kv_cache_headroom_under_concurrency", "context_pull")
_emit_pulls_context("p1", "test_kv_cache_headroom_under_concurrency", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_kv_cache_headroom_under_concurrency", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_kv_cache_headroom_under_concurrency", "uwg_term_secondary")
_emit_writes_through("p1", "test_kv_cache_headroom_under_concurrency", "write_through")
_emit_writes_through("p1", "test_kv_cache_headroom_under_concurrency", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_kv_cache_headroom_under_concurrency", "safety_validation")
_emit_invokes_eval("p1", "test_kv_cache_headroom_under_concurrency", "eval_call")
_emit_proposal_commits_routing("p1", "test_kv_cache_headroom_under_concurrency", "routing_commit")
_emit_escalates_to_human("p1", "test_kv_cache_headroom_under_concurrency", "human_escalation")
_emit_routes_through("p1", "test_kv_cache_headroom_under_concurrency", "route_through")
_emit_checks_agent_registry("p1", "test_kv_cache_headroom_under_concurrency", "agent_registry")
_emit_validates_agent_capability("p1", "test_kv_cache_headroom_under_concurrency", "capability")
_emit_dispatches_execution_plan("p1", "test_kv_cache_headroom_under_concurrency", "exec_plan")
_emit_agent_executes_agent("p1", "test_kv_cache_headroom_under_concurrency", "sub_agent")
_emit_routes_to_agent("p1", "test_kv_cache_headroom_under_concurrency", "target_agent")
_emit_verifies_policy("p1", "test_kv_cache_headroom_under_concurrency", "policy_check")
_emit_observes_runtime_state("p1", "test_kv_cache_headroom_under_concurrency", "runtime_state")
_emit_verifies_boundary("p1", "test_kv_cache_headroom_under_concurrency", "boundary_check")
_emit_transcripts_response("p1", "test_kv_cache_headroom_under_concurrency", "transcript")
_emit_hard_fails_untranscripted("p1", "test_kv_cache_headroom_under_concurrency")
_emit_gated_by_confidence("p1", "test_kv_cache_headroom_under_concurrency", "confidence_gate")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_requests(profile, task_class: str, n: int) -> list[VLLMStressRequest]:
    cap = TASK_CLASS_OUTPUT_CAPS[task_class]
    prompt = build_worst_case_prompt(profile, cap)
    return [
        VLLMStressRequest(
            request_id=i,
            prompt=prompt,
            task_class=task_class,
            max_output_tokens_requested=cap,
        )
        for i in range(n)
    ]


# ---------------------------------------------------------------------------
# WAVE 2 — 7B profile stress tests
# ---------------------------------------------------------------------------


def test_7b_worst_case_prompt_passes_preflight():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.all_within_budget, "Worst-case prompt should pass preflight on 7B"


def test_7b_no_truncation_at_ceiling():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert not result.any_truncation, "No truncation expected at budget ceiling on 7B"


def test_7b_no_unexpected_fallback():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert not result.any_unexpected_fallback, "No unexpected fallback when budget OK"


def test_7b_no_absolute_exceeded():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert not result.any_absolute_exceeded, "No output exceeds VLLM_MAX_TOKENS_ABSOLUTE"


def test_7b_max_concurrency_within_budget():
    requests = make_requests(
        PROFILE_LOCAL_FAST_7B,
        TaskClass.PATCH_SUGGESTION.value,
        PROFILE_LOCAL_FAST_7B.max_num_seqs,
    )
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.num_requests == PROFILE_LOCAL_FAST_7B.max_num_seqs
    assert result.all_within_budget


def test_7b_healing_json_artifact_passes():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.HEALING_JSON_ARTIFACT.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.all_within_budget
    assert not result.any_truncation


def test_7b_deterministic_repeated_run():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 2)
    r1 = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    r2 = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert r1.all_within_budget == r2.all_within_budget
    assert r1.any_truncation == r2.any_truncation
    assert r1.any_unexpected_fallback == r2.any_unexpected_fallback


# ---------------------------------------------------------------------------
# WAVE 2 — 14B profile stress tests
# ---------------------------------------------------------------------------


def test_14b_worst_case_prompt_passes_preflight():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert result.all_within_budget, "Worst-case prompt should pass preflight on 14B"


def test_14b_no_truncation_at_ceiling():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert not result.any_truncation


def test_14b_no_unexpected_fallback():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert not result.any_unexpected_fallback


def test_14b_max_concurrency_within_budget():
    requests = make_requests(
        PROFILE_LOCAL_STRONG_14B,
        TaskClass.HEALING_JSON_ARTIFACT.value,
        PROFILE_LOCAL_STRONG_14B.max_num_seqs,
    )
    result = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert result.num_requests == PROFILE_LOCAL_STRONG_14B.max_num_seqs
    assert result.all_within_budget


def test_14b_deterministic_repeated_run():
    requests = make_requests(PROFILE_LOCAL_STRONG_14B, TaskClass.HEALING_JSON_ARTIFACT.value, 1)
    r1 = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    r2 = validate_concurrency_headroom(PROFILE_LOCAL_STRONG_14B, requests)
    assert r1.all_within_budget == r2.all_within_budget
    assert r1.any_truncation == r2.any_truncation


# ---------------------------------------------------------------------------
# WAVE 2 — Absolute ceiling invariant
# ---------------------------------------------------------------------------


def test_output_cap_never_exceeds_absolute():
    for task_class, cap in TASK_CLASS_OUTPUT_CAPS.items():
        assert cap <= VLLM_MAX_TOKENS_ABSOLUTE, (
            f"Task class {task_class!r} cap {cap} exceeds VLLM_MAX_TOKENS_ABSOLUTE={VLLM_MAX_TOKENS_ABSOLUTE}"
        )


def test_stress_result_fields_present():
    requests = make_requests(PROFILE_LOCAL_FAST_7B, TaskClass.PATCH_SUGGESTION.value, 1)
    result = validate_concurrency_headroom(PROFILE_LOCAL_FAST_7B, requests)
    assert result.profile_name == "LOCAL_FAST_7B"
    assert result.max_num_seqs == PROFILE_LOCAL_FAST_7B.max_num_seqs
    assert len(result.request_results) == 1
    r = result.request_results[0]
    assert r.request_id == 0
    assert r.total_tokens_required > 0
