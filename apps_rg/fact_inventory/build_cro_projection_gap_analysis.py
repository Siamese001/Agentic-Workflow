"""Build CRO composite projection gap analysis reports (evidence audit; no graph mutation)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json"
LEDGER_PATH = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
CANDIDATE_LEDGER_PATH = (
    ROOT / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
)
TAXONOMY_PATH = ROOT / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"
COMPOSITE_CONFIG_PATH = ROOT / "apps_rg/config/domain_contract/composite_projection_profiles.yaml"
ARCHIVE_DIR = ROOT / "artifacts/apps_rg/fact_inventory/phase_i_resumes_archive_extracted"

OUT_JSON = ROOT / "docs/reports/apps_rg/cro_projection_profile_gap_analysis.json"
OUT_MD = ROOT / "docs/reports/apps_rg/cro_projection_profile_gap_analysis.md"

PROFILE_ID = "CHIEF_REVENUE_OFFICER_COMPOSITE"

CRO_CAPABILITY_GAPS = (
    ("marketing_demand_generation", "ABM, MQL/SQL, paid demand gen, brand/campaign ops"),
    ("customer_success_authoritative", "NRR/GRR, health scores, QBR cadence as confirmed facts"),
    ("quota_carrying_ae_primary", "Primary quota-carrying AE scope (design pending source)"),
    ("marketing_org_leadership", "Full marketing org P&L and team build-out"),
    ("board_investor_narrative", "Board/investor relations as primary CRO accountability"),
)

REJECT_CONFIDENCE = frozenset({"LOW", "NEEDS_VERIFICATION"})


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _pillar_linked_facts(ledger: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for p in ledger.get("pillars") or []:
        if isinstance(p, dict) and p.get("pillar_id"):
            out[str(p["pillar_id"])] = list(p.get("linked_fact_ids") or [])
    return out


def _facts_by_id(candidate: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        str(f["candidate_fact_id"]): f
        for f in candidate.get("candidate_facts") or []
        if isinstance(f, dict) and f.get("candidate_fact_id")
    }


def _archive_mining_notes() -> list[dict[str, str]]:
    paths = {
        "sales": ARCHIVE_DIR / "Sales_-_Amit_Ayer.txt",
        "vp_finance_sales_marketing": ARCHIVE_DIR / "Amit_Ayer_Resume_-_VP_Finance_Sales_Marketing.txt",
        "customer_success": ARCHIVE_DIR / "Head_of_Customer_Success_-_Amit_Ayer.txt",
        "revenue_operations": ARCHIVE_DIR / "Revenue_Operations_-_Amit_Ayer.txt",
    }
    notes: list[dict[str, str]] = []
    for key, path in paths.items():
        if not path.is_file():
            notes.append({"variant": key, "status": "MISSING", "note": str(path)})
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        notes.append(
            {
                "variant": key,
                "status": "PRESENT",
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "char_count": str(len(text)),
                "has_marketing_signal": str(
                    any(s in text.lower() for s in ("marketing", "demand", "campaign", "mql"))
                ),
                "has_cs_signal": str(
                    any(
                        s in text.lower()
                        for s in ("customer success", "retention", "nrr", "renewal", "churn")
                    )
                ),
            }
        )
    return notes


def build_gap_payload(
    *,
    ledger: dict[str, Any],
    design: dict[str, Any],
    candidate: dict[str, Any],
    wired_facts: list[dict[str, Any]],
    new_skills: list[str],
    rejected: list[dict[str, Any]],
) -> dict[str, Any]:
    profile = (ledger.get("role_family_projection_profiles") or {}).get(PROFILE_ID) or {}
    facts = _facts_by_id(candidate)
    pillars = _pillar_linked_facts(ledger)

    commercial_fact_ids = {
        str(f["candidate_fact_id"])
        for f in facts.values()
        for rf in f.get("role_families_supported") or []
        if rf
        in {
            "REVENUE_OPERATIONS",
            "SALES_STRATEGIC_ACCOUNTS",
            "PARTNERSHIPS_GTM",
            "CUSTOMER_SUCCESS",
            "STRATEGIC_FINANCE",
        }
    }

    on_pillar = {fid for ids in pillars.values() for fid in ids}
    under_linked = sorted(commercial_fact_ids - on_pillar)

    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "profile_id": PROFILE_ID,
        "profile_label": profile.get("label"),
        "profile_kind": profile.get("profile_kind", "composite_role_family_projection"),
        "role_family_weights": profile.get("role_family_weights") or {},
        "taxonomy_ids": profile.get("taxonomy_ids") or [],
        "top_weighted_pillars": profile.get("top_weighted_pillars") or [],
        "deprioritize_pillars": profile.get("deprioritize_pillars") or [],
        "standalone_cro_role_family_present": False,
        "facts_newly_wired": wired_facts,
        "new_skill_rows": new_skills,
        "facts_rejected": rejected,
        "under_linked_commercial_facts_remaining": [
            {
                "candidate_fact_id": fid,
                "confidence": facts[fid].get("confidence"),
                "reason": "not_linked_to_any_pillar_source_refs",
            }
            for fid in under_linked
            if fid in facts
        ],
        "unsupported_cro_capability_gaps": [
            {"capability_id": cid, "description": desc} for cid, desc in CRO_CAPABILITY_GAPS
        ],
        "archive_mining": _archive_mining_notes(),
        "explicit_non_claims": [
            "JD and briefing text are targeting-only; never proof.",
            "LOW and NEEDS_VERIFICATION candidate facts are not promoted to authoritative external skills.",
            "CHIEF_REVENUE_OFFICER_COMPOSITE is not a role_families taxonomy id.",
            "Head of Customer Success variant metrics (e.g. 20% NRR) are not resume claims until confirmed facts exist.",
            "Marketing demand-gen depth beyond archive GTM-alignment phrases is not asserted as proven skills.",
        ],
        "design_stats": design.get("stats") or {},
        "ledger_metadata": ledger.get("metadata") or {},
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# CRO composite projection — gap analysis",
        "",
        f"**Generated:** {payload['generated_at_utc']}",
        "",
        "## Composite profile",
        "",
        f"- **Profile id:** `{payload['profile_id']}`",
        f"- **Label:** {payload.get('profile_label')}",
        f"- **Standalone CRO role family:** {payload.get('standalone_cro_role_family_present')}",
        "",
        "### Role-family weights (canonical taxonomy ids only)",
        "",
    ]
    for rf, w in sorted((payload.get("role_family_weights") or {}).items(), key=lambda x: -x[1]):
        lines.append(f"- `{rf}`: {w}")
    lines.extend(["", "### Top weighted pillars", ""])
    for p in payload.get("top_weighted_pillars") or []:
        lines.append(f"- `{p.get('pillar_id')}` weight={p.get('weight')}")
    lines.extend(["", "## Facts newly wired to pillars", ""])
    if payload.get("facts_newly_wired"):
        for row in payload["facts_newly_wired"]:
            lines.append(
                f"- `{row['candidate_fact_id']}` → `{row['pillar_id']}` "
                f"(confidence={row.get('confidence')})"
            )
    else:
        lines.append("- _(none this pass)_")
    lines.extend(["", "## New skill rows", ""])
    for sid in payload.get("new_skill_rows") or []:
        lines.append(f"- `{sid}`")
    lines.extend(["", "## Facts rejected (not promoted to authoritative skills)", ""])
    for row in payload.get("facts_rejected") or []:
        lines.append(f"- `{row['candidate_fact_id']}`: {row.get('reason')}")
    lines.extend(["", "## Under-linked commercial facts remaining", ""])
    for row in payload.get("under_linked_commercial_facts_remaining") or []:
        lines.append(f"- `{row['candidate_fact_id']}` ({row.get('confidence')})")
    lines.extend(["", "## Unsupported CRO capability gaps", ""])
    for row in payload.get("unsupported_cro_capability_gaps") or []:
        lines.append(f"- **{row['capability_id']}:** {row['description']}")
    lines.extend(["", "## Explicit non-claims", ""])
    for note in payload.get("explicit_non_claims") or []:
        lines.append(f"- {note}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ledger = _load_json(LEDGER_PATH)
    design = _load_json(DESIGN_PATH)
    candidate = _load_json(CANDIDATE_LEDGER_PATH)

    wired = getattr(build_gap_payload, "_wired_cache", [])
    new_skills = getattr(build_gap_payload, "_skills_cache", [])
    rejected = getattr(build_gap_payload, "_rejected_cache", [])

    payload = build_gap_payload(
        ledger=ledger,
        design=design,
        candidate=candidate,
        wired_facts=wired,
        new_skills=new_skills,
        rejected=rejected,
    )
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(f"WROTE {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
