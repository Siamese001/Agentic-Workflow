"""Integration invariant: DeterminismDigestEmitter wired into execute_ssot.

Tests:
  1. _compute_pipeline_digest() exists and is callable.
  2. Two independent calls with identical targets produce identical 64-hex digest.
  3. Identical targets -> identical emitted DETERMINISM-DIGEST line.
  4. Different targets -> different digest (sensitivity check).
  5. Full emit path: DeterminismDigestEmitter.emit_once wraps _compute_pipeline_digest
     and produces exactly "DETERMINISM-DIGEST: <64-hex>".
  6. Two-run pipeline stdout simulation: capturing print() output from both runs
     shows exactly one DETERMINISM-DIGEST line per run, identical across runs.
  7. Tamper env (W_HARDEN_NEGCTRL_TAMPER=1) changes digest; clean run restores it.
"""

from __future__ import annotations

import io
import os
from contextlib import redirect_stdout
from unittest.mock import patch

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    SYSTEM_LEARNING_DIR,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_execute_ssot_digest_emission")
# REMOVED: _emit_applies_guardrail("p0", "test_execute_ssot_digest_emission", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_execute_ssot_digest_emission", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_execute_ssot_digest_emission", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_execute_ssot_digest_emission", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_digest_emission", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_digest_emission", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_digest_emission", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_digest_emission", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_execute_ssot_digest_emission", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_execute_ssot_digest_emission", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_execute_ssot_digest_emission", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_execute_ssot_digest_emission", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_execute_ssot_digest_emission", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_execute_ssot_digest_emission", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_execute_ssot_digest_emission", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_execute_ssot_digest_emission", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_execute_ssot_digest_emission", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_execute_ssot_digest_emission", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_execute_ssot_digest_emission", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_execute_ssot_digest_emission", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_execute_ssot_digest_emission", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_execute_ssot_digest_emission", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_digest_emission", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_digest_emission", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_digest_emission", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_digest_emission", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_execute_ssot_digest_emission", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_execute_ssot_digest_emission", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_execute_ssot_digest_emission", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_digest_emission", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_execute_ssot_digest_emission", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_digest_emission", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_execute_ssot_digest_emission", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_digest_emission", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_execute_ssot_digest_emission", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_digest_emission", "write_through")
# REMOVED: _emit_writes_through("p1", "test_execute_ssot_digest_emission", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_execute_ssot_digest_emission", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_execute_ssot_digest_emission", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_execute_ssot_digest_emission", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_execute_ssot_digest_emission", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_execute_ssot_digest_emission", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_execute_ssot_digest_emission", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_execute_ssot_digest_emission", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_execute_ssot_digest_emission", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_execute_ssot_digest_emission", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_execute_ssot_digest_emission", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_execute_ssot_digest_emission", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_execute_ssot_digest_emission", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_execute_ssot_digest_emission", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_execute_ssot_digest_emission", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_execute_ssot_digest_emission")
# REMOVED: _emit_gated_by_confidence("p1", "test_execute_ssot_digest_emission", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_execute_ssot_digest_emission")
# REMOVED: emit_determinism_digest("p0", "test_execute_ssot_digest_emission")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_execute_ssot_digest_emission", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_execute_ssot_digest_emission", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_execute_ssot_digest_emission", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_execute_ssot_digest_emission", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_execute_ssot_digest_emission", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_execute_ssot_digest_emission", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_execute_ssot_digest_emission", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_execute_ssot_digest_emission", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_execute_ssot_digest_emission", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_execute_ssot_digest_emission", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_execute_ssot_digest_emission", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_execute_ssot_digest_emission", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_execute_ssot_digest_emission", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_execute_ssot_digest_emission", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_execute_ssot_digest_emission", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_execute_ssot_digest_emission", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_execute_ssot_digest_emission", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_execute_ssot_digest_emission", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_execute_ssot_digest_emission", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_execute_ssot_digest_emission", "exec_snapshot_link")

pytestmark = pytest.mark.unit_min_deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _get_compute_fn():
    """Import _compute_pipeline_digest from execute_ssot."""
    from agentic_core.L0_routing.scripts.execute_ssot import _compute_pipeline_digest

    return _compute_pipeline_digest


def _emit_for_targets(targets: list[str]) -> str:
    """Run the full emit path: compute + emit_once. Return the printed line."""
    from agentic_core.L6_observability.engines.determinism_digest_emitter import (
        DeterminismDigestEmitter,
    )

    compute = _get_compute_fn()
    digest = compute(targets)
    return DeterminismDigestEmitter().emit_once(digest)


