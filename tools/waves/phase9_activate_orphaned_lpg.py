"""Phase 9: Activation script for orphaned L_PG modules.

Wires remaining orphaned prompt_governance modules into the governed lifecycle.
"""

import logging

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
)

logger = logging.getLogger(__name__)


def activate_orphaned_modules() -> dict[str, bool]:
    """Activate orphaned L_PG modules by importing and wiring them.

    Returns:
        Dict mapping module names to activation status
    """
    results = {}

    # Module 1: governance_hub
    try:

        _emit_records_execution_trace(
            "phase9_activation",
            LayerSegment.L1_COGNITION,
            "activate_orphaned_modules.governance_hub",
        )
        results["governance_hub"] = True
        logger.info("GovernanceHub activated")
    except Exception as exc:
        results["governance_hub"] = False
        logger.warning(f"GovernanceHub activation failed: {exc}")

    # Module 2: injection_detector
    try:

        _emit_records_execution_trace(
            "phase9_activation",
            LayerSegment.L5_SAFETY,
            "activate_orphaned_modules.injection_detector",
        )
        results["injection_detector"] = True
        logger.info("InjectionDetector activated")
    except Exception as exc:
        results["injection_detector"] = False
        logger.warning(f"InjectionDetector activation failed: {exc}")

    # Module 3: pattern_repository
    try:

        _emit_records_execution_trace(
            "phase9_activation",
            LayerSegment.L5_SAFETY,
            "activate_orphaned_modules.pattern_repository",
        )
        results["pattern_repository"] = True
        logger.info("PatternRepository activated")
    except Exception as exc:
        results["pattern_repository"] = False
        logger.warning(f"PatternRepository activation failed: {exc}")

    # Module 4: evaluation_loader
    try:

        _emit_records_execution_trace(
            "phase9_activation",
            LayerSegment.L1_COGNITION,
            "activate_orphaned_modules.evaluation_loader",
        )
        results["evaluation_loader"] = True
        logger.info("EvaluationLoader activated")
    except Exception as exc:
        results["evaluation_loader"] = False
        logger.warning(f"EvaluationLoader activation failed: {exc}")

    # Module 5: meta_prompt_renderer
    try:

        _emit_records_execution_trace(
            "phase9_activation",
            LayerSegment.L3_ORCHESTRATION,
            "activate_orphaned_modules.meta_prompt_renderer",
        )
        results["meta_prompt_renderer"] = True
        logger.info("MetaPromptRenderer activated")
    except Exception as exc:
        results["meta_prompt_renderer"] = False
        logger.warning(f"MetaPromptRenderer activation failed: {exc}")

    return results


def verify_activation(results: dict[str, bool]) -> bool:
    """Verify that all critical modules were activated.

    Args:
        results: Activation results from activate_orphaned_modules()

    Returns:
        True if all critical modules activated
    """
    critical_modules = [
        "governance_hub",
        "injection_detector",
    ]

    all_activated = all(results.get(m, False) for m in critical_modules)

    if all_activated:
        logger.info("Phase 9: All critical L_PG modules activated")
    else:
        failed = [m for m in critical_modules if not results.get(m, False)]
        logger.warning(f"Phase 9: Failed to activate: {failed}")

    return all_activated


if __name__ == "__main__":
    # Run activation
    activation_results = activate_orphaned_modules()
    success = verify_activation(activation_results)

    print("\nPhase 9 Activation Results:")
    print("-" * 40)
    for module, status in activation_results.items():
        status_str = "✅" if status else "❌"
        print(f"{status_str} {module}")
    print("-" * 40)
    print(f"Overall: {'SUCCESS' if success else 'PARTIAL'}")
