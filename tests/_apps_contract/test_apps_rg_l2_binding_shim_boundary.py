"""W6/W11 — apps_rg_l2_binding archived shim vs canonical apps_rg.runtime.bindings.l2_binding."""

from __future__ import annotations

import ast
import importlib
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

LEGACY_SHIM_MODULE = "agentic_core.L2_execution.apps_rg_l2_binding"
CORE_SHIM_PATH = REPO_ROOT / "agentic_core" / "L2_execution" / "apps_rg_l2_binding.py"
CANONICAL_MODULE = "apps_rg.runtime.bindings.l2_binding"
CANONICAL_PATH = REPO_ROOT / "apps_rg" / "runtime" / "bindings" / "l2_binding.py"

ALLOWED_SHIM_STRING_REFS: frozenset[str] = frozenset(
    {
        "tests/_apps_contract/test_apps_rg_l2_binding_shim_boundary.py",
        "tests/governance/test_apps_rg_l1_core_boundary.py",
        "ops_scripts/ci/check_agentic_core_addition.py",
        "tests/_apps_contract/test_apps_rg_exit_uwg_l4_no_bypass_boundary.py",
        "docs/reports/agent_inventory/_w11_fanin_scan.py",
        "docs/reports/agent_inventory/_w11_adg_expand.py",
        "apps_rg/runtime/bindings/l2_binding_adapter.py",
    }
)

PRODUCT_ENTRY_MODULES: tuple[str, ...] = (
    "apps_rg.__main__",
    "apps_rg.runtime.orchestration.canonical_dispatch",
    "agentic_core.runtime.entry.apps_rg_dispatch",
)


def _rel(p: Path) -> str:
    return p.relative_to(REPO_ROOT).as_posix()


def archived_shim_path() -> Path:
    matches = sorted(
        (REPO_ROOT / "archives").glob(
            "l2_rationalization_*/agentic_core/L2_execution/apps_rg_l2_binding.py"
        )
    )
    assert matches, "archived shim not found under archives/l2_rationalization_*/"
    return matches[-1]


def _file_imports_shim_module(path: Path) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if node.module == LEGACY_SHIM_MODULE or node.module.endswith(".apps_rg_l2_binding"):
                return True
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == LEGACY_SHIM_MODULE or alias.name.endswith("apps_rg_l2_binding"):
                    return True
    return False


def _python_files_importing_shim() -> list[str]:
    hits: list[str] = []
    archive_path = archived_shim_path()
    for py in REPO_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts or ".venv" in py.parts:
            continue
        if py.resolve() == archive_path.resolve():
            continue
        try:
            if _file_imports_shim_module(py):
                hits.append(_rel(py))
        except (OSError, SyntaxError):
            continue
    return sorted(hits)


def _python_files_mentioning_shim_string() -> list[str]:
    hits: list[str] = []
    for py in REPO_ROOT.rglob("*.py"):
        if "__pycache__" in py.parts or ".venv" in py.parts:
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except OSError:
            continue
        if "apps_rg_l2_binding" not in text:
            continue
        hits.append(_rel(py))
    return sorted(hits)


def test_archived_shim_source_matches_canonical_public_api() -> None:
    """Archived shim re-exports canonical symbols (source inspection, no core import)."""
    shim_text = archived_shim_path().read_text(encoding="utf-8")
    assert "from apps_rg.runtime.bindings.l2_binding import" in shim_text
    canon = importlib.import_module(CANONICAL_MODULE)
    for name in (
        "APPS_RG_L2_CERT_REF",
        "AppsRGQualityGatePolicy",
        "l2_execute_apps_rg",
    ):
        assert name in shim_text
        assert hasattr(canon, name)


def test_canonical_binding_delegates_to_adapter() -> None:
    adapter = importlib.import_module("apps_rg.runtime.bindings.l2_binding_adapter")
    canon = importlib.import_module(CANONICAL_MODULE)
    assert canon.l2_execute_apps_rg is adapter.l2_execute_apps_rg


def test_zero_python_importers_of_legacy_shim_module() -> None:
    importers = _python_files_importing_shim()
    assert importers == [], (
        f"unexpected Python importers of {LEGACY_SHIM_MODULE}:\n" + "\n".join(importers)
    )


def test_shim_string_refs_are_quarantine_evidence_only() -> None:
    refs = _python_files_mentioning_shim_string()
    archive_rel = _rel(archived_shim_path())
    unknown = [p for p in refs if p not in ALLOWED_SHIM_STRING_REFS and p != archive_rel]
    unknown = [p for p in unknown if "l2_binding_adapter.py" not in p and "_generate_l2_inventory.py" not in p]
    unknown = [p for p in unknown if not p.startswith("docs/reports/agent_inventory/w11_")]
    assert not unknown, f"unexpected shim string refs:\n" + "\n".join(unknown)


@pytest.mark.parametrize("mod_name", PRODUCT_ENTRY_MODULES)
def test_product_entry_modules_do_not_import_core_shim(mod_name: str) -> None:
    mod = importlib.import_module(mod_name)
    path = Path(mod.__file__).resolve()
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module == LEGACY_SHIM_MODULE:
            pytest.fail(f"{mod_name} imports {LEGACY_SHIM_MODULE}")
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == LEGACY_SHIM_MODULE:
                    pytest.fail(f"{mod_name} imports {LEGACY_SHIM_MODULE}")


def test_core_shim_removed_canonical_active_archive_retained() -> None:
    assert not CORE_SHIM_PATH.is_file(), "shim must not remain under agentic_core after archive"
    assert CANONICAL_PATH.is_file()
    archive = archived_shim_path()
    assert archive.is_file()
    assert "LEGACY_SHIM" in archive.read_text(encoding="utf-8")
    assert CANONICAL_MODULE.startswith("apps_rg")


def test_w11_archive_manifest_and_rollback_documented() -> None:
    archive = archived_shim_path()
    manifest = archive.parent.parent.parent / "MANIFEST.json"
    assert manifest.is_file()
    rollback = REPO_ROOT / "docs/reports/agent_inventory/w11_rollback_plan.md"
    assert rollback.is_file()
    assert "archives/l2_rationalization" in rollback.read_text(encoding="utf-8")
