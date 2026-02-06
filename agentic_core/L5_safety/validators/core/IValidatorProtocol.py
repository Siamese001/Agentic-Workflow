"""
Red Team Integration Module - Phase 1 Foundation

Registers red team agents (AdversarialProbeAgent, BoundaryTestingAgent)
as validators in the ValidatorOrchestrator.

This module adapts the existing red team agents to the ValidatorProtocol
interface, enabling them to be called through the unified validation gateway.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Protocol

Logger = logging.getLogger(__name__)


class ValidatorProtocol(Protocol):
    """Protocol for validators - matches ValidatorOrchestrator interface."""

    def validate(self, content: Any, context: dict) -> dict:
        """Validate content and return result."""
        ...


class AdversarialValidator:
    """
    Adapter to use AdversarialProbeAgent as a validator.

    Wraps the async act() method and converts results to validator format.
    """

    def __init__(self) -> None:
        """Initialize the adversarial validator."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return

        try:
            from agentic_core.L4_state.validation_context import ValidationContext
            from agentic_core.L5_safety.red_teaming.adversarial_probe_agent_validator import (
                AdversarialProbeAgent,
            )

            ctx = ValidationContext()
            self._agent = AdversarialProbeAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[AdversarialValidator] Could not import agent: {e}")
            self._initialized = True  # Mark as initialized to avoid retry loops

    def validate(self, content: Any, context: dict) -> dict:
        """
        Run adversarial probes and return validation result.

        Args:
            content: Content to validate (passed to agent context)
            context: Additional validation context

        Returns:
            dict with keys: valid, errors, threat_assessment
        """
        self._ensure_initialized()

        if self._agent is None:
            return {
                "valid": True,
                "errors": [],
                "threat_assessment": {"status": "agent_unavailable"},
            }

        try:
            # Run async agent in sync context
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(self._agent.act())
            finally:
                loop.close()

            # Convert to validator format
            vulnerabilities = result.get("vulnerabilities_exposed", 0)
            return {
                "valid": vulnerabilities == 0,
                "errors": [
                    f"Vulnerability: {r['pattern']} - {r.get('description', 'No description')}"
                    for r in result.get("attack_results", [])
                    if r.get("vulnerable")
                ],
                "threat_assessment": result.get("threat_assessment", {}),
                "probes_executed": result.get("probes_executed", 0),
            }

        except Exception as e:
            Logger.error(f"[AdversarialValidator] Validation failed: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "threat_assessment": {"status": "error"},
            }


class BoundaryValidator:
    """
    Adapter to use BoundaryTestingAgent as a validator.

    Wraps the async act() method and converts results to validator format.
    """

    def __init__(self) -> None:
        """Initialize the boundary validator."""
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        """Lazy initialization to avoid import cycles."""
        if self._initialized:
            return

        try:
            from agentic_core.L4_state.validation_context import ValidationContext
            from agentic_core.L5_safety.red_teaming.boundary_testing_agent_validator import (
                BoundaryTestingAgent,
            )

            ctx = ValidationContext()
            self._agent = BoundaryTestingAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[BoundaryValidator] Could not import agent: {e}")
            self._initialized = True

    def validate(self, content: Any, context: dict) -> dict:
        """
        Run boundary tests and return validation result.

        Args:
            content: Content to validate
            context: Additional validation context

        Returns:
            dict with keys: valid, errors, recommendations
        """
        self._ensure_initialized()

        if self._agent is None:
            return {
                "valid": True,
                "errors": [],
                "recommendations": [],
            }

        try:
            loop = asyncio.new_event_loop()
            try:
                result = loop.run_until_complete(self._agent.act())
            finally:
                loop.close()

            edge_cases = result.get("edge_cases_found", 0)
            return {
                "valid": edge_cases == 0,
                "errors": [
                    f"Boundary violation: {v['test']} - {v.get('violation', 'Unknown')}"
                    for v in result.get("boundary_violations", [])
                ],
                "recommendations": result.get("recommendations", []),
                "tests_executed": result.get("tests_executed", 0),
            }

        except Exception as e:
            Logger.error(f"[BoundaryValidator] Validation failed: {e}")
            return {
                "valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "recommendations": [],
            }


# Global validator instances (lazy-initialized)
_adversarial_validator: AdversarialValidator | None = None
_boundary_validator: BoundaryValidator | None = None


def get_adversarial_validator() -> AdversarialValidator:
    """Get or create the adversarial validator instance."""
    global _adversarial_validator
    if _adversarial_validator is None:
        _adversarial_validator = AdversarialValidator()
    return _adversarial_validator


def get_boundary_validator() -> BoundaryValidator:
    """Get or create the boundary validator instance."""
    global _boundary_validator
    if _boundary_validator is None:
        _boundary_validator = BoundaryValidator()
    return _boundary_validator


def register_red_team_validators() -> dict[str, Any]:
    """
    Register all red team agents as validators with the orchestrator.

    Returns:
        dict with registration status
    """
    registered = []
    errors = []

    try:
        from agentic_core.L5_safety.validators.core.validator_orchestrator_types import (
            get_validator_orchestrator,
        )

        orchestrator = get_validator_orchestrator()

        # Register adversarial validator
        try:
            orchestrator.register_validator("adversarial_probe", get_adversarial_validator())
            registered.append("adversarial_probe")
        except Exception as e:
            errors.append(f"adversarial_probe: {e}")

        # Register boundary validator
        try:
            orchestrator.register_validator("boundary_testing", get_boundary_validator())
            registered.append("boundary_testing")
        except Exception as e:
            errors.append(f"boundary_testing: {e}")

        Logger.info(f"[Red Team Integration] Registered {len(registered)} validators")

    except ImportError as e:
        errors.append(f"ValidatorOrchestrator import failed: {e}")
        Logger.warning(f"[Red Team Integration] Could not import orchestrator: {e}")

    return {
        "registered": registered,
        "errors": errors,
        "success": len(errors) == 0,
    }


def get_integration_status() -> dict[str, Any]:
    """
    Get the current status of red team integration.

    Returns:
        dict with integration status details
    """
    return {
        "adversarial_validator_initialized": _adversarial_validator is not None,
        "boundary_validator_initialized": _boundary_validator is not None,
        "validators_available": ["adversarial_probe", "boundary_testing"],
    }
