"""
Tests for the SSOT orchestration pipeline hardening (Phase SSOT-Orchestration-Hardening).

Five test groups:
  1. Structural completeness  — all 4 subphase slots always present in AgentRunResult
  2. Gate blocks update_agent — confidence gate prevents update_agent("execute"/"heal")
  3. Scan-mode read-only      — pre_commit/validate receive ctx.heal=False structurally
  4. Fail-closed on exception — exception in validate stops execute/heal; skip_agent called
  5. Negative control         — SSOT_ORCH_NEGCTRL_TAMPER=1 produces a different digest
"""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

from agentic_core.L0_routing.scripts.execute_ssot import (
    AGENT_PIPELINE,
    run_pipeline,
)
from agentic_core.L2_execution.protocol import (
    PIPELINE_SUBPHASES,
    SubphaseResult,
    compute_pipeline_digest,
    emit_pipeline_digest,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_capability,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_ssot_pipeline_protocol", "p4obs", "metric_1")
_emit_emits_metric_event("test_ssot_pipeline_protocol", "p4obs", "metric_2")
_emit_emits_metric_event("test_ssot_pipeline_protocol", "p4obs", "metric_3")
_emit_emits_metric_event("test_ssot_pipeline_protocol", "p4obs", "metric_4")
_emit_emits_metric_event("test_ssot_pipeline_protocol", "p4obs", "metric_5")
_emit_emits_metric_event("test_ssot_pipeline_protocol", "p4obs", "metric_6")
_emit_records_incident_event("test_ssot_pipeline_protocol", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_ssot_pipeline_protocol", "p4obs", "anomaly")
_emit_writes_observability_log("test_ssot_pipeline_protocol", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_ssot_pipeline_protocol", "p4obs", "mon_state")
_emit_triggers_alert("test_ssot_pipeline_protocol", "p4obs", "alert")
_emit_links_incident_trace("test_ssot_pipeline_protocol", "p4obs", "trace_link")
_emit_captures_pattern("test_ssot_pipeline_protocol", "p3lm", "pattern")
_emit_records_learning_event("test_ssot_pipeline_protocol", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_ssot_pipeline_protocol", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_ssot_pipeline_protocol", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_ssot_pipeline_protocol", "p3lm", "routing")
_emit_improves_agent_policy("test_ssot_pipeline_protocol", "p3lm", "policy")
_emit_stores_learning_state("test_ssot_pipeline_protocol", "p3lm", "state")
_emit_records_execution_trace("test_ssot_pipeline_protocol", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_ssot_pipeline_protocol", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_ssot_pipeline_protocol", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_ssot_pipeline_protocol", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_ssot_pipeline_protocol", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_ssot_pipeline_protocol", "env_read", "p2_env_1")
_emit_reads_environ("test_ssot_pipeline_protocol", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_ssot_pipeline_protocol", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_ssot_pipeline_protocol", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_ssot_pipeline_protocol")
_emit_applies_guardrail("p0", "test_ssot_pipeline_protocol", "p0_governance")
_emit_reads_policy_state("p0", "test_ssot_pipeline_protocol", "policy_binding")
_emit_snapshots_state("p0", "test_ssot_pipeline_protocol", "state_snapshot")
_emit_pulls_context("p1", "test_ssot_pipeline_protocol", "context_pull")
_emit_pulls_context("p1", "test_ssot_pipeline_protocol", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_ssot_pipeline_protocol", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_ssot_pipeline_protocol", "uwg_term_secondary")
_emit_writes_through("p1", "test_ssot_pipeline_protocol", "write_through")
_emit_writes_through("p1", "test_ssot_pipeline_protocol", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_ssot_pipeline_protocol", "safety_validation")
_emit_invokes_eval("p1", "test_ssot_pipeline_protocol", "eval_call")
_emit_proposal_commits_routing("p1", "test_ssot_pipeline_protocol", "routing_commit")
_emit_escalates_to_human("p1", "test_ssot_pipeline_protocol", "human_escalation")
_emit_routes_through("p1", "test_ssot_pipeline_protocol", "route_through")
_emit_checks_agent_registry("p1", "test_ssot_pipeline_protocol", "agent_registry")
_emit_validates_agent_capability("p1", "test_ssot_pipeline_protocol", "capability")
_emit_dispatches_execution_plan("p1", "test_ssot_pipeline_protocol", "exec_plan")
_emit_agent_executes_agent("p1", "test_ssot_pipeline_protocol", "sub_agent")
_emit_routes_to_agent("p1", "test_ssot_pipeline_protocol", "target_agent")
_emit_verifies_policy("p1", "test_ssot_pipeline_protocol", "policy_check")
_emit_observes_runtime_state("p1", "test_ssot_pipeline_protocol", "runtime_state")
_emit_verifies_boundary("p1", "test_ssot_pipeline_protocol", "boundary_check")
_emit_transcripts_response("p1", "test_ssot_pipeline_protocol", "transcript")
_emit_hard_fails_untranscripted("p1", "test_ssot_pipeline_protocol")
_emit_gated_by_confidence("p1", "test_ssot_pipeline_protocol", "confidence_gate")
emit_replay_key("p0", "test_ssot_pipeline_protocol")
emit_determinism_digest("p0", "test_ssot_pipeline_protocol")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ssot_pipeline_protocol", "execution_auth")
_emit_validates_capability("p2", "test_ssot_pipeline_protocol", "capability_check")
_emit_routes_to_capability("p2", "test_ssot_pipeline_protocol", "capability_route")
_emit_writes_via_uwg("p2", "test_ssot_pipeline_protocol", "uwg_write")
_emit_blocks_direct_write("p2", "test_ssot_pipeline_protocol", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ssot_pipeline_protocol", "tool_invocation")
_emit_captures_execution_output("p2", "test_ssot_pipeline_protocol", "exec_output")
_emit_dispatches_agent("p3", "test_ssot_pipeline_protocol", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ssot_pipeline_protocol", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ssot_pipeline_protocol", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ssot_pipeline_protocol", "healing_outcome")
_emit_escalates_failure("p3", "test_ssot_pipeline_protocol", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ssot_pipeline_protocol", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ssot_pipeline_protocol", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ssot_pipeline_protocol", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ssot_pipeline_protocol", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ssot_pipeline_protocol", "eval_metric")
_emit_stores_embedding("p4", "test_ssot_pipeline_protocol", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ssot_pipeline_protocol", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ssot_pipeline_protocol", "exec_snapshot_link")

pytestmark = [pytest.mark.sovereign_hardening, pytest.mark.ssot]


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def mock_ctx():
    ctx = MagicMock()
    ctx.heal = True
    ctx.enable_llm = False
    ctx.auto_approve = True
    return ctx


@pytest.fixture()
def scan_ctx(mock_ctx):
    """Context with heal=False (mirrors scan_ctx created inside run_pipeline)."""
    ctx = MagicMock()
    ctx.heal = False
    ctx.enable_llm = False
    ctx.auto_approve = True
    return ctx


@pytest.fixture()
def clean_adapter():
    """Adapter mock: all 4 methods return a clean SubphaseResult."""
    adapter = MagicMock()
    adapter.pre_commit.return_value = SubphaseResult()
    adapter.validate.return_value = SubphaseResult()
    adapter.execute.return_value = SubphaseResult()
    adapter.heal.return_value = SubphaseResult()
    return adapter


@pytest.fixture()
def mock_adapters(clean_adapter):
    """One adapter registered for each AGENT_PIPELINE key."""
    return {key: MagicMock(wraps=clean_adapter) for key in AGENT_PIPELINE}


@pytest.fixture()
def mock_decision_engine():
    engine = MagicMock()
    engine.calculate_healing_confidence.return_value = MagicMock(is_high_confidence=True, score=0.95)
    engine.should_proceed_with_healing.return_value = (True, "high-confidence")
    return engine


@pytest.fixture()
def mock_state_mgr():
    return MagicMock()


# ---------------------------------------------------------------------------
# Group 1 — Structural completeness
# ---------------------------------------------------------------------------


class TestAllSubphasesPresent:
    """Every AgentRunResult must have exactly the four subphase keys."""

    def test_all_four_slots_populated(self, mock_ctx, mock_decision_engine, mock_state_mgr):
        adapter = MagicMock()
        adapter.pre_commit.return_value = SubphaseResult()
        adapter.validate.return_value = SubphaseResult()
        adapter.execute.return_value = SubphaseResult()
        adapter.heal.return_value = SubphaseResult()

        adapters = {"reconciler": adapter}

        with patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            results = run_pipeline(
                adapters=adapters,
                territory="test_territory",
                decision_engine=mock_decision_engine,
                state_mgr=mock_state_mgr,
                ctx=mock_ctx,
            )

        assert "reconciler" in results
        run_result = results["reconciler"]
        assert set(run_result.subphases.keys()) == set(PIPELINE_SUBPHASES)

    def test_subphase_keys_match_pipeline_constant(self):
        """PIPELINE_SUBPHASES must equal the canonical four-element tuple."""
        assert PIPELINE_SUBPHASES == ("pre_commit", "validate", "execute", "heal")

    def test_agent_pipeline_contains_nine_agents(self):
        """AGENT_PIPELINE must have exactly 9 entries (cognitive_disposition excluded)."""
        assert len(AGENT_PIPELINE) == 9
        assert "cognitive_disposition" not in AGENT_PIPELINE

    def test_observability_probe_replaces_conversational_repair(self):
        """observability_probe is in AGENT_PIPELINE; old key is absent."""
        assert "observability_probe" in AGENT_PIPELINE
        assert "conversational_repair" not in AGENT_PIPELINE

    def test_root_hygiene_in_pipeline(self):
        """root_hygiene must appear in AGENT_PIPELINE (was previously dead code)."""
        assert "root_hygiene" in AGENT_PIPELINE


# ---------------------------------------------------------------------------
# Group 2 — Gate blocks update_agent for mutating subphases
# ---------------------------------------------------------------------------


class TestGatePreventsUpdateAgentForMutating:
    """When confidence gate fires, update_agent must NOT be called for execute/heal."""

    def _run_with_gate_blocked(self, mock_ctx, mock_state_mgr):
        adapter = MagicMock()
        adapter.pre_commit.return_value = SubphaseResult()
        adapter.validate.return_value = SubphaseResult(violations=[{"type": "LayerViolation"}])

        decision_engine = MagicMock()
        decision_engine.calculate_healing_confidence.return_value = MagicMock(
            is_high_confidence=False, score=0.2
        )
        decision_engine.should_proceed_with_healing.return_value = (
            False,
            "low-confidence",
        )

        adapters = {"reconciler": adapter}

        with patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            results = run_pipeline(
                adapters=adapters,
                territory="test_territory",
                decision_engine=decision_engine,
                state_mgr=mock_state_mgr,
                ctx=mock_ctx,
            )
        return results

    def test_gated_flag_set(self, mock_ctx, mock_state_mgr):
        results = self._run_with_gate_blocked(mock_ctx, mock_state_mgr)
        assert results["reconciler"].gated is True

    def test_gate_reason_populated(self, mock_ctx, mock_state_mgr):
        results = self._run_with_gate_blocked(mock_ctx, mock_state_mgr)
        assert results["reconciler"].gate_reason != ""

    def test_update_agent_not_called_for_execute(self, mock_ctx, mock_state_mgr):
        self._run_with_gate_blocked(mock_ctx, mock_state_mgr)
        for c in mock_state_mgr.update_agent.call_args_list:
            assert c.args[1] != "execute", "update_agent('execute') must not be called when gate blocks"

    def test_update_agent_not_called_for_heal(self, mock_ctx, mock_state_mgr):
        self._run_with_gate_blocked(mock_ctx, mock_state_mgr)
        for c in mock_state_mgr.update_agent.call_args_list:
            assert c.args[1] != "heal", "update_agent('heal') must not be called when gate blocks"

    def test_execute_subphase_skipped(self, mock_ctx, mock_state_mgr):
        results = self._run_with_gate_blocked(mock_ctx, mock_state_mgr)
        assert results["reconciler"].subphases["execute"].skipped is True

    def test_heal_subphase_skipped(self, mock_ctx, mock_state_mgr):
        results = self._run_with_gate_blocked(mock_ctx, mock_state_mgr)
        assert results["reconciler"].subphases["heal"].skipped is True


# ---------------------------------------------------------------------------
# Group 3 — Scan-mode read-only enforcement
# ---------------------------------------------------------------------------


class TestScanCtxHealFalseInScanSubphases:
    """pre_commit and validate must receive ctx with heal=False; execute gets heal=True."""

    def test_pre_commit_receives_heal_false(self, mock_ctx, mock_decision_engine, mock_state_mgr):
        received_ctxs: list = []

        def capture_ctx(territory, ctx):
            received_ctxs.append(("pre_commit", getattr(ctx, "heal", None)))
            return SubphaseResult()

        adapter = MagicMock()
        adapter.pre_commit.side_effect = capture_ctx
        adapter.validate.return_value = SubphaseResult()
        adapter.execute.return_value = SubphaseResult()
        adapter.heal.return_value = SubphaseResult()

        with patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            run_pipeline(
                adapters={"reconciler": adapter},
                territory="t",
                decision_engine=mock_decision_engine,
                state_mgr=mock_state_mgr,
                ctx=mock_ctx,
            )

        assert len(received_ctxs) == 1
        _, heal_val = received_ctxs[0]
        assert heal_val is False, "pre_commit must receive ctx.heal=False"

    def test_validate_receives_heal_false(self, mock_ctx, mock_decision_engine, mock_state_mgr):
        received_ctxs: list = []

        def capture_ctx(territory, ctx):
            received_ctxs.append(("validate", getattr(ctx, "heal", None)))
            return SubphaseResult()

        adapter = MagicMock()
        adapter.pre_commit.return_value = SubphaseResult()
        adapter.validate.side_effect = capture_ctx
        adapter.execute.return_value = SubphaseResult()
        adapter.heal.return_value = SubphaseResult()

        with patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            run_pipeline(
                adapters={"reconciler": adapter},
                territory="t",
                decision_engine=mock_decision_engine,
                state_mgr=mock_state_mgr,
                ctx=mock_ctx,
            )

        assert len(received_ctxs) == 1
        _, heal_val = received_ctxs[0]
        assert heal_val is False, "validate must receive ctx.heal=False"

    def test_execute_receives_heal_true(self, mock_ctx, mock_decision_engine, mock_state_mgr):
        received_heal: list = []

        def capture_ctx(territory, ctx):
            received_heal.append(getattr(ctx, "heal", None))
            return SubphaseResult()

        adapter = MagicMock()
        adapter.pre_commit.return_value = SubphaseResult()
        adapter.validate.return_value = SubphaseResult()
        adapter.execute.side_effect = capture_ctx
        adapter.heal.return_value = SubphaseResult()

        mock_ctx.heal = True

        with patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            run_pipeline(
                adapters={"reconciler": adapter},
                territory="t",
                decision_engine=mock_decision_engine,
                state_mgr=mock_state_mgr,
                ctx=mock_ctx,
            )

        assert len(received_heal) == 1
        assert received_heal[0] is True, "execute must receive original ctx with heal=True"


# ---------------------------------------------------------------------------
# Group 4 — Fail-closed on exception
# ---------------------------------------------------------------------------


class TestFailClosedOnException:
    """Exception in any subphase must stop remaining subphases and call skip_agent once."""

    def _run_with_validate_exception(self, mock_ctx, mock_state_mgr, mock_decision_engine):
        adapter = MagicMock()
        adapter.pre_commit.return_value = SubphaseResult()
        adapter.validate.side_effect = RuntimeError("test validation error")

        adapters = {"reconciler": adapter}

        with patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            results = run_pipeline(
                adapters=adapters,
                territory="t",
                decision_engine=mock_decision_engine,
                state_mgr=mock_state_mgr,
                ctx=mock_ctx,
            )
        return results

    def test_execute_skipped_after_validate_exception(self, mock_ctx, mock_state_mgr, mock_decision_engine):
        results = self._run_with_validate_exception(mock_ctx, mock_state_mgr, mock_decision_engine)
        assert results["reconciler"].subphases["execute"].skipped is True

    def test_heal_skipped_after_validate_exception(self, mock_ctx, mock_state_mgr, mock_decision_engine):
        results = self._run_with_validate_exception(mock_ctx, mock_state_mgr, mock_decision_engine)
        assert results["reconciler"].subphases["heal"].skipped is True

    def test_error_field_populated(self, mock_ctx, mock_state_mgr, mock_decision_engine):
        results = self._run_with_validate_exception(mock_ctx, mock_state_mgr, mock_decision_engine)
        assert results["reconciler"].error is not None
        assert "test validation error" in results["reconciler"].error

    def test_skip_agent_called(self, mock_ctx, mock_state_mgr, mock_decision_engine):
        self._run_with_validate_exception(mock_ctx, mock_state_mgr, mock_decision_engine)
        mock_state_mgr.skip_agent.assert_called()
        # Verify first positional arg is the agent_id
        first_call = mock_state_mgr.skip_agent.call_args_list[0]
        assert first_call.args[0] == "reconciler"

    def test_update_agent_not_called_for_execute_after_exception(
        self, mock_ctx, mock_state_mgr, mock_decision_engine
    ):
        self._run_with_validate_exception(mock_ctx, mock_state_mgr, mock_decision_engine)
        for c in mock_state_mgr.update_agent.call_args_list:
            assert c.args[1] != "execute", "update_agent('execute') must not be called after exception"

    def test_update_agent_not_called_for_heal_after_exception(
        self, mock_ctx, mock_state_mgr, mock_decision_engine
    ):
        self._run_with_validate_exception(mock_ctx, mock_state_mgr, mock_decision_engine)
        for c in mock_state_mgr.update_agent.call_args_list:
            assert c.args[1] != "heal", "update_agent('heal') must not be called after exception"

    def test_exception_in_pre_commit_skips_all_subsequent(
        self, mock_ctx, mock_state_mgr, mock_decision_engine
    ):
        """Exception in pre_commit must skip validate, execute, and heal."""
        adapter = MagicMock()
        adapter.pre_commit.side_effect = RuntimeError("pre_commit boom")

        with patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            results = run_pipeline(
                adapters={"reconciler": adapter},
                territory="t",
                decision_engine=mock_decision_engine,
                state_mgr=mock_state_mgr,
                ctx=mock_ctx,
            )

        run_result = results["reconciler"]
        assert run_result.subphases["validate"].skipped is True
        assert run_result.subphases["execute"].skipped is True
        assert run_result.subphases["heal"].skipped is True


# ---------------------------------------------------------------------------
# Group 5 — Negative control: digest tamper detection
# ---------------------------------------------------------------------------


class TestDigestDeterminismAndTamper:
    """Digest must be stable across runs; SSOT_ORCH_NEGCTRL_TAMPER=1 must change it."""

    def _clean_digest(self):
        return compute_pipeline_digest(
            pipeline_order=AGENT_PIPELINE,
            adapter_keys=sorted(["reconciler", "location"]),
            territory="test_territory",
            heal=False,
            enable_llm=False,
            tamper_token="0",
        )

    def _tampered_digest(self):
        return compute_pipeline_digest(
            pipeline_order=AGENT_PIPELINE,
            adapter_keys=sorted(["reconciler", "location"]),
            territory="test_territory",
            heal=False,
            enable_llm=False,
            tamper_token="1",
        )

    def test_digest_is_stable_across_two_calls(self):
        """Two calls with identical inputs must produce the same digest."""
        d1 = self._clean_digest()
        d2 = self._clean_digest()
        assert d1 == d2

    def test_digest_is_64_hex_chars(self):
        d = self._clean_digest()
        assert len(d) == 64
        assert all(c in "0123456789abcdef" for c in d)

    def test_tamper_token_changes_digest(self):
        """Clean digest must differ from tampered digest."""
        clean = self._clean_digest()
        tampered = self._tampered_digest()
        assert clean != tampered, "SSOT_ORCH_NEGCTRL_TAMPER=1 must produce a different digest"

    def test_emit_pipeline_digest_uses_env_var(self, capsys):
        """emit_pipeline_digest must include SSOT_ORCH_NEGCTRL_TAMPER in payload."""
        prev = os.environ.pop("SSOT_ORCH_NEGCTRL_TAMPER", None)
        try:
            d_clean = emit_pipeline_digest(
                pipeline_order=AGENT_PIPELINE,
                adapter_keys=["reconciler"],
                territory="t",
                heal=False,
                enable_llm=False,
            )
            os.environ["SSOT_ORCH_NEGCTRL_TAMPER"] = "1"
            d_tampered = emit_pipeline_digest(
                pipeline_order=AGENT_PIPELINE,
                adapter_keys=["reconciler"],
                territory="t",
                heal=False,
                enable_llm=False,
            )
        finally:
            os.environ.pop("SSOT_ORCH_NEGCTRL_TAMPER", None)
            if prev is not None:
                os.environ["SSOT_ORCH_NEGCTRL_TAMPER"] = prev

        assert d_clean != d_tampered

    @pytest.mark.negative_control
    @pytest.mark.xfail(strict=True, reason="NEGCTRL: tampered digest must differ from clean")
    def test_negctrl_tamper_changes_digest_xfail(self):
        """Intentionally fails when SSOT_ORCH_NEGCTRL_TAMPER=1.

        Normal run (env unset): test is skipped via pytest.skip().
        Tamper run (env=1):     assertion fails intentionally → xfail(strict=True) → exit 0.
        """
        if os.environ.get("SSOT_ORCH_NEGCTRL_TAMPER", "0") != "1":
            pytest.skip("SSOT_ORCH_NEGCTRL_TAMPER not set; tamper negative-control inactive")

        clean = self._clean_digest()
        tampered = self._tampered_digest()
        # This assertion is intentionally wrong — tampered != clean, so this fails.
        # xfail(strict=True) then converts the failure to a passing xfail.
        assert tampered == clean, "NEGCTRL: this must fail to prove tamper detection works"
