"""
Unified Registration Module for Orphan Agent Integration - Phase 1 Foundation

This module registers all previously-orphan agents into the validation
and healing infrastructure. Import this module at application startup
to enable all security and resilience features.

Usage:
    from agentic_core.L5_safety.validators import register_all_validators
    register_all_validators.initialize()

    # Check status
    status = register_all_validators.get_integration_status()
"""

from __future__ import annotations

import logging
from typing import Any

Logger = logging.getLogger(__name__)

_REGISTERED = False


def initialize() -> dict[str, Any]:
    """
    Initialize all orphan agent integrations.

    This function registers:
    - Red team validators (adversarial_probe, boundary_testing)
    - Chaos resilience healing strategy
    - Dependency pruning healing strategy

    Returns:
        dict with initialization status and details
    """
    global _REGISTERED

    if _REGISTERED:
        return {
            "status": "already_initialized",
            "validators": [],
            "strategies": [],
        }

    Logger.info("[Sovereign Integration] Initializing orphan agent integrations...")

    results = {
        "status": "initializing",
        "validators": [],
        "strategies": [],
        "errors": [],
    }

    # Red Team Validators
    try:
        from agentic_core.L5_safety.validators.red_team_integration_types import (
            register_red_team_validators,
        )

        red_team_result = register_red_team_validators()
        results["validators"].extend(red_team_result.get("registered", []))
        results["errors"].extend(red_team_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Red team integration unavailable: {e}")
        results["errors"].append(f"red_team_integration: {e}")

    # Chaos Engineering Healing
    try:
        from agentic_core.L5_safety.validators.chaos_healing_integration_types import (
            register_chaos_healing,
        )

        chaos_result = register_chaos_healing()
        results["strategies"].extend(chaos_result.get("registered", []))
        results["errors"].extend(chaos_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Chaos integration unavailable: {e}")
        results["errors"].append(f"chaos_healing_integration: {e}")

    # Dependency Pruning Healing
    try:
        from agentic_core.L5_safety.validators.dependency_healing_integration_types import (
            register_dependency_healing,
        )

        dep_result = register_dependency_healing()
        results["strategies"].extend(dep_result.get("registered", []))
        results["errors"].extend(dep_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Dependency integration unavailable: {e}")
        results["errors"].append(f"dependency_healing_integration: {e}")

    # Operational Healing (Historian, CostGovernor, TaskDecomposition)
    try:
        from agentic_core.L5_safety.validators.operational_healing_integration_types import (
            register_operational_healing,
        )

        op_result = register_operational_healing()
        results["strategies"].extend(op_result.get("registered", []))
        results["errors"].extend(op_result.get("errors", []))
    except ImportError as e:
        Logger.warning(f"[Sovereign Integration] Operational integration unavailable: {e}")
        results["errors"].append(f"operational_healing_integration: {e}")

    _REGISTERED = True
    results["status"] = "initialized" if not results["errors"] else "partial"

    Logger.info(
        f"[Sovereign Integration] Initialized: "
        f"{len(results['validators'])} validators, "
        f"{len(results['strategies'])} strategies",
    )

    return results


def get_integration_status() -> dict[str, Any]:
    """
    Return comprehensive status of all integrations.

    Returns:
        dict with:
        - initialized: bool
        - validators_registered: list of validator names
        - strategies_registered: list of strategy names
        - module_status: dict of each module's status
    """
    status = {
        "initialized": _REGISTERED,
        "validators_registered": [],
        "strategies_registered": [],
        "module_status": {},
    }

    # Check ValidatorOrchestrator
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import (
            get_validator_orchestrator,
        )

        orchestrator = get_validator_orchestrator()
        status["validators_registered"] = list(orchestrator._validators.keys())
        status["module_status"]["validator_orchestrator"] = "available"
    except ImportError:
        status["module_status"]["validator_orchestrator"] = "unavailable"

    # Check HealingSovereignOrchestrator
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import (
            get_healing_orchestrator,
        )

        orchestrator = get_healing_orchestrator()
        status["strategies_registered"] = list(orchestrator._strategies.keys())
        status["module_status"]["healing_orchestrator"] = "available"
    except ImportError:
        status["module_status"]["healing_orchestrator"] = "unavailable"

    # Check individual integration modules
    try:
        import importlib.util

        if importlib.util.find_spec("agentic_core.L5_safety.validators.red_team_integration"):
            status["module_status"]["red_team_integration"] = "available"
        else:
            status["module_status"]["red_team_integration"] = "unavailable"
    except ImportError:
        status["module_status"]["red_team_integration"] = "unavailable"

    try:
        if importlib.util.find_spec("agentic_core.L5_safety.validators.chaos_healing_integration"):
            status["module_status"]["chaos_healing_integration"] = "available"
        else:
            status["module_status"]["chaos_healing_integration"] = "unavailable"
    except ImportError:
        status["module_status"]["chaos_healing_integration"] = "unavailable"

    try:
        dep_module = "agentic_core.L5_safety.validators.dependency_healing_integration"
        if importlib.util.find_spec(dep_module):
            status["module_status"]["dependency_healing_integration"] = "available"
        else:
            status["module_status"]["dependency_healing_integration"] = "unavailable"
    except ImportError:
        status["module_status"]["dependency_healing_integration"] = "unavailable"

    return status


def reset() -> None:
    """
    Reset integration state (for testing purposes only).

    WARNING: This should only be used in test fixtures.
    """
    global _REGISTERED
    _REGISTERED = False

    # Reset orchestrator singletons if available
    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import (
            ValidatorOrchestrator,
        )

        ValidatorOrchestrator.reset_instance()
    except ImportError:
        pass

    try:
        from agentic_core.L5_safety.types.healing_orchestration_types import (
            HealingSovereignOrchestrator,
        )

        HealingSovereignOrchestrator.reset_instance()
    except ImportError:
        pass
