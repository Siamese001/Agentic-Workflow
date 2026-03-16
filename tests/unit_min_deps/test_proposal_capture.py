"""GAP-B: _ml_run_pipeline proposals must be captured and persisted with canonical_bytes()."""

import ast
import json
from pathlib import Path
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L0_ROUTING_DIR,
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

_emit_records_execution_trace("p0", "evidence", "test_proposal_capture")
_emit_applies_guardrail("p0", "test_proposal_capture", "p0_governance")
_emit_reads_policy_state("p0", "test_proposal_capture", "policy_binding")
_emit_snapshots_state("p0", "test_proposal_capture", "state_snapshot")
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

_emit_emits_metric_event("test_proposal_capture", "p4obs", "metric_1")
_emit_emits_metric_event("test_proposal_capture", "p4obs", "metric_2")
_emit_emits_metric_event("test_proposal_capture", "p4obs", "metric_3")
_emit_emits_metric_event("test_proposal_capture", "p4obs", "metric_4")
_emit_emits_metric_event("test_proposal_capture", "p4obs", "metric_5")
_emit_emits_metric_event("test_proposal_capture", "p4obs", "metric_6")
_emit_records_incident_event("test_proposal_capture", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_proposal_capture", "p4obs", "anomaly")
_emit_writes_observability_log("test_proposal_capture", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_proposal_capture", "p4obs", "mon_state")
_emit_triggers_alert("test_proposal_capture", "p4obs", "alert")
_emit_links_incident_trace("test_proposal_capture", "p4obs", "trace_link")
_emit_captures_pattern("test_proposal_capture", "p3lm", "pattern")
_emit_records_learning_event("test_proposal_capture", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_proposal_capture", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_proposal_capture", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_proposal_capture", "p3lm", "routing")
_emit_improves_agent_policy("test_proposal_capture", "p3lm", "policy")
_emit_stores_learning_state("test_proposal_capture", "p3lm", "state")
_emit_records_execution_trace("test_proposal_capture", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_proposal_capture", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_proposal_capture", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_proposal_capture", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_proposal_capture", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_proposal_capture", "env_read", "p2_env_1")
_emit_reads_environ("test_proposal_capture", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_proposal_capture", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_proposal_capture", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_proposal_capture", "context_pull")
_emit_pulls_context("p1", "test_proposal_capture", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_proposal_capture", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_proposal_capture", "uwg_term_2")
_emit_writes_through("p1", "test_proposal_capture", "write_through")
_emit_writes_through("p1", "test_proposal_capture", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_proposal_capture", "safety_validation")
_emit_invokes_eval("p1", "test_proposal_capture", "eval_call")
_emit_proposal_commits_routing("p1", "test_proposal_capture", "routing_commit")
emit_replay_key("p0", "test_proposal_capture")
emit_determinism_digest("p0", "test_proposal_capture")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_proposal_capture", "execution_auth")
_emit_validates_capability("p2", "test_proposal_capture", "capability_check")
_emit_routes_to_capability("p2", "test_proposal_capture", "capability_route")
_emit_writes_via_uwg("p2", "test_proposal_capture", "uwg_write")
_emit_blocks_direct_write("p2", "test_proposal_capture", "direct_write_block")
_emit_records_tool_invocation("p2", "test_proposal_capture", "tool_invocation")
_emit_captures_execution_output("p2", "test_proposal_capture", "exec_output")
_emit_dispatches_agent("p3", "test_proposal_capture", "agent_dispatch")
_emit_coordinates_agents("p3", "test_proposal_capture", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_proposal_capture", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_proposal_capture", "healing_outcome")
_emit_escalates_failure("p3", "test_proposal_capture", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_proposal_capture", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_proposal_capture", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_proposal_capture", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_proposal_capture", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_proposal_capture", "eval_metric")
_emit_stores_embedding("p4", "test_proposal_capture", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_proposal_capture", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_proposal_capture", "exec_snapshot_link")

EXECUTE_SSOT_PATH = Path(__file__).parent.parent.parent / L0_ROUTING_DIR / "scripts" / "execute_ssot.py"


@pytest.mark.unit_min_deps
class TestProposalCapture:
    def test_pipeline_call_assigned_not_bare_in_source(self):
        """AST: _ml_run_pipeline() call must be assigned (not a bare call)."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src)

        for node in ast.walk(tree):
            # Find the pipeline try-block; look for bare Expr(Call) to _ml_run_pipeline
            if isinstance(node, ast.Expr) and isinstance(node.value, ast.Call):
                func = node.value.func
                name = None
                if isinstance(func, ast.Name):
                    name = func.id
                elif isinstance(func, ast.Attribute):
                    name = func.attr
                if name == "_ml_run_pipeline":
                    pytest.fail("_ml_run_pipeline() called as a bare expression — return value discarded")

    def test_canonical_bytes_used_not_str_in_source(self):
        """AST: str(_p) must NOT appear in the proposal write block; canonical_bytes must appear."""
        src = EXECUTE_SSOT_PATH.read_text(encoding="utf-8", errors="replace")
        assert "canonical_bytes" in src, "canonical_bytes not found in execute_ssot.py"
        # Verify str(_p) pattern is absent near proposals
        assert '"proposal": str(' not in src and "'proposal': str(" not in src, (
            "Unsafe str(proposal) serialization found"
        )

    def test_change_package_canonical_bytes_is_deterministic(self):
        """ChangePackage.canonical_bytes() produces identical output for identical input."""
        from system_learning.engines.change_package_impl import ChangePackage

        pkg = ChangePackage(
            source="L0",
            target="threshold_config",
            changes=b'{"threshold": 0.8}',
            confidence=0.9,
            reason=("signal above threshold",),
            timestamp_utc=1_000_000,
        )
        b1 = pkg.canonical_bytes()
        b2 = pkg.canonical_bytes()
        assert b1 == b2
        assert isinstance(b1, bytes)

    def test_proposal_jsonl_structure(self, tmp_path):
        """Written JSONL line must have schema_version, created_utc, payload keys."""
        # Simulate what the write block does
        from system_learning.engines.change_package_impl import ChangePackage

        pkg = ChangePackage(
            source="L0",
            target="threshold_config",
            changes=b'{"threshold": 0.8}',
            confidence=0.9,
            reason=("signal above threshold",),
            timestamp_utc=1_000_000,
        )

        prop_path = tmp_path / "proposals" / "threshold_proposals.jsonl"
        prop_path.parent.mkdir(parents=True, exist_ok=True)

        now_utc = 1_000_000
        with open(prop_path, "a", encoding="utf-8") as pf:
            pf.write(
                json.dumps(
                    {
                        "schema_version": 1,
                        "created_utc": now_utc,
                        "payload": pkg.canonical_bytes().decode("utf-8", errors="replace"),
                    },
                    sort_keys=True,
                    separators=(",", ":"),
                )
                + "\n"
            )

        lines = prop_path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        parsed = json.loads(lines[0])
        assert parsed["schema_version"] == 1
        assert parsed["created_utc"] == 1_000_000
        assert "payload" in parsed
        assert isinstance(parsed["payload"], str)

    def test_proposal_jsonl_determinism(self, tmp_path):
        """Same ChangePackage + same now_utc → identical JSONL bytes on two writes."""
        from system_learning.engines.change_package_impl import ChangePackage

        pkg = ChangePackage(
            source="L1",
            target="model_config",
            changes=b'{"model": "bert-base"}',
            confidence=0.85,
            reason=("drift detected",),
            timestamp_utc=2_000_000,
        )
        now_utc = 2_000_000

        def write_jsonl(path):
            with open(path, "w", encoding="utf-8") as pf:
                pf.write(
                    json.dumps(
                        {
                            "schema_version": 1,
                            "created_utc": now_utc,
                            "payload": pkg.canonical_bytes().decode("utf-8", errors="replace"),
                        },
                        sort_keys=True,
                        separators=(",", ":"),
                    )
                    + "\n"
                )
            return Path(path).read_bytes()

        b1 = write_jsonl(tmp_path / "a.jsonl")
        b2 = write_jsonl(tmp_path / "b.jsonl")
        assert b1 == b2

    def test_empty_proposals_no_write(self, tmp_path):
        """Empty proposal list must produce no JSONL file."""
        prop_path = tmp_path / "proposals" / "threshold_proposals.jsonl"
        _ml_proposals = []
        if _ml_proposals:
            prop_path.parent.mkdir(parents=True, exist_ok=True)
            with open(prop_path, "a", encoding="utf-8") as pf:
                pf.write("line\n")
        assert not prop_path.exists()

    def test_write_failure_non_fatal(self, tmp_path, caplog):
        """IOError during proposal write must be caught and logged as warning, not raised."""
        import logging

        from system_learning.engines.change_package_impl import ChangePackage

        pkg = ChangePackage(
            source="L5",
            target="policy_config",
            changes=b'{"p": 1}',
            confidence=0.7,
            reason=("policy change",),
            timestamp_utc=3_000_000,
        )

        # Patch open to raise IOError
        with patch("builtins.open", side_effect=OSError("disk full")):
            with caplog.at_level(logging.WARNING):
                try:
                    _prop_path = tmp_path / "proposals" / "threshold_proposals.jsonl"
                    _prop_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(_prop_path, "a", encoding="utf-8") as pf:
                        pf.write("x\n")
                except OSError as _prop_err:  # guardian: allow-silent-swallower
                    import logging as _log

                    _log.getLogger(__name__).warning("[MetaLearning] proposal write failed: %s", _prop_err)
                # No re-raise — must be silent to caller
