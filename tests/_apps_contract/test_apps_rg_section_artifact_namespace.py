"""Section artifact namespace migration contracts."""
from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.section_binding_taxonomy import (
    APPS_RG_SECTION_SHIM_PREFERRED_NAMES,
    design_law_owner_for_artifact,
)
from apps_rg.runtime.section_evidence_package import mirror_preferred_section_shim_names


def test_preferred_section_shim_names_are_app_shims() -> None:
    for preferred in APPS_RG_SECTION_SHIM_PREFERRED_NAMES.values():
        assert design_law_owner_for_artifact(
            preferred,
            legacy_class="APP_SHIM",
            trusted=False,
            present=True,
        ) == "APP_SHIM"


def test_mirror_preferred_section_shim_names_dual_writes(tmp_path: Path) -> None:
    (tmp_path / "route_contract.json").write_text('{"legacy": true}\n', encoding="utf-8")
    mirrored = mirror_preferred_section_shim_names(tmp_path)
    assert {
        "legacy": "route_contract.json",
        "preferred": "apps_rg_section_route_contract.json",
    } in mirrored
    assert (tmp_path / "apps_rg_section_route_contract.json").is_file()
