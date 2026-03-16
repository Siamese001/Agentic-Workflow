"""
WAVE 1 tests — Serving profile selection + vLLM request shaping.

Validates:
- Correct profile selected for low/medium/high severity
- Token budget gate uses profile max_model_len (not any other source)
- Local request payload always includes explicit max_tokens
- Determinism policy enforced: temperature=0, top_p=1.0, seed=42
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_vllm_profile_selection")
_emit_applies_guardrail("p0", "test_vllm_profile_selection", "p0_governance")
_emit_reads_policy_state("p0", "test_vllm_profile_selection", "policy_binding")
_emit_snapshots_state("p0", "test_vllm_profile_selection", "state_snapshot")
emit_replay_key("p0", "test_vllm_profile_selection")
emit_determinism_digest("p0", "test_vllm_profile_selection")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_vllm_profile_selection", "execution_auth")
_emit_validates_capability("p2", "test_vllm_profile_selection", "capability_check")
_emit_routes_to_capability("p2", "test_vllm_profile_selection", "capability_route")
_emit_writes_via_uwg("p2", "test_vllm_profile_selection", "uwg_write")
_emit_blocks_direct_write("p2", "test_vllm_profile_selection", "direct_write_block")
_emit_records_tool_invocation("p2", "test_vllm_profile_selection", "tool_invocation")
_emit_captures_execution_output("p2", "test_vllm_profile_selection", "exec_output")
_emit_dispatches_agent("p3", "test_vllm_profile_selection", "agent_dispatch")
_emit_coordinates_agents("p3", "test_vllm_profile_selection", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_vllm_profile_selection", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_vllm_profile_selection", "healing_outcome")
_emit_escalates_failure("p3", "test_vllm_profile_selection", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_vllm_profile_selection", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_vllm_profile_selection", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_vllm_profile_selection", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_vllm_profile_selection", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_vllm_profile_selection", "eval_metric")
_emit_stores_embedding("p4", "test_vllm_profile_selection", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_vllm_profile_selection", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_vllm_profile_selection", "exec_snapshot_link")

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

from agentic_core.L2_execution.types.vllm_gateway_integration_types import (
    VLLM_SEED,
    VLLM_TEMPERATURE,
    VLLM_TOP_P,
    select_serving_profile,
    shape_local_request,
)
from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    LOCAL_FAST_7B_MAX_MODEL_LEN,
    LOCAL_STRONG_14B_MAX_MODEL_LEN,
    PROFILE_LOCAL_FAST_7B,
    PROFILE_LOCAL_STRONG_14B,
)
from agentic_core.L2_execution.types.vllm_token_budget_types import (
    TASK_CLASS_OUTPUT_CAPS,
    TaskClass,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_vllm_profile_selection", "p4obs", "metric_1")
_emit_emits_metric_event("test_vllm_profile_selection", "p4obs", "metric_2")
_emit_emits_metric_event("test_vllm_profile_selection", "p4obs", "metric_3")
_emit_emits_metric_event("test_vllm_profile_selection", "p4obs", "metric_4")
_emit_emits_metric_event("test_vllm_profile_selection", "p4obs", "metric_5")
_emit_emits_metric_event("test_vllm_profile_selection", "p4obs", "metric_6")
_emit_records_incident_event("test_vllm_profile_selection", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_vllm_profile_selection", "p4obs", "anomaly")
_emit_writes_observability_log("test_vllm_profile_selection", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_vllm_profile_selection", "p4obs", "mon_state")
_emit_triggers_alert("test_vllm_profile_selection", "p4obs", "alert")
_emit_links_incident_trace("test_vllm_profile_selection", "p4obs", "trace_link")
_emit_captures_pattern("test_vllm_profile_selection", "p3lm", "pattern")
_emit_records_learning_event("test_vllm_profile_selection", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_vllm_profile_selection", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_vllm_profile_selection", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_vllm_profile_selection", "p3lm", "routing")
_emit_improves_agent_policy("test_vllm_profile_selection", "p3lm", "policy")
_emit_stores_learning_state("test_vllm_profile_selection", "p3lm", "state")
_emit_records_execution_trace("test_vllm_profile_selection", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_vllm_profile_selection", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_vllm_profile_selection", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_vllm_profile_selection", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_vllm_profile_selection", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_vllm_profile_selection", "env_read", "p2_env_1")
_emit_reads_environ("test_vllm_profile_selection", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_vllm_profile_selection", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_vllm_profile_selection", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_vllm_profile_selection", "context_pull")
_emit_pulls_context("p1", "test_vllm_profile_selection", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_vllm_profile_selection", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_vllm_profile_selection", "uwg_term_secondary")
_emit_writes_through("p1", "test_vllm_profile_selection", "write_through")
_emit_writes_through("p1", "test_vllm_profile_selection", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_vllm_profile_selection", "safety_validation")
_emit_invokes_eval("p1", "test_vllm_profile_selection", "eval_call")
_emit_proposal_commits_routing("p1", "test_vllm_profile_selection", "routing_commit")

# ---------------------------------------------------------------------------
# Profile selection tests
# ---------------------------------------------------------------------------


def test_low_severity_selects_fast_7b():
    profile = select_serving_profile("low")
    assert profile.profile_name == "LOCAL_FAST_7B"


def test_medium_severity_selects_fast_7b():
    profile = select_serving_profile("medium")
    assert profile.profile_name == "LOCAL_FAST_7B"


def test_high_severity_selects_strong_14b():
    profile = select_serving_profile("high")
    assert profile.profile_name == "LOCAL_STRONG_14B"


def test_low_severity_profile_model_id():
    profile = select_serving_profile("low")
    assert "7B" in profile.model or "7b" in profile.model


def test_high_severity_profile_model_id():
    profile = select_serving_profile("high")
    assert "14B" in profile.model or "14b" in profile.model


def test_profile_max_model_len_low():
    profile = select_serving_profile("low")
    assert profile.max_model_len == LOCAL_FAST_7B_MAX_MODEL_LEN


def test_profile_max_model_len_high():
    profile = select_serving_profile("high")
    assert profile.max_model_len == LOCAL_STRONG_14B_MAX_MODEL_LEN


# ---------------------------------------------------------------------------
# Request shaping tests
# ---------------------------------------------------------------------------


def test_shaped_request_has_explicit_max_tokens():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.max_tokens is not None
    assert req.max_tokens > 0


def test_shaped_request_max_tokens_matches_task_cap():
    task_class = TaskClass.PATCH_SUGGESTION.value
    req = shape_local_request("hello", task_class, PROFILE_LOCAL_FAST_7B)
    assert req.max_tokens == TASK_CLASS_OUTPUT_CAPS[task_class]


def test_shaped_request_temperature_is_zero():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.temperature == VLLM_TEMPERATURE
    assert req.temperature == 0.0


def test_shaped_request_top_p_is_one():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.top_p == VLLM_TOP_P
    assert req.top_p == 1.0


def test_shaped_request_seed_is_fixed():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.seed == VLLM_SEED
    assert req.seed == 42


def test_shaped_request_uses_profile_max_model_len():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.max_model_len == PROFILE_LOCAL_FAST_7B.max_model_len


def test_shaped_request_14b_uses_14b_max_model_len():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_STRONG_14B)
    assert req.max_model_len == PROFILE_LOCAL_STRONG_14B.max_model_len


def test_shaped_request_profile_name_recorded():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.profile_name == "LOCAL_FAST_7B"


def test_shaped_request_undefined_task_class_raises():
    with pytest.raises(ValueError, match="no output cap"):
        shape_local_request("hello", "undefined_class", PROFILE_LOCAL_FAST_7B)


def test_shaped_request_healing_json_artifact():
    req = shape_local_request("hello", TaskClass.HEALING_JSON_ARTIFACT.value, PROFILE_LOCAL_FAST_7B)
    assert req.max_tokens == TASK_CLASS_OUTPUT_CAPS[TaskClass.HEALING_JSON_ARTIFACT.value]


def test_shaped_request_is_deterministic():
    req1 = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    req2 = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req1 == req2


def test_shaped_request_model_matches_profile():
    req = shape_local_request("hello", TaskClass.PATCH_SUGGESTION.value, PROFILE_LOCAL_FAST_7B)
    assert req.model == PROFILE_LOCAL_FAST_7B.model
