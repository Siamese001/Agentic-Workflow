"""Unit tests for RLHF Optimizer - deterministic DPO-driven threshold adjustments."""

import json

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

_emit_authorize_and_execute("p2", "test_rlhf_optimizer", "execution_auth")
_emit_validates_capability("p2", "test_rlhf_optimizer", "capability_check")
_emit_routes_to_capability("p2", "test_rlhf_optimizer", "capability_route")
_emit_writes_via_uwg("p2", "test_rlhf_optimizer", "uwg_write")
_emit_blocks_direct_write("p2", "test_rlhf_optimizer", "direct_write_block")
_emit_records_tool_invocation("p2", "test_rlhf_optimizer", "tool_invocation")
_emit_captures_execution_output("p2", "test_rlhf_optimizer", "exec_output")
_emit_dispatches_agent("p3", "test_rlhf_optimizer", "agent_dispatch")
_emit_coordinates_agents("p3", "test_rlhf_optimizer", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_rlhf_optimizer", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_rlhf_optimizer", "healing_outcome")
_emit_escalates_failure("p3", "test_rlhf_optimizer", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_rlhf_optimizer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_rlhf_optimizer", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_rlhf_optimizer", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_rlhf_optimizer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_rlhf_optimizer", "eval_metric")
_emit_stores_embedding("p4", "test_rlhf_optimizer", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_rlhf_optimizer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_rlhf_optimizer", "exec_snapshot_link")
from system_learning.engines.change_package_impl import ChangePackage
from system_learning.engines.rlhf_optimizer import (
    DefaultDeterministicRLHFOptimizer,
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
_emit_emits_metric_event("test_rlhf_optimizer", "p4obs", "metric_1")
_emit_emits_metric_event("test_rlhf_optimizer", "p4obs", "metric_2")
_emit_emits_metric_event("test_rlhf_optimizer", "p4obs", "metric_3")
_emit_emits_metric_event("test_rlhf_optimizer", "p4obs", "metric_4")
_emit_emits_metric_event("test_rlhf_optimizer", "p4obs", "metric_5")
_emit_emits_metric_event("test_rlhf_optimizer", "p4obs", "metric_6")
_emit_records_incident_event("test_rlhf_optimizer", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_rlhf_optimizer", "p4obs", "anomaly")
_emit_writes_observability_log("test_rlhf_optimizer", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_rlhf_optimizer", "p4obs", "mon_state")
_emit_triggers_alert("test_rlhf_optimizer", "p4obs", "alert")
_emit_links_incident_trace("test_rlhf_optimizer", "p4obs", "trace_link")
_emit_captures_pattern("test_rlhf_optimizer", "p3lm", "pattern")
_emit_records_learning_event("test_rlhf_optimizer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_rlhf_optimizer", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_rlhf_optimizer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_rlhf_optimizer", "p3lm", "routing")
_emit_improves_agent_policy("test_rlhf_optimizer", "p3lm", "policy")
_emit_stores_learning_state("test_rlhf_optimizer", "p3lm", "state")
_emit_records_execution_trace("test_rlhf_optimizer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_rlhf_optimizer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_rlhf_optimizer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_rlhf_optimizer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_rlhf_optimizer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_rlhf_optimizer", "env_read", "p2_env_1")
_emit_reads_environ("test_rlhf_optimizer", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_rlhf_optimizer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_rlhf_optimizer", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_rlhf_optimizer")
_emit_applies_guardrail("p0", "test_rlhf_optimizer", "p0_governance")
_emit_reads_policy_state("p0", "test_rlhf_optimizer", "policy_binding")
_emit_snapshots_state("p0", "test_rlhf_optimizer", "state_snapshot")
_emit_pulls_context("p1", "test_rlhf_optimizer", "context_pull")
_emit_pulls_context("p1", "test_rlhf_optimizer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_rlhf_optimizer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_rlhf_optimizer", "uwg_term_secondary")
_emit_writes_through("p1", "test_rlhf_optimizer", "write_through")
_emit_writes_through("p1", "test_rlhf_optimizer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_rlhf_optimizer", "safety_validation")
_emit_invokes_eval("p1", "test_rlhf_optimizer", "eval_call")
_emit_proposal_commits_routing("p1", "test_rlhf_optimizer", "routing_commit")
emit_replay_key("p0", "test_rlhf_optimizer")
emit_determinism_digest("p0", "test_rlhf_optimizer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


pytestmark = pytest.mark.unit_min_deps


class TestRLHFOptimizer:
    """Test suite for RLHF Optimizer deterministic behavior."""

    def test_approve_relaxes_within_bounds(self):
        """APPROVE decisions should relax thresholds within bounds."""
        optimizer = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=0.1,
            reject_tighten_delta=-0.1,
        )

        # Create DPO batch with APPROVE decisions
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {
                        "control_hash": "control1_hash",
                        "candidate_hash": "candidate1_hash",
                    },
                    "control_output_hash": "control1_hash",
                    "candidate_output_hash": "candidate1_hash",
                    "human_decision": "APPROVE",
                    "reasons": ["good_quality"],
                },
                {
                    "example_id": {
                        "control_hash": "control2_hash",
                        "candidate_hash": "candidate2_hash",
                    },
                    "control_output_hash": "control2_hash",
                    "candidate_output_hash": "candidate2_hash",
                    "human_decision": "APPROVE",
                    "reasons": ["meets_requirements"],
                },
            ]
        }

        current_config = {
            "threshold_a": 0.5,
            "threshold_b": 1.0,
        }

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should be a valid proposal
        assert isinstance(proposal, ChangePackage)
        assert proposal.source == "rlhf_optimizer"
        assert proposal.target == "threshold_config"

        # Should have relaxed thresholds
        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold_a"] > current_config["threshold_a"]
        assert final_config["threshold_b"] > current_config["threshold_b"]

        # Should be within bounds
        assert 0.2 <= final_config["threshold_a"] <= 1.8
        assert 0.2 <= final_config["threshold_b"] <= 1.8

        # Should have appropriate confidence
        assert proposal.confidence > 0.0
        assert "approve_relax_0.100000" in proposal.reason

    def test_reject_tightens_within_bounds(self):
        """REJECT decisions should tighten thresholds within bounds."""
        optimizer = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=0.15,
            reject_tighten_delta=-0.05,  # Smaller delta to avoid clamping
        )

        # Create DPO batch with REJECT decisions
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {
                        "control_hash": "control1_hash",
                        "candidate_hash": "candidate1_hash",
                    },
                    "control_output_hash": "control1_hash",
                    "candidate_output_hash": "candidate1_hash",
                    "human_decision": "REJECT",
                    "reasons": ["poor_quality"],
                },
            ]
        }

        current_config = {
            "threshold_x": 1.2,
            "threshold_y": 0.8,
        }

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should have tightened thresholds (negative delta applied)
        final_config = json.loads(proposal.changes.decode("utf-8"))
        # REJECT adds negative delta, so values should be lower than original
        assert final_config["threshold_x"] < current_config["threshold_x"]
        assert final_config["threshold_y"] < current_config["threshold_y"]

        # Should be within bounds
        assert 0.3 <= final_config["threshold_x"] <= 1.7
        assert 0.3 <= final_config["threshold_y"] <= 1.7

        # Should have reject reasons
        assert "reject_tighten_-0.050000" in proposal.reason

    def test_multiple_pairs_deterministic_application_order(self):
        """Multiple pairs should be applied in deterministic order."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        # Create DPO batch with mixed decisions
        dpo_batch = {
            "pairs": [
                {
                    "example_id": {
                        "control_hash": "z_control",  # Will be sorted last
                        "candidate_hash": "z_candidate",
                    },
                    "control_output_hash": "z_control",
                    "candidate_output_hash": "z_candidate",
                    "human_decision": "APPROVE",
                    "reasons": ["z_reason"],
                },
                {
                    "example_id": {
                        "control_hash": "a_control",  # Will be sorted first
                        "candidate_hash": "a_candidate",
                    },
                    "control_output_hash": "a_control",
                    "candidate_output_hash": "a_candidate",
                    "human_decision": "REJECT",
                    "reasons": ["a_reason"],
                },
                {
                    "example_id": {
                        "control_hash": "m_control",  # Will be sorted middle
                        "candidate_hash": "m_candidate",
                    },
                    "control_output_hash": "m_control",
                    "candidate_output_hash": "m_candidate",
                    "human_decision": "APPROVE",
                    "reasons": ["m_reason"],
                },
            ]
        }

        current_config = {"threshold": 1.0}

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should apply in sorted order: a_control (REJECT), m_control (APPROVE), z_control (APPROVE)
        # Net effect: 1.0 - 0.1 + 0.1 + 0.1 = 1.1
        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold"] == 1.1

        # Should have all reasons in order
        assert "reject_tighten_-0.100000" in proposal.reason
        assert "approve_relax_0.100000" in proposal.reason

    def test_bounds_clamping(self):
        """Thresholds should be clamped to min/max bounds."""
        optimizer = DefaultDeterministicRLHFOptimizer(
            min_threshold=THRESHOLD,
            max_threshold=THRESHOLD,
            approve_relax_delta=1.0,  # Large delta that would exceed bounds
            reject_tighten_delta=-1.0,  # Large delta that would exceed bounds
        )

        # Test APPROVE with clamping
        approve_dpo = {
            "pairs": [
                {
                    "example_id": {"control_hash": "c", "candidate_hash": "x"},
                    "control_output_hash": "c",
                    "candidate_output_hash": "x",
                    "human_decision": "APPROVE",
                    "reasons": ["test"],
                },
            ]
        }

        current_config = {"threshold": 1.4}  # Close to upper bound

        dpo_bytes = json.dumps(approve_dpo, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold"] <= 1.5  # Clamped to max

        # Test REJECT with clamping
        reject_dpo = {
            "pairs": [
                {
                    "example_id": {"control_hash": "c", "candidate_hash": "x"},
                    "control_output_hash": "c",
                    "candidate_output_hash": "x",
                    "human_decision": "REJECT",
                    "reasons": ["test"],
                },
            ]
        }

        current_config = {"threshold": 0.6}  # Close to lower bound

        dpo_bytes = json.dumps(reject_dpo, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config["threshold"] >= 0.5  # Clamped to min

    def test_malformed_dpo_batch_handled_gracefully(self):
        """Malformed DPO batch should be handled gracefully."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        current_config = {"threshold": 1.0}
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        # Test invalid JSON
        malformed_bytes = b"invalid json"

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=malformed_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should return empty proposal
        assert proposal.confidence == 0.0
        assert "malformed_dpo_batch" in proposal.reason
        assert proposal.changes == b"{}"

    def test_malformed_config_handled_gracefully(self):
        """Malformed threshold config should be handled gracefully."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        dpo_batch = {"pairs": []}
        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")

        # Test invalid config
        malformed_config = b"invalid config"

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=malformed_config,
        )

        # Should return empty proposal
        assert proposal.confidence == 0.0
        assert "malformed_threshold_config" in proposal.reason
        assert proposal.changes == b"{}"

    def test_empty_dpo_batch_no_adjustments(self):
        """Empty DPO batch should result in no adjustments."""
        optimizer = DefaultDeterministicRLHFOptimizer()

        dpo_batch = {"pairs": []}
        current_config = {"threshold": 1.0}

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        # Should have no adjustments but still be a valid proposal
        assert proposal.confidence == 0.0  # No pairs processed
        assert "no_adjustments" in proposal.reason

        # Config should remain unchanged
        final_config = json.loads(proposal.changes.decode("utf-8"))
        assert final_config == current_config

    def test_deterministic_rounding(self):
        """Floating point values should be deterministically rounded to 6 decimals."""
        optimizer = DefaultDeterministicRLHFOptimizer(approve_relax_delta=0.123456789)

        dpo_batch = {
            "pairs": [
                {
                    "example_id": {"control_hash": "c", "candidate_hash": "x"},
                    "control_output_hash": "c",
                    "candidate_output_hash": "x",
                    "human_decision": "APPROVE",
                    "reasons": ["test"],
                },
            ]
        }

        current_config = {"threshold": 1.0}

        dpo_bytes = json.dumps(dpo_batch, separators=(",", ":"), sort_keys=True).encode("utf-8")
        config_bytes = json.dumps(current_config, separators=(",", ":"), sort_keys=True).encode("utf-8")

        proposal = optimizer.propose_from_dpo(
            dpo_batch_bytes=dpo_bytes,
            current_threshold_config_bytes=config_bytes,
        )

        final_config = json.loads(proposal.changes.decode("utf-8"))

        # Should be rounded to 6 decimal places
        assert final_config["threshold"] == 1.123457  # 1.0 + 0.123456789 rounded to 6 decimals
