"""
Deterministic location invariant test for mixin classes.
Fails if any class ending with 'Mixin' is defined outside agentic_core/mixins/.
Runtime: <2s (AST-only, no imports of agentic_core).
"""

from __future__ import annotations

import ast
from pathlib import Path

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
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CANONICAL = REPO_ROOT / AGENTIC_CORE_DIR / "mixins"
AGENTIC_CORE = REPO_ROOT / AGENTIC_CORE_DIR


def _find_mixin_classes_outside_canonical() -> list[str]:
    """AST-scan all agentic_core/**/*.py for class *Mixin outside canonical."""
    violations: list[str] = []
    canonical_resolved = CANONICAL.resolve()
    for py in sorted(AGENTIC_CORE.rglob("*.py")):
        if "__pycache__" in str(py):
            continue
        try:
            py.resolve().relative_to(canonical_resolved)
            continue
        except ValueError:
            pass
        try:
            tree = ast.parse(py.read_text(encoding="utf-8"), filename=str(py))
        except (SyntaxError, UnicodeDecodeError, OSError):
            continue
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ClassDef) and node.name.endswith("Mixin"):
                rel = str(py.relative_to(REPO_ROOT)).replace("\\", "/")
                violations.append(f"{rel}:{node.lineno} class {node.name}")
    return violations


def test_no_mixin_definitions_outside_canonical():
    """FAIL if any class ending with Mixin is defined outside agentic_core/mixins/."""
    violations = _find_mixin_classes_outside_canonical()
    assert violations == [], f"{len(violations)} Mixin class(es) outside canonical folder:\n" + "\n".join(
        violations,
    )
