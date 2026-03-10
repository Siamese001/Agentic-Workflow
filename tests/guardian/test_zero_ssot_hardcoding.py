"""
Guardian Test: Zero SSOT Hardcoding Violations
================================================

Enforces zero-tolerance policy for hardcoded SSOT path literals across all
enforced sovereign territories.

POLICY:
-------
All path literals that reference sovereign directories MUST use SSOT constants
from `path_constants.py` or `ssot.py`. Hardcoded string literals like
"agentic_core", "apps_rg", "tests", etc. are FORBIDDEN in safe contexts.

SAFE CONTEXTS (must use constants):
- List/tuple/set elements: ["agentic_core", "apps_rg"] → [AGENTIC_CORE_DIR, APPS_RG_DIR]
- Path() constructor args: Path("agentic_core") → Path(AGENTIC_CORE_DIR)
- Simple assignments: x = "tests" → x = TESTS_DIR
- String comparisons: if x == "tools" → if x == TOOLS_DIR
- Collection methods: set.add("apps_lic") → set.add(APPS_LIC_DIR)

LEGITIMATE EXCLUSIONS (allowed to remain as strings):
- Dict keys: {"agentic_core/L0_routing": "L0"}
- Dict values in data schemas: {"path": "agentic_core/L5_safety"}
- Module name checks: module.startswith("agentic_core")
- Dict subscripts: REGISTRY["apps_rg"]["depth"]
- Docstrings and comments
- Default function arguments

TEST STRATEGY:
--------------
1. Scan all 10 enforced territories for hardcoded path literals
2. Use AST analysis to identify safe vs unsafe contexts
3. Assert zero fixable violations remain
4. Document legitimate exclusions for audit trail

USAGE:
------
    pytest tests/guardian/test_zero_ssot_hardcoding.py -v -m guardian

EXPECTED RESULT:
----------------
    PASS - Zero fixable SSOT hardcoding violations
    
FAILURE INDICATES:
------------------
    New hardcoded path literals introduced in safe contexts that must be
    replaced with SSOT constants using the automated fixer:
    
    python ops_scripts/ci/_fix_hardcoded_ssot_literals.py
"""

from __future__ import annotations

import ast
import os
import re
from pathlib import Path
from typing import Any

import pytest

# Import SSOT constants for validation
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ARCHIVES_DIR,
    DOCS_REPORTS_PLANS,
    ENFORCED_TERRITORIES,
    REPORTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# Constants to check for hardcoding
CONST_DEFS: list[tuple[str, str, str]] = [
    ("L3_ORCHESTRATION_DIR", L3_ORCHESTRATION_DIR, "path_constants"),
    ("L6_OBSERVABILITY_DIR", L6_OBSERVABILITY_DIR, "path_constants"),
    ("L1_COGNITION_DIR", L1_COGNITION_DIR, "path_constants"),
    ("L2_EXECUTION_DIR", L2_EXECUTION_DIR, "path_constants"),
    ("L0_MAINTENANCE_DIR", L0_MAINTENANCE_DIR, "path_constants"),
    ("L5_SAFETY_DIR", L5_SAFETY_DIR, "path_constants"),
    ("L4_STATE_DIR", L4_STATE_DIR, "path_constants"),
    ("AGENTIC_CORE_DIR", AGENTIC_CORE_DIR, "path_constants"),
    ("APPS_RG_DIR", APPS_RG_DIR, "path_constants"),
    ("APPS_LIC_DIR", APPS_LIC_DIR, "path_constants"),
    ("APPS_SHARED_DIR", APPS_SHARED_DIR, "path_constants"),
    ("OPS_SCRIPTS_DIR", OPS_SCRIPTS_DIR, "path_constants"),
    ("TESTS_DIR", TESTS_DIR, "path_constants"),
    ("TOOLS_DIR", TOOLS_DIR, "path_constants"),
    ("SYSTEM_LEARNING_DIR", SYSTEM_LEARNING_DIR, "path_constants"),
    ("DOCS_REPORTS_PLANS", DOCS_REPORTS_PLANS, "ssot"),
    ("ARCHIVES_DIR", ARCHIVES_DIR, "ssot"),
    ("REPORTS_DIR", REPORTS_DIR, "ssot"),
]

