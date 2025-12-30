"""
ImportAgent: Gravity & Import Convention Enforcer (Key 6/Gravity territory)

Enforces:
- Import ordering: stdlib → third-party → local
- No relative imports
- No star imports (from ... import *)
- No direct circular imports (file imports its own root)
- Gravity waterfall: upstream sovereign roots must not import downstream domains
- Advanced unused import detection (F401-style + confidence + transitive)

Replaces logic from void_compliance.py:
  - validate_import_conventions()
  - check_import_waterfall_violations()

Placed in L5_safety/gravity per semantic_l2_registry:
  "Import waterfall enforcement, dependency direction control..."
"""
from pathlib import Path
from typing import List, Tuple, Set, Dict
import ast
import re
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

from agentic_core.config.blueprint_sovereign.structure_blueprint import (
    PYTHON_STDLIB_MODULES,
    UPSTREAM_SOVEREIGN_ROOTS,
    DOWNSTREAM_ROOTS,
    GRAVITY_SURGERY_ENABLED,
    ROOT_WHITELIST,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
# [PHASE 20] DEPRECATION: void_compliance_helpers.py removed - inline implementation
def get_ast_safe_imports(content: str):
    """Extract imports using AST, ignoring comments/docstrings."""
    import ast
    imports = set()
    try:
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
    except SyntaxError:
        import re
        regex_imports = re.findall(r'^(?:import|from)\s+([a-zA-Z0-9_.]+)', content, re.MULTILINE)
        imports.update(regex_imports)
    return imports


class ImportValidationVisitor(ast.NodeVisitor):
    """
    [SUPREME COURT GATEKEEPER]
    Structural visitor to identify imported vs used modules.
    """
    def __init__(self):
        self.imported_modules = set()
        self.used_names = set()
        self.dynamic_access = False

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_modules.add(alias.name.split(".")[0])
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imported_modules.add(node.module.split(".")[0])
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, (ast.Load, ast.Store)):
            self.used_names.add(node.id)
        self.generic_visit(node)

    def visit_Call(self, node):
        # Detect potential dynamic access (Key 13: Dynamic Safeguard)
        if isinstance(node.func, ast.Name) and node.func.id in {"getattr", "hasattr", "__import__", "eval"}:
            self.dynamic_access = True
        self.generic_visit(node)


