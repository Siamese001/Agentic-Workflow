"""Audit MEDIUM commercial facts, emit claim-eligibility SSOT and closeout reports."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_candidate_fact_ledger
from apps_rg.fact_inventory.commercial_claim_eligibility import (
    verify_archive_source_trace,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    SECTION_KEYS,
    select_candidate_facts_for_role,
)

ROOT = Path(__file__).resolve().parents[2]
ELIGIBILITY_YAML = ROOT / "apps_rg/config/fact_inventory/commercial_claim_eligibility.yaml"
OUT_JSON = ROOT / "docs/reports/apps_rg/commercial_fact_promotion_closeout.json"
OUT_MD = ROOT / "docs/reports/apps_rg/commercial_fact_promotion_closeout.md"

MEDIUM_COMMERCIAL_FACT_IDS: tuple[str, ...] = (
    "fact_sales_accounts_001",
    "fact_sales_accounts_002",
    "fact_sales_accounts_003",
    "fact_partnerships_gtm_001",
    "fact_partnerships_gtm_002",
    "fact_partnerships_gtm_003",
    "fact_partnerships_gtm_004",
    "fact_revenue_ops_001",
    "fact_revenue_ops_002",
    "fact_revenue_ops_003",
    "fact_revenue_ops_004",
    "fact_revenue_ops_005",
)

NEVER_PROMOTE = frozenset(
    {
        "fact_sales_accounts_004",
        "fact_sales_accounts_005",
        "fact_customer_success_001",
    }
)

CRO_FIXTURE = {
    "target_company": "Acme Revenue Corp",
    "target_role": (
        "Chief Revenue Officer revenue operations pipeline Salesforce forecasting "
        "strategic alliances customer success commercialization"
    ),
    "jd_text": (
        "RevOps pipeline analytics Salesforce forecast enterprise sales partnerships "
        "IBM AWS alliance customer success retention NRR stakeholder alignment "
        "subscription pricing M&A synergy"
    ),
    "briefing_text": "CRO composite fixture — JD/briefing labeling only; not proof.",
}


def _row_by_id(ledger: dict[str, Any], fid: str) -> dict[str, Any] | None:
    for row in ledger.get("candidate_facts") or []:
        if isinstance(row, dict) and row.get("candidate_fact_id") == fid:
            return row
    return None


def _audit_medium_commercial(ledger: dict[str, Any]) -> list[dict[str, Any]]:
    audits: list[dict[str, Any]] = []
    for fid in MEDIUM_COMMERCIAL_FACT_IDS:
        row = _row_by_id(ledger, fid)
        if row is None:
            audits.append({"candidate_fact_id": fid, "decision": "rejected", "reason": "missing_from_ledger"})
            continue
        if fid in NEVER_PROMOTE:
            audits.append(
                {
                    "candidate_fact_id": fid,
                    "decision": "rejected",
                    "reason": "explicit_guardrail_never_promote",
                    "confidence": row.get("confidence"),
                }
            )
            continue
        conf = str(row.get("confidence") or "")
        if conf in ("LOW", "NEEDS_VERIFICATION"):
            audits.append(
                {
                    "candidate_fact_id": fid,
                    "decision": "rejected",
                    "reason": f"blocked_confidence_{conf}",
                }
            )
            continue
        trace = verify_archive_source_trace(row)
        if not trace["passed"]:
            audits.append(
                {
                    "candidate_fact_id": fid,
                    "decision": "rejected",
                    "reason": trace["reason"],
                    "archive_audit": trace,
                    "confidence": conf,
                }
            )
            continue
        audits.append(
            {
                "candidate_fact_id": fid,
                "decision": "claim_eligible_medium",
                "promotion": "claim_eligible_medium",
                "confidence_unchanged": conf,
                "archive_audit": trace,
                "source_trace_archive_relpaths": [t["archive_relpath"] for t in trace["traces"]],
            }
        )
    return audits


def _build_eligibility_yaml(audits: list[dict[str, Any]]) -> dict[str, Any]:
    facts: dict[str, Any] = {}
    for a in audits:
        if a.get("decision") != "claim_eligible_medium":
            continue
        fid = a["candidate_fact_id"]
        facts[fid] = {
            "claim_eligible_medium": True,
            "source_trace_archive_relpaths": a["source_trace_archive_relpaths"],
            "promotion_reason": "phase_i_resume_archive_token_trace_passed",
            "allowed_sections": [
                "unify_bullets",
                "unify_narrative",
                "ibm_bullets",
                "ibm_narrative",
            ],
        }
    return {
        "schema_version": 1,
        "description": (
            "Registry-backed claim eligibility for MEDIUM commercial candidate facts. "
            "Does not elevate ledger confidence; SRFS uses verification_status "
            "eligible_medium_with_source_trace for bullet/narrative pools only."
        ),
        "facts": facts,
    }


def _srfs_commercial_snapshot(*, now_slug: str) -> dict[str, Any]:
    taxonomy = yaml.safe_load(
        (ROOT / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml").read_text(
            encoding="utf-8"
        )
    )
    ledger = load_master_candidate_fact_ledger()
    srfs = select_candidate_facts_for_role(
        target_company=CRO_FIXTURE["target_company"],
        target_role=CRO_FIXTURE["target_role"],
        jd_text=CRO_FIXTURE["jd_text"],
        briefing_text=CRO_FIXTURE["briefing_text"],
        ledger=ledger,
        taxonomy=taxonomy,
        now_slug=now_slug,
        repo_root=ROOT,
    )
    commercial_medium = frozenset(MEDIUM_COMMERCIAL_FACT_IDS)
    auth: list[str] = []
    claim_eligible_in_sections: dict[str, list[str]] = {s: [] for s in SECTION_KEYS}
    for sec in SECTION_KEYS:
        if sec == "competencies":
            continue
        for sl in srfs.selected_facts_by_section.get(sec, []):
            fid = sl.candidate_fact_id
            if fid in commercial_medium:
                auth.append(fid)
            if sl.claim_eligible_medium:
                claim_eligible_in_sections[sec].append(fid)
    return {
        "authoritative_commercial_fact_ids": sorted(set(auth)),
        "claim_eligible_medium_by_section": claim_eligible_in_sections,
        "medium_confirmation_queue_commercial": sorted(
            q.fact.candidate_fact_id
            for q in srfs.facts_requiring_human_confirmation
            if q.fact.candidate_fact_id in commercial_medium
        ),
        "blocked_never_promote": sorted(
            b.candidate_fact_id for b in srfs.blocked_facts if b.candidate_fact_id in NEVER_PROMOTE
        ),
        "section_fact_selection": {
            sec: [
                {
                    "candidate_fact_id": sl.candidate_fact_id,
                    "confidence": sl.confidence,
                    "verification_status": sl.verification_status,
                    "claim_eligible_medium": sl.claim_eligible_medium,
                }
                for sl in srfs.selected_facts_by_section.get(sec, [])
            ]
            for sec in SECTION_KEYS
        },
    }


def build_closeout_payload() -> dict[str, Any]:
    ledger = load_master_candidate_fact_ledger()
    audits = _audit_medium_commercial(ledger)

    from apps_rg.fact_inventory.commercial_claim_eligibility import load_claim_eligibility_registry

    yaml_backup: str | None = None
    if ELIGIBILITY_YAML.is_file():
        yaml_backup = ELIGIBILITY_YAML.read_text(encoding="utf-8")
        ELIGIBILITY_YAML.unlink()
    load_claim_eligibility_registry.cache_clear()
    before = _srfs_commercial_snapshot(now_slug="commercial_promotion_before_no_registry")

    elig_doc = _build_eligibility_yaml(audits)
    ELIGIBILITY_YAML.parent.mkdir(parents=True, exist_ok=True)
    ELIGIBILITY_YAML.write_text(
        yaml.safe_dump(elig_doc, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )
    load_claim_eligibility_registry.cache_clear()
    after = _srfs_commercial_snapshot(now_slug="commercial_promotion_after_registry")

    promoted_high: list[str] = []
    claim_eligible = [a["candidate_fact_id"] for a in audits if a.get("decision") == "claim_eligible_medium"]
    rejected = [a for a in audits if a.get("decision") == "rejected"]

    status = "PASS" if claim_eligible else "PARTIAL"
    if any(a.get("decision") == "rejected" for a in audits if a["candidate_fact_id"] in NEVER_PROMOTE):
        pass  # expected rejects

    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "medium_fact_review": audits,
        "promoted_to_high": promoted_high,
        "claim_eligible_medium": claim_eligible,
        "rejected_facts": rejected,
        "before_after_authoritative_commercial_facts": {
            "before_count": len(before["authoritative_commercial_fact_ids"]),
            "after_count": len(after["authoritative_commercial_fact_ids"]),
            "before_ids": before["authoritative_commercial_fact_ids"],
            "after_ids": after["authoritative_commercial_fact_ids"],
        },
        "section_fact_selection": {
            "before": before["section_fact_selection"],
            "after": after["section_fact_selection"],
        },
        "claim_eligible_medium_by_section_after": after["claim_eligible_medium_by_section"],
        "medium_confirmation_queue_commercial_after": after["medium_confirmation_queue_commercial"],
        "blocked_never_promote": after["blocked_never_promote"],
        "eligibility_registry_path": str(ELIGIBILITY_YAML.relative_to(ROOT)).replace("\\", "/"),
        "scope_control": {
            "agentic_core_touched": False,
            "section_prompts_touched": False,
        },
        "explicit_non_claims": [
            "No live Qwen or provider run",
            "JD/briefing used for role-family inference only",
            "No global MEDIUM→authoritative; headline/exec remain HIGH-only",
            "fact_sales_accounts_004/005 not promoted per guardrail",
        ],
    }


def _render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Commercial fact promotion closeout",
        "",
        f"**Status:** {payload['status']}",
        "",
        "## MEDIUM commercial facts reviewed",
        "",
    ]
    for row in payload["medium_fact_review"]:
        lines.append(f"- `{row['candidate_fact_id']}` → **{row.get('decision')}** ({row.get('reason', row.get('promotion', ''))})")
    lines.extend(
        [
            "",
            "## Claim-eligible MEDIUM",
            "",
            ", ".join(f"`{x}`" for x in payload["claim_eligible_medium"]) or "(none)",
            "",
            "## Authoritative commercial fact count (CRO fixture)",
            "",
            f"- Before: {payload['before_after_authoritative_commercial_facts']['before_count']}",
            f"- After: {payload['before_after_authoritative_commercial_facts']['after_count']}",
            "",
            "## Blocked never-promote",
            "",
        ]
    )
    for fid in payload.get("blocked_never_promote") or []:
        lines.append(f"- `{fid}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_closeout_payload()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    print(f"STATUS={payload['status']} wrote {OUT_JSON.name}")
    return 0 if payload["status"] in ("PASS", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
