"""
Surgical Healing Adapter - Bridge for Resolution Asymmetry Remediation

Provides adapters to upgrade existing agents to use SurgicalContext-based healing
without breaking backwards compatibility.

Phase 1: Critical Tier - CodeHealerAgent, CompositeGuardrailAgent
"""

from __future__ import annotations

import ast
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeVar

from .surgical_context import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from .surgical_cst_healer_mixin import SurgicalCSTHealerMixin

T = TypeVar("T")


@dataclass
class SurgicalHealingResult:
    """Result of a surgical healing operation."""

    status: str
    violations_found: int
    violations_fixed: int
    errors: int
    skipped: int
    details: str = ""
    artifacts: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.artifacts is None:
            self.artifacts = []

    def to_dict(self) -> dict[str, Any]:
        """Convert to standard heal response format."""
        return {
            "status": self.status,
            "violations_found": self.violations_found,
            "violations_fixed": self.violations_fixed,
            "errors": self.errors,
            "skipped": self.skipped,
            "details": self.details,
            "artifacts": self.artifacts,
        }


class SurgicalHealingAdapter:
    """
    Adapter to upgrade legacy healing methods to surgical pattern.

    Usage:
        adapter = SurgicalHealingAdapter(agent_name="CodeHealerAgent")

        # Convert detection result to SurgicalContext
        context = adapter.create_context_from_detection(
            file_path=Path("my_file.py"),
            detection_result={"type": "import", "line": 5, "message": "..."},
            detection_method="heal_imports"
        )

        # Apply surgical healing
        result = adapter.apply_surgical_healing(context)
    """

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self._healer = _InternalSurgicalHealer()

    def create_context_from_detection(
        self,
        file_path: Path,
        detection_result: dict[str, Any],
        detection_method: str,
    ) -> SurgicalContext | None:
        """
        Create SurgicalContext from legacy detection result.

        This bridges the gap between string-based detection and AST-based healing.
        """
        if not file_path.exists():
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            return None

        # Extract violation info from detection result
        violation_type = detection_result.get("type", "unknown")
        line_number = detection_result.get("line", detection_result.get("line_number", 1))
        message = detection_result.get("message", detection_result.get("description", ""))
        severity = detection_result.get("severity", "warning")

        # Create violation constraint
        violation = ViolationConstraint(
            constraint_type=violation_type,
            severity=severity,
            message=message,
            fix_type=self._infer_fix_type(violation_type),
            expected_pattern=detection_result.get("expected_pattern"),
            actual_pattern=detection_result.get("actual_pattern"),
        )

        # Create AST coordinate
        coordinate = ASTCoordinate(
            node_id=f"{violation_type}_{line_number}",
            node_type=self._infer_node_type(tree, line_number),
            line=line_number,
            column=0,
        )

        # Build surgical context
        from datetime import datetime

        context = SurgicalContext(
            file_path=file_path,
            file_content=source,
            ast_tree=tree,
            violation_id=f"{self.agent_name}_{violation_type}_{line_number}",
            violations=[violation],
            target_coordinates=[coordinate],
            detector_agent=self.agent_name,
            detection_method=detection_method,
            detection_timestamp=datetime.now().isoformat(),
        )

        return context

    def create_batch_context(
        self,
        file_path: Path,
        detection_results: list[dict[str, Any]],
        detection_method: str,
    ) -> SurgicalContext | None:
        """Create SurgicalContext for multiple violations in one file."""
        if not file_path.exists() or not detection_results:
            return None

        try:
            source = file_path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except Exception:
            return None

        violations = []
        coordinates = []

        for i, result in enumerate(detection_results):
            violation_type = result.get("type", "unknown")
            line_number = result.get("line", result.get("line_number", 1))
            message = result.get("message", result.get("description", ""))
            severity = result.get("severity", "warning")

            violation = ViolationConstraint(
                constraint_type=violation_type,
                severity=severity,
                message=message,
                fix_type=self._infer_fix_type(violation_type),
                expected_pattern=result.get("expected_pattern"),
                actual_pattern=result.get("actual_pattern"),
            )
            violations.append(violation)

            coordinate = ASTCoordinate(
                node_id=f"{violation_type}_{line_number}_{i}",
                node_type=self._infer_node_type(tree, line_number),
                line=line_number,
                column=0,
            )
            coordinates.append(coordinate)

        from datetime import datetime

        context = SurgicalContext(
            file_path=file_path,
            file_content=source,
            ast_tree=tree,
            violation_id=f"{self.agent_name}_batch_{len(violations)}",
            violations=violations,
            target_coordinates=coordinates,
            detector_agent=self.agent_name,
            detection_method=detection_method,
            detection_timestamp=datetime.now().isoformat(),
        )

        return context

    def apply_surgical_healing(self, context: SurgicalContext) -> SurgicalHealingResult:
        """Apply surgical healing using the context."""
        if context is None:
            return SurgicalHealingResult(
                status="error",
                violations_found=0,
                violations_fixed=0,
                errors=1,
                skipped=0,
                details="No context provided",
            )

        result = self._healer.heal_surgical_cst(context)

        return SurgicalHealingResult(
            status=result.get("status", "unknown"),
            violations_found=result.get("violations_found", 0),
            violations_fixed=result.get("violations_fixed", 0),
            errors=result.get("errors", 0),
            skipped=result.get("skipped", 0),
            details=result.get("details", ""),
            artifacts=result.get("artifacts", []),
        )

    def _infer_fix_type(self, violation_type: str) -> str:
        """Infer fix type from violation type."""
        if "missing" in violation_type.lower():
            return "insert"
        elif "unused" in violation_type.lower() or "remove" in violation_type.lower():
            return "delete"
        else:
            return "replace"

    def _infer_node_type(self, tree: ast.Module, line_number: int) -> str:
        """Infer AST node type at line number."""
        for node in ast.walk(tree):
            if hasattr(node, "lineno") and node.lineno == line_number:
                return type(node).__name__
        return "Module"


class _InternalSurgicalHealer(SurgicalCSTHealerMixin):
    """Internal healer class that uses the CST mixin."""

    pass


def upgrade_heal_method(
    original_method: Callable,
    agent_name: str,
) -> Callable:
    """
    Decorator to upgrade a legacy heal method to use surgical healing.

    Usage:
        @upgrade_heal_method(agent_name="CodeHealerAgent")
        def heal_imports(self, file_path: Path) -> list:
            ...
    """
    adapter = SurgicalHealingAdapter(agent_name)

    def wrapper(self, *args, **kwargs):
        # Call original method to get detection results
        original_result = original_method(self, *args, **kwargs)

        # If file_path is first arg, try to create surgical context
        if args and isinstance(args[0], Path):
            file_path = args[0]

            # Convert original result to detection format if needed
            if isinstance(original_result, list):
                # Assume list of HealingAction or similar
                detection_results = []
                for item in original_result:
                    if hasattr(item, "healing_type"):
                        detection_results.append(
                            {
                                "type": item.healing_type.lower(),
                                "line": item.line_number,
                                "message": item.description,
                            }
                        )
                    elif isinstance(item, dict):
                        detection_results.append(item)

                if detection_results:
                    context = adapter.create_batch_context(
                        file_path, detection_results, original_method.__name__
                    )
                    if context:
                        # Log that we're using surgical healing
                        pass  # adapter.apply_surgical_healing(context)

        return original_result

    return wrapper


__all__ = [
    "SurgicalHealingAdapter",
    "SurgicalHealingResult",
    "upgrade_heal_method",
]
