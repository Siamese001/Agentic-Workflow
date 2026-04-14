"""Behavioral tests for IValidatorProtocol.py (phase: centralized async, ImportError handling)."""

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest


@pytest.mark.unit
class TestAdversarialValidator:
    # --- happy path ---

    def test_validate_agent_run_succeeds_no_vulnerabilities(self):
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        validator = AdversarialValidator()
        validator._initialized = True
        validator._agent = MagicMock()
        run_result = {
            "vulnerabilities_exposed": 0,
            "attack_results": [],
            "threat_assessment": {"status": "clean"},
            "probes_executed": 3,
        }
        with (
            patch("agentic_core.interfaces.IValidatorProtocol._emit_records_execution_trace"),
            patch("agentic_core.interfaces.IValidatorProtocol._run_agent", return_value=run_result),
        ):
            result = validator.validate("test content", {})
        assert result["valid"] is True
        assert result["errors"] == []

    # --- failure path ---

    def test_validate_agent_unavailable_returns_stub(self):
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        validator = AdversarialValidator()
        validator._initialized = True
        validator._agent = None  # simulates import failure at init
        with patch("agentic_core.interfaces.IValidatorProtocol._emit_records_execution_trace"):
            result = validator.validate("test content", {})
        assert result["valid"] is True
        assert result["threat_assessment"]["status"] == "agent_unavailable"

    def test_validate_agent_run_exception_returns_error(self):
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        validator = AdversarialValidator()
        validator._initialized = True
        validator._agent = MagicMock()
        with (
            patch("agentic_core.interfaces.IValidatorProtocol._emit_records_execution_trace"),
            patch(
                "agentic_core.interfaces.IValidatorProtocol._run_agent",
                side_effect=RuntimeError("agent crash"),
            ),
        ):
            result = validator.validate("test content", {})
        assert result["valid"] is False
        assert any("agent crash" in e for e in result["errors"])

    # --- edge case ---

    def test_validate_agent_unavailable_errors_list_empty(self):
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        validator = AdversarialValidator()
        validator._initialized = True
        validator._agent = None
        with patch("agentic_core.interfaces.IValidatorProtocol._emit_records_execution_trace"):
            result = validator.validate("", {})
        assert result["errors"] == []

    def test_ensure_initialized_import_error_sets_initialized_and_agent_none(self):
        """G4: ImportError during _ensure_initialized sets _initialized=True and _agent=None."""
        import sys
        from agentic_core.interfaces.IValidatorProtocol import AdversarialValidator

        validator = AdversarialValidator()
        assert validator._initialized is False
        assert validator._agent is None

        key = "agentic_core.L4_state.memory"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = None  # blocks import → ImportError branch
            validator._ensure_initialized()
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)

        assert validator._initialized is True
        assert validator._agent is None


@pytest.mark.unit
class TestBoundaryValidator:
    # --- happy path ---

    def test_validate_agent_unavailable_returns_valid_true(self):
        from agentic_core.interfaces.IValidatorProtocol import BoundaryValidator

        validator = BoundaryValidator()
        validator._initialized = True
        validator._agent = None
        with patch("agentic_core.interfaces.IValidatorProtocol._emit_records_execution_trace"):
            result = validator.validate("content", {})
        assert result["valid"] is True
        assert result["errors"] == []
        assert result["recommendations"] == []

    # --- failure path ---

    def test_validate_agent_run_exception_returns_error(self):
        from agentic_core.interfaces.IValidatorProtocol import BoundaryValidator

        validator = BoundaryValidator()
        validator._initialized = True
        validator._agent = MagicMock()
        with (
            patch("agentic_core.interfaces.IValidatorProtocol._emit_records_execution_trace"),
            patch(
                "agentic_core.interfaces.IValidatorProtocol._run_agent",
                side_effect=ValueError("boundary crash"),
            ),
        ):
            result = validator.validate("content", {})
        assert result["valid"] is False

    # --- edge case: ensures _ensure_initialized guards repeated calls ---

    def test_ensure_initialized_idempotent(self):
        from agentic_core.interfaces.IValidatorProtocol import BoundaryValidator

        validator = BoundaryValidator()
        validator._initialized = True
        validator._agent = None
        validator._ensure_initialized()  # second call should be a no-op
        assert validator._initialized is True


@pytest.mark.unit
class TestRegisterRedTeamValidators:
    # --- failure path ---

    def test_orchestrator_import_error_returns_failure(self):
        from agentic_core.interfaces.IValidatorProtocol import register_red_team_validators

        key = "agentic_core.L5_safety.types.healing_orchestration_types"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = None  # blocks import
            result = register_red_team_validators()
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert result["success"] is False
        assert len(result["errors"]) > 0
        assert result["registered"] == []

    # --- edge case ---

    def test_success_field_false_when_errors_present(self):
        from agentic_core.interfaces.IValidatorProtocol import register_red_team_validators

        key = "agentic_core.L5_safety.types.healing_orchestration_types"
        saved = sys.modules.pop(key, None)
        try:
            sys.modules[key] = None
            result = register_red_team_validators()
        finally:
            if saved is not None:
                sys.modules[key] = saved
            else:
                sys.modules.pop(key, None)
        assert result["success"] is not True


@pytest.mark.unit
class TestGetIntegrationStatusValidator:
    # --- happy path ---

    def test_returns_expected_keys(self):
        from agentic_core.interfaces.IValidatorProtocol import get_integration_status

        status = get_integration_status()
        assert "adversarial_validator_initialized" in status
        assert "boundary_validator_initialized" in status
        assert "validators_available" in status

    # --- edge case ---

    def test_validators_available_contains_named_entries(self):
        from agentic_core.interfaces.IValidatorProtocol import get_integration_status

        status = get_integration_status()
        assert "adversarial_probe" in status["validators_available"]
        assert "boundary_testing" in status["validators_available"]
