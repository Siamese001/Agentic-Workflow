"""Generic binding loader fixtures + manifest helper for native-core proofs."""

from __future__ import annotations

import shutil
from pathlib import Path

from agentic_core.runtime.bindings.app_binding_loader import (
    APP_BINDING_SECTIONS_MANIFEST,
    load_app_binding_package,
)
from agentic_core.runtime.bindings.app_binding_validation import validate_app_binding_package

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def _write_binding_manifest(pkg_root: Path, repo_root: Path) -> None:
    """Clone the canonical fixture package into *pkg_root* (temp harness)."""
    _ = repo_root
    if pkg_root.exists():
        shutil.rmtree(pkg_root)
    shutil.copytree(FIXTURE_PKG, pkg_root)


def test_load_fixture_binding_package() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    assert pkg.app_id == "apps_rg"
    assert "l1_static_plan_profile" in pkg.section_paths


def test_validate_fixture_binding_package_pass() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    result = validate_app_binding_package(pkg)
    assert result.status == "PASS"


def test_write_binding_manifest_roundtrip(tmp_path: Path) -> None:
    root = tmp_path / "pkg"
    _write_binding_manifest(root, REPO_ROOT)
    pkg = load_app_binding_package(root)
    assert pkg.manifest_path.name == APP_BINDING_SECTIONS_MANIFEST
    assert validate_app_binding_package(pkg).status == "PASS"