# Path-like function names
_PATH_CALLS = {
    "Path", "PurePath", "PurePosixPath", "PureWindowsPath",
    "walk", "makedirs", "mkdir", "listdir", "scandir", "isdir",
    "isfile", "exists", "join", "abspath", "realpath", "relpath",
    "expanduser", "glob", "rglob"
}


class _SafePositionCollector(ast.NodeVisitor):
    """Collect positions of string literals in safe-to-replace contexts."""

    def __init__(self) -> None:
        self._safe: set[tuple[int, int]] = set()
        self._parent: list[ast.AST] = []

    @property
    def safe(self) -> set[tuple[int, int]]:
        return self._safe

    def _push(self, node: ast.AST) -> None:
        self._parent.append(node)

    def _pop(self) -> None:
        self._parent.pop()

    def _mark(self, node: ast.Constant) -> None:
        self._safe.add((node.lineno, node.col_offset))

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self._push(node)
            self.visit(child)
            self._pop()

    def visit_Constant(self, node: ast.Constant) -> None:
        if not isinstance(node.value, str):
            return
        if not self._parent:
            return

        parent = self._parent[-1]

        # Safe: element in a List/Tuple/Set
        if isinstance(parent, (ast.List, ast.Tuple, ast.Set)):
            all_flat = all(
                isinstance(el, (ast.Constant, ast.Name, ast.Attribute))
                for el in parent.elts
            )
            if all_flat:
                gp = self._parent[-2] if len(self._parent) >= 2 else None
                if isinstance(gp, ast.Dict):
                    return
                self._mark(node)
            return

        # Safe: simple assignment X = "value"
        if isinstance(parent, ast.Assign):
            if parent.value is node:
                self._mark(node)
            return
        if isinstance(parent, ast.AnnAssign):
            if parent.value is node:
                self._mark(node)
            return

        # Safe: Path("value") / .add("value") / .append("value")
        if isinstance(parent, ast.Call):
            func = parent.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name in _PATH_CALLS:
                if node in parent.args:
                    self._mark(node)
                return
            if func_name in ("add", "append", "discard", "remove"):
                if len(parent.args) == 1 and parent.args[0] is node and not parent.keywords:
                    self._mark(node)
            return

        # Safe: "value" in x / x == "value"
        if isinstance(parent, ast.Compare):
            ops_safe = all(
                isinstance(op, (ast.In, ast.NotIn, ast.Eq, ast.NotEq))
                for op in parent.ops
            )
            if ops_safe:
                if parent.left is node:
                    self._mark(node)
                elif node in parent.comparators:
                    self._mark(node)
            return

        # Safe: BinOp root / "reports"
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div):
            if parent.right is node:
                if isinstance(parent.left, (ast.Name, ast.BinOp, ast.Attribute, ast.Call)):
                    self._mark(node)
            return


