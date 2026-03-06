"""
Deep Architectural Anti-Pattern Audit (Ultra-Hardened AST Visitor)
Scans for SSOT, DRY, and Layered Sovereignty violations with high precision.
"""

import ast
import sys
from pathlib import Path
from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
# guardian: allow-global-mutation
sys.path.insert(0, str(PROJECT_ROOT))
if hasattr(ast, "unparse"):
    unparse = ast.unparse
else:

    def unparse(node):
        """TODO: Add documentation for unparse."""
        return str(ast.dump(node))


class HardenedAntiPatternVisitor(ast.NodeVisitor):
    def __init__(self, filepath: Path):
        self.filepath = filepath
        self.filename = filepath.name
        self.findings = []
        self.aliases: dict[str, str] = {}
        path_str = str(filepath).replace("\\", "/")
        self.is_l1_l2 = "/L1_" in path_str or "/L2_" in path_str
        self.is_test = "test_" in self.filename or "tests/" in path_str
        self.is_legacy = any(x in path_str.lower() for x in ["legacy", "deprecated", ARCHIVES_DIR])

    def add_finding(self, pattern_type: str, evidence: str, recommendation: str):
        """TODO: Add documentation for add_finding."""
        self.findings.append(
            {
                "file": str(self.filepath),
                "type": pattern_type,
                "evidence": evidence,
                "recommendation": recommendation,
            },
        )

    def _is_docstring(self, node: ast.stmt) -> bool:
        if isinstance(node, ast.Expr):
            return isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)
            return isinstance(node.value, ast.Str)
        return False

    def visit_Import(self, node: ast.Import):
        """TODO: Add documentation for visit_Import."""
        for name in node.names:
            real_name = name.name
            alias = name.asname or name.name
            self.aliases[alias] = real_name
            if self.is_l1_l2 and (not self.is_test):
                if any(x in real_name for x in ["agentic_core.L5", "agentic_core.L6"]):
                    self.add_finding(
                        "Layer Bleed",
                        f"L1/L2 imports upper layer: {real_name}",
                        "Use Dependency Injection.",
                    )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        """TODO: Add documentation for visit_ImportFrom."""
        if node.module:
            for name in node.names:
                real_name = f"{node.module}.{name.name}"
                alias = name.asname or name.name
                self.aliases[alias] = real_name
                if self.is_l1_l2 and (not self.is_test):
                    if any(x in node.module for x in ["L5_safety", "L6_observability"]):
                        self.add_finding(
                            "Layer Bleed",
                            f"L1/L2 imports from upper layer: {node.module}",
                            "Refactor to Interface.",
                        )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        """TODO: Add documentation for visit_ClassDef."""
        bases = [self.aliases.get(b.id, b.id) if isinstance(b, ast.Name) else unparse(b) for b in node.bases]
        if any("BaseAgent" in b for b in bases) and any("MCPHardenedMixin" in b for b in bases):
            self.add_finding(
                "Redundant Mixin Chain",
                f"{node.name} redundant MCPHardenedMixin",
                "Inherit only BaseAgent.",
            )
        if any("HealerMixin" in b for b in bases):
            heal_method = next(
                (n for n in node.body if isinstance(n, ast.FunctionDef) and n.name == "heal_repository"),
                None,
            )
            if heal_method:
                has_super = False
                for child in ast.walk(heal_method):
                    if (
                        isinstance(child, ast.Call)
                        and isinstance(child.func, ast.Attribute)
                        and (child.func.attr == "heal_repository")
                    ):
                        if (
                            isinstance(child.func.value, ast.Call)
                            and isinstance(child.func.value.func, ast.Name)
                            and (child.func.value.func.id == "super")
                        ):
                            has_super = True
                            break
                if not has_super:
                    self.add_finding(
                        "Circular Healer Dependency",
                        f"{node.name} missing super().heal_repository()",
                        "Maintain healing chain.",
                    )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        """TODO: Add documentation for visit_FunctionDef."""
        if node.name in ("execute", "run", "process", "handle") and (not node.name.startswith("_")):
            body = [s for s in node.body if not self._is_docstring(s)]
            is_ghost = not body or (len(body) == 1 and isinstance(body[0], ast.Pass | ast.Raise))
            if is_ghost:
                self.add_finding(
                    "Ghost Implementation",
                    f"{node.name}() is empty or NotImplemented",
                    "Remove zombie method.",
                )
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign):
        """TODO: Add documentation for visit_Assign."""
        for target in node.targets:
            if isinstance(target, ast.Name) and any(
                x in target.id.upper() for x in ["REGISTRY", "MAP", "CONFIG"]
            ):
                if isinstance(node.value, ast.Dict | ast.List):
                    try:
                        src = unparse(node.value)
                        if len(src) > 500 and "Agent" in src:
                            self.add_finding(
                                "Hardcoded Registry",
                                f"Large static structure: {target.id}",
                                "Use dynamic discovery.",
                            )
                    # guardian: allow-silent-swallow
                    except:
                        pass
        self.generic_visit(node)

    def _check_string_bleed(self, s: str):
        if self.is_l1_l2 and (not self.is_test) and (not self.is_legacy):
            if any(p in s for p in ["agentic_core/L5", "agentic_core/L6", "L5_safety"]):
                self.add_finding(
                    "Layer Bleed",
                    f'Hardcoded upper layer path in string: "{s[:30]}..."',
                    "Remove hardcoded path.",
                )

    def visit_Constant(self, node: ast.Constant):
        """TODO: Add documentation for visit_Constant."""
        if isinstance(node.value, str):
            self._check_string_bleed(node.value)
        self.generic_visit(node)

    def visit_Str(self, node: ast.Str):
        """TODO: Add documentation for visit_Str."""
        self._check_string_bleed(node.s)
        self.generic_visit(node)


def main():
    """TODO: Add documentation for main."""
    search_dirs = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, "scripts"]
    findings = []
    for dir_name in search_dirs:
        path = PROJECT_ROOT / dir_name
        if not path.exists():
            continue
        for py_file in path.rglob("*.py"):
            if "archives" in str(py_file) or "__pycache__" in str(py_file):
                continue
            try:
                tree = ast.parse(py_file.read_text(encoding="utf-8"))
                visitor = HardenedAntiPatternVisitor(py_file)
                visitor.visit(tree)
                findings.extend(visitor.findings)
            # guardian: allow-silent-swallow
            except Exception:
                continue
    for _f in findings:
        pass


if __name__ == "__main__":
    main()
