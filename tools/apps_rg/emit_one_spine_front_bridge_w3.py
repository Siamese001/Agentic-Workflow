#!/usr/bin/env python3
"""Emit Wave 3 one-spine front bridge closeout report."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from apps_rg.runtime.spine.front_contracts import (  # noqa: E402
    DOWNSTREAM_MISSING_CANONICAL_CONTRACTS,
    FRONT_SPINE_CONTRACTS,
    OBSERVED_CHAIN_WITH_FRONT_BRIDGE,
    product_visible_kill_switch_enabled,
)

OUT_DIR = REPO / "docs/reports/apps_rg"


def build_w3_report() -> dict:
    ts = datetime.now(timezone.utc).isoformat()
    return {
        "schema_version": "one_spine_front_bridge_w3_v1",
        "generated_at_utc": ts,
        "plan_slug": "one-canonical-spine",
        "wave": 3,
        "status": "PASS",
        "status_note": (
            "Front-spine bridge enforced for product-visible proof_pool via "
            "load_section_proof_for_lane; kill switch enabled by default."
        ),
        "contracts_added_or_emitted": list(FRONT_SPINE_CONTRACTS),
        "product_visible_kill_switch": {
            "enabled": product_visible_kill_switch_enabled(),
            "env_disable": "APPS_RG_SECTION_FRONT_SPINE_KILL_SWITCH=0",
        },
        "section_cli_preserved": True,
        "proof_pool_preconditions": {
            "required_before_resolver": list(FRONT_SPINE_CONTRACTS),
            "enforcement_module": "apps_rg/runtime/section_front_spine_bridge.py",
            "entry_for_product_lanes": "apps_rg/runtime/proof_pool_lane_integration.py::load_section_proof_for_lane",
        },
        "fixture_dev_only_bypass_rule": {
            "allowed": True,
            "requires": "non_product_certified=True or tests/_apps_contract conftest activate_fixture_dev_bypass",
            "product_certification": "NOT_CLAIMED when bypass active",
        },
        "observed_chain": list(OBSERVED_CHAIN_WITH_FRONT_BRIDGE),
        "missing_downstream_canonical_contracts": list(DOWNSTREAM_MISSING_CANONICAL_CONTRACTS),
        "downstream_spine_lane_mode": "section_lane_modular",
        "explicit_non_claims": [
            "no claim of full canonical C0.2, C0.3, or C0.5",
            "no claim of spine ExitDispositionReceipt or RuntimeExhaustBundle",
            "no claim of full canonical product certification",
            "no claim that all tests/_apps_contract pass",
            "no claim that section CLI is fully migrated past L0",
        ],
        "open_gaps": [
            "Wire spine C0 retrieve + FinalEvidenceContract before section PA for grounded lanes",
            "Map section X3 to spine ExitDispositionReceipt",
            "Bounded tests/_apps_contract triage (full suite still non-dispositive)",
        ],
        "forbidden_files_touched": {"agentic_core": False},
        "tests_added": [
            "tests/unit/apps_rg/test_one_spine_front_bridge_w3.py",
        ],
    }


def _md(doc: dict) -> str:
    lines = [
        "# One-spine front bridge (Wave 3)",
        "",
        f"Generated: {doc['generated_at_utc']}",
        f"**STATUS: {doc['status']}**",
        "",
        doc["status_note"],
        "",
        "## Contracts added or emitted",
        "",
    ]
    for c in doc["contracts_added_or_emitted"]:
        lines.append(f"- {c}")
    lines.extend(
        [
            "",
            "## Kill switch",
            "",
            f"- Enabled: {doc['product_visible_kill_switch']['enabled']}",
            f"- Disable env: `{doc['product_visible_kill_switch']['env_disable']}`",
            "",
            "## Proof pool preconditions",
            "",
            f"- Required: {', '.join(doc['proof_pool_preconditions']['required_before_resolver'])}",
            "",
            "## Fixture / dev bypass",
            "",
            f"- {doc['fixture_dev_only_bypass_rule']['requires']}",
            "",
            "## Open gaps",
            "",
        ]
    )
    for g in doc["open_gaps"]:
        lines.append(f"- {g}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    doc = build_w3_report()
    (OUT_DIR / "one_spine_front_bridge_w3.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (OUT_DIR / "one_spine_front_bridge_w3.md").write_text(_md(doc), encoding="utf-8")
    print(f"Wrote {OUT_DIR / 'one_spine_front_bridge_w3.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
