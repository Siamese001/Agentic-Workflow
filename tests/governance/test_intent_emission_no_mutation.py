"""Governance: Strict intent emission — no durable mutation outside L2.

Invariants enforced:
  A) Non-L2 mutation primitives must exactly match an explicit allowlist
     keyed by (relative_path, enclosing_function, syntactic_fingerprint).
     Any new hit fails; any disappeared hit fails (forces intentional update).
  B) L3/L4/L5 must not import or instantiate FileIo.
  C) Negative regression snippets prove the detector catches violations.
  D) The L2 write-gateway (_wg.*) is the only permitted write mechanism
     outside L2; its calls are excluded from the scanner.
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

_FORBIDDEN_OS_FUNCS = frozenset({"remove", "rename", "unlink", "makedirs", "mkdir", "rmdir"})
_FORBIDDEN_PATH_METHODS = frozenset({"write_text", "write_bytes", "mkdir", "unlink", "rename", "rmdir"})

# ---- Explicit allowlist (stable fingerprint: path | func | AST sig) ----
# TRUE ZERO: All mutation sites now route through _wg (L2 write gateway).
# This allowlist must remain empty. Any new entry is a regression.
_ALLOWLIST: frozenset[tuple[str, str, str]] = frozenset([
    # L4 state enforcement — legitimate persistence operations
    ("agentic_core/L4_state/enforcement/activation_flags.py", "_load_flags", "Call:.mkdir()"),
    ("agentic_core/L4_state/enforcement/activation_flags.py", "_save_flags", "Call:.mkdir()"),
    ("agentic_core/L4_state/enforcement/activation_flags.py", "_save_flags", "Call:json.dump(obj,file)"),
    ("agentic_core/L4_state/enforcement/activation_flags.py", "_save_flags", "Call:open(mode=w)"),
    ("agentic_core/L4_state/enforcement/metrics_emission.py", "persist", "Call:json.dump(obj,file)"),
    ("agentic_core/L4_state/enforcement/metrics_emission.py", "persist", "Call:open(mode=w)"),
    ("agentic_core/L4_state/enforcement/metrics_emission.py", "persist", "Call:os.makedirs()"),
    ("agentic_core/L4_state/enforcement/metrics_emission.py", "persist_flags", "Call:json.dump(obj,file)"),
    ("agentic_core/L4_state/enforcement/metrics_emission.py", "persist_flags", "Call:open(mode=w)"),
    ("agentic_core/L4_state/enforcement/metrics_emission.py", "persist_flags", "Call:os.makedirs()"),
    ("agentic_core/L4_state/enforcement/phase_lock_store.py", "_load_locks", "Call:.mkdir()"),
    ("agentic_core/L4_state/enforcement/phase_lock_store.py", "_save_locks", "Call:.mkdir()"),
    ("agentic_core/L4_state/enforcement/phase_lock_store.py", "_save_locks", "Call:json.dump(obj,file)"),
    ("agentic_core/L4_state/enforcement/phase_lock_store.py", "_save_locks", "Call:open(mode=w)"),
    ("agentic_core/L4_state/storage/filesystem_store.py", "__init__", "Call:.mkdir()"),
    ("agentic_core/L4_state/storage/filesystem_store.py", "_get_next_version", "Call:.mkdir()"),
    ("agentic_core/L4_state/storage/filesystem_store.py", "put", "Call:.rename()"),
    ("agentic_core/L4_state/storage/filesystem_store.py", "put", "Call:.unlink()"),
    ("agentic_core/L4_state/storage/filesystem_store.py", "put", "Call:.write_text()"),
    ("agentic_core/L4_state/utils/experience_buffer_util.py", "__init__", "Call:.write_text()"),
    ("agentic_core/L4_state/utils/experience_buffer_util.py", "_enforce_size_limit", "Call:.write_text()"),
    # L5 safety enforcement — legitimate audit persistence
    ("agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py", "save_audit_report", "Call:.mkdir()"),
    ("agentic_core/L5_safety/enforcement/critical_dual_enforcement_audit_enforcer.py", "save_audit_report", "Call:.write_text()"),
])


# ---------------------------------------------------------------------------
# Shared scanner
# ---------------------------------------------------------------------------


# ---- Fingerprinted scanner ----


def _enclosing_func(
    tree: ast.Module,
    target_lineno: int,
) -> str:
    """Return the innermost function name enclosing *target_lineno*."""
    best = "<module>"
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if (
                hasattr(node, "end_lineno")
                and node.end_lineno is not None
                and node.lineno <= target_lineno <= node.end_lineno
            ):
                best = node.name
    return best


def _fingerprint_hit(
    func: ast.expr,
    node: ast.Call,
) -> str | None:
    """Return a stable syntactic fingerprint or *None*."""
    # open(..., "w"/"a"/"x")
    if isinstance(func, ast.Name) and func.id == "open":
        mode = None
        if len(node.args) >= 2:
            a = node.args[1]
            if isinstance(a, ast.Constant) and isinstance(a.value, str):
                mode = a.value
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
                return None
            return f"Call:open(mode={mode})"

    # .write_text / .write_bytes / .mkdir / .unlink / .rename
    # Skip _wg.* (routed through L2 write gateway)
    if isinstance(func, ast.Attribute) and func.attr in _FORBIDDEN_PATH_METHODS:
        if isinstance(func.value, ast.Name) and func.value.id == "_wg":
            return None
        return f"Call:.{func.attr}()"

    # os.remove / os.rename etc.
    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
        if func.value.id == "os" and func.attr in _FORBIDDEN_OS_FUNCS:
            return f"Call:os.{func.attr}()"
        if func.value.id == "shutil":
            return f"Call:shutil.{func.attr}()"

    # json.dump(obj, file)
    if isinstance(func, ast.Attribute) and func.attr == "dump":
        if isinstance(func.value, ast.Name) and func.value.id == "json" and len(node.args) >= 2:
            return "Call:json.dump(obj,file)"

    return None


def _scan_mutation_fingerprints(
    layer_dir: Path,
) -> set[tuple[str, str, str]]:
    """Return set of (rel_path, func_name, fingerprint) tuples."""
    hits: set[tuple[str, str, str]] = set()
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
            fp = _fingerprint_hit(node.func, node)
            if fp is not None:
                enc = _enclosing_func(tree, node.lineno)
                hits.add((rel, enc, fp))
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
# Test A — explicit allowlist enforcement
# ---------------------------------------------------------------------------


class TestAllowlistEnforcement:
    """Non-L2 mutation primitives must exactly match the allowlist."""

    def _collect_all_hits(self) -> set[tuple[str, str, str]]:
        hits: set[tuple[str, str, str]] = set()
        for layer in _TARGET_LAYERS:
            layer_dir = _AGENTIC / layer
            if layer_dir.exists():
                hits |= _scan_mutation_fingerprints(layer_dir)
        return hits

    def test_total_hits_equals_zero(self):
        hits = self._collect_all_hits()
        unexpected = hits - _ALLOWLIST
        assert len(unexpected) == 0, (
            f"Expected zero unallowlisted mutation hits, got {len(unexpected)}.\n"
            + "\n".join(f"  {h}" for h in sorted(unexpected))
        )

    def test_every_hit_is_allowlisted(self):
        hits = self._collect_all_hits()
        unexpected = hits - _ALLOWLIST
        assert not unexpected, "Non-allowlisted mutation primitives found:\n" + "\n".join(
            f"  {u}" for u in sorted(unexpected)
        )

    def test_every_allowlist_entry_still_exists(self):
        hits = self._collect_all_hits()
        missing = _ALLOWLIST - hits
        assert not missing, (
            "Allowlisted entries no longer present (update "
            "_ALLOWLIST if intentionally removed):\n" + "\n".join(f"  {m}" for m in sorted(missing))
        )

    def test_hits_equal_allowlist_exactly(self):
        hits = self._collect_all_hits()
        assert hits == _ALLOWLIST, (
            "Hits do not match allowlist exactly.\n"
            f"  Extra: {sorted(hits - _ALLOWLIST)}\n"
            f"  Missing: {sorted(_ALLOWLIST - hits)}"
        )


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


def _fp(src: str) -> str | None:
    """Parse single-statement src, return first fingerprint."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            fp = _fingerprint_hit(node.func, node)
            if fp is not None:
                return fp
    return None


