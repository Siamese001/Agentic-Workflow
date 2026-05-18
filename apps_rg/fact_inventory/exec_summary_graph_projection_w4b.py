"""W4B: deterministic executive_summary graph→SRFS→prompt inspection (no live generation)."""
from __future__ import annotations

import json
import re
from dataclasses import asdict
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.arsenal_graph_w4a_spec import AGENTIC_CAPABILITY_DOMAINS
from apps_rg.fact_inventory.candidate_fact_ledger import (
    load_master_candidate_fact_ledger,
    load_master_role_family_taxonomy,
)
from apps_rg.fact_inventory.executive_summary_arsenal_projection import (
    project_executive_summary_arsenal,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
)
from apps_rg.fact_inventory.exec_summary_srfs_arsenal import (
    allocate_executive_summary_with_arsenal,
    compute_executive_summary_reserved_fact_ids,
    resolve_arsenal_role_family_key,
)
from apps_rg.fact_inventory.selected_role_fact_set import (
    infer_role_family_priorities,
    select_candidate_facts_for_role,
    selected_role_fact_set_to_json_dict,
    sorted_high_rows_global,
)
from apps_rg.runtime.dispatch.executive_summary_pa import compile_executive_summary_prompt
from apps_rg.runtime.sections.selected_role_fact_set import (
    build_allowed_fact_ids_for_section,
    build_section_fact_plan,
    build_srfs_integration_envelope,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

DOMAIN_ID_TO_LABEL: dict[str, str] = {d["domain_id"]: d["label"] for d in AGENTIC_CAPABILITY_DOMAINS}

ROLE_FAMILY_INSPECTION_KEYS: tuple[str, ...] = (
    "SVP_ENGINEERING_AI_PLATFORM",
    "AI_FINANCIAL_SERVICES",
    "ANTHROPIC_PARTNERSHIPS_APPLIED_AI",
    "FIELD_CTO",
    "CHIEF_AI_OFFICER",
)

ROLE_FAMILY_FIXTURES: dict[str, dict[str, str]] = {
    "SVP_ENGINEERING_AI_PLATFORM": {
        "target_role": "SVP Engineering AI Platform leadership agentic kubernetes orchestration",
        "jd_text": (
            "engineering platform leadership microservices cloud AWS governance "
            "agentic AI deterministic routing runtime gates productization"
        ),
        "briefing_text": "C-suite steering for governed platform modernization.",
        "target_company": "Acme Labs",
    },
    "AI_FINANCIAL_SERVICES": {
        "target_role": "AI Financial Services governance risk actuarial derivatives",
        "jd_text": (
            "enterprise risk controls Basel CCAR actuarial foundation derivatives hedging "
            "governance evidence grounding audit proof controlled write HITL"
        ),
        "briefing_text": "Regulated financial services AI controls.",
        "target_company": "Acme Financial",
    },
    "ANTHROPIC_PARTNERSHIPS_APPLIED_AI": {
        "target_role": "Director Partnerships alliances ISV co-sell applied AI pre-sales",
        "jd_text": (
            "RevOps forecasting pipeline analytics Salesforce quotas ISV alliances "
            "partner engineering pre-sales enterprise adoption approval workflow"
        ),
        "briefing_text": "Partner-led applied AI motion.",
        "target_company": "Partner Corp",
    },
    "FIELD_CTO": {
        "target_role": "Field CTO presales solution architecture cloud AWS stakeholder",
        "jd_text": (
            "field CTO customer workshops solution architecture cloud AWS "
            "context engineering prompt boundaries sandbox execution"
        ),
        "briefing_text": "Customer-facing technical leadership.",
        "target_company": "Enterprise Co",
    },
    "CHIEF_AI_OFFICER": {
        "target_role": "Chief AI Officer executive leadership governance platform strategy",
        "jd_text": (
            "chief AI officer governance runtime evaluation learning calibration "
            "productization operating model multi-judge exit control"
        ),
        "briefing_text": "Enterprise AI strategy and governance.",
        "target_company": "Global Corp",
    },
}

BANNED_PHRASES_PROMPT_CONTRACT: tuple[str, ...] = (
    "applied depth",
    "documented credential training",
    "quantitative methods training",
    "distributed systems training",
    "fully autonomous production agents",
    "self-learning runtime",
    "autonomous AGI without oversight",
    "unsupervised production agents",
    "unsupported GraphRAG claims",
    "unsupported partner engineering claims",
)

PARTNERSHIP_MEDIUM_PREFIX = "fact_partnerships_gtm_"


def _repo_paths() -> tuple[Path, Path, Path]:
    return (
        REPO_ROOT / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        REPO_ROOT / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml",
        REPO_ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
    )


def _domain_labels(domain_ids: tuple[str, ...]) -> list[str]:
    return [DOMAIN_ID_TO_LABEL.get(d, d) for d in domain_ids]


def _prompt_allowed_phrases(facts: list[dict[str, Any]]) -> list[str]:
    return [str(f.get("claim_text") or "").strip() for f in facts if f.get("claim_text")]


def _extract_allowed_ids_from_prompt(content: str) -> list[str]:
    ids: list[str] = []
    in_block = False
    for line in content.splitlines():
        if "ALLOWED_SOURCE_FACT_IDS" in line:
            in_block = True
            continue
        if in_block and line.strip().startswith("- ") and line.strip().endswith(":"):
            in_block = False
        if in_block and line.strip().startswith("- "):
            token = line.strip()[2:].split(":")[0].strip()
            if token.startswith("fact_"):
                ids.append(token)
    return ids


def _jd_briefing_proof_excluded(content: str) -> dict[str, bool]:
    return {
        "jd_targeting_only_in_prompt": "JD_TEXT (targeting only" in content and "NOT PROOF" in content,
        "briefing_targeting_only_in_prompt": "BRIEFING (targeting only" in content and "NOT PROOF" in content,
        "jd_used_as_proof_false_required": "jd_used_as_proof" in content,
    }


def _skill_id_excluded_from_source_fact_ids(content: str) -> dict[str, Any]:
    allowed = _extract_allowed_ids_from_prompt(content)
    skill_in_allowed = [x for x in allowed if x.startswith("skill_")]
    skill_mentions = re.findall(r"\bskill_[a-z0-9_]+\b", content)
    return {
        "allowed_ids_all_fact_prefixed": all(x.startswith("fact_") for x in allowed) if allowed else True,
        "skill_id_in_allowed_list": skill_in_allowed,
        "skill_id_mentions_in_prompt": sorted(set(skill_mentions))[:20],
        "excluded_ok": not skill_in_allowed,
    }


def _banned_phrases_enforced(content: str) -> dict[str, bool]:
    """Map W4C contract phrases to compiled-prompt guardrails (srfs_forbidden_phrase_contract block)."""
    low = content.lower()
    in_contract = "srfs_forbidden_phrase_contract" in low
    contract_slice = low
    if in_contract:
        start = low.index("srfs_forbidden_phrase_contract")
        contract_slice = low[start : start + 2500]
    return {
        phrase: phrase.lower() in contract_slice
        for phrase in BANNED_PHRASES_PROMPT_CONTRACT
    }  # case-insensitive match in forbidden-phrase contract slice


def inspect_role_family_projection(
    role_family_key: str,
    *,
    repo_root: Path | None = None,
    ledger_path: Path | None = None,
    taxonomy_path: Path | None = None,
    arsenal_path: Path | None = None,
) -> dict[str, Any]:
    """Full graph → SRFS → compiled-prompt inspection for one role family."""
    root = repo_root or REPO_ROOT
    lp, tp, ap = _repo_paths()
    ledger_path = ledger_path or lp
    taxonomy_path = taxonomy_path or tp
    arsenal_path = arsenal_path or ap

    fixture = ROLE_FAMILY_FIXTURES[role_family_key]
    ledger = load_master_candidate_fact_ledger(path=ledger_path)
    taxonomy = load_master_role_family_taxonomy(path=taxonomy_path)
    arsenal = load_master_skills_arsenal_ledger(path=arsenal_path)

    priorities = infer_role_family_priorities(
        target_role=fixture["target_role"],
        jd_text=fixture["jd_text"],
        briefing_text=fixture.get("briefing_text", ""),
        taxonomy=taxonomy,
    )
    auto_resolved_key = resolve_arsenal_role_family_key(
        role_family_priorities=priorities,
        target_role=fixture["target_role"],
        jd_text=fixture["jd_text"],
        briefing_text=fixture.get("briefing_text", ""),
    )
    resolved_key = role_family_key
    projection = project_executive_summary_arsenal(resolved_key, ledger=arsenal)

    high_rows = [
        r
        for r in ledger.get("candidate_facts") or []
        if isinstance(r, dict) and str(r.get("confidence") or "").upper() == "HIGH"
    ]
    high_sorted = sorted_high_rows_global(
        high_rows,
        role_family_priorities=priorities,
        taxonomy=taxonomy,
    )
    exec_reserved = compute_executive_summary_reserved_fact_ids(
        high_sorted,
        projection=projection,
        role_family_key=resolved_key,
        arsenal_ledger=arsenal,
        role_family_priorities=priorities,
    )

    srfs = select_candidate_facts_for_role(
        target_company=fixture["target_company"],
        target_role=fixture["target_role"],
        jd_text=fixture["jd_text"],
        briefing_text=fixture.get("briefing_text", ""),
        ledger=ledger,
        taxonomy=taxonomy,
        source_ledger_path=str(ledger_path),
        taxonomy_ref=str(taxonomy_path),
        repo_root=root,
        now_slug=f"W4B_{role_family_key[:12]}",
    )
    used_global = set()
    for sec, slices in srfs.selected_facts_by_section.items():
        if sec == "executive_summary":
            continue
        for sl in slices:
            used_global.add(sl.candidate_fact_id)
    exec_slices = allocate_executive_summary_with_arsenal(
        high_sorted,
        reserved_ids=exec_reserved,
        used_global=used_global,
        taxonomy=taxonomy,
        projection=projection,
        role_family_key=resolved_key,
        arsenal_ledger=arsenal,
        role_family_priorities=priorities,
        max_total=10,
        max_per_domain_family=2,
    )

    srfs_dict = selected_role_fact_set_to_json_dict(srfs)
    exec_fact_ids = [s.candidate_fact_id for s in exec_slices]
    srfs_dict.setdefault("selected_facts_by_section", {})["executive_summary"] = [
        asdict(s) for s in exec_slices
    ]
    plan = build_section_fact_plan(srfs_dict, "executive_summary")
    ordered_ids, allowed_set = build_allowed_fact_ids_for_section(srfs_dict, "executive_summary")
    envelope = build_srfs_integration_envelope(
        srfs_dict,
        executive_summary_plan_facts=list(plan.get("facts") or []),
        artifact_path_resolved=str(root / "artifacts/w4b_inspection" / f"{role_family_key}.json"),
    )

    runtime_payload = {
        "run_id": f"w4b_{role_family_key.lower()}",
        "target_title": fixture["target_role"][:80],
        "target_company": fixture["target_company"],
        "jd_text": fixture["jd_text"],
        "briefing": fixture.get("briefing_text", ""),
        "selected_fact_plan": plan,
        "allowed_fact_ids": ordered_ids,
        "srfs_integration": envelope,
        "proof_pool_metadata": {
            "proof_pool_type": "selected_role_fact_set",
            "graph_aware": True,
            "arsenal_role_family_key": resolved_key,
        },
    }

    compiled = compile_executive_summary_prompt(runtime_payload, run_id=runtime_payload["run_id"])
    content = compiled.artifact.messages[0]["content"]

    exec_slices_srfs = srfs.selected_facts_by_section["executive_summary"]
    allowed_packet = [
        {"fact_id": str(f["fact_id"]), "claim_text": str(f.get("claim_text") or "")}
        for f in plan.get("facts") or []
    ]

    skill_rows_by_id = {r["skill_id"]: r for r in arsenal.get("skill_rows") or []}
    prompt_phrases = _prompt_allowed_phrases(allowed_packet)
    blocked_skill_phrases: list[str] = []
    for sid in projection.blocked_or_pending_skill_ids:
        row = skill_rows_by_id.get(sid)
        if row:
            blocked_skill_phrases.extend(list(row.get("forbidden_phrases") or []))

    medium_partner_in_exec = [fid for fid in exec_fact_ids if PARTNERSHIP_MEDIUM_PREFIX in fid]

    return {
        "role_family_key": role_family_key,
        "resolved_arsenal_role_family_key": resolved_key,
        "auto_resolved_from_targeting": auto_resolved_key,
        "identity_node": projection.identity_node,
        "selected_epoch_nodes": list(projection.selected_epoch_nodes),
        "selected_pillar_nodes": list(projection.selected_pillar_nodes),
        "selected_domain_nodes": list(projection.selected_domain_nodes),
        "selected_domain_labels": _domain_labels(projection.selected_domain_nodes),
        "top_internal_skill_ids": list(projection.internal_ranked_skill_ids[:25]),
        "external_eligible_skill_ids": list(projection.external_eligible_skill_ids[:25]),
        "linked_fact_ids_from_projection": list(projection.linked_fact_ids),
        "blocked_or_pending_skill_ids": list(projection.blocked_or_pending_skill_ids[:30]),
        "executive_summary_srfs_fact_ids": exec_fact_ids,
        "allowed_fact_packet_fact_ids": [p["fact_id"] for p in allowed_packet],
        "allowed_fact_packet": allowed_packet,
        "prompt_facing_allowed_phrases": prompt_phrases,
        "skill_forbidden_phrases_blocked_from_external": sorted(set(blocked_skill_phrases))[:15],
        "jd_briefing_proof_exclusion": _jd_briefing_proof_excluded(content),
        "skill_id_source_fact_id_exclusion": _skill_id_excluded_from_source_fact_ids(content),
        "banned_phrases_enforced_in_prompt": _banned_phrases_enforced(content),
        "graph_metadata_present": bool(arsenal.get("graph_metadata")),
        "actuarial_differentiator_in_projection": projection.actuarial_differentiator_included,
        "governance_risk_in_projection": projection.governance_risk_included,
        "partner_gtm_in_projection": projection.partner_gtm_included,
        "medium_partner_gtm_facts_in_exec_srfs": medium_partner_in_exec,
        "claim_verification_summary_excerpt": list(projection.claim_verification_summary[:5]),
        "external_claim_policy_summary_excerpt": list(projection.external_claim_policy_summary[:5]),
        "exec_allocation_hints": [s.allocation_hint for s in exec_slices],
        "arsenal_influenced_reservation": any("arsenal" in (h or "") for h in [s.allocation_hint for s in exec_slices]),
        "srfs_auto_exec_fact_ids": [s.candidate_fact_id for s in exec_slices_srfs],
        "prompt_forbidden_phrases_section_present": "srfs_forbidden_phrase_contract" in content.lower(),
    }


def inspect_all_role_families(
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    inspections = {
        key: inspect_role_family_projection(key, repo_root=repo_root)
        for key in ROLE_FAMILY_INSPECTION_KEYS
    }
    return {
        "schema_version": "exec_summary_graph_projection_w4b_v1",
        "role_families_inspected": list(ROLE_FAMILY_INSPECTION_KEYS),
        "inspections": inspections,
        "partner_gtm_medium_caveat": (
            "fact_partnerships_gtm_* rows remain MEDIUM in candidate ledger; "
            "they do not enter HIGH SRFS executive_summary proof."
        ),
        "readiness_for_live_run": _readiness_assessment(inspections),
    }


def _readiness_assessment(inspections: dict[str, dict[str, Any]]) -> dict[str, Any]:
    blockers: list[str] = []
    for key, row in inspections.items():
        if not row.get("executive_summary_srfs_fact_ids"):
            blockers.append(f"{key}: empty executive_summary SRFS slice")
        if row.get("medium_partner_gtm_facts_in_exec_srfs"):
            blockers.append(f"{key}: MEDIUM partner facts leaked into exec SRFS")
        if not row.get("skill_id_source_fact_id_exclusion", {}).get("excluded_ok"):
            blockers.append(f"{key}: skill_id found in allowed source_fact_ids")
    agentic_in_exec = any(
        "fact_engineering_platform_001" in row.get("executive_summary_srfs_fact_ids", [])
        for row in inspections.values()
    )
    if not agentic_in_exec:
        blockers.append("No fact_engineering_platform_001 in any exec SRFS slice (agentic anchor thin)")

    blockers.append(
        "Executive_summary runtime proof not complete without live apps_rg generation run."
    )
    return {
        "ready_for_live_executive_summary_rerun": False,
        "blockers": blockers,
        "expected_anthropic_judge_risk": (
            "Semantic density and mechanism vocabulary may still soft-fail Anthropic judge "
            "until live run validates S2/S5 repair; graph ranking does not replace fact-backed prose."
        ),
        "honest_caveat": (
            "Graph domains rank internal capabilities; external proof remains fact_id-only from "
            "HIGH candidate ledger. Deep agentic rows are mostly REPO_EVIDENCE_PORTFOLIO / internal. "
            "Executive_summary runtime proof is not complete without a live generation run."
        ),
    }


def write_w4b_audit_reports(
    *,
    repo_root: Path | None = None,
    md_path: Path | None = None,
    json_path: Path | None = None,
) -> tuple[Path, Path]:
    root = repo_root or REPO_ROOT
    bundle = inspect_all_role_families(repo_root=root)
    md_path = md_path or (root / "docs/reports/apps_rg/exec_summary_graph_projection_w4b.md")
    json_path = json_path or (root / "docs/reports/apps_rg/exec_summary_graph_projection_w4b.json")
    md_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Executive Summary Graph Projection W4B Audit",
        "",
        "Offline inspection: graph → SRFS → compiled prompt (no live generation).",
        "",
        f"**Role families inspected:** {', '.join(bundle['role_families_inspected'])}",
        "",
        "## Readiness",
        "",
        f"- Ready for live executive_summary rerun: **{bundle['readiness_for_live_run']['ready_for_live_executive_summary_rerun']}**",
        f"- Blockers: {bundle['readiness_for_live_run']['blockers'] or 'none'}",
        "",
        "## Partner/GTM caveat",
        "",
        bundle["partner_gtm_medium_caveat"],
        "",
    ]
    for key in ROLE_FAMILY_INSPECTION_KEYS:
        row = bundle["inspections"][key]
        lines.extend(
            [
                f"## {key}",
                "",
                f"- Identity: `{row['identity_node']}`",
                f"- Domains (labels): {', '.join(row['selected_domain_labels'][:8])}",
                f"- SRFS fact IDs: `{', '.join(row['executive_summary_srfs_fact_ids'])}`",
                f"- Allowed packet IDs: `{', '.join(row['allowed_fact_packet_fact_ids'])}`",
                f"- External-eligible skills (sample): `{', '.join(row['external_eligible_skill_ids'][:8])}`",
                f"- Arsenal reservation hints: `{row['arsenal_influenced_reservation']}`",
                f"- MEDIUM partner in exec SRFS: `{row['medium_partner_gtm_facts_in_exec_srfs']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Honest caveat",
            "",
            bundle["readiness_for_live_run"]["honest_caveat"],
            "",
        ]
    )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    json_path.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    return md_path, json_path


def main() -> int:
    md, js = write_w4b_audit_reports()
    print(f"WROTE {md}")
    print(f"WROTE {js}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
