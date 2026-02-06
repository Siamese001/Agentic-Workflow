from __future__ import annotations

import ast

"""Brief description of functionality and purpose."""

from pathlib import Path

from agentic_core.L5_safety.validators.structure_blueprint_config import SEMANTIC_L2_REGISTRY

# [GRAVITY] Resolve project root for relative path calculation
try:
    project_root = Path(__file__).resolve().parents[3]
except IndexError:
    project_root = Path.cwd()


# NAMING FIXED: ASTRelocator → AstRelocator
class AstRelocator(ast.NodeVisitor):
    """
    [L6 SURGERY] AST-based code relocation engine.
    Surgically extracts classes/functions and calculates their sovereign coordinates.
    """

    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content_lines = content.splitlines()
        self.tree = ast.parse(content)
        self.entities: list[dict] = []
        self.current_class: str | None = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Capture top-level classes."""
        self.entities.append(
            {
                "type": "class",
                "name": node.name,
                "lineno": node.lineno,
                # Python 3.8+ support for decorators in line count
                "start_line": getattr(node, "lineno", node.lineno),
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "node": node,
                "suggested_location": self._suggest_placement(node, node.name, "Class"),
            },
        )
        # Track context to skip inner functions
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Capture top-level functions (skip methods)."""
        if self.current_class:
            return self.generic_visit(node)

        self.entities.append(
            {
                "type": "function",
                "name": node.name,
                "lineno": node.lineno,
                "start_line": getattr(node, "lineno", node.lineno),
                "end_lineno": getattr(node, "end_lineno", node.lineno),
                "node": node,
                "suggested_location": self._suggest_placement(node, node.name, "Function"),
            },
        )
        self.generic_visit(node)

    def _suggest_placement(self, node: ast.AST, name: str, entity_type: str) -> tuple[str, str, float]:
        """
        [SEMANTIC SCORING] Calculates placement confidence using the Rich Semantic Registry.
        Returns (L1, L2, Confidence_Score).
        """
        best_match = ("utils", "general_helpers", 0.0)
        name_lower = name.lower()
        docstring = ast.get_docstring(node) or ""
        doc_lower = docstring.lower()

        for l1, l2_dict in SEMANTIC_L2_REGISTRY.items():
            for l2, meta in l2_dict.items():
                score = 0.0

                # 1. Name/Keyword Match (Strong Signal)
                for kw in meta.get("keywords", []):
                    if kw in name_lower:
                        score += 3.0
                    elif kw in doc_lower:
                        score += 1.0

                # 2. Entity Type Match (Weak Signal)
                if entity_type in meta.get("entity_types", []):
                    score += 0.5

                # 3. Purpose/Docstring Match (Medium Signal)
                purpose_words = meta.get("purpose", "").lower().split()
                doc_words = set(doc_lower.split())
                # Check for overlap in significant words (len > 3) to avoid "the", "and", etc.
                matches = [w for w in purpose_words if len(w) > 3 and w in doc_words]

                if matches:
                    score += 1.5  # Base score for any match
                    # [BONUS] Reward high semantic overlap
                    if len(matches) > 3:
                        score += 1.0 * len(matches)

                # 4. Base Class Match (High Signal - Structural Proof)
                if entity_type == "Class" and hasattr(node, "bases"):
                    for base in node.bases:
                        # Handle simple names (class A(B)) and attributes (class A(mod.B))
                        base_name = getattr(base, "id", "") or getattr(
                            getattr(base, "attr", None),
                            "value",
                            "",
                        )
                        if base_name and any(base_name in b for b in meta.get("bases", [])):
                            score += 4.0  # Massive boost for explicit inheritance match

                # [WINNER SELECTION]
                if score > best_match[2]:
                    best_match = (l1, l2, score)

        return best_match

    def get_movable_entities(self) -> list[dict]:
        self.visit(self.tree)
        return self.entities

    @staticmethod
    def extract_entity_code(content_lines: list[str], start: int, end: int) -> str:
        """Surgically extract code block including decorators."""
        # Convert 1-based lineno to 0-based index
        # Note: Decorators are usually included in lineno in Py3.8+
        lines = content_lines[start - 1 : end]
        return "\n".join(lines) + "\n"

    @staticmethod
    def generate_import_fix(old_path: Path, new_path: Path, entity_name: str) -> str:
        """Generate the import string required to access the moved entity."""
        try:
            # Calculate module path relative to project root
            rel_path = new_path.relative_to(project_root)
            module_path = str(rel_path.with_suffix("")).replace("/", ".").replace("\\", ".")
            return f"from {module_path} import {entity_name}"
        except ValueError:
            return f"# Could not resolve import for {entity_name}"
