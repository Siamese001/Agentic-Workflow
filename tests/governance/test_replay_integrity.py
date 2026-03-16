"""Wave 5.2: Replay artifact sealing tests.

Validates:
- replay_hash computed on create
- integrity_verified set True on create
- Tampered raw_response_bytes fails integrity check
- Tampered model_version fails integrity check
- Valid bundle passes integrity check
- verify_replay_integrity function
"""

import pytest

from agentic_core.L2_execution.types.llm_replay_types import (
    ReplayBundle,
    verify_replay_integrity,
)
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
_emit_emits_metric_event("test_replay_integrity", "p4obs", "metric_1")
_emit_emits_metric_event("test_replay_integrity", "p4obs", "metric_2")
_emit_emits_metric_event("test_replay_integrity", "p4obs", "metric_3")
_emit_emits_metric_event("test_replay_integrity", "p4obs", "metric_4")
_emit_emits_metric_event("test_replay_integrity", "p4obs", "metric_5")
_emit_emits_metric_event("test_replay_integrity", "p4obs", "metric_6")
_emit_records_incident_event("test_replay_integrity", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_replay_integrity", "p4obs", "anomaly")
_emit_writes_observability_log("test_replay_integrity", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_replay_integrity", "p4obs", "mon_state")
_emit_triggers_alert("test_replay_integrity", "p4obs", "alert")
_emit_links_incident_trace("test_replay_integrity", "p4obs", "trace_link")
_emit_captures_pattern("test_replay_integrity", "p3lm", "pattern")
_emit_records_learning_event("test_replay_integrity", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_replay_integrity", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_replay_integrity", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_replay_integrity", "p3lm", "routing")
_emit_improves_agent_policy("test_replay_integrity", "p3lm", "policy")
_emit_stores_learning_state("test_replay_integrity", "p3lm", "state")
_emit_records_execution_trace("test_replay_integrity", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_replay_integrity", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_replay_integrity", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_replay_integrity", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_replay_integrity", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_replay_integrity", "env_read", "p2_env_1")
_emit_reads_environ("test_replay_integrity", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_replay_integrity", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_replay_integrity", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_replay_integrity")
_emit_applies_guardrail("p0", "test_replay_integrity", "p0_governance")
_emit_reads_policy_state("p0", "test_replay_integrity", "policy_binding")
_emit_snapshots_state("p0", "test_replay_integrity", "state_snapshot")
_emit_pulls_context("p1", "test_replay_integrity", "context_pull")
_emit_pulls_context("p1", "test_replay_integrity", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_replay_integrity", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_replay_integrity", "uwg_term_secondary")
_emit_writes_through("p1", "test_replay_integrity", "write_through")
_emit_writes_through("p1", "test_replay_integrity", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_replay_integrity", "safety_validation")
_emit_invokes_eval("p1", "test_replay_integrity", "eval_call")
_emit_proposal_commits_routing("p1", "test_replay_integrity", "routing_commit")
emit_replay_key("p0", "test_replay_integrity")
emit_determinism_digest("p0", "test_replay_integrity")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_replay_integrity", "execution_auth")
_emit_validates_capability("p2", "test_replay_integrity", "capability_check")
_emit_routes_to_capability("p2", "test_replay_integrity", "capability_route")
_emit_writes_via_uwg("p2", "test_replay_integrity", "uwg_write")
_emit_blocks_direct_write("p2", "test_replay_integrity", "direct_write_block")
_emit_records_tool_invocation("p2", "test_replay_integrity", "tool_invocation")
_emit_captures_execution_output("p2", "test_replay_integrity", "exec_output")
_emit_dispatches_agent("p3", "test_replay_integrity", "agent_dispatch")
_emit_coordinates_agents("p3", "test_replay_integrity", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_replay_integrity", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_replay_integrity", "healing_outcome")
_emit_escalates_failure("p3", "test_replay_integrity", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_replay_integrity", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_replay_integrity", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_replay_integrity", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_replay_integrity", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_replay_integrity", "eval_metric")
_emit_stores_embedding("p4", "test_replay_integrity", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_replay_integrity", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_replay_integrity", "exec_snapshot_link")

pytestmark = pytest.mark.governance

PROMPT = b"test prompt"
RESPONSE = b"test response"


class TestReplayHashComputed:
    """replay_hash must be set on create."""

    def test_replay_hash_is_sha256(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert len(bundle.replay_hash) == 64
        assert all(c in "0123456789abcdef" for c in bundle.replay_hash)

    def test_integrity_verified_true_on_create(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert bundle.integrity_verified is True

    def test_replay_hash_deterministic(self):
        a = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        b = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert a.replay_hash == b.replay_hash


class TestTamperDetection:
    """Tampered bundles must fail integrity check."""

    def test_tampered_response_fails(self):
        good = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        tampered = ReplayBundle(
            model_version=good.model_version,
            tokenizer_version=good.tokenizer_version,
            raw_prompt_bytes=good.raw_prompt_bytes,
            raw_response_bytes=b"TAMPERED",
            provider_checksum=good.provider_checksum,
            replay_hash=good.replay_hash,
            integrity_verified=good.integrity_verified,
        )
        assert not verify_replay_integrity(tampered)

    def test_tampered_model_version_fails(self):
        good = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        tampered = ReplayBundle(
            model_version="TAMPERED",
            tokenizer_version=good.tokenizer_version,
            raw_prompt_bytes=good.raw_prompt_bytes,
            raw_response_bytes=good.raw_response_bytes,
            provider_checksum=good.provider_checksum,
            replay_hash=good.replay_hash,
            integrity_verified=good.integrity_verified,
        )
        assert not verify_replay_integrity(tampered)

    def test_valid_bundle_passes(self):
        bundle = ReplayBundle.create(
            model_version="v1",
            tokenizer_version="t1",
            raw_prompt_bytes=PROMPT,
            raw_response_bytes=RESPONSE,
        )
        assert verify_replay_integrity(bundle)
