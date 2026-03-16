"""
Test for FailureSignal import fix in healing_tier_dispatcher.py.

Covers:
- FailureSignal is properly imported and available
- handle_qwen_oom_via_router can construct FailureSignal without NameError
- OOM escalation path works end-to-end
"""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_healing_tier_dispatcher_failure_signal_import")
_emit_applies_guardrail("p0", "test_healing_tier_dispatcher_failure_signal_import", "p0_governance")
_emit_reads_policy_state("p0", "test_healing_tier_dispatcher_failure_signal_import", "policy_binding")
_emit_snapshots_state("p0", "test_healing_tier_dispatcher_failure_signal_import", "state_snapshot")
emit_replay_key("p0", "test_healing_tier_dispatcher_failure_signal_import")
emit_determinism_digest("p0", "test_healing_tier_dispatcher_failure_signal_import")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


class TestFailureSignalImport:
    """Test that FailureSignal is properly imported in healing_tier_dispatcher."""

    def test_failure_signal_imported_in_module(self):
        """FailureSignal should be imported at module level in healing_tier_dispatcher."""
        from agentic_core.L2_execution.healers import healing_tier_dispatcher

        # Should be able to access FailureSignal from the module
        assert hasattr(healing_tier_dispatcher, "FailureSignal")

        # Should be the correct type from healing_tier_types
        from agentic_core.L2_execution.healers.healing_tier_types import FailureSignal as ExpectedType

        assert healing_tier_dispatcher.FailureSignal is ExpectedType

    def test_handle_qwen_oom_via_router_function_exists_and_references_failure_signal(self):
        """handle_qwen_oom_via_router should reference FailureSignal in its implementation."""
        import inspect

        from agentic_core.L2_execution.healers.healing_tier_dispatcher import handle_qwen_oom_via_router

        # Get the source code of the function
        source = inspect.getsource(handle_qwen_oom_via_router)

        # Should reference FailureSignal (the bug was it wasn't imported)
        assert "FailureSignal" in source
        assert "failure_signal =" in source or "FailureSignal(" in source

    def test_oom_handler_uses_route_healing_tier(self):
        """OOM handler should call route_healing_tier (the single choke point)."""
        import inspect

        from agentic_core.L2_execution.healers.healing_tier_dispatcher import handle_qwen_oom_via_router

        # Get the source code
        source = inspect.getsource(handle_qwen_oom_via_router)

        # Should call route_healing_tier (the single choke point)
        assert "route_healing_tier" in source


class TestOOMEscalationPath:
    """Test the full OOM escalation workflow."""

    def test_oom_escalation_routes_through_single_choke_point(self):
        """OOM escalation should route through route_healing_tier (single choke point)."""
        from unittest.mock import patch

        from agentic_core.L2_execution.healers.healing_tier_config import HealingTierConfig
        from agentic_core.L2_execution.healers.healing_tier_dispatcher import handle_qwen_oom_via_router
        from agentic_core.L2_execution.healers.healing_tier_types import (
            HealingDecision,
            HealingInput,
            HealingTier,
        )

        config = HealingTierConfig()

        healing_input = HealingInput(
            failure_type="test_failure",
            error_signature="test_sig",
            trace_id="test_trace",
            retry_count=0,
            blast_radius_estimate=0.1,
            required_tools=(),
            violation_metadata_refs=(),
            agent_id="test_agent",
        )

        # Mock route_healing_tier to verify it's called
        mock_decision = HealingDecision(
            heal_confidence=0.5,
            tier=HealingTier.GEMINI_2_5_PRO,
            reason_codes=("oom_escalation",),
        )

        with patch(
            "agentic_core.L2_execution.healers.healing_tier_dispatcher.route_healing_tier",
            return_value=mock_decision,
        ) as mock_route:
            decision = handle_qwen_oom_via_router(healing_input, config)

            # Should have called route_healing_tier (the single choke point)
            assert mock_route.called
            # Should return the decision from the router
            assert decision is mock_decision


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