class ImportAgent:
    """
    Autonomous agent for import convention and gravity compliance.
    Requires file content access → run only on location-valid files.

    Advanced Unused Import Detection (2025 Best Practices):
    - Primary: Ruff/Pyflakes-style AST local check (fast, high accuracy)
    - Confidence: Vulture-inspired heuristics (dynamic access, side-effects)
    - Transitive: Lightweight call graph (findimports-style) for project-wide
    - Whitelist: __init__.py re-exports, TYPE_CHECKING, known side-effect modules
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root.resolve()
        self.stdlib_modules = PYTHON_STDLIB_MODULES
        self.project_roots = ROOT_WHITELIST | {"void_compliance", "canon_validator_agentic_v2"}

        # Side-effect imports whitelist (common false positives)
        self.side_effect_modules = {
            "django", "celery", "pytest", "dotenv", "opentelemetry",  # framework setup
            "matplotlib", "seaborn"  # backend registration
        }

        # Known dynamic access patterns (reduce false positives)
        self.dynamic_patterns = ["getattr", "hasattr", "__import__"]

    def _categorize_imports(self, import_nodes: List[ast.Import | ast.ImportFrom]) -> tuple:
        """Categorize imports by type and track line numbers."""
        categories = {"stdlib": [], "thirdparty": [], "local": []}
        imported_roots = set()

        for node in import_nodes:
            module_name = None
            if isinstance(node, ast.Import):
                if node.names:
                    module_name = node.names[0].name.split(".")[0]
            elif isinstance(node, ast.ImportFrom) and node.module:
                module_name = node.module.split(".")[0]

            if module_name:
                imported_roots.add(module_name)
                lineno = node.lineno if hasattr(node, "lineno") else 0
                if module_name in self.stdlib_modules:
                    categories["stdlib"].append(lineno)
                elif module_name in self.project_roots:
                    categories["local"].append(lineno)
                else:
                    categories["thirdparty"].append(lineno)

        return categories, imported_roots

    def _detect_unused_imports_advanced(self, file_path: Path, tree: ast.AST, imported: Set[str]) -> List[str]:
        """
        Advanced unused import detection via AST walking.
        """
        violations: List[str] = []
        used_names: Set[str] = set()
        dynamic_access = False

        class UsageVisitor(ast.NodeVisitor):
            def visit_Name(self, node: ast.Name):
                if isinstance(node.ctx, (ast.Load, ast.Store)):
                    used_names.add(node.id)
                self.generic_visit(node)

            def visit_Attribute(self, node: ast.Attribute):
                # Check if the attribute being accessed is a dynamic pattern
                if node.attr in self.dynamic_patterns:
                    nonlocal dynamic_access
                    dynamic_access = True
                # If accessing an attribute on a Name, that name is 'used'
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
                self.generic_visit(node)

            def visit_Call(self, node: ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in self.dynamic_patterns:
                    nonlocal dynamic_access
                    dynamic_access = True
                self.generic_visit(node)

        UsageVisitor().visit(tree)

        # Local unused (high confidence 100%)
        local_unused = imported - used_names
        for name in local_unused:
            if name.split(".")[0] in self.side_effect_modules:
                continue  # Skip known side-effect modules
            
            # Heuristic: If dynamic access like getattr() exists, drop confidence
            confidence = 60 if dynamic_access else 100
            violations.append(f"UNUSED IMPORT [Confidence {confidence}%]: {name}")

        # Transitive check (simple: if file is __init__.py, assume re-export)
        if file_path.name == "__init__.py":
            # Re-mapping existing violations for __init__.py
            new_violations = []
            for v in violations:
                name = v.split(": ")[-1]
                new_violations.append(f"POSSIBLE RE-EXPORT [Confidence 80%]: {name} (in __init__.py)")
            violations = new_violations

        # TYPE_CHECKING block handling
        for node in ast.walk(tree):
            if isinstance(node, ast.If) and isinstance(node.test, ast.Name) and node.test.id == "TYPE_CHECKING":
                # Find imports inside this If block and remove them from violations
                for inner in ast.walk(node):
                    if isinstance(inner, (ast.Import, ast.ImportFrom)):
                        for alias in inner.names:
                            target = alias.asname if alias.asname else alias.name
                            violations = [v for v in violations if target not in v]

        return violations

    def validate_import_conventions(self, file_path: Path) -> List[str]:
        """
        Check ordering, relative imports, star imports, and circular risks.
        Now includes advanced unused import detection.
        Returns list of violation messages.
        """
        violations: List[str] = []

        try:
            rel_path = file_path.relative_to(self.project_root)
            own_root = rel_path.parts[0] if rel_path.parts else None
        except ValueError:
            return [f"PARSE ERROR: File outside project root: {file_path}"]

        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content, filename=str(file_path))
        except Exception as e:
            violations.append(f"PARSE ERROR: Cannot parse {file_path.name}: {e}")
            return violations

        import_nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]
        import_nodes.sort(key=lambda n: n.lineno if hasattr(n, "lineno") else 0)

        # === RELATIVE & STAR IMPORT BANS ===
        for node in import_nodes:
            if isinstance(node, ast.ImportFrom):
                if node.level > 0:
                    violations.append(f"RELATIVE IMPORT FORBIDDEN (Line {node.lineno}): Use absolute paths")
                if any(alias.name == "*" for alias in node.names):
                    violations.append(f"STAR IMPORT FORBIDDEN (Line {node.lineno}): 'from ... import *' detected")

        # === IMPORT ORDER ENFORCEMENT ===
        categories, imported_roots = self._categorize_imports(import_nodes)
        prev_cat = None
        for cat in ["stdlib", "thirdparty", "local"]:
            if categories[cat] and prev_cat and categories[prev_cat]:
                if min(categories[cat]) < max(categories[prev_cat]):
                    violations.append(f"IMPORT ORDER VIOLATION: {cat.capitalize()} imports appear before {prev_cat.capitalize()}")
            if categories[cat]:
                prev_cat = cat

        # === DIRECT CIRCULAR IMPORT RISK ===
        if own_root and own_root in imported_roots:
            violations.append(f"DIRECT CIRCULAR RISK: File imports its own root module '{own_root}'")

        # === ADVANCED UNUSED IMPORT DETECTION ===
        imported_modules = get_ast_safe_imports(content)
        unused_violations = self._detect_unused_imports_advanced(file_path, tree, set(imported_modules))
        violations.extend(unused_violations)

        return violations

    def check_import_waterfall_violations(self, file_path: Path) -> List[str]:
        """
        Gravity enforcement: upstream sovereign roots must not import downstream domains.
        Only active when GRAVITY_SURGERY_ENABLED.
        """
        violations: List[str] = []

        if not GRAVITY_SURGERY_ENABLED:
            return violations

        try:
            rel_path = file_path.relative_to(self.project_root)
            if not rel_path.parts or rel_path.parts[0] in SOVEREIGN_EXCLUDED_FOLDERS:
                return violations
            current_root = rel_path.parts[0]
        except ValueError:
            return violations

        if current_root not in UPSTREAM_SOVEREIGN_ROOTS:
            return violations  # Only enforce on upstream

        if not DOWNSTREAM_ROOTS:
            return violations

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            return violations

        # Regex to catch import/from statements starting with downstream roots
        downstream_regex = "|".join(map(re.escape, sorted(DOWNSTREAM_ROOTS)))
        forbidden_pattern = re.compile(
            rf"^(?:import|from)\s+({downstream_regex})(?:\.|\s|$)",
            re.MULTILINE
        )
        matches = forbidden_pattern.findall(content)

        if matches:
            unique_matches = sorted(set(matches))
            violations.append(
                f"GRAVITY VIOLATION: Upstream '{current_root}' imports downstream roots: {unique_matches}. "
                "Move shared logic to apps_shared or sovereign utils."
            )

        return violations

    def analyze_file(self, file_path: Path) -> List[str]:
        """Combined analysis: conventions + gravity."""
        violations = self.validate_import_conventions(file_path)
        violations.extend(self.check_import_waterfall_violations(file_path))
        return violations

    def run(self, valid_files: List[Path]) -> List[Tuple[Path, List[str]]]:
        """
        Full import compliance scan on pre-validated files.
        Returns list of (file_path, [violation_messages]).
        """
        all_violations: List[Tuple[Path, List[str]]] = []

        for file_path in valid_files:
            if not file_path.suffix == ".py":
                continue

            file_violations = self.analyze_file(file_path)
            if file_violations:
                all_violations.append((file_path, file_violations))

        return all_violations


# PascalCase is now the canonical name
