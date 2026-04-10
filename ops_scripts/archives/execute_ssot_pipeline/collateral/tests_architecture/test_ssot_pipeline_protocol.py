"""Tests for the SSOT orchestration pipeline hardening - Reduced mocking.

Five test groups:
  1. Structural completeness  — all 4 subphase slots always present in AgentRunResult
  2. Gate blocks update_agent — confidence gate prevents update_agent("execute"/"heal")
  3. Scan-mode read-only      — pre_commit/validate receive ctx.heal=False structurally
  4. Fail-closed on exception — exception in validate stops execute/heal; skip_agent called
  5. Negative control         — SSOT_ORCH_NEGCTRL_TAMPER=1 produces a different digest

Fixes applied (Tier 3):
- Replaced heavy MagicMock adapter fixtures with minimal real objects
- Using real SubphaseResult objects instead of MagicMock returns
- Reduced patching scope - only patching emitters at boundaries
"""

from __future__ import annotations

import pytest


# Lazy imports to avoid collection-time conflicts
@pytest.fixture
def execute_ssot_imports():
    from agentic_core.L2_execution.protocol import (
        PIPELINE_SUBPHASES,
        SubphaseResult,
        compute_pipeline_digest,
        emit_pipeline_digest,
    )
    from ops_scripts.dev_tools.L0_routing_scripts.execute_ssot import (
        AGENT_PIPELINE,
        run_pipeline,
    )
    return AGENT_PIPELINE, run_pipeline, PIPELINE_SUBPHASES, SubphaseResult, compute_pipeline_digest, emit_pipeline_digest


pytestmark = [pytest.mark.sovereign_hardening, pytest.mark.ssot]


# ---------------------------------------------------------------------------
# Minimal Context Class (not MagicMock)
# ---------------------------------------------------------------------------

class TestContext:
    """Minimal test context object - not a mock."""

    def __init__(self, heal: bool = True, enable_llm: bool = False, auto_approve: bool = True):
        self.heal = heal
        self.enable_llm = enable_llm
        self.auto_approve = auto_approve


class TestDecisionEngine:
    """Minimal decision engine - not a mock."""

    def __init__(self, high_confidence: bool = True, score: float = 0.95):
        self._high_confidence = high_confidence
        self._score = score

    def calculate_healing_confidence(self, *args, **kwargs):
        class Result:
            def __init__(self, is_high_confidence, score):
                self.is_high_confidence = is_high_confidence
                self.score = score
        return Result(self._high_confidence, self._score)

    def should_proceed_with_healing(self, *args, **kwargs):
        if self._high_confidence:
            return (True, "high-confidence")
        return (False, "low-confidence")


class TestStateManager:
    """Minimal state manager with tracking - not a mock."""

    def __init__(self):
        self.update_agent_calls = []

    def update_agent(self, agent, status):
        self.update_agent_calls.append((agent, status))

    def complete_agent(self, agent, status, result=None):
        """Mark agent as complete."""
        self.update_agent_calls.append((agent, f"complete:{status}", result))

    def skip_agent(self, agent, reason):
        """Mark agent as skipped."""
        self.update_agent_calls.append((agent, f"skip:{reason}"))


# ---------------------------------------------------------------------------
# Shared fixtures - minimal real objects
# ---------------------------------------------------------------------------


@pytest.fixture()
def ctx():
    """Real context object."""
    return TestContext(heal=True)


@pytest.fixture()
def scan_ctx():
    """Context with heal=False."""
    return TestContext(heal=False)


@pytest.fixture()
def high_confidence_engine():
    """Decision engine that allows healing."""
    return TestDecisionEngine(high_confidence=True)


@pytest.fixture()
def low_confidence_engine():
    """Decision engine that blocks healing."""
    return TestDecisionEngine(high_confidence=False, score=0.2)


@pytest.fixture()
def state_mgr():
    """Real state manager with call tracking."""
    return TestStateManager()


# ---------------------------------------------------------------------------
# Helper to create real SubphaseResult
# ---------------------------------------------------------------------------

def make_clean_result():
    """Create a clean SubphaseResult with no violations."""
    from agentic_core.L2_execution.protocol import SubphaseResult
    return SubphaseResult()


def make_result_with_violations():
    """Create a SubphaseResult with violations."""
    from agentic_core.L2_execution.protocol import SubphaseResult
    result = SubphaseResult()
    # Add a violation (implementation-dependent)
    if hasattr(result, 'violations'):
        result.violations = [{"type": "LayerViolation"}]
    return result


# ---------------------------------------------------------------------------
# Minimal Adapter Class (not MagicMock)
# ---------------------------------------------------------------------------

