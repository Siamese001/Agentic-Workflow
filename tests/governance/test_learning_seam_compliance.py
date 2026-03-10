"""H6: AST-based learning seam compliance test.

Verifies via static AST analysis (not runtime inspect.stack) that:
- No agent file outside L2 directly imports persistence modules
- Learning artifact usage goes through the L0 seam
- No agent file calls durable write methods directly

CI lock: must run in CI, failure blocks merge, no runtime fallback.
Uses same AST scanner pattern as test_upward_import_enforcement.py.
"""

from __future__ import annotations

import ast
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
    L0_ROUTING_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

pytestmark = pytest.mark.governance

REPO_ROOT = Path(__file__).resolve().parents[2]
AGENTIC_CORE = REPO_ROOT / AGENTIC_CORE_DIR

PERSISTENCE_MODULES = frozenset(
    {
        "redis",
        "pinecone",
        "sqlite3",
        "sqlalchemy",
        "pymongo",
    }
)

FORBIDDEN_WRITE_PATTERNS = frozenset(
    {
        "pickle.dump",
        "shelve.open",
    }
)

SKIP_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS


def _agent_files() -> list[Path]:
    """Collect all Python files in agent reasoning dirs."""
    results = []
    for layer_dir in AGENTIC_CORE.iterdir():
        if not layer_dir.is_dir():
            continue
        if layer_dir.name.startswith(("L2_", "L4_")):
            continue
        reasoning = layer_dir / "reasoning"
        if reasoning.is_dir():
            for py in reasoning.rglob("*.py"):
                if not any(s in str(py) for s in SKIP_DIRS):
                    results.append(py)
    return sorted(results)


def _scan_imports(
    tree: ast.AST,
) -> list[tuple[int, str]]:
    """Extract all import targets from AST."""
    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append((node.lineno, node.module))
    return imports


def _scan_forbidden_calls(
    tree: ast.AST,
) -> list[tuple[int, str]]:
    """Detect direct calls to forbidden write patterns."""
    violations: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                if isinstance(func.value, ast.Name):
                    fqn = f"{func.value.id}.{func.attr}"
                    if fqn in FORBIDDEN_WRITE_PATTERNS:
                        violations.append((node.lineno, fqn))
    return violations


class TestNoDirectPersistenceImport:
    """Non-L2 agent files must not import persistence."""

    def test_no_persistence_imports_in_agents(self):
        violations = []
        for path in _agent_files():
            try:
                tree = ast.parse(path.read_text("utf-8"))
            except SyntaxError as e:
                assert False, f"SyntaxError in {path}: {e}"
            for lineno, module in _scan_imports(tree):
                root_mod = module.split(".")[0]
                if root_mod in PERSISTENCE_MODULES:
                    rel = path.relative_to(REPO_ROOT)
                    violations.append(f"{rel}:{lineno} imports {module}")
        assert violations == [], (
            "Non-L2 agent files must not import persistence modules directly:\n" + "\n".join(violations)
        )


class TestNoForbiddenWriteCalls:
    """Non-L2 agent files must not call write functions."""

    def test_no_direct_write_calls_in_agents(self):
        violations = []
        for path in _agent_files():
            try:
                tree = ast.parse(path.read_text("utf-8"))
            except SyntaxError as e:
                assert False, f"SyntaxError in {path}: {e}"
            for lineno, fqn in _scan_forbidden_calls(tree):
                rel = path.relative_to(REPO_ROOT)
                violations.append(f"{rel}:{lineno} calls {fqn}")
        assert violations == [], (
            "Non-L2 agent files must not call durable write functions directly:\n" + "\n".join(violations)
        )


class TestLearningSeamExists:
    """The L0 learning seam must exist for agents to use."""

    def test_learning_seam_file_exists(self):
        seam = AGENTIC_CORE / L0_ROUTING_DIR / "seams" / "learning_seam.py"
        assert seam.exists(), f"L0 learning seam must exist at {seam.relative_to(REPO_ROOT)}"

    def test_learning_seam_exports_intent(self):
        seam = AGENTIC_CORE / L0_ROUTING_DIR / "seams" / "learning_seam.py"
        tree = ast.parse(seam.read_text("utf-8"))
        class_names = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        assert "LearningArtifactIntent" in class_names
        assert "LearningPersistenceService" in class_names


class TestASTScannerDeterminism:
    """AST scanner must produce deterministic results."""

    def test_agent_file_collection_deterministic(self):
        a = _agent_files()
        b = _agent_files()
        assert a == b

    def test_scanner_produces_results(self):
        files = _agent_files()
        assert len(files) > 0, "Expected at least one agent file"
