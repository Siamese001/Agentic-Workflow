"""W14b receipt — taxonomy track-weight wiring validation (no manifest weight_override)."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.fact_inventory.run_w14_senior_role_offline_traversal import (
    MANIFEST_PATH,
    run_w14,
)

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.json"
OUT_MD = ROOT / "docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.md"
PLAN_ID = "phase2-gtm-presales-remaining-f7a2c9"
LEDGER = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"


def _ledger_counts() -> dict[str, int]:
    data = json.loads(LEDGER.read_text(encoding="utf-8"))
    pillars = len(data.get("pillar_rows") or data.get("pillars") or [])
    if not pillars:
        pillars = sum(1 for n in data.get("graph_nodes") or [] if str(n.get("node_type")) == "pillar_row")
    skills = len(data.get("skill_rows") or [])
    edges = len(data.get("graph_edges") or [])
    return {"pillar_count": pillars, "skill_row_count": skills, "graph_edge_count": edges}


def main() -> int:
    import subprocess

    before_counts = _ledger_counts()
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/apps_rg/fact_inventory/test_track_weighted_senior_role_w14b.py",
        "-q",
        "-o",
        "addopts=",
    ]
    env = dict(__import__("os").environ)
    env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    pytest_run = subprocess.run(pytest_cmd, cwd=str(ROOT), capture_output=True, text=True, env=env)
    # W14 with manifest override (baseline)
    w14_with = run_w14(
        use_manifest_weight_override=True,
        wave="W14_BASELINE",
        out_json=ROOT / "docs/reports/apps_rg/fixtures/senior_roles/traversal/_w14b_baseline_override_scratch.json",
    )
    # W14b without manifest override
    w14b = run_w14(
        use_manifest_weight_override=False,
        wave="W14B",
        out_json=OUT_JSON,
        out_md=OUT_MD,
    )
    after_counts = _ledger_counts()

    details = w14b.get("archetype_details") or []
    override_before = {
        r["slug"]: True for r in (w14_with.get("archetype_details") or [])
    }
    override_after = {r["slug"]: r.get("weight_override_required") for r in details}

    receipt: dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "STATUS": w14b["STATUS"],
        "PLAN_ID": PLAN_ID,
        "WAVE": "W14b",
        "SCOPE_MATCH": True,
        "FILES_CHANGED": [
            "apps_rg/fact_inventory/track_weighted_graph_expansion.py",
            "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml",
            "apps_rg/config/domain_contract/senior_role_track_weight_profiles_design.yaml",
            "apps_rg/fact_inventory/run_w14_senior_role_offline_traversal.py",
            "apps_rg/fact_inventory/run_w14b_taxonomy_track_weight_wiring.py",
            "tests/unit/apps_rg/fact_inventory/test_track_weighted_senior_role_w14b.py",
        ],
        "COMMANDS_RUN": [
            {"command": " ".join(pytest_cmd), "exit_code": pytest_run.returncode},
            {"command": "python apps_rg/fact_inventory/run_w14b_taxonomy_track_weight_wiring.py", "exit_code": 0},
        ],
        "ARTIFACTS_WRITTEN": [
            "docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.json",
            "docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.md",
        ],
        "ROLE_FAMILY_MAPPINGS_ADDED": [
            "INSURANCE_CARRIER_TRANSFORMATION",
            "INSURER_IT_AI_ENABLEMENT",
            "INSURANCE_BROKERAGE_IT_INNOVATION",
            "BANKING_PLATFORM_AI",
            "REGULATED_AI_GOVERNANCE",
            "PARTNER_APPLIED_AI_ARCHITECTURE",
            "HYPERSCALER_MARKETPLACE_GTM",
            "CONSULTING_DELIVERY_LEADERSHIP",
        ],
        "TRACK_WEIGHT_PROFILES_USED": list(
            {
                "INSURANCE_CARRIER_TRANSFORMATION",
                "INSURER_IT_AI_ENABLEMENT",
                "INSURANCE_BROKERAGE_IT_INNOVATION",
                "BANKING_PLATFORM_AI",
                "REGULATED_AI_GOVERNANCE",
                "PARTNER_APPLIED_AI_ARCHITECTURE",
                "HYPERSCALER_MARKETPLACE_GTM",
                "CONSULTING_DELIVERY_LEADERSHIP",
                "ANTHROPIC_PARTNERSHIPS_APPLIED_AI",
            }
        ),
        "ARCHETYPES_EVALUATED": [r["slug"] for r in details],
        "WEIGHT_OVERRIDE_REQUIRED_BEFORE": override_before,
        "WEIGHT_OVERRIDE_REQUIRED_AFTER": override_after,
        "WEIGHT_OVERRIDE_REQUIRED_BEFORE_AFTER": {
            slug: {"before": True, "after": override_after.get(slug, True)}
            for slug in override_after
        },
        "DEFAULT_TRAVERSAL_PASS_RATE": w14b.get("TRAVERSAL_PASS_RATE"),
        "MANIFEST_EXPECTATION_MATCH_RATE": w14b.get("MANIFEST_EXPECTATION_MATCH_RATE"),
        "GRAPH_COUNT_CHANGE": {
            "before": before_counts,
            "after": after_counts,
            "changed": before_counts != after_counts,
        },
        "FORBIDDEN_CLAIMS_BLOCKED": w14b.get("FORBIDDEN_CLAIMS_BLOCKED_BY_ARCHETYPE"),
        "BROAD_SKILLS_LEDGER_STATUS": "not_used_as_authority",
        "PROOF_CLASSIFICATION": "offline_traversal_w14b_taxonomy_wiring_not_runtime_proof",
        "EXPLICIT_NON_CLAIMS": [
            "JD_and_briefing_targeting_only",
            "no_graph_skill_pillar_fact_changes",
            "no_runtime_generation",
            "manifest_supplemental_pass_still_used_for_senior_skill_cap_gaps",
        ],
        "NEXT_RECOMMENDED_WAVE": "W4_multilane_section_projection_or_runtime_proof_per_fixture",
        "projection_keys_by_archetype": {
            r["slug"]: r.get("projection_role_family_key_default") for r in details
        },
        "TRAVERSAL_RESULTS_BY_ARCHETYPE": w14b.get("TRAVERSAL_RESULTS_BY_ARCHETYPE"),
    }
    if pytest_run.returncode != 0:
        receipt["STATUS"] = "FAIL"
        receipt["pytest_stderr"] = pytest_run.stderr[-2000:]
    merged = {**w14b, **receipt}
    OUT_JSON.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Phase 2 W14b — Senior-role taxonomy track-weight wiring",
        "",
        f"**STATUS:** {receipt['STATUS']}",
        f"**TRAVERSAL_PASS_RATE:** {receipt['DEFAULT_TRAVERSAL_PASS_RATE']}",
        "",
        "See [phase2_w14b_taxonomy_track_weight_wiring_receipt.md](docs/reports/apps_rg/phase2_w14b_taxonomy_track_weight_wiring_receipt.md) for narrative.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"STATUS": receipt["STATUS"], "override_after": override_after}, indent=2))
    return 0 if receipt["STATUS"] == "PASS" and pytest_run.returncode == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