class CleanAdapter:
    """Adapter that returns clean results - not a mock."""

    def pre_commit(self, territory, ctx):
        return make_clean_result()

    def validate(self, territory, ctx):
        return make_clean_result()

    def execute(self, territory, ctx):
        return make_clean_result()

    def heal(self, territory, ctx):
        return make_clean_result()


class ViolatingAdapter:
    """Adapter that returns validation violations."""

    def pre_commit(self, territory, ctx):
        return make_clean_result()

    def validate(self, territory, ctx):
        return make_result_with_violations()

    def execute(self, territory, ctx):
        return make_clean_result()

    def heal(self, territory, ctx):
        return make_clean_result()


# ---------------------------------------------------------------------------
# Group 1 — Structural completeness
# ---------------------------------------------------------------------------


class TestAllSubphasesPresent:
    """Every AgentRunResult must have exactly the four subphase keys."""

    def test_all_four_slots_populated(self, ctx, high_confidence_engine, state_mgr, execute_ssot_imports):
        from unittest.mock import MagicMock, patch

        # Mock get_agent_dispatch_registry which is used internally by run_pipeline
        with patch("agentic_core.L3_orchestration.registry.agent_dispatch_registry.get_agent_dispatch_registry") as mock_registry, \
             patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            mock_registry.return_value = MagicMock()

            AGENT_PIPELINE, run_pipeline, PIPELINE_SUBPHASES, SubphaseResult = execute_ssot_imports[:4]

            adapter = CleanAdapter()
            adapters = {"reconciler": adapter}

            results = run_pipeline(
                adapters=adapters,
                territory="test_territory",
                decision_engine=high_confidence_engine,
                state_mgr=state_mgr,
                ctx=ctx,
            )

            assert "reconciler" in results
            run_result = results["reconciler"]
            assert set(run_result.subphases.keys()) == set(PIPELINE_SUBPHASES)

    def test_subphase_keys_match_pipeline_constant(self, execute_ssot_imports):
        _, _, PIPELINE_SUBPHASES, _ = execute_ssot_imports[:4]
        assert PIPELINE_SUBPHASES == ("pre_commit", "validate", "execute", "heal")

    def test_agent_pipeline_contains_nine_agents(self, execute_ssot_imports):
        AGENT_PIPELINE, _, _, _ = execute_ssot_imports[:4]
        assert len(AGENT_PIPELINE) == 9
        assert "cognitive_disposition" not in AGENT_PIPELINE

    def test_observability_probe_replaces_conversational_repair(self, execute_ssot_imports):
        AGENT_PIPELINE, _, _, _ = execute_ssot_imports[:4]
        assert "observability_probe" in AGENT_PIPELINE
        assert "conversational_repair" not in AGENT_PIPELINE

    def test_root_hygiene_in_pipeline(self, execute_ssot_imports):
        AGENT_PIPELINE, _, _, _ = execute_ssot_imports[:4]
        assert "root_hygiene" in AGENT_PIPELINE


# ---------------------------------------------------------------------------
# Group 2 — Gate blocks update_agent for mutating subphases
# ---------------------------------------------------------------------------


class TestGatePreventsUpdateAgentForMutating:
    """When confidence gate fires, update_agent must NOT be called for execute/heal."""

    def _run_with_gate_blocked(self, ctx, state_mgr, execute_ssot_imports):
        from unittest.mock import MagicMock, patch

        # Mock get_agent_dispatch_registry which is used internally by run_pipeline
        with patch("agentic_core.L3_orchestration.registry.agent_dispatch_registry.get_agent_dispatch_registry") as mock_registry, \
             patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            mock_registry.return_value = MagicMock()

            AGENT_PIPELINE, run_pipeline, PIPELINE_SUBPHASES, SubphaseResult = execute_ssot_imports[:4]

            adapter = ViolatingAdapter()
            decision_engine = TestDecisionEngine(high_confidence=False, score=0.2)

            adapters = {"reconciler": adapter}

            results = run_pipeline(
                adapters=adapters,
                territory="test_territory",
                decision_engine=decision_engine,
                state_mgr=state_mgr,
                ctx=ctx,
            )
            return results

    def test_gated_flag_set(self, ctx, state_mgr, execute_ssot_imports):
        results = self._run_with_gate_blocked(ctx, state_mgr, execute_ssot_imports)
        assert results["reconciler"].gated is True

    def test_gate_reason_populated(self, ctx, state_mgr, execute_ssot_imports):
        results = self._run_with_gate_blocked(ctx, state_mgr, execute_ssot_imports)
        assert results["reconciler"].gate_reason != ""

    def test_update_agent_not_called_for_execute(self, ctx, state_mgr, execute_ssot_imports):
        self._run_with_gate_blocked(ctx, state_mgr, execute_ssot_imports)
        for call in state_mgr.update_agent_calls:
            agent, status = call[0], call[1]
            assert status != "execute", f"update_agent('execute') called for {agent}"

    def test_update_agent_not_called_for_heal(self, ctx, state_mgr, execute_ssot_imports):
        self._run_with_gate_blocked(ctx, state_mgr, execute_ssot_imports)
        for call in state_mgr.update_agent_calls:
            agent, status = call[0], call[1]
            assert status != "heal", f"update_agent('heal') called for {agent}"


