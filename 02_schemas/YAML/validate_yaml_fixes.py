#!/usr/bin/env python3
"""
02_schemas/YAML/validate_yaml_fixes.py
Validate semantic cache operations against proposed YAML architectural fixes.

This module ensures no operations target directories we plan to remove,
providing safety validation before architectural changes.

Auto-hardened by WINDSURF v7 — Production-ready, type-safe, zero-loss.
"""

from __future__ import annotations

import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# Redundant directory patterns that should be validated before removal
REDUNDANT_PATTERNS: List[str] = [
    'L5_safety/P1_retrieve',
    'L5_safety/P2_inspect',
    'L5_safety/P3_aggregate',
    'L2_execution/P1_retrieve',
    'L3_orchestration/P1_retrieve',
    'L3_orchestration/P2_inspect',
    'L4_memory/P2_inspect',
]


class YAMLValidationError(Exception):
    """Raised when YAML validation fails."""

    def __init__(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(message)
        self.message = message
        self.context = context or {}


def load_migration_plan(plan_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load the current migration plan to analyze operation targets.

    Args:
        plan_path: Optional path to migration plan JSON. Defaults to standard location.

    Returns:
        Parsed migration plan dictionary.

    Raises:
        YAMLValidationError: If plan file cannot be loaded or parsed.
    """
    if plan_path is None:
        plan_path = Path("02_schemas/01_agentic_core_migration_and_rewrite_plan.json")

    if not plan_path.exists():
        raise YAMLValidationError(
            f"Migration plan not found: {plan_path}",
            context={"path": str(plan_path)},
        )

    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise YAMLValidationError(
            f"Invalid JSON in migration plan: {e}",
            context={"path": str(plan_path), "error": str(e)},
        ) from e
    except OSError as e:
        raise YAMLValidationError(
            f"Failed to read migration plan: {e}",
            context={"path": str(plan_path), "error": str(e)},
        ) from e


def analyze_operation_targets(
    plan: Optional[Dict[str, Any]] = None,
) -> Tuple[List[str], List[Tuple[str, List[Dict[str, Any]]]], int]:
    """
    Analyze which paths are targeted by semantic operations.

    Args:
        plan: Optional pre-loaded migration plan. Will load if not provided.

    Returns:
        Tuple of (safe_to_remove, needs_review, total_redundant_ops).

    Raises:
        YAMLValidationError: If plan cannot be loaded.
    """
    logger.debug("Validating YAML architectural fixes")

    if plan is None:
        plan = load_migration_plan()

    operations = plan.get('operations', [])
    logger.debug("Analyzing %d operations from migration plan", len(operations))

    # Count operations targeting each pattern
    pattern_counts: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for op in operations:
        target_path = op.get('target_path', '')

        for pattern in REDUNDANT_PATTERNS:
            if pattern in target_path:
                pattern_counts[pattern].append({
                    'target_path': target_path,
                    'operation_type': op.get('operation_type', 'unknown'),
                    'archive_name': op.get('archive_name', 'unknown'),
                })

    total_redundant_ops = 0
    safe_to_remove: List[str] = []
    needs_review: List[Tuple[str, List[Dict[str, Any]]]] = []

    for pattern in REDUNDANT_PATTERNS:
        ops = pattern_counts.get(pattern, [])
        count = len(ops)
        total_redundant_ops += count

        if count == 0:
            safe_to_remove.append(pattern)
            logger.debug("Pattern %s: 0 operations (SAFE TO REMOVE)", pattern)
        else:
            needs_review.append((pattern, ops))
            logger.debug("Pattern %s: %d operations (NEEDS REVIEW)", pattern, count)

    logger.info(
        "Analysis complete: %d operations, %d redundant, %d safe, %d need review",
        len(operations),
        total_redundant_ops,
        len(safe_to_remove),
        len(needs_review),
    )

    return safe_to_remove, needs_review, total_redundant_ops


def generate_yaml_fix_recommendations(
    safe_to_remove: List[str],
    needs_review: List[Tuple[str, List[Dict[str, Any]]]],
    total_redundant_ops: int,
) -> Dict[str, Any]:
    """
    Generate specific YAML fix recommendations based on validation.

    Args:
        safe_to_remove: List of patterns safe to remove.
        needs_review: List of (pattern, operations) tuples needing review.
        total_redundant_ops: Total count of redundant operations.

    Returns:
        Dictionary containing recommendations and metadata.
    """
    recommendations: Dict[str, Any] = {
        "safe_to_remove": safe_to_remove,
        "needs_review": [p for p, _ in needs_review],
        "total_redundant_ops": total_redundant_ops,
        "can_proceed": total_redundant_ops == 0,
    }

    if total_redundant_ops == 0:
        logger.info("No operations target redundant directories - safe to proceed")
        recommendations["status"] = "SAFE"
        recommendations["message"] = "All redundant patterns can be safely removed"
    else:
        logger.warning(
            "%d operations target redundant directories - manual review required",
            total_redundant_ops,
        )
        recommendations["status"] = "REVIEW_REQUIRED"
        recommendations["message"] = f"{total_redundant_ops} operations need review"

    return recommendations


def check_current_yaml_state(yaml_path: Optional[Path] = None) -> Dict[str, bool]:
    """
    Check current YAML state to see what's already fixed.

    Args:
        yaml_path: Optional path to YAML file. Defaults to standard location.

    Returns:
        Dictionary mapping phase names to presence status.

    Raises:
        YAMLValidationError: If YAML file cannot be read.
    """
    if yaml_path is None:
        yaml_path = Path("unified_structure_subatomic.yaml")

    if not yaml_path.exists():
        raise YAMLValidationError(
            f"YAML file not found: {yaml_path}",
            context={"path": str(yaml_path)},
        )

    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except OSError as e:
        raise YAMLValidationError(
            f"Failed to read YAML file: {e}",
            context={"path": str(yaml_path), "error": str(e)},
        ) from e

    state = {
        "L5_P1_retrieve": 'L5_safety:\n    P1_retrieve:' in content,
        "L5_P2_inspect": 'L5_safety:\n    P2_inspect:' in content,
        "L5_P3_aggregate": 'L5_safety:\n    P3_aggregate:' in content,
    }

    if not any(state.values()):
        logger.info("L5_safety already fixed (only P4_safety present)")
    else:
        present = [k for k, v in state.items() if v]
        logger.warning("L5_safety still has redundant phases: %s", present)

    return state


def main() -> int:
    """
    Main entry point for YAML validation.

    Returns:
        Exit code (0 for success, 1 for errors).
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )

    try:
        safe_to_remove, needs_review, total_redundant_ops = analyze_operation_targets()
        recommendations = generate_yaml_fix_recommendations(
            safe_to_remove, needs_review, total_redundant_ops
        )
        check_current_yaml_state()

        logger.info("Validation complete: %s", recommendations["status"])
        return 0 if recommendations["can_proceed"] else 1

    except YAMLValidationError as e:
        logger.error("Validation failed: %s", e.message)
        return 1
    except Exception as e:
        logger.exception("Unexpected error during validation: %s", e)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
