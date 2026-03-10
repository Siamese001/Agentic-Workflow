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
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENT_PIPELINE,
    run_pipeline,
)
from agentic_core.L2_execution.protocol import (
    PIPELINE_SUBPHASES,
    SubphaseResult,
    compute_pipeline_digest,
    emit_pipeline_digest,
)

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
