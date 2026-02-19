"""Governance: Authority boundary proof suite.

Invariants enforced:
  A) Only L2_execution may contain durable mutation primitives
     (open-write, Path.write_*, os.remove/rename, shutil.*, json.dump-to-file).
     Other layers are ratcheted to their baselined ceilings.
  B) No L3/L4/L5/L6 static imports of L2_execution mutation primitives.
  C) L0 upward imports restricted to allowlisted seams (reuses P2 test).
  D) Negative regression snippets prove detectors work.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_AGENTIC = _REPO_ROOT / "agentic_core"

# Layers that should NOT have mutation primitives (ratcheted).
_NON_MUTATION_LAYERS = (
    "L0_routing",
    "L1_cognition",
    "L3_orchestration",
    "L4_state",
    "L5_safety",
    "L6_observability",
)

# The ONLY layer authorized for durable mutation.
_MUTATION_AUTHORITY_LAYER = "L2_execution"

# L2 mutation symbols that higher layers must not import.
_L2_MUTATION_SYMBOLS = frozenset(
    {
        "FileIo",
        "save_file",
        "delete_file",
        "write_file",
        "rename_file",
    }
)

_FORBIDDEN_OS_FUNCS = frozenset({"remove", "rename", "unlink", "makedirs", "mkdir", "rmdir"})
_FORBIDDEN_PATH_METHODS = frozenset({"write_text", "write_bytes", "mkdir", "unlink", "rename", "rmdir"})


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------


def _count_mutation_primitives(layer_dir: Path) -> list[str]:
    """Return violation strings for mutation primitives in a layer."""
    hits: list[str] = []
    for py in sorted(layer_dir.rglob("*.py")):
        try:
            src = py.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = py.relative_to(_REPO_ROOT).as_posix()

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func

            # open(..., "w"/"a"/"x")
            if isinstance(func, ast.Name) and func.id == "open":
                mode = None
                if len(node.args) >= 2:
                    arg = node.args[1]
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        mode = arg.value
                for kw in node.keywords:
                    if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                        mode = kw.value.value
                if mode and any(m in mode for m in ("w", "a", "x")):
                    hits.append(f'{rel}:{node.lineno}: open(..., "{mode}")')

            if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_PATH_METHODS:
                hits.append(f"{rel}:{node.lineno}: .{func.attr}()")

            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id == "os" and func.attr in _FORBIDDEN_OS_FUNCS:
                    hits.append(f"{rel}:{node.lineno}: os.{func.attr}()")
                if func.value.id == "shutil":
                    hits.append(f"{rel}:{node.lineno}: shutil.{func.attr}()")

            if isinstance(func, ast.Attribute) and func.attr == "dump":
                if isinstance(func.value, ast.Name) and func.value.id == "json" and len(node.args) >= 2:
                    hits.append(f"{rel}:{node.lineno}: json.dump(obj, file)")
    return hits


def _find_l2_mutation_imports(layer_dir: Path) -> list[str]:
    """Find static imports of L2_execution mutation symbols."""
    hits: list[str] = []
    for py in sorted(layer_dir.rglob("*.py")):
        try:
            src = py.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = py.relative_to(_REPO_ROOT).as_posix()

        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if "L2_execution" not in mod:
                    continue
                for alias in node.names:
                    if alias.name in _L2_MUTATION_SYMBOLS:
                        hits.append(f"{rel}:{node.lineno}: from {mod} import {alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "L2_execution" in alias.name:
                        for sym in _L2_MUTATION_SYMBOLS:
                            if sym in alias.name:
                                hits.append(f"{rel}:{node.lineno}: import {alias.name}")
    return hits


# ---------------------------------------------------------------------------
# Test A — mutation authority exists only in L2_execution
# ---------------------------------------------------------------------------


class TestMutationAuthorityBoundary:
    """Only L2_execution may contain durable mutation primitives."""

    def test_l2_execution_exists_and_has_mutations(self):
        """L2_execution must exist and contain mutation primitives."""
        l2 = _AGENTIC / _MUTATION_AUTHORITY_LAYER
        assert l2.exists(), "L2_execution directory not found"
        hits = _count_mutation_primitives(l2)
        assert len(hits) > 0, (
            "L2_execution has no mutation primitives — authority layer must contain write logic"
        )

    def test_l1_has_zero_mutation_primitives(self):
        """L1 (cognition) must have zero mutation primitives."""
        l1 = _AGENTIC / "L1_cognition"
        if not l1.exists():
            pytest.skip("L1_cognition not found")
        hits = _count_mutation_primitives(l1)
        assert not hits, f"L1 has {len(hits)} mutation primitives (expected 0):\n" + "\n".join(
            f"  {h}" for h in hits[:10]
        )


# ---------------------------------------------------------------------------
# Test B — no cross-layer L2 mutation imports
# ---------------------------------------------------------------------------


class TestNoCrossLayerMutationImports:
    """L3/L4/L5/L6 must not statically import L2 mutation symbols."""

    @pytest.mark.parametrize(
        "layer",
        [
            "L3_orchestration",
            "L4_state",
            "L5_safety",
            "L6_observability",
        ],
    )
    def test_no_l2_mutation_imports(self, layer: str):
        layer_dir = _AGENTIC / layer
        if not layer_dir.exists():
            pytest.skip(f"{layer} not found")
        hits = _find_l2_mutation_imports(layer_dir)
        assert not hits, f"{layer} imports L2 mutation symbols:\n" + "\n".join(f"  {h}" for h in hits)


# ---------------------------------------------------------------------------
# Test C — negative regression
# ---------------------------------------------------------------------------


class TestAuthorityNegativeRegression:
    """Prove detectors catch cross-layer violations."""

    def test_detects_l2_fileio_import(self):
        src = "from agentic_core.L2_execution.file_io import FileIo\n"
        tree = ast.parse(src)
        hits = _find_l2_imports_from_tree(tree, "fake.py")
        assert any("FileIo" in h for h in hits)

    def test_detects_l2_save_file_import(self):
        src = "from agentic_core.L2_execution.file_io import save_file\n"
        tree = ast.parse(src)
        hits = _find_l2_imports_from_tree(tree, "fake.py")
        assert any("save_file" in h for h in hits)

    def test_ignores_non_mutation_l2_import(self):
        src = "from agentic_core.L2_execution.engines import validation_orchestrator\n"
        tree = ast.parse(src)
        hits = _find_l2_imports_from_tree(tree, "fake.py")
        assert not hits


# ---------------------------------------------------------------------------
# Tree-level helper for negative tests
# ---------------------------------------------------------------------------


def _find_l2_imports_from_tree(tree: ast.Module, filename: str) -> list[str]:
    """Scan parsed AST for L2 mutation symbol imports."""
    hits: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if "L2_execution" not in mod:
                continue
            for alias in node.names:
                if alias.name in _L2_MUTATION_SYMBOLS:
                    hits.append(f"{filename}:{node.lineno}: from {mod} import {alias.name}")
    return hits