def _collect_safe_positions(source: str) -> set[tuple[int, int]]:
    """Collect line/col positions of string literals in safe contexts."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return set()
    collector = _SafePositionCollector()
    collector.visit(tree)
    return collector.safe


def _scan_file_for_violations(fpath: Path) -> list[dict[str, Any]]:
    """Scan a single file for fixable SSOT hardcoding violations."""
    try:
        content = fpath.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return []

    lines = content.splitlines()
    safe_positions = _collect_safe_positions(content)
    violations = []

    for const, literal, _ in CONST_DEFS:
        # Skip if constant already in file and literal not present
        if const in content and literal not in content:
            continue

        pat = re.compile(r"""(?P<q>['"])""" + re.escape(literal) + r"""(?P=q)""")

        for lineno, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("import ") or stripped.startswith("from "):
                continue

            match = pat.search(line)
            if not match:
                continue

            col_offset = match.start() + 1  # +1 for quote
            if (lineno, col_offset) in safe_positions:
                violations.append({
                    "file": str(fpath),
                    "line": lineno,
                    "const": const,
                    "literal": literal,
                    "text": line.strip(),
                })

    return violations


@pytest.mark.guardian
def test_zero_ssot_hardcoding_violations():
    """
    GUARDIAN: Assert zero fixable SSOT hardcoding violations across all enforced territories.
    
    This test scans all Python files in the 10 enforced sovereign territories and
    validates that no hardcoded path literals exist in safe contexts where they
    should be replaced with SSOT constants.
    
    FAILURE INDICATES:
        New hardcoded path literals have been introduced. Run the automated fixer:
        
        python ops_scripts/ci/_fix_hardcoded_ssot_literals.py
        
    LEGITIMATE EXCLUSIONS:
        - Dict keys/values in data schemas
        - Module name prefix checks (e.g., module.startswith("agentic_core"))
        - Dict subscripts (e.g., REGISTRY["apps_rg"]["depth"])
        - Docstrings and comments
        - Default function arguments
    """
    ROOT = Path(__file__).resolve().parents[2]
    all_violations = []

    # Scan all enforced territories
    for territory in sorted(ENFORCED_TERRITORIES):
        scan_root = ROOT / territory
        if not scan_root.exists():
            continue

        for dirpath, dirs, files in os.walk(scan_root):
            # Exclude sovereign excluded folders
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]

            for fname in files:
                if not fname.endswith(".py"):
                    continue

                fpath = Path(dirpath) / fname

                # Skip SSOT definition files themselves
                rel_path = fpath.relative_to(ROOT).as_posix()
                if "structure_blueprint" in rel_path or "path_constants" in rel_path:
                    continue

                violations = _scan_file_for_violations(fpath)
                all_violations.extend(violations)

    # Assert zero fixable violations
    if all_violations:
        violation_summary = "\n".join([
            f"  {v['file']}:{v['line']} [{v['const']}] {v['literal']!r} in: {v['text'][:80]}"
            for v in all_violations[:20]
        ])
        total = len(all_violations)
        msg = (
            f"\n{'='*80}\n"
            f"SSOT HARDCODING VIOLATIONS DETECTED: {total} fixable violations found\n"
            f"{'='*80}\n\n"
            f"The following hardcoded path literals must be replaced with SSOT constants:\n\n"
            f"{violation_summary}\n"
        )
        if total > 20:
            msg += f"\n... and {total - 20} more violations\n"
        msg += (
            f"\n{'='*80}\n"
            f"FIX: Run the automated fixer to replace all hardcoded literals:\n"
            f"{'='*80}\n\n"
            f"    python ops_scripts/ci/_fix_hardcoded_ssot_literals.py\n\n"
            f"This will replace hardcoded strings with SSOT constants and inject\n"
            f"the necessary imports automatically.\n"
        )
        pytest.fail(msg)

    # Test passes - zero violations
    print(f"\n✓ Zero SSOT hardcoding violations across {len(ENFORCED_TERRITORIES)} enforced territories")


@pytest.mark.guardian
def test_ssot_constants_are_defined():
    """
    GUARDIAN: Verify all SSOT constants used in the hardcoding check are properly defined.
    
    This ensures the test itself is valid and all expected constants exist.
    """
    for const_name, const_value, source in CONST_DEFS:
        assert const_value, f"SSOT constant {const_name} from {source} is empty or None"
        assert isinstance(const_value, str), f"SSOT constant {const_name} must be a string, got {type(const_value)}"
        assert len(const_value) > 0, f"SSOT constant {const_name} must not be empty"

    print(f"\n✓ All {len(CONST_DEFS)} SSOT constants are properly defined")


if __name__ == "__main__":
    # Allow running directly for quick validation
    pytest.main([__file__, "-v", "-m", "guardian"])
