"""
Test for remediation_dispatcher exception handling fix.

Covers:
- Healer exceptions are caught and converted to HealCheckResult with FAILED status
- No dead/unreachable code after raise (result is properly constructed)
- LLM escalation is triggered when needs_llm_escalation=True
"""

from unittest.mock import patch

import pytest


class TestHealerExceptionHandling:
    """Test that healer exceptions are properly caught and converted to FAILED results."""

    def test_healer_exception_caught_and_converted_to_failed_result(self):
        """When healer raises exception, should catch it and return HealCheckResult with FAILED status."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import (
            HealCheckResult,
            HealStatus,
            _invoke_healer,
        )

        # Mock a healer that raises an exception
        def failing_healer(check_dict, repo_root=None, apply=False):
            raise ValueError("Healer internal error")

        check_id = "test_check"
        check_dict = {"check_id": check_id, "violations": []}
        repo_root = "/fake/repo"

        # Mock the HEALER_REGISTRY
        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {check_id: failing_healer},
        ):
            result = _invoke_healer(
                check_id=check_id,
                check_dict=check_dict,
                repo_root=repo_root,
                apply=False,
                retry_count=0,
                tier_invoker=None,
            )

            # Should return a HealCheckResult with FAILED status
            assert isinstance(result, HealCheckResult)
            assert result.status == HealStatus.FAILED
            assert "ValueError" in result.notes
            assert "Healer internal error" in result.notes
            assert result.needs_llm_escalation is True
            assert result.escalation_hint == "failure_type=healer_error"

    def test_healer_exception_triggers_llm_escalation_when_in_allowlist(self):
        """When healer raises exception and check_id is in allowlist, should trigger LLM escalation."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import (
            _invoke_healer,
        )

        def failing_healer(check_dict, repo_root=None, apply=False):
            raise RuntimeError("Healer crashed")

        check_id = "test_check_in_allowlist"
        check_dict = {"check_id": check_id, "violations": []}

        # Mock both HEALER_REGISTRY and HEALER_ESCALATION_ALLOWLIST
        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {check_id: failing_healer},
        ):
            with patch(
                "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_ESCALATION_ALLOWLIST",
                frozenset([check_id]),
            ):
                # Mock _tier_escalate to verify it's called
                with patch(
                    "agentic_core.L2_execution.scripts.remediation_dispatcher._tier_escalate",
                    return_value="escalation_note",
                ) as mock_escalate:
                    result = _invoke_healer(
                        check_id=check_id,
                        check_dict=check_dict,
                        repo_root="/fake/repo",
                        apply=False,
                        retry_count=0,
                        tier_invoker=None,
                    )

                    # Should have called _tier_escalate
                    assert mock_escalate.called
                    # Result should include escalation note
                    assert "escalation_note" in result.notes

    def test_healer_success_does_not_trigger_exception_path(self):
        """When healer succeeds, should return its result without exception handling."""
        from agentic_core.L2_execution.scripts.remediation_dispatcher import (
            HealCheckResult,
            HealStatus,
            _invoke_healer,
        )

        def successful_healer(check_dict, repo_root=None, apply=False):
            return HealCheckResult(
                check_id="test_check",
                status=HealStatus.HEALED,
                changes_made=("fixed_file.py",),
                rollback_info=None,
                notes="All good",
                needs_llm_escalation=False,
                escalation_hint=None,
            )

        check_id = "test_check"
        check_dict = {"check_id": check_id, "violations": []}

        with patch(
            "agentic_core.L2_execution.scripts.remediation_dispatcher.HEALER_REGISTRY",
            {check_id: successful_healer},
        ):
            result = _invoke_healer(
                check_id=check_id,
                check_dict=check_dict,
                repo_root="/fake/repo",
                apply=False,
                retry_count=0,
                tier_invoker=None,
            )

            # Should return the healer's success result unchanged
            assert result.status == HealStatus.HEALED
            assert result.notes == "All good"
            assert result.needs_llm_escalation is False


class TestNoDeadCodeAfterRaise:
    """Verify that the dead code after raise has been removed."""

    def test_exception_handler_constructs_result_not_unreachable_code(self):
        """The except block should construct HealCheckResult, not have dead code after raise."""
        import inspect

        from agentic_core.L2_execution.scripts.remediation_dispatcher import _invoke_healer

        # Get the source code of the function
        source = inspect.getsource(_invoke_healer)

        # The fixed version should NOT have "raise  # Re-raise after logging/handling"
        # followed by unreachable result construction
        assert "raise  # Re-raise after logging/handling" not in source

        # Should have proper exception handling that constructs result
        assert "except Exception as exc:" in source
        assert "result = HealCheckResult(" in source


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
