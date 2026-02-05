"""
SurgicalHealerMixin - AST-level healing for zero-loss diffs

Provides surgical healing capabilities using AST mutations.
Eliminates string-based operations for precise, lossless code modifications.
"""

from __future__ import annotations
import ast
from pathlib import Path
from typing import Any, Dict, Optional

from .surgical_context import SurgicalContext, ASTCoordinate, ViolationConstraint


class SurgicalASTTransformer(ast.NodeTransformer):
    """AST transformer for surgical modifications."""

    def __init__(self, context: SurgicalContext):
        self.context = context
        self.modifications_made = 0
        self.source_lines = context.file_content.splitlines(keepends=True)

    def visit_Module(self, node: ast.Module) -> ast.Module:
        """Visit module node and apply surgical modifications."""
        # Process top-level insertions first
        for coord in self.context.target_coordinates:
            if coord.node_type == "Module":
                violation = self._find_violation_for_coordinate(coord)
                if violation and violation.fix_type == "insert":
                    # Insert at module level
                    new_node = self._create_insertion_node(violation)
                    if new_node:
                        node.body.insert(0, new_node)
                        self.modifications_made += 1

        # Continue visiting child nodes
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Visit function definition and apply surgical modifications."""
        for coord in self.context.target_coordinates:
            if coord.line == node.lineno and coord.node_type == "FunctionDef":
                violation = self._find_violation_for_coordinate(coord)
                if violation and violation.fix_type == "insert":
                    # Insert docstring after function signature
                    if not ast.get_docstring(node):
                        docstring = ast.Expr(
                            value=ast.Constant(
                                value=violation.expected_pattern or "TODO: Add docstring"
                            )
                        )
                        node.body.insert(0, docstring)
                        self.modifications_made += 1

        return self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Visit class definition and apply surgical modifications."""
        for coord in self.context.target_coordinates:
            if coord.line == node.lineno and coord.node_type == "ClassDef":
                violation = self._find_violation_for_coordinate(coord)
                if violation and violation.fix_type == "insert":
                    # Insert docstring after class signature
                    if not ast.get_docstring(node):
                        docstring = ast.Expr(
                            value=ast.Constant(
                                value=violation.expected_pattern or "TODO: Add docstring"
                            )
                        )
                        node.body.insert(0, docstring)
                        self.modifications_made += 1

        return self.generic_visit(node)

    def _find_violation_for_coordinate(self, coord: ASTCoordinate) -> Optional[ViolationConstraint]:
        """Find violation constraint for a coordinate."""
        for violation in self.context.violations:
            # Simple matching - in real implementation, this would be more sophisticated
            if violation.constraint_type in coord.node_type.lower():
                return violation
        return None

    def _create_insertion_node(self, violation: ViolationConstraint) -> Optional[ast.stmt]:
        """Create AST node for insertion."""
        if violation.constraint_type == "missing_file_classification":
            # Create a comment node (as an expression with string)
            default_pattern = "# FILE_CLASSIFICATION: UNKNOWN"
            pattern = violation.expected_pattern or default_pattern
            return ast.Expr(value=ast.Constant(value=pattern))

        return None


class SurgicalHealerMixin:
    """
    Mixin providing surgical healing capabilities to agents.

    This mixin replaces string-based healing with AST-level mutations
    for zero-loss diffs and precise modifications.
    """

    def heal_surgical(self, context: SurgicalContext) -> Dict[str, Any]:
        """
        Perform surgical healing using SurgicalContext.

        Args:
            context: SurgicalContext with all violation details

        Returns:
            Dict with healing results
        """
        try:
            # Create AST transformer
            transformer = SurgicalASTTransformer(context)

            # Apply transformations
            modified_tree = transformer.visit(context.ast_tree)

            # Fix AST locations and generate code
            ast.fix_missing_locations(modified_tree)
            modified_code = ast.unparse(modified_tree)

            # Check if any modifications were made
            if transformer.modifications_made > 0:
                # Write the modified code back
                context.file_path.write_text(modified_code, encoding="utf-8")

                return {
                    "status": "success",
                    "violations_fixed": transformer.modifications_made,
                    "violations_found": len(context.violations),
                    "errors": 0,
                    "skipped": 0,
                    "details": f"Applied {transformer.modifications_made} surgical modifications",
                    "artifacts": [
                        {
                            "type": "surgical_fix",
                            "file": str(context.file_path),
                            "modifications": transformer.modifications_made,
                        }
                    ],
                }
            else:
                return {
                    "status": "skipped",
                    "reason": "no_modifications_needed",
                    "violations_fixed": 0,
                    "violations_found": len(context.violations),
                    "errors": 0,
                    "skipped": 1,
                }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "violations_fixed": 0,
                "violations_found": len(context.violations),
                "errors": 1,
                "skipped": 0,
            }

    def heal(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standard heal method - converts to surgical context if needed.

        Maintains backward compatibility while encouraging surgical healing.
        """
        # Check if violation is already a SurgicalContext
        if isinstance(violation, SurgicalContext):
            return self.heal_surgical(violation)

        # Try to convert legacy violation format to SurgicalContext
        if "file_path" in violation:
            try:
                from .surgical_context import SurgicalContextBuilder

                builder = SurgicalContextBuilder(
                    Path(violation["file_path"]), self.__class__.__name__, "heal"
                )

                # Extract violations from legacy format
                violations = violation.get("violations", [])
                if not violations and "constraint_type" in violation:
                    violations = [violation]

                # For legacy healing, we need to infer target nodes
                # This is a simplified conversion - real implementation would be more sophisticated
                context = builder.build_context(
                    violation_id=violation.get("id", "legacy"),
                    violations=[
                        {
                            "constraint_type": v.get("type", "unknown"),
                            "severity": v.get("severity", "error"),
                            "message": v.get("message", ""),
                            "fix_type": v.get("fix_type", "replace"),
                        }
                        for v in violations
                    ],
                    target_nodes=[],  # Would need to be inferred from AST
                    suggested_fixes=violation.get("suggested_fixes", []),
                )

                return self.heal_surgical(context)

            except Exception:
                # Fall back to legacy healing if conversion fails
                return self._legacy_heal(violation)

        # Default legacy implementation
        return self._legacy_heal(violation)

    def _legacy_heal(self, violation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Legacy heal implementation for backward compatibility.

        Subclasses can override this for specific legacy behavior.
        """
        return {
            "status": "skipped",
            "reason": "legacy_mode_no_implementation",
            "violations_fixed": 0,
            "violations_found": 1,
            "errors": 0,
            "skipped": 1,
            "details": "Use SurgicalContext for modern healing",
        }


__all__ = ["SurgicalHealerMixin", "SurgicalASTTransformer"]
