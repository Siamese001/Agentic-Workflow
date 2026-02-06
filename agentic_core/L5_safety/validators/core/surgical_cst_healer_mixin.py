"""
CST-based Surgical Healing Mixin - Zero-Loss Healing Implementation

Replaces AST-based healing with LibCST to preserve comments, whitespace,
and formatting while applying surgical modifications.

This is the CST Pivot implementation to prevent data loss.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import libcst as cst

from .cst_transformers_types import (
    create_bare_except_fixer,
    create_blank_line_normalizer,
    create_docstring_inserter,
    create_future_import_inserter,
    create_import_remover,
    create_trailing_whitespace_fixer,
    create_type_hint_inserter,
)
from .surgical_context_types import (
    ASTCoordinate,
    SurgicalContext,
    ViolationConstraint,
)


@dataclass
class CSTModification:
    """Represents a CST modification operation."""

    node_type: str
    line_number: int
    operation: str  # "insert", "delete", "replace"
    new_content: str | None = None
    old_content: str | None = None


class SurgicalCSTTransformer(cst.CSTTransformer):
    """CST transformer that applies surgical modifications while preserving formatting."""

    def __init__(self, context: SurgicalContext):
        self.context = context
        self.modifications_made = 0
        self.modifications: list[CSTModification] = []

        # Convert violations to CST modifications
        self._prepare_modifications()

    def _prepare_modifications(self):
        """Convert violation constraints to CST modifications."""
        for violation in self.context.violations:
            if violation.target_coordinate:
                mod = CSTModification(
                    node_type=violation.constraint_type,
                    line_number=violation.target_coordinate.line,
                    operation=violation.fix_type,
                    new_content=violation.expected_pattern,
                    old_content=violation.actual_pattern,
                )
                self.modifications.append(mod)

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        """Handle ClassDef nodes."""
        return self._apply_modifications_if_needed(original_node, updated_node, "ClassDef")

    def leave_FunctionDef(
        self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef
    ) -> cst.FunctionDef:
        """Handle FunctionDef nodes."""
        return self._apply_modifications_if_needed(original_node, updated_node, "FunctionDef")

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        """Handle Import nodes."""
        return self._apply_modifications_if_needed(original_node, updated_node, "Import")

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        """Handle ImportFrom nodes."""
        return self._apply_modifications_if_needed(original_node, updated_node, "ImportFrom")

    def leave_SimpleStatementLine(
        self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine
    ) -> cst.SimpleStatementLine:
        """Handle SimpleStatementLine nodes (for bare except, etc.)."""
        return self._apply_modifications_if_needed(original_node, updated_node, "SimpleStatementLine")

    def _apply_modifications_if_needed(
        self, original_node: cst.CSTNode, updated_node: cst.CSTNode, node_type: str
    ) -> cst.CSTNode:
        """Apply modifications if this node matches any violation."""
        if not hasattr(original_node, "position") or not original_node.position:
            return updated_node

        line_num = original_node.position.line

        # Find modifications for this line and node type
        line_mods = [m for m in self.modifications if m.line_number == line_num]

        if not line_mods:
            return updated_node

        # Apply modifications
        result_node = updated_node

        for mod in line_mods:
            if mod.operation == "insert" and mod.new_content:
                result_node = self._apply_insertion(result_node, mod)
                self.modifications_made += 1
            elif mod.operation == "delete":
                result_node = self._apply_deletion(result_node, mod)
                self.modifications_made += 1
            elif mod.operation == "replace" and mod.new_content:
                result_node = self._apply_replacement(result_node, mod)
                self.modifications_made += 1

        return result_node

    def _apply_insertion(self, node: cst.CSTNode, modification: CSTModification) -> cst.CSTNode:
        """Apply insertion modification."""
        if isinstance(node, cst.ClassDef) or isinstance(node, cst.FunctionDef):
            # Insert docstring as first statement in body
            docstring = cst.SimpleStatementLine(
                body=[cst.Expr(value=cst.SimpleString(value=f'"{modification.new_content}"'))]
            )

            new_body = [docstring] + list(node.body.body)
            new_module_body = cst.Module(body=new_body)

            if isinstance(node, cst.ClassDef):
                return node.with_changes(body=new_module_body)
            else:  # FunctionDef
                return node.with_changes(body=new_module_body)

        return node

    def _apply_deletion(self, node: cst.CSTNode, modification: CSTModification) -> cst.CSTNode:
        """Apply deletion modification."""
        if isinstance(node, cst.Import) or isinstance(node, cst.ImportFrom):
            # For imports, we need to remove them from the module
            # This is handled at the module level
            return cst.RemoveFromParent()

        return node

    def _apply_replacement(self, node: cst.CSTNode, modification: CSTModification) -> cst.CSTNode:
        """Apply replacement modification."""
        if isinstance(node, cst.SimpleStatementLine):
            # Handle bare except replacement
            if "bare_except" in modification.node_type:
                except_handler = cst.ExceptHandler(
                    body=cst.IndentBlock(
                        body=[cst.SimpleStatementLine(body=[cst.Expr(value=cst.Name(value="pass"))])]
                    )
                )
                return cst.SimpleStatementLine(body=[except_handler])

        return node


class SurgicalCSTHealerMixin:
    """
    CST-based Surgical Healing Mixin.

    Uses LibCST for zero-loss healing that preserves comments, whitespace,
    and formatting while applying precise surgical modifications.
    """

    def heal_surgical_cst(self, context: SurgicalContext) -> dict[str, Any]:
        """
        Perform surgical healing using LibCST for zero-loss modifications.

        Args:
            context: SurgicalContext with all violation details

        Returns:
            Dict with healing results
        """
        try:
            # Verification Gate pre-check to prevent Epistemic Cascade
            if hasattr(self, "gate"):
                for violation in context.violations:
                    # Map violation types to verification actions
                    action_type = self._map_violation_to_action_type(violation.constraint_type)
                    target_node = self._extract_target_node(violation)

                    if target_node and not self.gate.verify_action(
                        context.file_path, action_type, target_node
                    ):
                        return {
                            "status": "skipped",
                            "violations_found": len(context.violations),
                            "violations_fixed": 0,
                            "errors": 0,
                            "skipped": len(context.violations),
                            "details": f"Hallucination detected: Target '{target_node}' not found in AST for action '{action_type}'",
                            "artifacts": [
                                {
                                    "type": "verification_gate_block",
                                    "action_type": action_type,
                                    "target_node": target_node,
                                    "reason": "Target not found in AST",
                                }
                            ],
                        }

            # Parse source with CST (preserves all formatting)
            source_code = context.file_path.read_text(encoding="utf-8")
            cst_tree = cst.parse_module(source_code)

            # Determine which transformer to use based on violations
            total_modifications = 0

            # Handle import removals
            import_remover = create_import_remover(context.violations)
            if import_remover:
                cst_tree = cst_tree.visit(import_remover)
                total_modifications += import_remover.modifications_made

            # Handle docstring insertions
            docstring_inserter = create_docstring_inserter(context.violations)
            if docstring_inserter:
                cst_tree = cst_tree.visit(docstring_inserter)
                total_modifications += docstring_inserter.modifications_made

            # Handle bare except fixes
            bare_except_fixer = create_bare_except_fixer(context.violations)
            if bare_except_fixer:
                cst_tree = cst_tree.visit(bare_except_fixer)
                total_modifications += bare_except_fixer.modifications_made

            # Handle future import insertions
            future_import_inserter = create_future_import_inserter(context.violations)
            if future_import_inserter:
                cst_tree = cst_tree.visit(future_import_inserter)
                total_modifications += future_import_inserter.modifications_made

            # Handle structural fixes - trailing whitespace
            whitespace_fixer = create_trailing_whitespace_fixer(context.violations)
            if whitespace_fixer:
                cst_tree = cst_tree.visit(whitespace_fixer)
                total_modifications += whitespace_fixer.modifications_made

            # Handle structural fixes - blank line normalization
            blank_line_normalizer = create_blank_line_normalizer(context.violations)
            if blank_line_normalizer:
                cst_tree = cst_tree.visit(blank_line_normalizer)
                total_modifications += blank_line_normalizer.modifications_made

            # Handle type hint insertions
            type_hint_inserter = create_type_hint_inserter(context.violations)
            if type_hint_inserter:
                cst_tree = cst_tree.visit(type_hint_inserter)
                total_modifications += type_hint_inserter.modifications_made

            # Check if any modifications were made
            if total_modifications > 0:
                # Generate code with CST (preserves formatting and comments)
                modified_code = cst_tree.code

                # Write the modified code back
                context.file_path.write_text(modified_code, encoding="utf-8")

                return {
                    "status": "success",
                    "violations_found": len(context.violations),
                    "violations_fixed": total_modifications,
                    "errors": 0,
                    "skipped": len(context.violations) - total_modifications,
                    "details": f"Fixed {total_modifications} violations using CST transformers",
                    "artifacts": [
                        {
                            "type": "cst_modification",
                            "modifications_made": total_modifications,
                            "preserved_formatting": True,
                        }
                    ],
                }
            else:
                return {
                    "status": "success",
                    "violations_found": len(context.violations),
                    "violations_fixed": 0,
                    "errors": 0,
                    "skipped": len(context.violations),
                    "details": "No modifications needed",
                    "artifacts": [],
                }

        except Exception as e:
            return {
                "status": "error",
                "violations_found": len(context.violations),
                "violations_fixed": 0,
                "errors": 1,
                "skipped": len(context.violations),
                "details": f"CST healing failed: {str(e)}",
                "artifacts": [
                    {
                        "type": "error",
                        "error": str(e),
                    }
                ],
            }

    def _create_cst_insertion_node(self, violation: ViolationConstraint) -> cst.CSTNode | None:
        """Create CST node for insertion."""
        if violation.constraint_type == "missing_file_classification":
            # Create a comment statement
            pattern = violation.expected_pattern or "# FILE_CLASSIFICATION: UNKNOWN"
            return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value=pattern))])

        return None

    def _find_cst_node_by_coordinate(self, tree: cst.Module, coordinate: ASTCoordinate) -> cst.CSTNode | None:
        """Find CST node at specific coordinate."""

        class CoordinateFinder(cst.CSTVisitor):
            def __init__(self, target_line: int):
                self.target_line = target_line
                self.found_node = None

            def visit_ClassDef(self, node: cst.ClassDef) -> bool:
                if hasattr(node, "position") and node.position and node.position.line == self.target_line:
                    self.found_node = node
                    return False  # Don't visit children
                return True

            def visit_FunctionDef(self, node: cst.FunctionDef) -> bool:
                if hasattr(node, "position") and node.position and node.position.line == self.target_line:
                    self.found_node = node
                    return False  # Don't visit children
                return True

            def visit_Import(self, node: cst.Import) -> bool:
                if hasattr(node, "position") and node.position and node.position.line == self.target_line:
                    self.found_node = node
                    return False
                return True

            def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
                if hasattr(node, "position") and node.position and node.position.line == self.target_line:
                    self.found_node = node
                    return False
                return True

        finder = CoordinateFinder(coordinate.line)
        tree.visit(finder)
        return finder.found_node

    def _map_violation_to_action_type(self, constraint_type: str) -> str:
        """Map violation constraint type to verification gate action type."""
        mapping = {
            "unused_import": "delete_import",
            "missing_import": "modify_function",  # For adding imports
            "bare_except": "modify_function",  # For modifying exception handlers
            "missing_future_import": "modify_function",  # For adding imports
            "trailing_whitespace": "modify_variable",  # Structural change
            "excessive_blank_lines": "modify_variable",  # Structural change
            "missing_docstring": "modify_function",  # For adding docstrings
            "missing_type_hint": "modify_method",  # For adding type hints
        }
        return mapping.get(constraint_type, "modify_function")  # Default fallback

    def _extract_target_node(self, violation: ViolationConstraint) -> str | None:
        """Extract target node name from violation for verification."""
        if hasattr(violation, "target_node") and violation.target_node:
            return violation.target_node

        # Try to extract from expected_pattern or actual_pattern
        if violation.expected_pattern:
            # Extract import name from pattern like "import requests" or "from os import path"
            if "import " in violation.expected_pattern:
                parts = violation.expected_pattern.split()
                if "from" in parts:
                    # Handle "from module import name"
                    import_idx = parts.index("import")
                    if import_idx < len(parts) - 1:
                        return parts[import_idx + 1].strip(",'\"")
                elif "import" in parts:
                    # Handle "import module"
                    import_idx = parts.index("import")
                    if import_idx < len(parts) - 1:
                        return parts[import_idx + 1].strip(",'\"")

        # Try to extract from violation message
        if violation.message:
            if "unused import:" in violation.message:
                return violation.message.split("unused import:")[-1].strip()
            elif "Missing" in violation.message and "import" in violation.message:
                # Extract import name from missing import messages
                words = violation.message.split()
                for i, word in enumerate(words):
                    if word == "import" and i + 1 < len(words):
                        return words[i + 1].strip(",'\"")

        # Fallback: use constraint_type as identifier
        return violation.constraint_type if violation.constraint_type else None
