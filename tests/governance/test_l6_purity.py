"""Governance: L6 purity enforcement — observation only, no persistence.

Invariants enforced (ratchet pattern):
  A) L6 write-primitive count must not exceed the baselined ceiling.
  B) L6 must not import or instantiate FileIo.
  C) Negative regression snippets prove the detector catches violations.

L6 (observability) should be a pure observation layer. The baseline
ceiling captures the current architectural reality and enforces a
monotonic-decrease ratchet toward zero.
"""

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L6_OBSERVABILITY_DIR,
)

pytestmark = pytest.mark.governance

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_L6_ROOT = _REPO_ROOT / L6_OBSERVABILITY_DIR

# Baselined ceiling (post write-gateway refactoring 2026-02).
# Ceiling 1 (was 0): drift_registry.py:132 calls .mkdir(parents=True, exist_ok=True)
# in _persist() to ensure the timeline directory exists before appending.
# Remediation: pre-create the directory at initialisation time via L2 write gateway,
# then decrement this ceiling back to 0.
_L6_WRITE_CEILING = 1

_FORBIDDEN_OS_FUNCS = frozenset({"remove", "rename", "unlink", "makedirs", "mkdir", "rmdir"})
_FORBIDDEN_PATH_METHODS = frozenset({"write_text", "write_bytes", "mkdir", "unlink", "rename", "rmdir"})


# ---------------------------------------------------------------------------
# Shared scanner
# ---------------------------------------------------------------------------


def _scan_write_primitives(root: Path) -> list[str]:
    """Return violation strings for write/mutation primitives."""
    hits: list[str] = []
    for py in sorted(root.rglob("*.py")):
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
                    # Exclude stdout/stderr reconfiguration
                    if (
                        node.args
                        and isinstance(node.args[0], ast.Call)
                        and isinstance(node.args[0].func, ast.Attribute)
                        and node.args[0].func.attr == "fileno"
                    ):
                        continue
                    hits.append(f'{rel}:{node.lineno}: open(..., "{mode}")')

            # .write_text / .write_bytes / .mkdir / .unlink / .rename
            # Skip _wg.* calls (routed through L2 write gateway)
            if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_PATH_METHODS:
                if isinstance(func.value, ast.Name) and func.value.id == "_wg":
                    continue
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


def _scan_fileio_imports(root: Path) -> list[str]:
    """Return FileIo import violations."""
    hits: list[str] = []
    for py in sorted(root.rglob("*.py")):
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
# Test A — L6 write-primitive ratchet
# ---------------------------------------------------------------------------


class TestL6WritePrimitiveRatchet:
    """L6 write-primitive count must not exceed ceiling."""

    def test_l6_does_not_exceed_write_ceiling(self):
        if not _L6_ROOT.exists():
            pytest.fail("L6_observability not found")
        hits = _scan_write_primitives(_L6_ROOT)
        assert len(hits) <= _L6_WRITE_CEILING, (
            f"L6 has {len(hits)} write primitives, "
            f"exceeding ceiling of {_L6_WRITE_CEILING}.\n" + "\n".join(f"  {h}" for h in hits[:20])
        )


# ---------------------------------------------------------------------------
# Test B — no FileIo imports in L6
# ---------------------------------------------------------------------------


class TestL6NoFileIoImports:
    """L6 must not import or instantiate FileIo."""

    def test_no_fileio_imports_in_l6(self):
        if not _L6_ROOT.exists():
            pytest.fail("L6_observability not found")
        hits = _scan_fileio_imports(_L6_ROOT)
        assert not hits, "L6 imports FileIo:\n" + "\n".join(f"  {h}" for h in hits)


# ---------------------------------------------------------------------------
# Test C — negative regression
# ---------------------------------------------------------------------------


class TestL6NegativeRegression:
    """Prove detectors catch L6-relevant patterns."""

    def test_detects_open_append(self):
        src = 'f = open("log.txt", "a")\n'
        tree = ast.parse(src)
        hits = _scan_tree(tree, "fake.py")
        assert any("open" in h for h in hits)

    def test_detects_write_text(self):
        src = "from pathlib import Path\nPath('r').write_text('x')\n"
        tree = ast.parse(src)
        hits = _scan_tree(tree, "fake.py")
        assert any("write_text" in h for h in hits)

    def test_ignores_read_open(self):
        src = 'f = open("data.txt", "r")\n'
        tree = ast.parse(src)
        hits = _scan_tree(tree, "fake.py")
        assert not hits


# ---------------------------------------------------------------------------
# Tree-level helper for negative tests
# ---------------------------------------------------------------------------


def _scan_tree(tree: ast.Module, filename: str) -> list[str]:
    """Scan parsed AST for write primitives."""
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
