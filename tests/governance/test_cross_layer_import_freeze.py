"""Wave 6.2: Cross-Layer Import Freeze Audit.

Extends AST scanner to enforce no L0/L1/L3/L5/L6 imports from:
- L2_execution/*
- L4_state/*
- persistence clients (redis, pinecone, shelve, pickle)

Also includes a regression test that a temporary illegal import
would be detected.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = REPO_ROOT / "agentic_core"

FORBIDDEN_MODULES = {
    "redis",
    "pinecone",
    "shelve",
    "pickle",
    "sqlite3",
    "pymongo",
}

FORBIDDEN_LAYER_PREFIXES = (
    "agentic_core.L2_execution",
    "agentic_core.L4_state",
)

SCANNED_LAYERS = (
    "L0_routing",
    "L1_cognition",
    "L3_orchestration",
    "L5_safety",
    "L6_observability",
)


def _extract_imports(tree: ast.AST) -> list[tuple[int, str]]:
    """Extract all import module names with line numbers."""
    results = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                results.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                results.append((node.lineno, node.module))
    return results


def _scan_layer(layer_name: str) -> list[str]:
    """Scan a layer for forbidden imports."""
    layer_dir = AGENTIC_CORE / layer_name
    if not layer_dir.exists():
        return []
    violations = []
    for py_file in sorted(layer_dir.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue
        try:
            tree = ast.parse(
                py_file.read_text("utf-8"),
                filename=str(py_file),
            )
        except SyntaxError:
            continue
        for lineno, module in _extract_imports(tree):
            for prefix in FORBIDDEN_LAYER_PREFIXES:
                if module.startswith(prefix):
                    rel = py_file.relative_to(REPO_ROOT)
                    violations.append(f"{rel}:{lineno} imports {module}")
            top_module = module.split(".")[0]
            if top_module in FORBIDDEN_MODULES:
                rel = py_file.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{lineno} imports {module}")
    return violations


# Pre-existing violation count as of Phase 6 baseline.
# These are architectural debt in L5/L6 importing from
# L2/L4 — not introduced by hardening work.
BASELINED_VIOLATION_COUNT = 149  # guardian:allow(magic_configuration)


class TestCrossLayerImportFreeze:
    """No NEW L0/L1/L3/L5/L6 imports from L2/L4."""

    def test_no_new_violations(self):
        all_violations = []
        for layer in SCANNED_LAYERS:
            all_violations.extend(_scan_layer(layer))
        assert len(all_violations) <= BASELINED_VIOLATION_COUNT, (
            f"New cross-layer import violations "
            f"({len(all_violations)} > "
            f"{BASELINED_VIOLATION_COUNT}):\n" + "\n".join(all_violations)
        )

    def test_baseline_not_stale(self):
        """Catch if violations are fixed without updating baseline."""
        all_violations = []
        for layer in SCANNED_LAYERS:
            all_violations.extend(_scan_layer(layer))
        assert len(all_violations) >= BASELINED_VIOLATION_COUNT - 5, (
            f"Violation count dropped significantly "
            f"({len(all_violations)} vs baseline "
            f"{BASELINED_VIOLATION_COUNT}). "
            f"Update BASELINED_VIOLATION_COUNT."
        )


class TestRegressionDetection:
    """Verify scanner detects a synthetic violation."""

    def test_synthetic_violation_detected(self):
        code = "from agentic_core.L2_execution.types.llm_replay_types import ReplayBundle\n"
        tree = ast.parse(code)
        imports = _extract_imports(tree)
        assert len(imports) == 1
        _, module = imports[0]
        assert any(module.startswith(p) for p in FORBIDDEN_LAYER_PREFIXES)

    def test_persistence_client_detected(self):
        code = "import redis\n"
        tree = ast.parse(code)
        imports = _extract_imports(tree)
        assert len(imports) == 1
        _, module = imports[0]
        assert module.split(".")[0] in FORBIDDEN_MODULES
