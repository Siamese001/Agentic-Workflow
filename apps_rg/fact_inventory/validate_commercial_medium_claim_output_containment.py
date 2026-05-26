"""Prove claim_eligible MEDIUM commercial facts stay lane-contained and archive-backed.

Offline harness: CRO SRFS fixture + proof-pool plan facts (no live LLM).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import yaml

from apps_rg.fact_inventory.candidate_fact_ledger import load_master_candidate_fact_ledger
from apps_rg.fact_inventory.commercial_claim_eligibility import (
    is_claim_eligible_medium,
    registry_fact_entry,
    verify_archive_source_trace,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    SECTION_KEYS,
    classify_company_lane,
    select_candidate_facts_for_role,
)
from apps_rg.fact_inventory.validate_commercial_srfs_projection import (
    CRO_FIXTURE,
    MEDIUM_COMMERCIAL_FACT_IDS,
    REJECTED_FACT_IDS,
)
from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool
from apps_rg.runtime.spine.front_contracts import build_section_front_spine_from_args

ROOT = Path(__file__).resolve().parents[2]
OUT_JSON = ROOT / "docs/reports/apps_rg/commercial_medium_claim_output_containment.json"
OUT_MD = ROOT / "docs/reports/apps_rg/commercial_medium_claim_output_containment.md"

BULLET_NARRATIVE_SECTIONS: tuple[str, ...] = (
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
)
HEADLINE_EXEC_SECTIONS: tuple[str, ...] = ("headline", "executive_summary")

BLOCKED_FACT_IDS = frozenset(REJECTED_FACT_IDS | {"fact_customer_success_001"})

_SECTION_LANE_EXPECTED: dict[str, str] = {
    "unify_bullets": "unify",
    "unify_narrative": "unify",
    "ibm_bullets": "ibm_only",
    "ibm_narrative": "ibm_only",
}


def _ledger_row(ledger: dict[str, Any], fid: str) -> dict[str, Any] | None:
    for row in ledger.get("candidate_facts") or []:
        if isinstance(row, dict) and row.get("candidate_fact_id") == fid:
            return row
    return None


def _containment_lane_args() -> SimpleNamespace:
    """Minimal CLI-shaped args for offline CRO fixture proof-pool resolution."""
    return SimpleNamespace(
        target_company=CRO_FIXTURE["target_company"],
        target_role=CRO_FIXTURE["target_role"],
        target_title=CRO_FIXTURE["target_role"],
        jd_text=CRO_FIXTURE["jd_text"],
        briefing=CRO_FIXTURE["briefing_text"],
        base_resume_ref=None,
        tenant_id="default",
    )


def _overclaim_verdict(row: dict[str, Any], *, claim_text: str) -> dict[str, Any]:
    audit = verify_archive_source_trace(row)
    entry = registry_fact_entry(str(row["candidate_fact_id"]), repo_root=ROOT) or {}
    trace_paths = list(entry.get("source_trace_archive_relpaths") or [])
    for rel in trace_paths:
        if not (ROOT / rel).is_file():
            audit = {**audit, "passed": False, "reason": "registry_trace_path_missing_on_disk"}
            break
    ledger_claim = str(row.get("claim_text") or "").strip()
    claim_stable = ledger_claim == str(claim_text).strip()
    passed = bool(audit.get("passed")) and claim_stable and bool(trace_paths)
    return {
        "overclaim_verdict": "PASS" if passed else "FAIL",
        "claim_text_stable_vs_ledger": claim_stable,
        "archive_audit": audit,
        "registry_trace_paths": trace_paths,
    }


def build_containment_payload() -> dict[str, Any]:
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
        now_slug="commercial_medium_claim_containment",
        repo_root=ROOT,
    )

    violations: list[str] = []
    claim_by_section: dict[str, list[dict[str, Any]]] = {s: [] for s in BULLET_NARRATIVE_SECTIONS}
    source_trace_matrix: list[dict[str, Any]] = []
    overclaim_rows: list[dict[str, Any]] = []
    all_selected_ids: set[str] = set()

    for sec in SECTION_KEYS:
        for sl in srfs.selected_facts_by_section.get(sec, []):
            all_selected_ids.add(sl.candidate_fact_id)

    for sec in HEADLINE_EXEC_SECTIONS:
        for sl in srfs.selected_facts_by_section.get(sec, []):
            conf = str(sl.confidence or "").upper()
            if conf != "HIGH":
                violations.append(f"{sec}: non-HIGH fact {sl.candidate_fact_id} confidence={conf}")
            if sl.candidate_fact_id in MEDIUM_COMMERCIAL_FACT_IDS:
                violations.append(f"{sec}: MEDIUM commercial fact {sl.candidate_fact_id} in HIGH-only pool")
            if sl.claim_eligible_medium:
                violations.append(f"{sec}: claim_eligible_medium flag on {sl.candidate_fact_id}")

    for sec in BULLET_NARRATIVE_SECTIONS:
        expected_lane = _SECTION_LANE_EXPECTED[sec]
        for sl in srfs.selected_facts_by_section.get(sec, []):
            fid = sl.candidate_fact_id
            row = _ledger_row(ledger, fid)
            claim_entry = {
                "section_id": sec,
                "candidate_fact_id": fid,
                "confidence": sl.confidence,
                "verification_status": sl.verification_status,
                "claim_eligible_medium": sl.claim_eligible_medium,
                "claim_text": sl.claim_text,
                "company_lane": sl.company_lane,
                "source_trace_archive_relpaths": list(sl.source_trace_archive_relpaths),
            }
            claim_by_section[sec].append(claim_entry)

            if fid in MEDIUM_COMMERCIAL_FACT_IDS:
                if not sl.claim_eligible_medium:
                    violations.append(f"{sec}: MEDIUM commercial {fid} missing claim_eligible_medium")
                if sl.verification_status != "eligible_medium_with_source_trace":
                    violations.append(
                        f"{sec}: {fid} verification_status={sl.verification_status!r}"
                    )
                if not sl.source_trace_archive_relpaths:
                    violations.append(f"{sec}: {fid} missing source_trace_archive_relpaths")
                if not is_claim_eligible_medium(fid, repo_root=ROOT):
                    violations.append(f"{sec}: {fid} not in commercial_claim_eligibility registry")
                if sl.company_lane != expected_lane:
                    violations.append(
                        f"{sec}: {fid} lane={sl.company_lane} expected={expected_lane} for section"
                    )

            if fid in MEDIUM_COMMERCIAL_FACT_IDS or sl.claim_eligible_medium:
                if row is None:
                    violations.append(f"{sec}: missing ledger row for {fid}")
                    continue
                verdict = _overclaim_verdict(row, claim_text=sl.claim_text)
                overclaim_rows.append({"section_id": sec, "candidate_fact_id": fid, **verdict})
                source_trace_matrix.append(
                    {
                        "candidate_fact_id": fid,
                        "section_id": sec,
                        "trace_paths": verdict["registry_trace_paths"],
                        "archive_token_hit_ratio": verdict["archive_audit"].get("token_hit_ratio"),
                        "overclaim_verdict": verdict["overclaim_verdict"],
                    }
                )
                if verdict["overclaim_verdict"] != "PASS":
                    violations.append(f"{sec}: overclaim or unstable claim for {fid}")

    for blocked_id in BLOCKED_FACT_IDS:
        if blocked_id in all_selected_ids:
            violations.append(f"blocked fact {blocked_id} entered a section pool")
        blocked_row = next((b for b in srfs.blocked_facts if b.candidate_fact_id == blocked_id), None)
        if blocked_row is None and blocked_id in REJECTED_FACT_IDS:
            violations.append(f"expected {blocked_id} in srfs.blocked_facts")

    unpromoted_medium_in_pool = {
        fid
        for fid in all_selected_ids
        if fid in MEDIUM_COMMERCIAL_FACT_IDS and not is_claim_eligible_medium(fid, repo_root=ROOT)
    }
    if unpromoted_medium_in_pool:
        violations.append(f"unpromoted MEDIUM commercial in pools: {sorted(unpromoted_medium_in_pool)}")

    section_proof_pools: dict[str, dict[str, Any]] = {}
    lane_args = _containment_lane_args()
    for sec in BULLET_NARRATIVE_SECTIONS:
        front_spine = build_section_front_spine_from_args(
            section_id=sec,
            args=lane_args,
            repo_root=ROOT,
            jd_text_override=CRO_FIXTURE["jd_text"],
            briefing_text_override=CRO_FIXTURE["briefing_text"],
        )
        pool = resolve_section_proof_pool(
            section=sec,
            selected_role_fact_set_path=None,
            repo_root=ROOT,
            target_company=CRO_FIXTURE["target_company"],
            target_role=CRO_FIXTURE["target_role"],
            jd_text=CRO_FIXTURE["jd_text"],
            briefing_text=CRO_FIXTURE["briefing_text"],
            front_spine=front_spine,
            product_visible=True,
        )
        plan_facts = list(pool.selected_fact_plan.get("facts") or [])
        plan_ids = [str(f.get("fact_id") or f.get("candidate_fact_id") or "") for f in plan_facts]
        section_proof_pools[sec] = {
            "proof_source": pool.proof_source,
            "fact_count": len(plan_facts),
            "fact_ids": plan_ids,
            "fixture_claim_texts": [
                {
                    "fact_id": str(f.get("fact_id") or ""),
                    "claim_text": str(f.get("claim_text") or "")[:240],
                    "confidence": str(f.get("confidence") or ""),
                    "source_trace_archive_relpaths": list(
                        f.get("source_trace_archive_relpaths") or ()
                    ),
                }
                for f in plan_facts
            ],
        }
        for f in plan_facts:
            conf = str(f.get("confidence") or "").upper()
            fid = str(f.get("fact_id") or "")
            if conf == "MEDIUM":
                if str(f.get("srfs_verification_status") or "") != "eligible_medium_with_source_trace":
                    violations.append(f"{sec} proof pool: MEDIUM {fid} missing eligible verification")
                if not f.get("source_trace_archive_relpaths"):
                    violations.append(f"{sec} proof pool: MEDIUM {fid} missing trace in plan fact")

    headline_exec_proof = {
        sec: [
            {
                "candidate_fact_id": sl.candidate_fact_id,
                "confidence": sl.confidence,
                "verification_status": sl.verification_status,
            }
            for sl in srfs.selected_facts_by_section.get(sec, [])
        ]
        for sec in HEADLINE_EXEC_SECTIONS
    }

    has_fixture_output = any(section_proof_pools[s]["fact_count"] > 0 for s in BULLET_NARRATIVE_SECTIONS)
    if violations:
        status = "FAIL"
    elif has_fixture_output:
        status = "PASS"
    else:
        status = "PARTIAL"

    return {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "fixture": CRO_FIXTURE,
        "sections_tested": list(BULLET_NARRATIVE_SECTIONS),
        "headline_executive_high_only_proof": headline_exec_proof,
        "claim_eligible_medium_by_section": {
            sec: [c["candidate_fact_id"] for c in rows if c.get("claim_eligible_medium")]
            for sec, rows in claim_by_section.items()
        },
        "fixture_claims_by_section": claim_by_section,
        "source_trace_matrix": source_trace_matrix,
        "overclaim_verdicts": overclaim_rows,
        "blocked_facts_proof": {
            "blocked_ids": sorted(BLOCKED_FACT_IDS),
            "in_any_section_pool": sorted(all_selected_ids & BLOCKED_FACT_IDS),
            "srfs_blocked_rows": [
                {
                    "candidate_fact_id": b.candidate_fact_id,
                    "confidence": b.confidence,
                    "block_reason": b.block_reason,
                }
                for b in srfs.blocked_facts
                if b.candidate_fact_id in BLOCKED_FACT_IDS
            ],
        },
        "section_proof_pool_fixture_output": section_proof_pools,
        "violations": violations,
        "x2_x3_status": {
            "ran": False,
            "note": "Offline SRFS + proof-pool fixture only; no live provider X2/X3",
        },
        "scope_control": {
            "agentic_core_touched": False,
            "section_prompts_touched": False,
            "skills_graph_mutated": False,
            "facts_promoted_this_wave": False,
        },
        "explicit_non_claims": [
            "No live Qwen/provider run",
            "No X2/X3 gate execution in this harness",
            "JD/briefing labeling-only for CRO fixture",
        ],
    }


def _render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Commercial MEDIUM claim output containment",
        "",
        f"**Status:** {payload['status']}",
        "",
        "## Sections tested",
        "",
        ", ".join(f"`{s}`" for s in payload["sections_tested"]),
        "",
        "## Headline / executive_summary (HIGH-only)",
        "",
    ]
    for sec, rows in payload["headline_executive_high_only_proof"].items():
        lines.append(f"### `{sec}`")
        for r in rows:
            lines.append(f"- `{r['candidate_fact_id']}` [{r['confidence']}] {r['verification_status']}")
    lines.extend(["", "## Claim-eligible MEDIUM by section", ""])
    for sec, ids in payload["claim_eligible_medium_by_section"].items():
        lines.append(f"- **{sec}**: {ids or '[]'}")
    lines.extend(["", "## Overclaim verdicts", ""])
    for row in payload["overclaim_verdicts"]:
        lines.append(
            f"- `{row['candidate_fact_id']}` @ {row['section_id']}: **{row['overclaim_verdict']}** "
            f"(archive hit={row['archive_audit'].get('token_hit_ratio')})"
        )
    lines.extend(["", "## Blocked facts", ""])
    bf = payload["blocked_facts_proof"]
    lines.append(f"- In pools: `{bf['in_any_section_pool']}` (expected `[]`)")
    if payload.get("violations"):
        lines.extend(["", "## Violations", ""])
        for v in payload["violations"]:
            lines.append(f"- {v}")
    return "\n".join(lines) + "\n"


def main() -> int:
    payload = build_containment_payload()
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    print(f"STATUS={payload['status']} wrote {OUT_JSON.name}")
    return 0 if payload["status"] in ("PASS", "PARTIAL") else 1


if __name__ == "__main__":
    raise SystemExit(main())