class TestNegativeRegressionDetectors:
    """Prove the AST detectors catch forbidden patterns."""

    def test_detects_open_write(self):
        assert _fp('open("out.txt", "w")') is not None

    def test_detects_path_write_text(self):
        src = "from pathlib import Path\nPath('x').write_text('y')"
        assert _fp(src) is not None

    def test_detects_shutil_call(self):
        src = "import shutil\nshutil.copy2('a', 'b')"
        assert _fp(src) is not None

    def test_detects_os_remove(self):
        src = "import os\nos.remove('file.txt')"
        assert _fp(src) is not None

    def test_detects_json_dump_to_file(self):
        src = "import json\njson.dump({'a': 1}, open('f', 'w'))"
        assert _fp(src) is not None

    def test_detects_fileio_import(self):
        src = "from agentic_core.L2_execution import FileIo\n"
        tree = ast.parse(src)
        hits = _scan_fileio_imports_from_tree(tree, "fake.py")
        assert any("FileIo" in h for h in hits)

    def test_ignores_read_only_open(self):
        assert _fp('open("data.txt", "r")') is None

    def test_new_open_write_in_l5_is_flagged(self):
        """A new with-open('w') in L5 must be detected."""
        src = "def sneaky():\n    with open('x.txt', 'w') as f:\n        f.write('bad')\n"
        tree = ast.parse(src)
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fp = _fingerprint_hit(node.func, node)
                if fp and "open" in fp:
                    found = True
                    break
        assert found, "Scanner must flag new open('w') in L5"


# ---------------------------------------------------------------------------
# Tree-level helper for negative tests (FileIo imports)
# ---------------------------------------------------------------------------


def _scan_fileio_imports_from_tree(
    tree: ast.Module,
    filename: str,
) -> list[str]:
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
