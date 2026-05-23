"""W2 — one-spine inventory SSOT (pa-exec-flowchart-gap-f2a8c3)."""

from __future__ import annotations

import json
from pathlib import Path

from apps_rg.runtime.one_spine_inventory import (
    SECTION_FRONT_EMITTED_CONTRACTS,
    build_one_spine_section_path_inventory,
)
from apps_rg.runtime.spine.front_contracts import (
    build_section_front_spine_from_args,
    product_visible_kill_switch_enabled,
)
from apps_rg.runtime.section_spine_terminology import CANONICAL_SPINE_CHAIN

REPO = Path(__file__).resolve().parents[2]


def test_inventory_two_paths_false_single_entry():
    inv = build_one_spine_section_path_inventory()
    assert inv["two_paths_found"] is False
    assert "section_front_spine_bridge" in inv["path_a_section_cli"]["front_bridge"]
    assert inv["section_cli_status"]["u0_package_path_required"] is True


def test_inventory_contract_matrix_front_emissions():
    inv = build_one_spine_section_path_inventory()
    by_type = {r["contract_type"]: r for r in inv["contract_bypass_matrix"]}
    for ct in SECTION_FRONT_EMITTED_CONTRACTS:
        assert by_type[ct]["section_cli_emits_canonical"] is True


def test_front_bridge_attaches_runtime_package():
    from types import SimpleNamespace

    bridge = build_section_front_spine_from_args(
        section_id="competencies",
        args=SimpleNamespace(
            target_company="Acme",
            target_title="VP Eng",
            target_role="VP Eng",
            jd_text="JD",
            briefing="brief",
            base_resume_ref="",
        ),
        repo_root=REPO,
    )
    ap = dict(bridge.validated_request.app_payload or {})
    assert ap.get("runtime_customization_package")
    assert ap.get("profile_manifest", {}).get("runtime_customization_package_ref")


def test_kill_switch_enabled_for_product():
    assert product_visible_kill_switch_enabled() is True


def test_emit_inventory_json_ssot(tmp_path: Path) -> None:
    """Optional: refresh on-disk report when APPS_RG_EMIT_INVENTORY=1."""
    import os

    if os.environ.get("APPS_RG_EMIT_INVENTORY") != "1":
        return
    out = REPO / "docs/reports/apps_rg/one_spine_section_path_inventory.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        json.dumps(build_one_spine_section_path_inventory(), indent=2) + "\n",
        encoding="utf-8",
    )


def test_canonical_target_unchanged():
    inv = build_one_spine_section_path_inventory()
    assert inv["canonical_spine_target"] == list(CANONICAL_SPINE_CHAIN)
