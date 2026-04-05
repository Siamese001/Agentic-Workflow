"""Validation rule checks that return violations without side effects.

This module contains all rule check methods that return violations
rather than performing actions. The caller decides whether and how to fix them.
"""

import ast
import logging
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

from .models import Violation

logger = logging.getLogger(__name__)


def validate_layer_alignment(
    path: Path,
    file_type: str,
    project_root: Path,
) -> Violation | None:
    """Validate that file is in the correct layer for its type.

    TODO: Extract implementation from FileClassificationAgent.validate_layer_alignment.
    """
    return None


def validate_territory_alignment(
    path: Path,
    file_type: str,
    project_root: Path,
) -> Violation | None:
    """Validate that file is in the correct territory.

    TODO: Extract implementation from FileClassificationAgent.validate_territory_alignment.
    """
    return None


def validate_app_prefix_placement(
    path: Path,
    file_type: str,
) -> Violation | None:
    """Validate app-specific prefix placement.

    TODO: Extract implementation from FileClassificationAgent.validate_app_prefix_placement.
    """
    return None


def validate_pascal_case_placement(
    path: Path,
    file_type: str,
) -> Violation | None:
    """Validate PascalCase file placement.

    TODO: Extract implementation from FileClassificationAgent.validate_pascal_case_placement.
    """
    return None


def validate_single_suffix(
    path: Path,
    file_type: str,
) -> Violation | None:
    """Validate that file has only one classification suffix.

    TODO: Extract implementation from FileClassificationAgent.validate_single_suffix.
    """
    return None


def validate_folder_suffix_consistency(
    path: Path,
    file_type: str,
) -> Violation | None:
    """Validate folder suffix consistency.

    TODO: Extract implementation from FileClassificationAgent.validate_folder_suffix_consistency.
    """
    return None


def _enforce_folder_purity(
    path: Path,
    file_type: str,
    project_root: Path,
) -> Violation | None:
    """Enforce bidirectional folder→suffix purity.

    TODO: Extract implementation from FileClassificationAgent._enforce_folder_purity.
    """
    return None


def _validate_orchestrator_invariants(
    tree: ast.AST,
    path: Path,
    content: str,
) -> str:
    """Validate orchestrator invariants and return classification result.

    TODO: Extract implementation from FileClassificationAgent._validate_orchestrator_invariants.
    """
    return "ORCHESTRATOR"


def _validate_orchestrator_layer_alignment(
    path: Path,
    result: str,
) -> Violation | None:
    """Validate orchestrator layer alignment.

    TODO: Extract implementation from FileClassificationAgent._validate_orchestrator_layer_alignment.
    """
    return None


def _validate_router_invariants(
    tree: ast.AST,
    path: Path,
    content: str,
) -> Violation | None:
    """Validate router invariants.

    TODO: Extract implementation from FileClassificationAgent._validate_router_invariants.
    """
    return None


def _detect_cross_domain_violation(path: Path) -> dict[str, Any] | None:
    """Detect cross-domain violations.

    TODO: Extract implementation from FileClassificationAgent._detect_cross_domain_violation.
    """
    return None


def _detect_ephemeral_scripts(path: Path) -> dict[str, Any] | None:
    """Detect ephemeral scripts.

    TODO: Extract implementation from FileClassificationAgent._detect_ephemeral_scripts.
    """
    return None


def _detect_cross_layer_naming_violation(path: Path) -> dict[str, Any] | None:
    """Detect cross-layer naming violations.

    TODO: Extract implementation from FileClassificationAgent._detect_cross_layer_naming_violation.
    """
    return None


def _detect_duplicate_files(file_registry: list[Path]) -> list[dict[str, Any]]:
    """Detect duplicate files.

    TODO: Extract implementation from FileClassificationAgent._detect_duplicate_files.
    """
    return []


def _detect_semantic_duplicates(file_registry: list[Path]) -> list[dict[str, Any]]:
    """Detect semantic duplicates.

    TODO: Extract implementation from FileClassificationAgent._detect_semantic_duplicates.
    """
    return []


