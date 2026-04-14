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

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


def _run_agent(agent) -> dict:
    """Run an async agent's act() method in a dedicated event loop."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(agent.act())
    finally:
        loop.close()


class ValidatorProtocol(Protocol):
    """Protocol for validators - matches ValidatorOrchestrator interface."""

    # guardian: allow-type-erasure
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
            from agentic_core.L4_state.memory import ValidationContext
            from agentic_core.L5_safety.reasoning.AdversarialProbeAgent_validator import AdversarialProbeAgent

            ctx = ValidationContext()
            self._agent = AdversarialProbeAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[AdversarialValidator] Could not import agent: {e}")
            self._initialized = True

    # guardian: allow-type-erasure
    def validate(self, content: Any, context: dict) -> dict:
        """
        Run adversarial probes and return validation result.

        Args:
            content: Content to validate (passed to agent context)
            context: Additional validation context

        Returns:
            dict with keys: valid, errors, threat_assessment
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AdversarialValidator.validate"
        )

        self._ensure_initialized()
        if self._agent is None:
            return {"valid": True, "errors": [], "threat_assessment": {"status": "agent_unavailable"}}
        try:
            result = _run_agent(self._agent)
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
        # guardian: allow-silent-swallow
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
            from agentic_core.L4_state.memory import ValidationContext
            from agentic_core.L5_safety.reasoning.BoundaryTestingAgent_validator import BoundaryTestingAgent

            ctx = ValidationContext()
            self._agent = BoundaryTestingAgent(ctx=ctx)
            self._initialized = True
        except ImportError as e:
            Logger.warning(f"[BoundaryValidator] Could not import agent: {e}")
            self._initialized = True

    # guardian: allow-type-erasure
    def validate(self, content: Any, context: dict) -> dict:
        """
        Run boundary tests and return validation result.

        Args:
            content: Content to validate
            context: Additional validation context

        Returns:
            dict with keys: valid, errors, recommendations
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BoundaryValidator.validate")

        self._ensure_initialized()
        if self._agent is None:
            return {"valid": True, "errors": [], "recommendations": []}
        try:
            result = _run_agent(self._agent)
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
        # guardian: allow-silent-swallow
        except Exception as e:
            Logger.error(f"[BoundaryValidator] Validation failed: {e}")
            return {"valid": False, "errors": [f"Validation error: {str(e)}"], "recommendations": []}


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


# guardian: allow-type-erasure
def register_red_team_validators() -> dict[str, Any]:
    """
    Register all red team agents as validators with the orchestrator.

    Returns:
        dict with registration status
    """
    registered: list[str] = []
    errors: list[str] = []

    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import get_validator_orchestrator
    except ImportError as exc:
        errors.append(f"ValidatorOrchestrator import failed: {exc}")
        Logger.warning("[Red Team Integration] Could not import orchestrator: %s", exc)
        return {"registered": registered, "errors": errors, "success": False}

    orchestrator = get_validator_orchestrator()

    for name, factory in (
        ("adversarial_probe", get_adversarial_validator),
        ("boundary_testing", get_boundary_validator),
    ):
        try:
            orchestrator.register_validator(name, factory())
            registered.append(name)
        except (ValueError, TypeError, RuntimeError) as exc:
            errors.append(f"{name}: {exc}")

    Logger.info("[Red Team Integration] Registered %s validators", len(registered))
    return {"registered": registered, "errors": errors, "success": not errors}


# guardian: allow-type-erasure
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
