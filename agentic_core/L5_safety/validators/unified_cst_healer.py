"""
Unified CST Healer - Single Entry Point for All CST-Based Healing

Provides a unified interface for all healing operations using LibCST,
ensuring zero-loss transformations with proper orchestration.
"""

from __future__ import annotations

import ast
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import libcst as cst

from .surgical_context import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)
from .cst_transformers import (
    create_import_remover,
    create_docstring_inserter,
    create_bare_except_fixer,
    create_future_import_inserter,
    create_trailing_whitespace_fixer,
    create_blank_line_normalizer,
    create_type_hint_inserter,
)

Logger = logging.getLogger(__name__)


@dataclass
class HealingConfig:
    """Configuration for unified healing operations."""

    enable_import_healing: bool = True
    enable_docstring_healing: bool = True
    enable_bare_except_healing: bool = True
    enable_future_import_healing: bool = True
    enable_whitespace_healing: bool = True
    enable_blank_line_healing: bool = True
    enable_type_hint_healing: bool = True
    dry_run: bool = False
    max_blank_lines: int = 2


@dataclass
class HealingResult:
    """Result of a healing operation."""

    status: str  # "success", "error", "partial"
    violations_found: int = 0
    violations_fixed: int = 0
    errors: int = 0
    skipped: int = 0
    details: str = ""
    artifacts: List[Dict[str, Any]] = field(default_factory=list)
    modified_files: Set[Path] = field(default_factory=set)


