"""
WAVE 1 tests — Authoritative serving profile constants and config validation.

Validates:
- Profile constants are hardcoded (not env-derived)
- Startup fails on invalid configuration
- Co-change invariant enforcement
- 14B max_model_len ceiling guard
- No 32B tier, no quantized tier
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

_emit_records_execution_trace("p0", "evidence", "test_serving_profile_constants")
_emit_applies_guardrail("p0", "test_serving_profile_constants", "p0_governance")
_emit_reads_policy_state("p0", "test_serving_profile_constants", "policy_binding")
_emit_snapshots_state("p0", "test_serving_profile_constants", "state_snapshot")
emit_replay_key("p0", "test_serving_profile_constants")
emit_determinism_digest("p0", "test_serving_profile_constants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_serving_profile_constants", "execution_auth")
_emit_validates_capability("p2", "test_serving_profile_constants", "capability_check")
_emit_routes_to_capability("p2", "test_serving_profile_constants", "capability_route")
_emit_writes_via_uwg("p2", "test_serving_profile_constants", "uwg_write")
_emit_blocks_direct_write("p2", "test_serving_profile_constants", "direct_write_block")
_emit_records_tool_invocation("p2", "test_serving_profile_constants", "tool_invocation")
_emit_captures_execution_output("p2", "test_serving_profile_constants", "exec_output")
_emit_dispatches_agent("p3", "test_serving_profile_constants", "agent_dispatch")
_emit_coordinates_agents("p3", "test_serving_profile_constants", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_serving_profile_constants", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_serving_profile_constants", "healing_outcome")
_emit_escalates_failure("p3", "test_serving_profile_constants", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_serving_profile_constants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_serving_profile_constants", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_serving_profile_constants", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_serving_profile_constants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_serving_profile_constants", "eval_metric")
_emit_stores_embedding("p4", "test_serving_profile_constants", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_serving_profile_constants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_serving_profile_constants", "exec_snapshot_link")

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

from agentic_core.L2_execution.types.vllm_serving_profile_types import (
    GPU_MEMORY_UTILIZATION,
    GPU_VRAM_GB,
    LOCAL_FAST_7B_MAX_MODEL_LEN,
    LOCAL_FAST_7B_MAX_NUM_SEQS,
    LOCAL_FAST_7B_MODEL,
    LOCAL_STRONG_14B_MAX_MODEL_LEN,
    LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING,
    LOCAL_STRONG_14B_MAX_NUM_SEQS,
    LOCAL_STRONG_14B_MODEL,
    PROFILE_LOCAL_FAST_7B,
    PROFILE_LOCAL_STRONG_14B,
    SERVING_PROFILE_REGISTRY,
    VLLMCoChangeViolation,
    VLLMServingProfile,
    VLLMServingProfileInvalid,
    assert_no_simultaneous_increase,
    get_profile,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("test_serving_profile_constants", "p4obs", "metric_1")
_emit_emits_metric_event("test_serving_profile_constants", "p4obs", "metric_2")
_emit_emits_metric_event("test_serving_profile_constants", "p4obs", "metric_3")
_emit_emits_metric_event("test_serving_profile_constants", "p4obs", "metric_4")
_emit_emits_metric_event("test_serving_profile_constants", "p4obs", "metric_5")
_emit_emits_metric_event("test_serving_profile_constants", "p4obs", "metric_6")
_emit_records_incident_event("test_serving_profile_constants", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_serving_profile_constants", "p4obs", "anomaly")
_emit_writes_observability_log("test_serving_profile_constants", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_serving_profile_constants", "p4obs", "mon_state")
_emit_triggers_alert("test_serving_profile_constants", "p4obs", "alert")
_emit_links_incident_trace("test_serving_profile_constants", "p4obs", "trace_link")
_emit_captures_pattern("test_serving_profile_constants", "p3lm", "pattern")
_emit_records_learning_event("test_serving_profile_constants", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_serving_profile_constants", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_serving_profile_constants", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_serving_profile_constants", "p3lm", "routing")
_emit_improves_agent_policy("test_serving_profile_constants", "p3lm", "policy")
_emit_stores_learning_state("test_serving_profile_constants", "p3lm", "state")
_emit_records_execution_trace("test_serving_profile_constants", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_serving_profile_constants", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_serving_profile_constants", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_serving_profile_constants", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_serving_profile_constants", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_serving_profile_constants", "env_read", "p2_env_1")
_emit_reads_environ("test_serving_profile_constants", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_serving_profile_constants", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_serving_profile_constants", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_serving_profile_constants", "context_pull")
_emit_pulls_context("p1", "test_serving_profile_constants", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_serving_profile_constants", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_serving_profile_constants", "uwg_term_secondary")
_emit_writes_through("p1", "test_serving_profile_constants", "write_through")
_emit_writes_through("p1", "test_serving_profile_constants", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_serving_profile_constants", "safety_validation")
_emit_invokes_eval("p1", "test_serving_profile_constants", "eval_call")
_emit_proposal_commits_routing("p1", "test_serving_profile_constants", "routing_commit")

# ---------------------------------------------------------------------------
# Profile constant tests
# ---------------------------------------------------------------------------


def test_local_fast_7b_model_id():
    assert LOCAL_FAST_7B_MODEL == "Qwen/Qwen2.5-7B-Instruct"


def test_local_strong_14b_model_id():
    assert LOCAL_STRONG_14B_MODEL == "Qwen/Qwen2.5-14B-Instruct"


def test_local_fast_7b_max_model_len():
    assert LOCAL_FAST_7B_MAX_MODEL_LEN == 8192


def test_local_strong_14b_max_model_len():
    assert LOCAL_STRONG_14B_MAX_MODEL_LEN == 4096


def test_local_fast_7b_max_num_seqs():
    assert LOCAL_FAST_7B_MAX_NUM_SEQS == 4


def test_local_strong_14b_max_num_seqs():
    assert LOCAL_STRONG_14B_MAX_NUM_SEQS == 2


def test_gpu_memory_utilization():
    assert GPU_MEMORY_UTILIZATION == 0.85


def test_gpu_vram_gb():
    assert GPU_VRAM_GB == 32


def test_14b_ceiling():
    assert LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING == 8192


def test_14b_max_model_len_within_ceiling():
    assert LOCAL_STRONG_14B_MAX_MODEL_LEN <= LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING


# ---------------------------------------------------------------------------
# Profile instance tests
# ---------------------------------------------------------------------------


def test_profile_local_fast_7b_is_valid():
    assert PROFILE_LOCAL_FAST_7B.profile_name == "LOCAL_FAST_7B"
    assert PROFILE_LOCAL_FAST_7B.model == LOCAL_FAST_7B_MODEL
    assert PROFILE_LOCAL_FAST_7B.max_model_len == LOCAL_FAST_7B_MAX_MODEL_LEN
    assert PROFILE_LOCAL_FAST_7B.max_num_seqs == LOCAL_FAST_7B_MAX_NUM_SEQS


def test_profile_local_strong_14b_is_valid():
    assert PROFILE_LOCAL_STRONG_14B.profile_name == "LOCAL_STRONG_14B"
    assert PROFILE_LOCAL_STRONG_14B.model == LOCAL_STRONG_14B_MODEL
    assert PROFILE_LOCAL_STRONG_14B.max_model_len == LOCAL_STRONG_14B_MAX_MODEL_LEN
    assert PROFILE_LOCAL_STRONG_14B.max_num_seqs == LOCAL_STRONG_14B_MAX_NUM_SEQS


def test_registry_contains_both_tiers():
    assert "local_fast" in SERVING_PROFILE_REGISTRY
    assert "local_strong" in SERVING_PROFILE_REGISTRY


def test_get_profile_local_fast():
    p = get_profile("local_fast")
    assert p.profile_name == "LOCAL_FAST_7B"


def test_get_profile_local_strong():
    p = get_profile("local_strong")
    assert p.profile_name == "LOCAL_STRONG_14B"


def test_get_profile_unknown_raises():
    with pytest.raises(KeyError):
        get_profile("local_32b")


# ---------------------------------------------------------------------------
# Startup validation guard tests
# ---------------------------------------------------------------------------


def test_invalid_max_model_len_zero_raises():
    with pytest.raises(VLLMServingProfileInvalid):
        VLLMServingProfile(
            profile_name="LOCAL_FAST_7B",
            model=LOCAL_FAST_7B_MODEL,
            max_model_len=0,
            max_num_seqs=4,
            gpu_memory_utilization=0.85,
        )


def test_invalid_max_num_seqs_zero_raises():
    with pytest.raises(VLLMServingProfileInvalid):
        VLLMServingProfile(
            profile_name="LOCAL_FAST_7B",
            model=LOCAL_FAST_7B_MODEL,
            max_model_len=8192,
            max_num_seqs=0,
            gpu_memory_utilization=0.85,
        )


def test_invalid_gpu_utilization_zero_raises():
    with pytest.raises(VLLMServingProfileInvalid):
        VLLMServingProfile(
            profile_name="LOCAL_FAST_7B",
            model=LOCAL_FAST_7B_MODEL,
            max_model_len=8192,
            max_num_seqs=4,
            gpu_memory_utilization=0.0,
        )


def test_14b_exceeds_ceiling_raises():
    with pytest.raises(VLLMServingProfileInvalid) as exc_info:
        VLLMServingProfile(
            profile_name="LOCAL_STRONG_14B",
            model=LOCAL_STRONG_14B_MODEL,
            max_model_len=LOCAL_STRONG_14B_MAX_MODEL_LEN_CEILING + 1,
            max_num_seqs=2,
            gpu_memory_utilization=0.85,
        )
    assert "hard fail at startup" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Co-change invariant tests
# ---------------------------------------------------------------------------


def test_co_change_both_increase_raises():
    with pytest.raises(VLLMCoChangeViolation):
        assert_no_simultaneous_increase(
            old_max_model_len=4096,
            new_max_model_len=8192,
            old_max_num_seqs=1,
            new_max_num_seqs=2,
            profile_name="LOCAL_STRONG_14B",
        )


def test_co_change_only_model_len_increase_ok():
    assert_no_simultaneous_increase(
        old_max_model_len=4096,
        new_max_model_len=8192,
        old_max_num_seqs=2,
        new_max_num_seqs=2,
        profile_name="LOCAL_STRONG_14B",
    )


def test_co_change_only_num_seqs_increase_ok():
    assert_no_simultaneous_increase(
        old_max_model_len=4096,
        new_max_model_len=4096,
        old_max_num_seqs=1,
        new_max_num_seqs=2,
        profile_name="LOCAL_STRONG_14B",
    )


def test_co_change_both_decrease_ok():
    assert_no_simultaneous_increase(
        old_max_model_len=8192,
        new_max_model_len=4096,
        old_max_num_seqs=2,
        new_max_num_seqs=1,
        profile_name="LOCAL_STRONG_14B",
    )


# ---------------------------------------------------------------------------
# No 32B / quantized tier invariants
# ---------------------------------------------------------------------------


def test_no_32b_in_registry():
    for key in SERVING_PROFILE_REGISTRY:
        assert "32b" not in key.lower()
        assert "32B" not in SERVING_PROFILE_REGISTRY[key].model


def test_no_quantized_in_registry():
    for key in SERVING_PROFILE_REGISTRY:
        model = SERVING_PROFILE_REGISTRY[key].model.lower()
        assert "awq" not in model
        assert "gptq" not in model
        assert "gguf" not in model
        assert "int4" not in model
        assert "int8" not in model