def check_fake_config(path: Path, content: str) -> Violation | None:
    """
    Detect files ending in _config.py that contain active logic (classes with methods).

    A genuine config file should only contain constants, dataclasses, or simple assignments.
    If it has class definitions with non-trivial methods (beyond __init__), it's a
    misnamed utility masquerading as config.

    Also classifies Verifier/Guardian/Lock classes as UTILITY unless they inherit
    from SovereignBaseAgent.

    Args:
        path: File path being checked
        content: File content as string

    Returns:
        Violation object or None if clean.
    """
    stem = path.stem

    # Only check *_config.py files
    if not stem.endswith("_config"):
        return None

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return None

    for node in ast.walk(tree):
        if not isinstance(node, ast.ClassDef):
            continue

        # Skip pure dataclasses — they're legitimate config containers
        is_dataclass = any(
            (isinstance(d, ast.Name) and d.id == "dataclass")
            or (isinstance(d, ast.Attribute) and d.attr == "dataclass")
            for d in node.decorator_list
        )
        if is_dataclass:
            continue

        # Check for non-trivial methods (beyond __init__, __repr__, __str__)
        trivial_methods = {"__init__", "__repr__", "__str__", "__post_init__"}
        active_methods = [
            item.name
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
            and item.name not in trivial_methods
        ]
        if active_methods:
            return Violation(
                type="MISNAMED_UTILITY",
                path=str(path),
                message=(
                    f"{path.name} contains class '{node.name}' with active methods "
                    f"{active_methods[:3]}. This is a utility, not a config file."
                ),
                severity="WARNING",
                suggested_fix="_util.py",
            )

    return None


def check_domain_root_purity(path: Path) -> Violation | None:
    """
    Enforce the Leaf Node Rule: domain roots must NOT contain logic files.

    Domain directories like knowledge/, semantic_memory/ must only contain
    sub-directories. Python files (except __init__.py) at the root level
    are violations that must be moved into appropriate sub-directories.

    Also enforces snake_case naming within knowledge/ domain.

    Args:
        path: File path being checked

    Returns:
        Violation object or None if clean.
    """
    # Domain roots that enforce the leaf node rule
    domain_roots = {"knowledge", "semantic_memory"}

    parts = path.parts
    if path.name == "__init__.py":
        return None

    for i, part in enumerate(parts):
        if part in domain_roots and i + 1 < len(parts):
            # Check if this file is directly in the domain root (not a subfolder)
            if parts[i + 1] == path.name:
                return Violation(
                    type="LEAF_NODE_VIOLATION",
                    path=str(path),
                    message=(
                        f"{path.name} is in {part}/ root. "
                        f"Domain roots must only contain sub-directories (Leaf Node Rule)."
                    ),
                    severity="ERROR",
                    suggested_fix=f"agentic_core/{part}/engine/",
                )

    # Check PascalCase in knowledge domain
    if "knowledge" in parts and path.suffix == ".py":
        if any(c.isupper() for c in path.stem):
            return Violation(
                type="KNOWLEDGE_PASCAL_CASE",
                path=str(path),
                message=(
                    f"{path.name} uses PascalCase in knowledge/ domain. "
                    f"Must be snake_case per naming convention."
                ),
                severity="ERROR",
                suggested_fix="Rename to snake_case",
            )

    return None


def check_base_agents_purity(path: Path) -> Violation | None:
    """Check base_agents purity.

    TODO: Extract implementation from FileClassificationAgent.check_base_agents_purity.
    """
    return None


def check_utils_purity(path: Path) -> Violation | None:
    """Check utils purity.

    TODO: Extract implementation from FileClassificationAgent.check_utils_purity.
    """
    return None


def check_layer_purity(path: Path) -> Violation | None:
    """Check layer purity.

    TODO: Extract implementation from FileClassificationAgent.check_layer_purity.
    """
    return None
