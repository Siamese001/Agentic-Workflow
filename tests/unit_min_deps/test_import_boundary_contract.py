"""
Structural invariant: agentic_core must NEVER import from ops_scripts.

AST-based deterministic scan. No heuristics. No exceptions.
Guardian hard gate per §28 Layer Boundary Enforcement Lock.
"""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
)

ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = ROOT / AGENTIC_CORE_DIR


def _scan_boundary_violations() -> list[str]:
    """AST scan: find all agentic_core modules importing from ops_scripts."""
    violations: list[str] = []
    for py_file in AGENTIC_CORE.rglob("*.py"):
        if "__pycache__" in py_file.parts:
            continue
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (SyntaxError, UnicodeDecodeError):
            continue

        rel = py_file.relative_to(ROOT)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name and alias.name.startswith(OPS_SCRIPTS_DIR):
                        violations.append(f"{rel}:{node.lineno}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(OPS_SCRIPTS_DIR):
                    violations.append(f"{rel}:{node.lineno}: from {node.module} import ...")
    return violations


class TestAgenticCoreOpsScriptsBoundary:
    """Hard gate: agentic_core must not import ops_scripts."""

    def test_no_agentic_core_imports_ops_scripts(self) -> None:
        violations = _scan_boundary_violations()
        assert not violations, f"Found {len(violations)} agentic_core → ops_scripts import(s):\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_synthetic_violation_detected(self, tmp_path: Path) -> None:
        """Negative test: prove the scanner catches a synthetic violation."""
        fake_module = tmp_path / "fake_module.py"
        fake_module.write_text(
            textwrap.dedent("""\
                from ops_scripts.general import some_function
            """),
            encoding="utf-8",
        )
        try:
            source = fake_module.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(fake_module))
        except SyntaxError:
            pytest.fail("Synthetic violation file has syntax error")

        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith(OPS_SCRIPTS_DIR):
                    found = True
        assert found, "Scanner failed to detect synthetic ops_scripts import"