def _capture_emit(targets: list[str]) -> str:
    """Capture stdout from the emit path, return only DETERMINISM-DIGEST lines."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        line = _emit_for_targets(targets)
        print(line)
    captured = buf.getvalue()
    det_lines = [l for l in captured.splitlines() if l.startswith("DETERMINISM-DIGEST:")]
    return det_lines


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestComputePipelineDigestExists:
    
    @pytest.mark.unit_min_deps
    def test_returns_64_hex_string(self):
        fn = _get_compute_fn()
        result = fn([AGENTIC_CORE_DIR])
        assert isinstance(result, str)
        assert len(result) == 64
        assert all(c in "0123456789abcdef" for c in result)


class TestTwoRunIdenticalDigest:
    """Core closure proof: two independent runs produce identical digest."""

    _TARGETS = [AGENTIC_CORE_DIR, SYSTEM_LEARNING_DIR, APPS_LIC_DIR]

    @pytest.mark.unit_min_deps
    def test_run1_equals_run2(self):
        fn = _get_compute_fn()
        run1 = fn(self._TARGETS)
        run2 = fn(self._TARGETS)
        assert run1 == run2, f"Two-run digest mismatch:\n  run1={run1}\n  run2={run2}"

    @pytest.mark.unit_min_deps
    def test_run1_equals_run2_single_target(self):
        fn = _get_compute_fn()
        run1 = fn(["L5_safety"])
        run2 = fn(["L5_safety"])
        assert run1 == run2

    @pytest.mark.unit_min_deps
    def test_run1_equals_run2_empty_targets(self):
        fn = _get_compute_fn()
        run1 = fn([])
        run2 = fn([])
        assert run1 == run2

    @pytest.mark.unit_min_deps
    def test_different_targets_different_digest(self):
        fn = _get_compute_fn()
        d1 = fn([AGENTIC_CORE_DIR])
        d2 = fn([SYSTEM_LEARNING_DIR])
        assert d1 != d2, "Different targets must produce different digest"

    @pytest.mark.unit_min_deps
    def test_target_order_does_not_matter(self):
        """Digest uses sorted targets — order must not affect output."""
        fn = _get_compute_fn()
        d1 = fn([AGENTIC_CORE_DIR, SYSTEM_LEARNING_DIR])
        d2 = fn([SYSTEM_LEARNING_DIR, AGENTIC_CORE_DIR])
        assert d1 == d2, "Target order must not affect digest (sorted internally)"


class TestEmitLineFormat:
    """The emitted line must be DETERMINISM-DIGEST: <64-hex>."""

    @pytest.mark.unit_min_deps
    def test_emit_line_format(self):
        line = _emit_for_targets([AGENTIC_CORE_DIR])
        assert line.startswith("DETERMINISM-DIGEST: "), f"Bad format: {line!r}"
        hex_part = line.split(": ", 1)[1]
        assert len(hex_part) == 64
        assert all(c in "0123456789abcdef" for c in hex_part)

    @pytest.mark.unit_min_deps
    def test_two_runs_emit_identical_line(self):
        line1 = _emit_for_targets([AGENTIC_CORE_DIR])
        line2 = _emit_for_targets([AGENTIC_CORE_DIR])
        assert line1 == line2, f"Emitted lines differ:\n  run1={line1!r}\n  run2={line2!r}"

    @pytest.mark.unit_min_deps
    def test_duplicate_emitter_raises(self):
        from agentic_core.L6_observability.engines.determinism_digest_emitter import (
            DeterminismDigestEmitter,
            DuplicateEmissionError,
        )

        fn = _get_compute_fn()
        emitter = DeterminismDigestEmitter()
        digest = fn([AGENTIC_CORE_DIR])
        emitter.emit_once(digest)
        with pytest.raises(DuplicateEmissionError):
            emitter.emit_once(digest)


class TestTwoRunStdoutCapture:
    """Simulate the pipeline print() path: exactly one DETERMINISM-DIGEST line per run."""

    _TARGETS = [AGENTIC_CORE_DIR, SYSTEM_LEARNING_DIR]

    @pytest.mark.unit_min_deps
    def test_exactly_one_digest_line_per_run(self):
        lines_run1 = _capture_emit(self._TARGETS)
        lines_run2 = _capture_emit(self._TARGETS)
        assert len(lines_run1) == 1, (
            f"Expected exactly 1 DETERMINISM-DIGEST line in run1, got {len(lines_run1)}: {lines_run1}"
        )
        assert len(lines_run2) == 1, (
            f"Expected exactly 1 DETERMINISM-DIGEST line in run2, got {len(lines_run2)}: {lines_run2}"
        )

    @pytest.mark.unit_min_deps
    def test_two_runs_stdout_lines_identical(self):
        lines_run1 = _capture_emit(self._TARGETS)
        lines_run2 = _capture_emit(self._TARGETS)
        assert lines_run1[0] == lines_run2[0], (
            f"Captured digest lines differ:\n  run1={lines_run1[0]!r}\n  run2={lines_run2[0]!r}"
        )

    @pytest.mark.unit_min_deps
    def test_captured_line_is_correct_format(self):
        lines = _capture_emit(self._TARGETS)
        assert lines[0].startswith("DETERMINISM-DIGEST: ")
        hex_part = lines[0].split(": ", 1)[1]
        assert len(hex_part) == 64
        assert all(c in "0123456789abcdef" for c in hex_part)


class TestNegativeControlTwoRun:
    """Tamper env breaks digest; restoring it restores identical output."""

    _TARGETS = [AGENTIC_CORE_DIR]

    @pytest.mark.unit_min_deps
    def test_tamper_changes_digest(self):
        fn = _get_compute_fn()
        with patch.dict(os.environ, {}, clear=False):
            if "W_HARDEN_NEGCTRL_TAMPER" in os.environ:
                del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            clean = fn(self._TARGETS)
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            tampered = fn(self._TARGETS)
        assert clean != tampered, "Negative control FAILED: W_HARDEN_NEGCTRL_TAMPER=1 did not change digest"

    @pytest.mark.unit_min_deps
    def test_restore_after_tamper_gives_clean_digest(self):
        fn = _get_compute_fn()
        with patch.dict(os.environ, {}, clear=False):
            if "W_HARDEN_NEGCTRL_TAMPER" in os.environ:
                del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            clean1 = fn(self._TARGETS)
        with patch.dict(os.environ, {"W_HARDEN_NEGCTRL_TAMPER": "1"}):
            _ = fn(self._TARGETS)
        with patch.dict(os.environ, {}, clear=False):
            if "W_HARDEN_NEGCTRL_TAMPER" in os.environ:
                del os.environ["W_HARDEN_NEGCTRL_TAMPER"]
            restored = fn(self._TARGETS)
        assert clean1 == restored, (
            f"Digest did not restore after tamper removal:\n  clean1={clean1}\n  restored={restored}"
        )
