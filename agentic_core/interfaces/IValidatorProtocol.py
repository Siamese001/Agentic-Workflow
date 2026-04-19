"""
Red Team Integration Module - Phase 1 Foundation.

Registers red team agents as validators in the ValidatorOrchestrator.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Protocol

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

Logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    """Structured result from a validation scan."""

    total_violations: int
    compliance_score: float
    violations: list
    scan_duration: float
    is_compliant: bool

    def to_markdown(self) -> str:
        status = "COMPLIANT" if self.is_compliant else "NON-COMPLIANT"
        lines = [
            "# Validation Report",
            f"**Status**: {status}",
            f"**Compliance Score**: {self.compliance_score}%",
            f"**Scan Duration**: {self.scan_duration:.2f}s",
        ]
        if self.violations:
            lines.append(f"**Violations**: {len(self.violations)} violations")
        return "\n".join(lines)


def _run_agent(agent) -> dict[str, Any]:
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(agent.act())
    finally:
        loop.close()


class ValidatorProtocol(Protocol):
    """Protocol for validators."""

    def validate(self, content: Any, context: dict[str, Any]) -> dict[str, Any]: ...


class AdversarialValidator:
    def __init__(self) -> None:
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        try:
            from agentic_core.L4_state.memory import ValidationContext
            from agentic_core.L5_safety.reasoning.AdversarialProbeAgent_validator import AdversarialProbeAgent
        except ImportError as exc:  # guardian: allow-log-and-swallow allow-return-none-swallow -- adversarial probe agent optional: logged and skipped, validator runs in degraded mode
            Logger.warning("[AdversarialValidator] Could not import agent: %s", exc)
            self._initialized = True
            return

        self._agent = AdversarialProbeAgent(ctx=ValidationContext())
        self._initialized = True

    def validate(self, content: Any, context: dict[str, Any]) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(_uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "AdversarialValidator.validate",
        )

        self._ensure_initialized()
        if self._agent is None:
            return {"valid": True, "errors": [], "threat_assessment": {"status": "agent_unavailable"}}

        try:
            result = _run_agent(self._agent)
        except Exception as exc:  # guardian: allow-broad-exception -- _run_agent wraps arbitrary async agent code that may raise any exception type
            Logger.error("[AdversarialValidator] Validation failed: %s", exc)
            return {
                "valid": False,
                "errors": [f"Validation error: {exc}"],
                "threat_assessment": {"status": "error"},
            }

        vulnerabilities = result.get("vulnerabilities_exposed", 0)
        return {
            "valid": vulnerabilities == 0,
            "errors": [
                f"Vulnerability: {row['pattern']} - {row.get('description', 'No description')}"
                for row in result.get("attack_results", [])
                if row.get("vulnerable")
            ],
            "threat_assessment": result.get("threat_assessment", {}),
            "probes_executed": result.get("probes_executed", 0),
        }


class BoundaryValidator:
    def __init__(self) -> None:
        self._agent = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        try:
            from agentic_core.L4_state.memory import ValidationContext
            from agentic_core.L5_safety.reasoning.BoundaryTestingAgent_validator import BoundaryTestingAgent
        except ImportError as exc:  # guardian: allow-log-and-swallow allow-return-none-swallow -- boundary testing agent optional: logged and skipped, validator runs in degraded mode
            Logger.warning("[BoundaryValidator] Could not import agent: %s", exc)
            self._initialized = True
            return

        self._agent = BoundaryTestingAgent(ctx=ValidationContext())
        self._initialized = True

    def validate(self, content: Any, context: dict[str, Any]) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415

        _emit_records_execution_trace(
            str(_uuid.uuid4()),
            LayerSegment.L3_ORCHESTRATION,
            "BoundaryValidator.validate",
        )

        self._ensure_initialized()
        if self._agent is None:
            return {"valid": True, "errors": [], "recommendations": []}

        try:
            result = _run_agent(self._agent)
        except Exception as exc:  # guardian: allow-broad-exception -- _run_agent wraps arbitrary async agent code that may raise any exception type
            Logger.error("[BoundaryValidator] Validation failed: %s", exc)
            return {"valid": False, "errors": [f"Validation error: {exc}"], "recommendations": []}

        edge_cases = result.get("edge_cases_found", 0)
        return {
            "valid": edge_cases == 0,
            "errors": [
                f"Boundary violation: {row['test']} - {row.get('violation', 'Unknown')}"
                for row in result.get("boundary_violations", [])
            ],
            "recommendations": result.get("recommendations", []),
            "tests_executed": result.get("tests_executed", 0),
        }


_adversarial_validator: AdversarialValidator | None = None
_boundary_validator: BoundaryValidator | None = None


def get_adversarial_validator() -> AdversarialValidator:
    global _adversarial_validator
    if _adversarial_validator is None:
        _adversarial_validator = AdversarialValidator()
    return _adversarial_validator


def get_boundary_validator() -> BoundaryValidator:
    global _boundary_validator
    if _boundary_validator is None:
        _boundary_validator = BoundaryValidator()
    return _boundary_validator


def register_red_team_validators() -> dict[str, Any]:
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


def get_integration_status() -> dict[str, Any]:
    return {
        "adversarial_validator_initialized": _adversarial_validator is not None,
        "boundary_validator_initialized": _boundary_validator is not None,
        "validators_available": ["adversarial_probe", "boundary_testing"],
    }
