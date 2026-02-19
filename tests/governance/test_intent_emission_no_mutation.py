"""Governance: Strict intent emission — no durable mutation outside L2.2.

Invariants enforced (ratchet pattern):
  A) L3/L4/L5 mutation primitive count must not exceed the baselined ceiling.
  B) L3/L4/L5 must not import or instantiate FileIo.
  C) Negative regression snippets prove the detector catches violations.

The baseline ceiling captures the current architectural reality. Any *new*
mutation primitive added to L3/L4/L5 will fail the test, enforcing a
monotonic-decrease ratchet toward zero.
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
_TARGET_LAYERS = ("L3_orchestration", "L4_state", "L5_safety")

# Baselined ceilings per layer (from inventory scan 2026-02-19).
# These numbers must only ever decrease.
_CEILING = {
    "L3_orchestration": 29,
    "L4_state": 50,
    "L5_safety": 373,
}

_FORBIDDEN_OS_FUNCS = frozenset({"remove", "rename", "unlink", "makedirs", "mkdir", "rmdir"})
_FORBIDDEN_PATH_METHODS = frozenset({"write_text", "write_bytes", "mkdir", "unlink", "rename", "rmdir"})


# ---------------------------------------------------------------------------
# Shared scanner
# ---------------------------------------------------------------------------


def _scan_mutation_primitives(layer_dir: Path) -> list[str]:
    """Return list of violation strings for forbidden mutation primitives."""
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

            # .write_text / .write_bytes / .mkdir / .unlink / .rename
            if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_PATH_METHODS:
                hits.append(f"{rel}:{node.lineno}: .{func.attr}()")

            # os.remove / os.rename etc.
            if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                if func.value.id == "os" and func.attr in _FORBIDDEN_OS_FUNCS:
                    hits.append(f"{rel}:{node.lineno}: os.{func.attr}()")
                if func.value.id == "shutil":
                    hits.append(f"{rel}:{node.lineno}: shutil.{func.attr}()")

            # json.dump(obj, file)
            if isinstance(func, ast.Attribute) and func.attr == "dump":
                if isinstance(func.value, ast.Name) and func.value.id == "json" and len(node.args) >= 2:
                    hits.append(f"{rel}:{node.lineno}: json.dump(obj, file)")
    return hits


def _scan_fileio_imports(layer_dir: Path) -> list[str]:
    """Return list of FileIo import violations."""
    hits: list[str] = []
    for py in sorted(layer_dir.rglob("*.py")):
        try:
            src = py.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        rel = py.relative_to(_REPO_ROOT).as_posix()

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                for alias in node.names:
                    if "FileIo" in alias.name:
                        hits.append(f"{rel}:{node.lineno}: from {mod} import {alias.name}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if "FileIo" in alias.name:
                        hits.append(f"{rel}:{node.lineno}: import {alias.name}")
    return hits


# ---------------------------------------------------------------------------
# Test A — mutation primitive ratchet
# ---------------------------------------------------------------------------


class TestMutationPrimitiveRatchet:
    """Mutation primitive count must not exceed baselined ceiling."""

    @pytest.mark.parametrize("layer", _TARGET_LAYERS)
    def test_layer_does_not_exceed_ceiling(self, layer: str):
        layer_dir = _AGENTIC / layer
        if not layer_dir.exists():
            pytest.skip(f"{layer} directory not found")
        hits = _scan_mutation_primitives(layer_dir)
        ceiling = _CEILING[layer]
        assert len(hits) <= ceiling, (
            f"{layer} has {len(hits)} mutation primitives, "
            f"exceeding ceiling of {ceiling}.\n"
            f"New violations:\n" + "\n".join(f"  {h}" for h in hits[:20])
        )

    def test_total_does_not_exceed_aggregate_ceiling(self):
        total = 0
        for layer in _TARGET_LAYERS:
            layer_dir = _AGENTIC / layer
            if not layer_dir.exists():
                continue
            total += len(_scan_mutation_primitives(layer_dir))
        aggregate = sum(_CEILING.values())
        assert total <= aggregate, f"Aggregate mutation primitives ({total}) exceed ceiling ({aggregate})"


# ---------------------------------------------------------------------------
# Test B — no FileIo imports in L3/L4/L5
# ---------------------------------------------------------------------------


class TestNoFileIoImports:
    """L3/L4/L5 must not import or instantiate FileIo."""

    @pytest.mark.parametrize("layer", _TARGET_LAYERS)
    def test_no_fileio_imports(self, layer: str):
        layer_dir = _AGENTIC / layer
        if not layer_dir.exists():
            pytest.skip(f"{layer} directory not found")
        hits = _scan_fileio_imports(layer_dir)
        assert not hits, f"{layer} imports FileIo:\n" + "\n".join(f"  {h}" for h in hits)


# ---------------------------------------------------------------------------
# Test C — negative regression snippets
# ---------------------------------------------------------------------------


class TestNegativeRegressionDetectors:
    """Prove the AST detectors catch forbidden patterns."""

    def test_detects_open_write(self):
        src = 'f = open("out.txt", "w")\n'
        tree = ast.parse(src)
        hits = _scan_mutation_primitives_from_tree(tree, "fake.py")
        assert any("open" in h for h in hits)

    def test_detects_path_write_text(self):
        src = "from pathlib import Path\nPath('x').write_text('y')\n"
        tree = ast.parse(src)
        hits = _scan_mutation_primitives_from_tree(tree, "fake.py")
        assert any("write_text" in h for h in hits)

    def test_detects_shutil_call(self):
        src = "import shutil\nshutil.copy2('a', 'b')\n"
        tree = ast.parse(src)
        hits = _scan_mutation_primitives_from_tree(tree, "fake.py")
        assert any("shutil" in h for h in hits)

    def test_detects_os_remove(self):
        src = "import os\nos.remove('file.txt')\n"
        tree = ast.parse(src)
        hits = _scan_mutation_primitives_from_tree(tree, "fake.py")
        assert any("os.remove" in h for h in hits)

    def test_detects_json_dump_to_file(self):
        src = "import json\njson.dump({'a': 1}, open('f', 'w'))\n"
        tree = ast.parse(src)
        hits = _scan_mutation_primitives_from_tree(tree, "fake.py")
        assert any("json.dump" in h for h in hits)

    def test_detects_fileio_import(self):
        src = "from agentic_core.L2_execution import FileIo\n"
        tree = ast.parse(src)
        hits = _scan_fileio_imports_from_tree(tree, "fake.py")
        assert any("FileIo" in h for h in hits)

    def test_ignores_read_only_open(self):
        src = 'f = open("data.txt", "r")\n'
        tree = ast.parse(src)
        hits = _scan_mutation_primitives_from_tree(tree, "fake.py")
        assert not any("open" in h for h in hits)


# ---------------------------------------------------------------------------
# Tree-level helpers for negative tests
# ---------------------------------------------------------------------------


def _scan_mutation_primitives_from_tree(tree: ast.Module, filename: str) -> list[str]:
    """Scan an already-parsed AST for mutation primitives."""
    hits: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func

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
                hits.append(f'{filename}:{node.lineno}: open(..., "{mode}")')

        if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_PATH_METHODS:
            hits.append(f"{filename}:{node.lineno}: .{func.attr}()")

        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == "os" and func.attr in _FORBIDDEN_OS_FUNCS:
                hits.append(f"{filename}:{node.lineno}: os.{func.attr}()")
            if func.value.id == "shutil":
                hits.append(f"{filename}:{node.lineno}: shutil.{func.attr}()")

        if isinstance(func, ast.Attribute) and func.attr == "dump":
            if isinstance(func.value, ast.Name) and func.value.id == "json" and len(node.args) >= 2:
                hits.append(f"{filename}:{node.lineno}: json.dump(obj, file)")
    return hits


def _scan_fileio_imports_from_tree(tree: ast.Module, filename: str) -> list[str]:
    """Scan an already-parsed AST for FileIo imports."""
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                if "FileIo" in alias.name:
                    hits.append(f"{filename}:{node.lineno}: from {mod} import {alias.name}")
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if "FileIo" in alias.name:
                    hits.append(f"{filename}:{node.lineno}: import {alias.name}")
    return hits