class UnifiedCSTHealer:
    """
    Unified entry point for all CST-based healing operations.

    Provides orchestration of multiple transformers with proper
    ordering and conflict resolution.
    """

    def __init__(self, config: Optional[HealingConfig] = None):
        """
        Initialize the unified healer.

        Args:
            config: Healing configuration (uses defaults if not provided)
        """
        self.config = config or HealingConfig()
        self._transformer_order = [
            "future_import",  # Must come first
            "import",
            "docstring",
            "bare_except",
            "type_hint",
            "whitespace",
            "blank_line",
        ]

    def heal_file(
        self,
        file_path: Path,
        violations: Optional[List[ViolationConstraint]] = None,
    ) -> HealingResult:
        """
        Heal a single file using all enabled transformers.

        Args:
            file_path: Path to the file to heal
            violations: Optional list of specific violations to fix

        Returns:
            HealingResult with details of the operation
        """
        result = HealingResult(status="success")

        try:
            content = file_path.read_text(encoding="utf-8")
        except Exception as e:
            Logger.error(f"Failed to read {file_path}: {e}")
            return HealingResult(
                status="error",
                errors=1,
                details=f"Failed to read file: {e}",
            )

        try:
            ast_tree = ast.parse(content)
        except SyntaxError as e:
            Logger.error(f"Failed to parse {file_path}: {e}")
            return HealingResult(
                status="error",
                errors=1,
                details=f"Syntax error: {e}",
            )

        # Auto-detect violations if not provided
        if violations is None:
            violations = self._detect_violations(content, file_path)

        result.violations_found = len(violations)

        if not violations:
            result.details = "No violations detected"
            return result

        # Create surgical context
        context = SurgicalContext(
            file_path=file_path,
            file_content=content,
            ast_tree=ast_tree,
            violations=violations,
            target_coordinates=[v.target_coordinate for v in violations if v.target_coordinate],
            detector_agent="UnifiedCSTHealer",
            detection_method="heal_file",
            detection_timestamp=datetime.now().isoformat(),
            violation_id=f"unified_heal_{file_path.name}",
        )

        # Apply transformers
        heal_result = self._apply_transformers(context)

        result.violations_fixed = heal_result.get("violations_fixed", 0)
        result.errors = heal_result.get("errors", 0)
        result.skipped = result.violations_found - result.violations_fixed
        result.details = heal_result.get("details", "")
        result.artifacts = heal_result.get("artifacts", [])

        if result.violations_fixed > 0:
            result.modified_files.add(file_path)

        return result

    def heal_files(
        self,
        file_paths: List[Path],
        violations_map: Optional[Dict[Path, List[ViolationConstraint]]] = None,
    ) -> HealingResult:
        """
        Heal multiple files.

        Args:
            file_paths: List of file paths to heal
            violations_map: Optional mapping of paths to violations

        Returns:
            Aggregated HealingResult
        """
        total_result = HealingResult(status="success")

        for file_path in file_paths:
            violations = violations_map.get(file_path) if violations_map else None
            result = self.heal_file(file_path, violations)

            total_result.violations_found += result.violations_found
            total_result.violations_fixed += result.violations_fixed
            total_result.errors += result.errors
            total_result.skipped += result.skipped
            total_result.modified_files.update(result.modified_files)
            total_result.artifacts.extend(result.artifacts)

        if total_result.errors > 0:
            total_result.status = "partial" if total_result.violations_fixed > 0 else "error"

        total_result.details = (
            f"Processed {len(file_paths)} files, "
            f"fixed {total_result.violations_fixed} violations, "
            f"{total_result.errors} errors"
        )

        return total_result

    def _detect_violations(self, content: str, file_path: Path) -> List[ViolationConstraint]:
        """
        Auto-detect violations in the content.

        Args:
            content: File content
            file_path: Path to the file

        Returns:
            List of detected violations
        """
        violations = []
        lines = content.split("\n")

        # Detect missing __future__ import
        if self.config.enable_future_import_healing:
            has_future = any("from __future__" in line for line in lines[:10])
            if not has_future and file_path.suffix == ".py":
                coord = ASTCoordinate(line=1, column=0, node_id="future_import", node_type="Module")
                violation = ViolationConstraint(
                    constraint_type="missing_future_import",
                    severity="warning",
                    message="Missing __future__ annotations import",
                    fix_type="insert",
                )
                violation.target_coordinate = coord
                violations.append(violation)

        # Detect bare except clauses
        if self.config.enable_bare_except_healing:
            import re

            for i, line in enumerate(lines):
                if re.match(r"^\s*except\s*:\s*$", line):
                    coord = ASTCoordinate(
                        line=i + 1,
                        column=0,
                        node_id=f"bare_except_{i + 1}",
                        node_type="ExceptHandler",
                    )
                    violation = ViolationConstraint(
                        constraint_type="bare_except",
                        severity="warning",
                        message=f"Bare except at line {i + 1}",
                        fix_type="replace",
                    )
                    violation.target_coordinate = coord
                    violations.append(violation)

        # Detect trailing whitespace
        if self.config.enable_whitespace_healing:
            has_trailing = any(line.rstrip() != line for line in lines)
            if has_trailing:
                coord = ASTCoordinate(line=1, column=0, node_id="trailing_ws", node_type="Module")
                violation = ViolationConstraint(
                    constraint_type="trailing_whitespace",
                    severity="warning",
                    message="Trailing whitespace detected",
                    fix_type="replace",
                )
                violation.target_coordinate = coord
                violations.append(violation)

        # Detect excessive blank lines
        if self.config.enable_blank_line_healing:
            blank_count = 0
            has_excessive = False
            for line in lines:
                if line.strip() == "":
                    blank_count += 1
                    if blank_count > self.config.max_blank_lines:
                        has_excessive = True
                        break
                else:
                    blank_count = 0

            if has_excessive:
                coord = ASTCoordinate(line=1, column=0, node_id="blank_lines", node_type="Module")
                violation = ViolationConstraint(
                    constraint_type="excessive_blank_lines",
                    severity="warning",
                    message="Excessive blank lines detected",
                    fix_type="replace",
                )
                violation.target_coordinate = coord
                violations.append(violation)

        return violations

    def _apply_transformers(self, context: SurgicalContext) -> Dict[str, Any]:
        """
        Apply all enabled transformers in the correct order.

        Args:
            context: Surgical context with violations

        Returns:
            Dict with healing results
        """
        try:
            source_code = context.file_path.read_text(encoding="utf-8")
            cst_tree = cst.parse_module(source_code)
            total_modifications = 0

            # Apply transformers in order
            transformer_factories = {
                "future_import": (
                    create_future_import_inserter,
                    self.config.enable_future_import_healing,
                ),
                "import": (
                    create_import_remover,
                    self.config.enable_import_healing,
                ),
                "docstring": (
                    create_docstring_inserter,
                    self.config.enable_docstring_healing,
                ),
                "bare_except": (
                    create_bare_except_fixer,
                    self.config.enable_bare_except_healing,
                ),
                "type_hint": (
                    create_type_hint_inserter,
                    self.config.enable_type_hint_healing,
                ),
                "whitespace": (
                    create_trailing_whitespace_fixer,
                    self.config.enable_whitespace_healing,
                ),
                "blank_line": (
                    create_blank_line_normalizer,
                    self.config.enable_blank_line_healing,
                ),
            }

            for transformer_name in self._transformer_order:
                factory, enabled = transformer_factories.get(transformer_name, (None, False))
                if not enabled or factory is None:
                    continue

                transformer = factory(context.violations)
                if transformer:
                    cst_tree = cst_tree.visit(transformer)
                    total_modifications += transformer.modifications_made

            # Write back if modifications were made
            if total_modifications > 0 and not self.config.dry_run:
                modified_code = cst_tree.code
                context.file_path.write_text(modified_code, encoding="utf-8")

            return {
                "status": "success",
                "violations_found": len(context.violations),
                "violations_fixed": total_modifications,
                "errors": 0,
                "details": f"Fixed {total_modifications} violations",
                "artifacts": [
                    {
                        "type": "cst_modification",
                        "modifications_made": total_modifications,
                        "preserved_formatting": True,
                    }
                ],
            }

        except Exception as e:
            Logger.error(f"Error applying transformers: {e}")
            return {
                "status": "error",
                "violations_found": len(context.violations),
                "violations_fixed": 0,
                "errors": 1,
                "details": f"Error: {e}",
                "artifacts": [],
            }
