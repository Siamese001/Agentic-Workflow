"""Generic profile validators — structural presence only."""

from __future__ import annotations

from pathlib import Path

from agentic_core.runtime.bindings.app_binding_loader import load_app_binding_package
from agentic_core.runtime.bindings.app_binding_validation import REQUIRED_BINDING_SECTIONS, infer_repo_root
from agentic_core.runtime.bindings.profile_validators import run_profile_validators

REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PKG = REPO_ROOT / "tests/_core_contract/fixtures/apps_rg_binding_package"


def test_run_profile_validators_on_fixture_pass() -> None:
    pkg = load_app_binding_package(FIXTURE_PKG)
    rr = infer_repo_root(pkg.package_root)
    assert rr is not None
    sections = {k: pkg.section_paths[k] for k in REQUIRED_BINDING_SECTIONS}
    details = run_profile_validators(sections, rr)
    assert details
    assert all(d.status == "PASS" for d in details)
