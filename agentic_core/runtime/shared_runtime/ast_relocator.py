import ast
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# [GRAVITY] Resolve project root for relative path calculation
try:
    project_root = Path(__file__).resolve().parents[3]
except IndexError:
    project_root = Path.cwd()

class ASTRelocator(ast.NodeVisitor):
    """
    [L6 SURGERY] AST-based code relocation engine.
    Surgically extracts classes/functions and calculates their sovereign coordinates.
    """
    def __init__(self, file_path: Path, content: str):
        self.file_path = file_path
        self.content_lines = content.splitlines()
        self.tree = ast.parse(content)
        self.entities: List[Dict] = []
        self.current_class: Optional[str] = None

    def visit_ClassDef(self, node: ast.ClassDef):
        """Capture top-level classes."""
        self.entities.append({
            "type": "class",
            "name": node.name,
            "lineno": node.lineno,
            # Python 3.8+ support for decorators in line count
            "start_line": getattr(node, 'lineno', node.lineno), 
            "end_lineno": getattr(node, 'end_lineno', node.lineno),
            "node": node,
            "suggested_location": self._suggest_placement(node.name)
        })
        # Track context to skip inner functions
        old_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = old_class

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Capture top-level functions (skip methods)."""
        if self.current_class:
            return self.generic_visit(node)

        self.entities.append({
            "type": "function",
            "name": node.name,
            "lineno": node.lineno,
            "start_line": getattr(node, 'lineno', node.lineno),
            "end_lineno": getattr(node, 'end_lineno', node.lineno),
            "node": node,
            "suggested_location": self._suggest_placement(node.name)
        })
        self.generic_visit(node)

    def _suggest_placement(self, name: str) -> Tuple[str, str]:
        """
        [SSOT MAPPING] Heuristic mapping to L1/L2 coordinates.
        Returns (L1_Folder, L2_Folder).
        """
        name_lower = name.lower()

        # L5 Safety
        if any(k in name_lower for k in ["guard", "security", "protect", "policy", "law"]):
            return ("L5_safety", "guardrails")
        if any(k in name_lower for k in ["validator", "check", "verify"]):
            return ("L5_safety", "validators")

        # L4 State
        if any(k in name_lower for k in ["memory", "context", "history", "log"]):
            return ("L4_state", "memory")
        if any(k in name_lower for k in ["file", "disk", "storage"]):
            return ("L4_state", "filesystem")

        # L2 Execution
        if any(k in name_lower for k in ["tool", "search", "api", "client", "scrape"]):
            return ("L2_execution", "tool_registry")
        
        # L3 Orchestration
        if any(k in name_lower for k in ["agent", "manager", "orchestrator", "workflow"]):
            return ("L3_orchestration", "workflow_engines")

        # Config / Schemas
        if any(k in name_lower for k in ["config", "setting", "env"]):
            return ("config", "environments")
        if any(k in name_lower for k in ["schema", "model", "type", "request"]):
            return ("schemas", "models")

        # Default Fallback
        return ("utils", "helpers")

    def get_movable_entities(self) -> List[Dict]:
        self.visit(self.tree)
        return self.entities

    @staticmethod
    def extract_entity_code(content_lines: List[str], start: int, end: int) -> str:
        """Surgically extract code block including decorators."""
        # Convert 1-based lineno to 0-based index
        # Note: Decorators are usually included in lineno in Py3.8+
        lines = content_lines[start-1:end]
        return "\n".join(lines) + "\n"

    @staticmethod
    def generate_import_fix(old_path: Path, new_path: Path, entity_name: str) -> str:
        """Generate the import string required to access the moved entity."""
        try:
            # Calculate module path relative to project root
            rel_path = new_path.relative_to(project_root)
            module_path = str(rel_path.with_suffix('')).replace('/', '.').replace('\\', '.')
            return f"from {module_path} import {entity_name}"
        except ValueError:
            return f"# Could not resolve import for {entity_name}"
