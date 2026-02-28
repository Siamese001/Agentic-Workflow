"""Governance: L0 upward import isolation.

Invariants enforced:
  A) No L0 file contains a MODULE-LEVEL static import of agentic_core.L1_-L6_.
  B) Only allowlisted seam files may use importlib.import_module to load
     agentic_core.L1_-L6_ modules.
  C) Non-allowlisted L0 files must not use importlib targeting higher layers.
"""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[2]
_L0_ROOT = _REPO_ROOT / "agentic_core" / "L0_routing"
_HIGHER_PREFIXES = (
    "agentic_core.L1_",
    "agentic_core.L2_",
    "agentic_core.L3_",
    "agentic_core.L4_",
    "agentic_core.L5_",
    "agentic_core.L6_",
)

# Repo-relative paths of seam files permitted to dynamic-load higher layers.
_SEAM_ALLOWLIST = frozenset(
    [
        "agentic_core/L0_routing/seams/canonical_truth_seam.py",
        "agentic_core/L0_routing/seams/layer_emission_seam.py",
        "agentic_core/L0_routing/seams/observability_seam.py",
        "agentic_core/L0_routing/seams/safety_enforcement_seam.py",
        "agentic_core/L0_routing/seams/safety_kernel_seam.py",
        "agentic_core/L0_routing/seams/safety_reasoning_seam.py",
        "agentic_core/L0_routing/seams/safety_validators_seam.py",
        "agentic_core/L0_routing/seams/vigilance_seam.py",
        "agentic_core/L0_routing/seams/learning_seam.py",
        "agentic_core/L0_routing/seams/elevator_shaft_seam.py",
        "agentic_core/L0_routing/seams/c0_context_retriever.py",
    ]
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError:
        return None


def _is_higher_layer(module: str) -> bool:
    return any(module.startswith(p) for p in _HIGHER_PREFIXES)


def _module_level_upward_imports(tree: ast.Module) -> list[tuple[int, str]]:
    """Return (lineno, module) for module-level static imports of higher layers."""
    hits = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if _is_higher_layer(alias.name):
                    hits.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if _is_higher_layer(mod):
                hits.append((node.lineno, mod))
    return hits


def _importlib_higher_layer_calls(tree: ast.Module) -> list[tuple[int, str]]:
    """Return (lineno, module) for importlib.import_module calls targeting higher layers."""
    hits = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_importlib = (isinstance(func, ast.Attribute) and func.attr == "import_module") or (
            isinstance(func, ast.Name) and func.id == "import_module"
        )
        if not is_importlib:
            continue
        if not node.args:
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            if _is_higher_layer(arg.value):
                hits.append((node.lineno, arg.value))
    return hits


def _all_l0_files() -> list[Path]:
    return sorted(_L0_ROOT.rglob("*.py"))


# ---------------------------------------------------------------------------
# Test A -- zero module-level static upward imports anywhere in L0
# ---------------------------------------------------------------------------


class TestNoStaticUpwardImportsInL0:
    def test_zero_module_level_static_upward_imports(self):
        """No L0 file may have a module-level static import of L1-L6."""
        violations = []
        for py in _all_l0_files():
            tree = _parse(py)
            if tree is None:
                continue
            rel = py.relative_to(_REPO_ROOT).as_posix()
            for lineno, mod in _module_level_upward_imports(tree):
                violations.append(f"{rel}:{lineno}: {mod}")

        assert not violations, "Module-level static upward imports found in L0:\n" + "\n".join(
            f"  {v}" for v in violations
        )

    def test_negative_regression_detector_catches_static_import(self):
        """Detector must flag a synthetic module-level upward import."""
        src = "from agentic_core.L2_execution.engines import validation_orchestrator\n"
        tree = ast.parse(src)
        hits = _module_level_upward_imports(tree)
        assert hits, "Detector failed to catch a module-level upward import"
        assert hits[0][1] == "agentic_core.L2_execution.engines"

    def test_negative_regression_lazy_in_function_not_flagged(self):
        """Lazy in-function imports must NOT be flagged as module-level violations."""
        src = (
            "def _get_x():\n"
            "    from agentic_core.L5_safety.enforcement.activation_gate"
            " import assert_activation_allowed\n"
            "    return assert_activation_allowed\n"
        )
        tree = ast.parse(src)
        hits = _module_level_upward_imports(tree)
        assert not hits, "Lazy in-function import was incorrectly flagged as module-level"


# ---------------------------------------------------------------------------
# Test B -- only allowlisted seam files may importlib-load higher layers
# ---------------------------------------------------------------------------


class TestImportlibAllowlistEnforcement:
    def test_only_allowlisted_seams_use_importlib_for_higher_layers(self):
        """Non-allowlisted L0 files must not importlib-load L1-L6 modules."""
        violations = []
        for py in _all_l0_files():
            tree = _parse(py)
            if tree is None:
                continue
            rel = py.relative_to(_REPO_ROOT).as_posix()
            if rel in _SEAM_ALLOWLIST:
                continue
            for lineno, mod in _importlib_higher_layer_calls(tree):
                violations.append(f"{rel}:{lineno}: importlib.import_module({mod!r})")

        assert not violations, (
            "Non-allowlisted L0 files use importlib to load higher-layer modules:\n"
            + "\n".join(f"  {v}" for v in violations)
        )

    def test_all_allowlisted_seam_files_exist(self):
        """Every path in the allowlist must exist on disk."""
        missing = [p for p in _SEAM_ALLOWLIST if not (_REPO_ROOT / p).exists()]
        assert not missing, "Allowlisted seam files not found on disk:\n" + "\n".join(
            f"  {m}" for m in sorted(missing)
        )

    def test_allowlist_covers_all_seam_files(self):
        """Every *.py under L0_routing/seams/ must be in the allowlist."""
        seams_dir = _L0_ROOT / "seams"
        actual = {
            f.relative_to(_REPO_ROOT).as_posix() for f in seams_dir.glob("*.py") if f.name != "__init__.py"
        }
        unlisted = actual - _SEAM_ALLOWLIST
        assert not unlisted, "Seam files not in allowlist (add or justify):\n" + "\n".join(
            f"  {u}" for u in sorted(unlisted)
        )

    def test_negative_regression_importlib_higher_layer_detected(self):
        """Detector must flag importlib.import_module targeting a higher layer."""
        src = (
            "import importlib\nmod = importlib.import_module('agentic_core.L3_orchestration.Orchestrator')\n"
        )
        tree = ast.parse(src)
        hits = _importlib_higher_layer_calls(tree)
        assert hits, "Detector failed to catch importlib targeting a higher layer"
        assert hits[0][1] == "agentic_core.L3_orchestration.Orchestrator"

    def test_negative_regression_importlib_dynamic_var_not_flagged(self):
        """importlib.import_module with a dynamic variable must NOT be flagged."""
        src = "import importlib\nname = some_var.module_name\nmod = importlib.import_module(name)\n"
        tree = ast.parse(src)
        hits = _importlib_higher_layer_calls(tree)
        assert not hits, "Dynamic importlib call was incorrectly flagged"
