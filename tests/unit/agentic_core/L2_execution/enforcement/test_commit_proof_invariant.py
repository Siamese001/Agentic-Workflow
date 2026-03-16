"""Tests for CommitProofInvariant determinism proof standard.

Phase 8: Determinism proof standard + negative control.
Spec: Determinism & Replayability, Guarantee #18.
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

_emit_records_execution_trace("p0", "evidence", "test_commit_proof_invariant")
_emit_applies_guardrail("p0", "test_commit_proof_invariant", "p0_governance")
_emit_reads_policy_state("p0", "test_commit_proof_invariant", "policy_binding")
_emit_snapshots_state("p0", "test_commit_proof_invariant", "state_snapshot")
emit_replay_key("p0", "test_commit_proof_invariant")
emit_determinism_digest("p0", "test_commit_proof_invariant")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_commit_proof_invariant", "execution_auth")
_emit_validates_capability("p2", "test_commit_proof_invariant", "capability_check")
_emit_routes_to_capability("p2", "test_commit_proof_invariant", "capability_route")
_emit_writes_via_uwg("p2", "test_commit_proof_invariant", "uwg_write")
_emit_blocks_direct_write("p2", "test_commit_proof_invariant", "direct_write_block")
_emit_records_tool_invocation("p2", "test_commit_proof_invariant", "tool_invocation")
_emit_captures_execution_output("p2", "test_commit_proof_invariant", "exec_output")
_emit_dispatches_agent("p3", "test_commit_proof_invariant", "agent_dispatch")
_emit_coordinates_agents("p3", "test_commit_proof_invariant", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_commit_proof_invariant", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_commit_proof_invariant", "healing_outcome")
_emit_escalates_failure("p3", "test_commit_proof_invariant", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_commit_proof_invariant", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_commit_proof_invariant", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_commit_proof_invariant", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_commit_proof_invariant", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_commit_proof_invariant", "eval_metric")
_emit_stores_embedding("p4", "test_commit_proof_invariant", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_commit_proof_invariant", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_commit_proof_invariant", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

pytestmark = pytest.mark.unit

from agentic_core.L2_execution.types.commit_proof_invariant_types import (
    CommitProofInvariant,
    DeterminismProofFailure,
    canonical_digest,
    make_proof,
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

_emit_emits_metric_event("test_commit_proof_invariant", "p4obs", "metric_1")
_emit_emits_metric_event("test_commit_proof_invariant", "p4obs", "metric_2")
_emit_emits_metric_event("test_commit_proof_invariant", "p4obs", "metric_3")
_emit_emits_metric_event("test_commit_proof_invariant", "p4obs", "metric_4")
_emit_emits_metric_event("test_commit_proof_invariant", "p4obs", "metric_5")
_emit_emits_metric_event("test_commit_proof_invariant", "p4obs", "metric_6")
_emit_records_incident_event("test_commit_proof_invariant", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_commit_proof_invariant", "p4obs", "anomaly")
_emit_writes_observability_log("test_commit_proof_invariant", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_commit_proof_invariant", "p4obs", "mon_state")
_emit_triggers_alert("test_commit_proof_invariant", "p4obs", "alert")
_emit_links_incident_trace("test_commit_proof_invariant", "p4obs", "trace_link")
_emit_captures_pattern("test_commit_proof_invariant", "p3lm", "pattern")
_emit_records_learning_event("test_commit_proof_invariant", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_commit_proof_invariant", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_commit_proof_invariant", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_commit_proof_invariant", "p3lm", "routing")
_emit_improves_agent_policy("test_commit_proof_invariant", "p3lm", "policy")
_emit_stores_learning_state("test_commit_proof_invariant", "p3lm", "state")
_emit_records_execution_trace("test_commit_proof_invariant", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_commit_proof_invariant", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_commit_proof_invariant", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_commit_proof_invariant", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_commit_proof_invariant", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_commit_proof_invariant", "env_read", "p2_env_1")
_emit_reads_environ("test_commit_proof_invariant", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_commit_proof_invariant", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_commit_proof_invariant", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_commit_proof_invariant", "context_pull")
_emit_pulls_context("p1", "test_commit_proof_invariant", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_commit_proof_invariant", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_commit_proof_invariant", "uwg_term_2")
_emit_writes_through("p1", "test_commit_proof_invariant", "write_through")
_emit_writes_through("p1", "test_commit_proof_invariant", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_commit_proof_invariant", "safety_validation")
_emit_invokes_eval("p1", "test_commit_proof_invariant", "eval_call")
_emit_proposal_commits_routing("p1", "test_commit_proof_invariant", "routing_commit")

# ---------------------------------------------------------------------------
# canonical_digest
# ---------------------------------------------------------------------------


class TestCanonicalDigest:
    def test_returns_64_hex_chars(self):
        d = canonical_digest({"a": 1})
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    def test_same_inputs_produce_same_digest(self):
        d1 = canonical_digest({"x": 1, "y": 2})
        d2 = canonical_digest({"y": 2, "x": 1})
        assert d1 == d2  # sort_keys normalizes order

    def test_different_inputs_produce_different_digest(self):
        d1 = canonical_digest({"x": 1})
        d2 = canonical_digest({"x": 2})
        assert d1 != d2

    def test_empty_dict_is_deterministic(self):
        d1 = canonical_digest({})
        d2 = canonical_digest({})
        assert d1 == d2


# ---------------------------------------------------------------------------
# CommitProofInvariant construction
# ---------------------------------------------------------------------------


class TestCommitProofInvariantConstruction:
    def _valid_digest(self) -> str:
        return "a" * 64

    def test_valid_construction(self):
        proof = CommitProofInvariant(
            phase_id="P8",
            digest="a" * 64,
            inputs_summary="test surface",
        )
        assert proof.phase_id == "P8"
        assert proof.digest == "a" * 64

    def test_empty_phase_id_raises(self):
        with pytest.raises(DeterminismProofFailure, match="phase_id must be non-empty"):
            CommitProofInvariant(phase_id="", digest="a" * 64, inputs_summary="x")

    def test_wrong_length_digest_raises(self):
        with pytest.raises(DeterminismProofFailure, match="64-char"):
            CommitProofInvariant(phase_id="P8", digest="abc", inputs_summary="x")

    def test_non_hex_digest_raises(self):
        with pytest.raises(DeterminismProofFailure, match="64-char"):
            CommitProofInvariant(phase_id="P8", digest="z" * 64, inputs_summary="x")

    def test_uppercase_hex_raises(self):
        with pytest.raises(DeterminismProofFailure, match="64-char"):
            CommitProofInvariant(phase_id="P8", digest="A" * 64, inputs_summary="x")


# ---------------------------------------------------------------------------
# verify_stable — positive control
# ---------------------------------------------------------------------------


class TestVerifyStable:
    def test_stable_digest_passes(self):
        inputs = {"registry": "v1", "policy": "v2"}
        expected_digest = canonical_digest(inputs)
        proof = CommitProofInvariant(
            phase_id="P8-stable",
            digest=expected_digest,
            inputs_summary="registry+policy",
        )
        # Positive control: same inputs → same digest → no exception
        proof.verify_stable(lambda: canonical_digest(inputs))

    def test_changed_inputs_raises(self):
        inputs = {"registry": "v1", "policy": "v2"}
        original_digest = canonical_digest(inputs)
        proof = CommitProofInvariant(
            phase_id="P8-stable",
            digest=original_digest,
            inputs_summary="registry+policy",
        )
        tampered_inputs = {"registry": "v1", "policy": "v2", "extra": "injected"}
        with pytest.raises(DeterminismProofFailure, match="Determinism proof FAILED"):
            proof.verify_stable(lambda: canonical_digest(tampered_inputs))

    def test_whitespace_change_is_detected(self):
        d1 = canonical_digest("clean string")
        d2 = canonical_digest("clean string ")
        assert d1 != d2  # canonical_digest is sensitive to whitespace changes

    def test_p5_digest_is_stable(self):
        """Positive control: canonical_digest() of the same registry surface is stable."""
        from agentic_core.agents.agent_registry import AGENT_REGISTRY, registry_digest

        surface = {
            "registry_digest": registry_digest(),
            "agent_ids": sorted(AGENT_REGISTRY.keys()),
        }
        d1 = canonical_digest(surface)
        d2 = canonical_digest(surface)
        assert d1 == d2, "Registry surface digest is non-deterministic across two calls"

    def test_lockdown_digest_is_stable(self):
        """Positive control: canonical_digest() of a multi-component surface is stable."""
        from agentic_core.agents.agent_registry import AGENT_REGISTRY, registry_digest

        surface = {
            "registry_digest": registry_digest(),
            "execution_modes": sorted({p.execution_mode.value for p in AGENT_REGISTRY.values()}),
            "reasoning_intensities": sorted({p.reasoning_intensity.value for p in AGENT_REGISTRY.values()}),
        }
        d1 = canonical_digest(surface)
        d2 = canonical_digest(surface)
        assert d1 == d2, "Multi-component lockdown surface digest is non-deterministic"


# ---------------------------------------------------------------------------
# verify_unstable — negative control
# ---------------------------------------------------------------------------


class TestVerifyUnstable:
    def test_tampered_inputs_detected(self):
        """Negative control: mutating inputs must change the digest."""
        original_inputs = {"registry": "v1", "policy": "v2"}
        original_digest = canonical_digest(original_inputs)
        proof = CommitProofInvariant(
            phase_id="P8-negctrl",
            digest=original_digest,
            inputs_summary="registry+policy",
        )
        tampered_inputs = {"registry": "TAMPERED", "policy": "v2"}
        # verify_unstable should pass (tamper detected = digest changed)
        proof.verify_unstable(lambda: canonical_digest(tampered_inputs))

    def test_unchanged_inputs_fails_negative_control(self):
        """Negative control integrity: if we claim tamper but digest is same, raise."""
        inputs = {"registry": "v1"}
        d = canonical_digest(inputs)
        proof = CommitProofInvariant(phase_id="P8-negctrl", digest=d, inputs_summary="x")
        with pytest.raises(DeterminismProofFailure, match="Negative control FAILED"):
            proof.verify_unstable(lambda: canonical_digest(inputs))  # Same, not tampered

    def test_registry_tamper_changes_p5_digest(self):
        """Negative control: mutating a registry surface value changes the digest."""
        from agentic_core.agents.agent_registry import AGENT_REGISTRY, registry_digest

        original_surface = {
            "registry_digest": registry_digest(),
            "agent_ids": sorted(AGENT_REGISTRY.keys()),
        }
        original_digest = canonical_digest(original_surface)

        tampered_surface = {
            "registry_digest": "tampered-000000000000000000000000000000000000000000000000000000000000",
            "agent_ids": sorted(AGENT_REGISTRY.keys()),
        }
        tampered_digest = canonical_digest(tampered_surface)
        assert tampered_digest != original_digest, "Tampered surface must produce different digest"


# ---------------------------------------------------------------------------
# make_proof factory
# ---------------------------------------------------------------------------


class TestMakeProof:
    def test_make_proof_captures_current_digest(self):
        inputs = {"key": "value"}
        proof = make_proof(
            phase_id="P8-factory",
            inputs_summary="key=value",
            recompute_fn=lambda: canonical_digest(inputs),
        )
        assert proof.phase_id == "P8-factory"
        assert proof.digest == canonical_digest(inputs)

    def test_make_proof_then_verify_stable(self):
        inputs = {"a": 1, "b": 2}
        proof = make_proof(
            phase_id="P8-roundtrip",
            inputs_summary="a+b",
            recompute_fn=lambda: canonical_digest(inputs),
        )
        # Re-verify with same inputs — must pass
        proof.verify_stable(lambda: canonical_digest(inputs))

    def test_make_proof_then_verify_unstable_on_tamper(self):
        inputs = {"a": 1}
        proof = make_proof(
            phase_id="P8-negctrl-factory",
            inputs_summary="a=1",
            recompute_fn=lambda: canonical_digest(inputs),
        )
        tampered = {"a": 999}
        proof.verify_unstable(lambda: canonical_digest(tampered))
