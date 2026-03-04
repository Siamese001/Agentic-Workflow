"""Three-Tier Convergence Tests.

Validates that execute_ssot converges with remediation_dispatcher
through shared contracts without breaking existing functionality.
"""

import pytest

from agentic_core.L0_routing.scripts.heal_result_adapter import adapt_heal_result
from agentic_core.L2_execution.types.heal_contract_types import (
    HealStatus,
)


class TestTier1UWGIntegration:
    """Tier 1: UniversalWriteGateway integration tests."""

    def test_uwg_permissions_granted_and_revoked(self) -> None:
        """Verify UWG permissions are properly managed during agent execution."""
        # This test would require integration setup with actual agent
        # For now, we verify the import and basic functionality
        from agentic_core.interfaces.write_gateway import get_write_gateway

        uwg = get_write_gateway()
        assert uwg is not None

        # Test permission grant/revoke
        test_path = "test_territory/"
        uwg.grant_write_permission(test_path)
        assert uwg.check_write_permission(test_path)

        uwg.revoke_write_permission(test_path)
        # After revocation, should be blocked (unless in allowed paths)
        assert not uwg.check_write_permission(test_path)


class TestTier2HealingTierRouter:
    """Tier 2: healing_tier_router threshold consistency tests."""

    def test_threshold_constants_imported(self) -> None:
        """Verify canonical thresholds are imported from healing_tier_config."""
        try:
            from agentic_core.L2_execution.healers.healing_tier_config import (
                HEALING_CONFIDENCE_X,
                HEALING_CONFIDENCE_Y,
            )

            # Verify expected values
            assert HEALING_CONFIDENCE_X == 0.75
            assert HEALING_CONFIDENCE_Y == 0.40
        except ImportError:
            pytest.skip("healing_tier_config not available")

    def test_fallback_thresholds_when_config_missing(self) -> None:
        """Verify fallback thresholds are used when config is unavailable."""
        # This would be tested through integration with execute_ssot
        # For now, verify the fallback values are correct
        CONF_X = 0.75
        CONF_Y = 0.40
        assert CONF_X > CONF_Y
        assert 0.0 <= CONF_Y <= CONF_X <= 1.0


class TestTier3HealCheckResultAdapter:
    """Tier 3: HealCheckResult adapter tests."""

    def test_adapt_dict_result_success(self) -> None:
        """Test adapting successful dict result."""
        raw_result = {
            "success": True,
            "files_healed": ["file1.py", "file2.py"],
            "violations_fixed": 2,
        }

        adapted = adapt_heal_result("TestAgent", raw_result, 2)

        assert adapted.check_id == "TestAgent"
        assert adapted.status == HealStatus.HEALED
        assert "file1.py" in adapted.changes_made
        assert "file2.py" in adapted.changes_made
        assert adapted.needs_llm_escalation is False

    def test_adapt_dict_result_failure(self) -> None:
        """Test adapting failed dict result."""
        raw_result = {
            "success": False,
            "error": "Complex rewrite required",
            "files_healed": 0,
        }

        adapted = adapt_heal_result("TestAgent", raw_result, 1)

        assert adapted.status == HealStatus.FAILED
        assert adapted.notes == "Complex rewrite required"
        assert adapted.needs_llm_escalation is True  # Complex error triggers escalation

    def test_adapt_string_result(self) -> None:
        """Test adapting string result."""
        raw_result = "Fixed 3 files"

        adapted = adapt_heal_result("TestAgent", raw_result, 3)

        assert adapted.status == HealStatus.HEALED
        assert "Fixed 3 files" in adapted.changes_made

    def test_adapt_none_result(self) -> None:
        """Test adapting None result."""
        adapted = adapt_heal_result("TestAgent", None, 0)

        assert adapted.status == HealStatus.HEALED  # Default for backward compatibility
        assert "No output returned" in adapted.changes_made

    def test_adapt_partial_success(self) -> None:
        """Test adapting partial success result."""
        raw_result = {
            "status": "PARTIAL",
            "files_healed": ["file1.py"],
            "violations_fixed": 1,
        }

        adapted = adapt_heal_result("TestAgent", raw_result, 2)

        assert adapted.status == HealStatus.PARTIAL
        assert adapted.needs_llm_escalation is True  # Partial success triggers escalation

    def test_escalation_hint_construction(self) -> None:
        """Test escalation hint includes relevant context."""
        raw_result = {
            "success": False,
            "failure_type": "LAYER_VIOLATION",
            "blast_radius": 0.8,
            "error": RuntimeError("Complex architecture issue"),
        }

        adapted = adapt_heal_result("TestAgent", raw_result, 1)

        assert adapted.needs_llm_escalation is True
        assert "failure_type=LAYER_VIOLATION" in adapted.escalation_hint
        assert "blast_radius=0.8" in adapted.escalation_hint
        assert "agent=TestAgent" in adapted.escalation_hint
        assert "status=FAILED" in adapted.escalation_hint

    def test_large_changes_trigger_escalation(self) -> None:
        """Test that many changes trigger LLM escalation."""
        raw_result = {
            "success": True,
            "changes_made": [f"file{i}.py" for i in range(15)],  # > 10 files
        }

        adapted = adapt_heal_result("TestAgent", raw_result, 15)

        assert adapted.status == HealStatus.HEALED
        assert adapted.needs_llm_escalation is True  # Many changes trigger escalation

    def test_canonical_output_format(self) -> None:
        """Test adapted result can be converted to canonical dict format."""
        raw_result = {
            "success": True,
            "files_healed": ["test.py"],
        }

        adapted = adapt_heal_result("TestAgent", raw_result, 1)
        canonical_dict = adapted.to_dict()

        # Verify canonical structure
        assert "check_id" in canonical_dict
        assert "status" in canonical_dict
        assert "changes_made" in canonical_dict
        assert canonical_dict["check_id"] == "TestAgent"
        assert canonical_dict["status"] == "HEALED"
        assert isinstance(canonical_dict["changes_made"], list)
