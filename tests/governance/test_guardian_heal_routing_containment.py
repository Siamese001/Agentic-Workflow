"""Governance: Guardian-Heal Orchestrator static containment checks.

AST-based static analysis — no runtime imports of L3 code required.

Invariants enforced:
  A) No new static upward imports in L3_orchestration __init__ files.
  B) guardian_heal_orchestrator.py has zero direct open() write calls.
  C) All mutation in guardian_heal_orchestrator.py delegates to L2 write
     gateway.
  D) No new L3->L5 static module-level imports in __init__ files.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

_REPO_ROOT = Path(__file__).resolve().parents[2]
_L3_ROOT = _REPO_ROOT / "agentic_core" / "L3_orchestration"
_GHO_PATH = _L3_ROOT / "scripts" / "guardian_heal_orchestrator.py"


# ---------------------------------------------------------------------------
# A — No upward imports in __init__ files
# ---------------------------------------------------------------------------


class TestNoNewUpwardImportsInInitFiles:
    """__init__.py files in L3_orchestration must not introduce upward imports."""

    _HIGHER_PREFIXES = (
        "agentic_core.L4_",
        "agentic_core.L5_",
        "agentic_core.L6_",
    )

    def _check_init(self, init_path: Path) -> list[str]:
        if not init_path.exists():
            return []
        tree = ast.parse(init_path.read_text(encoding="utf-8"))
        violations = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod.startswith(p) for p in self._HIGHER_PREFIXES):
                    violations.append(f"{init_path.name}:{node.lineno}: {mod}")
        return violations

    def test_l3_init_no_upward_imports(self) -> None:
        violations = self._check_init(_L3_ROOT / "__init__.py")
        assert not violations, f"Upward imports in L3 __init__.py: {violations}"

    def test_l3_scripts_init_no_upward_imports(self) -> None:
        violations = self._check_init(_L3_ROOT / "scripts" / "__init__.py")
        assert not violations, f"Upward imports in scripts/__init__.py: {violations}"

    def test_l3_engines_init_no_upward_imports(self) -> None:
        violations = self._check_init(_L3_ROOT / "engines" / "__init__.py")
        assert not violations, f"Upward imports in engines/__init__.py: {violations}"


# ---------------------------------------------------------------------------
# B — Zero direct open() write calls in guardian_heal_orchestrator.py
# ---------------------------------------------------------------------------

_WRITE_MODE_RE = re.compile(r"""open\s*\([^)]*['"][wa]""")


class TestGHONoDirectWrites:
    """guardian_heal_orchestrator.py must not contain direct file writes."""

    def test_no_open_write_calls(self) -> None:
        """AST scan: no open() calls with write mode in GHO script."""
        if not _GHO_PATH.exists():
            pytest.skip("guardian_heal_orchestrator.py not present")
        src = _GHO_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src)
        violations = []
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if isinstance(func, ast.Name) and func.id == "open":
                for arg in node.args[1:]:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if "w" in arg.value or "a" in arg.value:
                            violations.append(f"line {node.lineno}: open(..., '{arg.value}')")
        assert not violations, (
            "Direct write-mode open() calls found in "
            "guardian_heal_orchestrator.py:\n" + "\n".join(f"  {v}" for v in violations)
        )


# ---------------------------------------------------------------------------
# C — All mutation delegates to L2 write gateway
# ---------------------------------------------------------------------------


class TestGHOMutationDelegation:
    """All mutation in GHO must go through _wg (L2 write gateway)."""

    _MUTATION_PRIMITIVES = (
        "write_text",
        "write_bytes",
        "unlink",
        "rmtree",
        "os.remove",
        "shutil.rmtree",
    )

    def test_no_direct_mutation_primitives(self) -> None:
        """No direct filesystem mutation primitives in GHO."""
        if not _GHO_PATH.exists():
            pytest.skip("guardian_heal_orchestrator.py not present")
        src = _GHO_PATH.read_text(encoding="utf-8")
        violations = []
        for i, line in enumerate(src.splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("#"):
                continue
            for prim in self._MUTATION_PRIMITIVES:
                if prim in stripped and "_wg." not in stripped:
                    violations.append(f"line {i}: {stripped[:80]}")
        assert not violations, "Direct mutation primitives (not via _wg) found:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_write_gateway_is_sole_mutation_path(self) -> None:
        """_wg usage confirms L2 write gateway delegation."""
        if not _GHO_PATH.exists():
            pytest.skip("guardian_heal_orchestrator.py not present")
        src = _GHO_PATH.read_text(encoding="utf-8")
        wg_calls = [
            line.strip() for line in src.splitlines() if "_wg." in line and not line.strip().startswith("#")
        ]
        wg_ops = {c.split("_wg.")[1].split("(")[0] for c in wg_calls}
        assert "write_json" in wg_ops, "_wg.write_json not found — mutation not routed through L2"
        assert "remove_file" in wg_ops, "_wg.remove_file not found — cleanup not routed through L2"


# ---------------------------------------------------------------------------
# D — No new L3->L5 static module-level imports in __init__ files
# ---------------------------------------------------------------------------


class TestDirectoryWideUpwardImportFreeze:
    """Verify no new static upward imports introduced by integration."""

    _L5_PREFIX = "agentic_core.L5_"

    def _module_level_imports(self, path: Path, prefix: str) -> list[str]:
        """Find module-level imports matching prefix."""
        if not path.exists():
            return []
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            return []
        hits = []
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if mod.startswith(prefix):
                    hits.append(f"{path.name}:{node.lineno}: {mod}")
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith(prefix):
                        hits.append(f"{path.name}:{node.lineno}: {alias.name}")
        return hits

    def test_no_l5_imports_in_l3_init_files(self) -> None:
        """No __init__.py in L3 may statically import L5."""
        init_files = list(_L3_ROOT.rglob("__init__.py"))
        violations = []
        for f in init_files:
            violations.extend(self._module_level_imports(f, self._L5_PREFIX))
        assert not violations, "L3 __init__ files import L5:\n" + "\n".join(f"  {v}" for v in violations)
