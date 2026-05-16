"""Generic nested-ref closure validator."""

from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.app_binding_validation import REQUIRED_BINDING_SECTIONS, infer_repo_root
from agentic_core.runtime.bindings.ref_validators import validate_extended_nested_refs

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_extended_nested_refs_fixture_pass() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    rr = infer_repo_root(pkg.package_root)
    assert rr is not None
    detail = validate_extended_nested_refs(
        section_paths=pkg.section_paths,
        repo_root=rr,
        required_sections=REQUIRED_BINDING_SECTIONS,
    )
    assert detail.status == "PASS"


def test_optional_manifest_declarations_absent_ok() -> None:
    from agentic_core.runtime.bindings.ref_validators import validate_optional_manifest_declarations

    assert validate_optional_manifest_declarations({"sections": {}}) == []