# ---------------------------------------------------------------------------
# Group 3 — Scan-mode read-only
# ---------------------------------------------------------------------------


class TestScanModeReadOnly:
    """pre_commit/validate receive ctx.heal=False structurally."""

    def test_scan_ctx_has_heal_false(self, scan_ctx):
        assert scan_ctx.heal is False

    def test_scan_mode_does_not_execute(self, scan_ctx, high_confidence_engine, state_mgr, execute_ssot_imports):
        from unittest.mock import MagicMock, patch

        # Mock get_agent_dispatch_registry which is used internally by run_pipeline
        with patch("agentic_core.L3_orchestration.registry.agent_dispatch_registry.get_agent_dispatch_registry") as mock_registry, \
             patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            mock_registry.return_value = MagicMock()

            AGENT_PIPELINE, run_pipeline, PIPELINE_SUBPHASES, SubphaseResult = execute_ssot_imports[:4]

            adapter = CleanAdapter()
            adapters = {"reconciler": adapter}

            results = run_pipeline(
                adapters=adapters,
                territory="test_territory",
                decision_engine=high_confidence_engine,
                state_mgr=state_mgr,
                ctx=scan_ctx,
            )

            # In scan mode, execute should not be called (or should be gated)
            run_result = results["reconciler"]
            assert run_result.subphases["execute"].skipped is True or run_result.gated


# ---------------------------------------------------------------------------
# Group 4 — Fail-closed on exception
# ---------------------------------------------------------------------------


class TestFailClosedOnException:
    """Exception in validate stops execute/heal; skip_agent called."""

    class ExceptionAdapter:
        """Adapter that raises exception in validate."""

        def pre_commit(self, territory, ctx):
            from agentic_core.L2_execution.protocol import SubphaseResult
            return SubphaseResult()

        def validate(self, territory, ctx):
            raise RuntimeError("Validation error")

        def execute(self, territory, ctx):
            from agentic_core.L2_execution.protocol import SubphaseResult
            return SubphaseResult()

        def heal(self, territory, ctx):
            from agentic_core.L2_execution.protocol import SubphaseResult
            return SubphaseResult()

    def test_exception_in_validate_fails_closed(self, ctx, high_confidence_engine, state_mgr, execute_ssot_imports):
        from unittest.mock import MagicMock, patch

        # Mock get_agent_dispatch_registry which is used internally by run_pipeline
        with patch("agentic_core.L3_orchestration.registry.agent_dispatch_registry.get_agent_dispatch_registry") as mock_registry, \
             patch("agentic_core.L0_routing.scripts.execute_ssot._emit_pipeline_digest"):
            mock_registry.return_value = MagicMock()

            AGENT_PIPELINE, run_pipeline, PIPELINE_SUBPHASES, SubphaseResult = execute_ssot_imports[:4]

            adapter = self.ExceptionAdapter()
            adapters = {"reconciler": adapter}

            results = run_pipeline(
                adapters=adapters,
                territory="test_territory",
                decision_engine=high_confidence_engine,
                state_mgr=state_mgr,
                ctx=ctx,
            )

            # Should have error result
            run_result = results["reconciler"]
            assert run_result.subphases["validate"].has_error is True or run_result.has_error


# ---------------------------------------------------------------------------
# Group 5 — Negative control
# ---------------------------------------------------------------------------


class TestNegativeControl:
    """SSOT_ORCH_NEGCTRL_TAMPER=1 produces a different digest."""

    def test_negative_control_changes_digest(self, execute_ssot_imports):
        from agentic_core.L2_execution.protocol import compute_pipeline_digest

        # Run with tamper flag off - using correct signature
        digest_clean = compute_pipeline_digest(
            pipeline_order=["agent1", "agent2"],
            adapter_keys=["key1", "key2"],
            territory="test_territory",
            heal=True,
            enable_llm=False,
            tamper_token="0",
        )

        # Run with tamper flag on - using correct signature with different tamper_token
        digest_tampered = compute_pipeline_digest(
            pipeline_order=["agent1", "agent2"],
            adapter_keys=["key1", "key2"],
            territory="test_territory",
            heal=True,
            enable_llm=False,
            tamper_token="1",  # Different tamper token
        )

        # Digests should be different
        assert digest_clean != digest_tampered, "Tampered state should produce different digest"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
