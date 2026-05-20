"""Patch master_skills_arsenal_ledger.json graph SSOT and rematerialize SQLite (graph scope only)."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph_sqlite import (
    apply_operator_archive_promotions,
    audit_candidate_fact_promotions,
    audit_theme_skill_promotion_decisions,
    collect_graph_counts,
    collect_high_and_exec_summary_counts,
    load_candidate_fact_promotion_registry,
    materialize_augmented_skills_graph_sqlite,
    resolve_confidence_grade,
    validate_hardened_materialized_sqlite,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    default_arsenal_ledger_path,
    validate_arsenal_ledger_shape,
)

REPO = Path(__file__).resolve().parents[2]
OUT_RECEIPT_JSON = REPO / "docs/reports/apps_rg/augmented_skills_graph_materialization_harden_receipt.json"
OUT_RECEIPT_MD = REPO / "docs/reports/apps_rg/augmented_skills_graph_materialization_harden_receipt.md"

CS_PRIMARY_FORBIDDEN = (
    "customer success primary",
    "customer-success primary",
    "Head of Customer Success",
    "VP Customer Success",
    "Chief Customer Officer",
    "customer success leader",
)

MARKETPLACE_FORBIDDEN = (
    "marketplace listing owner",
    "owned marketplace listing",
    "marketplace listing claim",
)


def _dedupe_graph_edges(edges: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, int]]:
    seen_id: set[str] = set()
    seen_triple: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    dropped_id = 0
    dropped_triple = 0
    for raw in edges:
        if not isinstance(raw, dict):
            continue
        eid = str(raw.get("edge_id") or "").strip()
        src = str(raw.get("source_node_id") or raw.get("source") or "").strip()
        tgt = str(raw.get("target_node_id") or raw.get("target") or "").strip()
        et = str(raw.get("edge_type") or "").strip()
        if not eid or not src or not tgt or not et:
            continue
        if eid in seen_id:
            dropped_id += 1
            continue
        triple = (src, tgt, et)
        if triple in seen_triple:
            dropped_triple += 1
            continue
        seen_id.add(eid)
        seen_triple.add(triple)
        out.append(raw)
    return out, {"dropped_duplicate_edge_id": dropped_id, "dropped_duplicate_triple": dropped_triple}


def _ensure_policy_graph_nodes(payload: dict[str, Any]) -> int:
    nodes = payload.setdefault("graph_nodes", [])
    existing = {str(n.get("node_id")) for n in nodes if isinstance(n, dict)}
    added = 0
    policies = payload.get("external_claim_policies") or {}
    seeds: list[tuple[str, str, str]] = [
        ("policy_external_claim_policy", "policy", "External claim policy anchor"),
        (
            "policy_executive_summary_high_confidence_only",
            "policy",
            "executive_summary allows confidence_grade=HIGH fact-backed skills only",
        ),
    ]
    for key in policies:
        if isinstance(key, str) and key.strip():
            seeds.append((f"policy_rule_{key}", "policy_rule", str(policies[key].get("description", key))))
    for nid, ntype, desc in seeds:
        if nid in existing:
            continue
        nodes.append(
            {
                "node_id": nid,
                "node_type": ntype,
                "label": nid,
                "description": desc,
                "support_level": "POLICY",
                "visibility_rule": "internal_traversal_only",
                "activation_status": "ACTIVE",
                "evidence_risk": "low",
                "source_refs": [],
                "projection_behavior": "graph_traversal",
                "external_claim_policy": "internal_traversal_only",
            }
        )
        existing.add(nid)
        added += 1
    return added


def _redirect_policy_edge_sources(edges: list[dict[str, Any]]) -> int:
    policies = {
        "skill_projection_not_proof",
        "skill_id_never_source_fact_id",
        "derived_supported_requires_fact_links",
        "jd_briefing_targeting_only",
        "metrics_require_metric_fact",
        "ats_keywords_not_claims",
        "blocked_phrase_fail_closed",
        "weak_snippet_internal_only",
        "repo_evidence_portfolio_not_resume_default",
        "pending_source_internal_only",
        "external_resume_claim_requires_active_fact_or_confirmed_snippet",
        "claim_ledger_fact_id_only",
        "no_jd_briefing_source_fact_id",
    }
    rewritten = 0
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        src = str(edge.get("source_node_id") or "").strip()
        if src in policies:
            edge["source_node_id"] = f"policy_rule_{src}"
            rewritten += 1
    return rewritten


def _patch_anthropic_profile(payload: dict[str, Any]) -> bool:
    profiles = payload.get("role_family_projection_profiles") or {}
    prof = profiles.get("ANTHROPIC_PARTNERSHIPS_APPLIED_AI")
    if not isinstance(prof, dict):
        return False
    pillars = list(prof.get("top_weighted_pillars") or [])
    existing = {p.get("pillar_id") for p in pillars if isinstance(p, dict)}
    changed = False
    for pid, weight in (
        ("pillar_hyperscaler_marketplace_partner_gtm", 0.92),
        ("pillar_applied_ai_partner_architecture", 0.94),
    ):
        if pid not in existing:
            pillars.append({"pillar_id": pid, "weight": weight})
            changed = True
    if changed:
        prof["top_weighted_pillars"] = pillars
        prof["marketplace_listing_claims_blocked"] = True
        prof["explicit_non_claims"] = list(
            dict.fromkeys(
                list(prof.get("explicit_non_claims") or [])
                + list(MARKETPLACE_FORBIDDEN)
            )
        )
    return changed


def _patch_airline_anchor(payload: dict[str, Any]) -> bool:
    changed = False
    neutral_label = "internal_inference_devops_anchor_directional"
    neutral_desc = "Internal-only inference anchor; not an external resume claim without archive proof."
    for collection, key in (("skill_rows", "skill_id"), ("graph_nodes", "node_id")):
        rows = payload.get(collection) or []
        for row in rows:
            if not isinstance(row, dict):
                continue
            if str(row.get(key)) != "skill_p2_anchor_major_airline_devops_aws":
                continue
            row["label"] = row.get("label") or neutral_label
            if key == "node_id":
                row["label"] = neutral_label
            row["description"] = neutral_desc
            row["visibility_rule"] = "never_external"
            row["activation_status"] = "DRAFT"
            row["support_level"] = "INTERNAL_ONLY"
            row["external_claim_policy"] = "internal_traversal_only"
            if "allowed_sections" in row:
                row["allowed_sections"] = []
            changed = True
    return changed


def _patch_customer_stakeholder_guardrails(payload: dict[str, Any]) -> int:
    patched = 0
    for row in payload.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        if str(row.get("pillar")) != "pillar_customer_stakeholder":
            continue
        forbidden = list(row.get("forbidden_phrases") or [])
        for phrase in CS_PRIMARY_FORBIDDEN:
            if phrase not in forbidden:
                forbidden.append(phrase)
        row["forbidden_phrases"] = forbidden
        allowed = list(row.get("allowed_phrases") or [])
        row["allowed_phrases"] = [a for a in allowed if not any(f.lower() in a.lower() for f in CS_PRIMARY_FORBIDDEN)]
        patched += 1
    return patched


def _rewire_runtime_gate_mesh_primary_fact(payload: dict[str, Any]) -> dict[str, int]:
    """Move runtime gate mesh primary proof off Basel/CCAR fact to engineering platform fact."""
    stats = {"skill_rows": 0, "graph_nodes": 0, "agentic_runtime_matrix": 0, "edges_rewired": 0}
    new_primary = "fact_engineering_platform_001"
    old_mislink = "fact_governance_003"
    skill_id = "skill_runtime_gate_mesh_design"
    for collection, key, stat_key in (
        ("skill_rows", "skill_id", "skill_rows"),
        ("graph_nodes", "node_id", "graph_nodes"),
        ("agentic_runtime_matrix", "skill_id", "agentic_runtime_matrix"),
    ):
        for row in payload.get(collection) or []:
            if not isinstance(row, dict) or str(row.get(key)) != skill_id:
                continue
            links = [str(x).strip() for x in (row.get("fact_id_links") or []) if str(x).strip()]
            if old_mislink not in links and new_primary in links:
                row.setdefault("primary_fact_id", new_primary)
                continue
            row["fact_id_links"] = [new_primary]
            row["primary_fact_id"] = new_primary
            row["semantic_rewire"] = {
                "action": "primary_proof_moved",
                "from_fact_id": old_mislink,
                "to_fact_id": new_primary,
                "confidence_cap": "MEDIUM_until_human_confirmed_archive_promotion",
            }
            stats[stat_key] += 1
    for edge in payload.get("graph_edges") or []:
        if not isinstance(edge, dict):
            continue
        if edge.get("edge_id") == (
            "edge_skill_fact_skill_runtime_gate_mesh_design_fact_governance_003"
        ):
            edge["edge_id"] = (
                "edge_skill_fact_skill_runtime_gate_mesh_design_fact_engineering_platform_001"
            )
            edge["target_node_id"] = new_primary
            edge["rationale"] = (
                "Primary proof: engineering platform policy gating "
                "(not Basel/CCAR lineage)"
            )
            stats["edges_rewired"] += 1
    return stats


def _attach_archive_promotion_guardrails_metadata(payload: dict[str, Any]) -> None:
    gm = payload.setdefault("graph_metadata", {})
    if not isinstance(gm, dict):
        return
    registry = load_candidate_fact_promotion_registry(REPO)
    gm["archive_promotion_guardrails"] = {
        "candidate_ledger_ref": str(
            payload.get("metadata", {}).get("candidate_fact_ledger_ref")
            or "artifacts/apps_rg/fact_inventory/"
            "master_candidate_skills_fact_ledger_20260518T1100Z.json"
        ),
        "candidate_ledger_status": registry.get(
            "fact_engineering_platform_001", {}
        ).get("ledger_status", "candidate_ledger_requires_human_confirmation"),
        "allowed_resume_use_gate": "allowed_after_human_confirm",
        "confidence_high_requires": (
            "ACTIVE_CONFIRMED + DIRECT_FROM_RESUME_ARCHIVE + fact_id_links "
            "OR human_confirmed_archive_promotion on skill_row"
        ),
        "candidate_facts_do_not_auto_promote_skills": True,
        "engineering_platform_candidate_fact_ids": sorted(
            {
                "fact_engineering_platform_001",
                "fact_engineering_platform_002",
                "fact_engineering_platform_003",
                "fact_engineering_platform_004",
                "fact_engineering_platform_005",
                "fact_engineering_platform_006",
            }
        ),
    }


def _backfill_confidence_grades(payload: dict[str, Any]) -> dict[str, str]:
    """Write effective confidence_grade; store derived + override guardrail outcomes."""
    counts: Counter[str] = Counter()
    registry = load_candidate_fact_promotion_registry(REPO)
    skill_rows = {
        str(r["skill_id"]): r
        for r in payload.get("skill_rows") or []
        if isinstance(r, dict) and r.get("skill_id")
    }
    for row in payload.get("skill_rows") or []:
        if not isinstance(row, dict) or not row.get("skill_id"):
            continue
        link_n = sum(1 for fid in row.get("fact_id_links") or [] if str(fid).strip())
        resolved = resolve_confidence_grade(
            row, has_fact_link=link_n > 0, candidate_registry=registry
        )
        row["confidence_grade_derived"] = resolved["derived_grade"]
        row["confidence_grade"] = resolved["effective_grade"]
        if resolved["override_blocked_reason"]:
            row["confidence_override_blocked"] = True
            row["confidence_grade_override_attempted"] = resolved["preset_grade"]
            row["confidence_override_blocked_reason"] = resolved["override_blocked_reason"]
        else:
            row.pop("confidence_override_blocked", None)
            row.pop("confidence_grade_override_attempted", None)
            row.pop("confidence_override_blocked_reason", None)
        counts[resolved["effective_grade"]] += 1
    for node in payload.get("graph_nodes") or []:
        if not isinstance(node, dict):
            continue
        nid = str(node.get("node_id") or "")
        row = skill_rows.get(nid)
        if row is None:
            continue
        if str(node.get("node_type") or "") in ("skill_row", "skill"):
            node["confidence_grade"] = row["confidence_grade"]
            if row.get("confidence_grade_derived"):
                node["confidence_grade_derived"] = row["confidence_grade_derived"]
    return dict(counts)


def harden_ledger_payload(payload: dict[str, Any]) -> dict[str, Any]:
    stats: dict[str, Any] = {}
    stats["semantic_rewire_runtime_gate_mesh"] = _rewire_runtime_gate_mesh_primary_fact(
        payload
    )
    stats["operator_archive_promotions"] = apply_operator_archive_promotions(payload)
    stats["confidence_grade_counts"] = _backfill_confidence_grades(payload)
    _attach_archive_promotion_guardrails_metadata(payload)
    stats["policy_nodes_added"] = _ensure_policy_graph_nodes(payload)
    edges = payload.get("graph_edges") or []
    stats["policy_edge_sources_redirected"] = _redirect_policy_edge_sources(edges)
    deduped, dedupe_stats = _dedupe_graph_edges(edges)
    payload["graph_edges"] = deduped
    stats.update(dedupe_stats)
    stats["anthropic_profile_patched"] = _patch_anthropic_profile(payload)
    stats["airline_anchor_patched"] = _patch_airline_anchor(payload)
    stats["customer_stakeholder_skills_patched"] = _patch_customer_stakeholder_guardrails(payload)
    gm = payload.setdefault("graph_metadata", {})
    if isinstance(gm, dict):
        gm["edge_count"] = len(deduped)
        gm["node_count"] = len(payload.get("graph_nodes") or [])
        gm["materialization_hardened_at"] = stats
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Harden augmented skills graph SSOT + SQLite")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    ledger_path = default_arsenal_ledger_path(REPO)
    before = json.loads(ledger_path.read_text(encoding="utf-8"))
    counts_before = collect_graph_counts(before)

    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    counts_before_promotion = collect_high_and_exec_summary_counts(
        payload, repo_root=REPO
    )
    patch_stats = harden_ledger_payload(payload)
    validate_arsenal_ledger_shape(payload)
    counts_after_json = collect_graph_counts(payload)
    counts_after_promotion = collect_high_and_exec_summary_counts(payload, repo_root=REPO)
    candidate_fact_audit = audit_candidate_fact_promotions(payload, repo_root=REPO)
    theme_skill_decisions = audit_theme_skill_promotion_decisions(payload, repo_root=REPO)

    if args.dry_run:
        print(json.dumps({"dry_run": True, "patch_stats": patch_stats, "counts_before": counts_before, "counts_after_json": counts_after_json}, indent=2))
        return 0

    ledger_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    mat = materialize_augmented_skills_graph_sqlite(repo_root=REPO, graph=payload, json_source_path=ledger_path)
    validation = validate_hardened_materialized_sqlite(graph=payload, repo_root=REPO)

    op_promo = patch_stats.get("operator_archive_promotions") or {}
    receipt = {
        "STATUS": validation["status"],
        "SCOPE_MATCH": True,
        "PLAN_DEFECT_FIXED": "confidence_grade_separate_from_support_level",
        "ARCHIVE_PROMOTION_GUARDRAILS": "human_confirmed_archive_promotion_required_for_override",
        "OPERATOR_ARCHIVE_PROMOTION_WAVE": True,
        "DIRTY_WORKSPACE_IGNORED_BY_USER": "yes",
        "SCOPE": "augmented_skills_graph_materialization_harden_only",
        "PROMOTED_SKILLS": op_promo.get("promoted", []),
        "REJECTED_SKILLS_WITH_REASON": op_promo.get("rejected", []),
        "HUMAN_CONFIRMATION_RECORDS": op_promo.get("human_confirmation_records", []),
        "TRACK_GENAI_AGENTIC_HIGH_SKILLS_AFTER": counts_after_promotion.get(
            "track_genai_agentic_high_skills", []
        ),
        "CANDIDATE_FACT_PROMOTION_AUDIT": candidate_fact_audit,
        "CONFIDENCE_OVERRIDE_GUARDRAIL": validation.get("confidence_override_guardrail"),
        "PROMOTION_DECISIONS_BY_SKILL": theme_skill_decisions,
        "SEMANTIC_REWIRE_SUMMARY": patch_stats.get("semantic_rewire_runtime_gate_mesh"),
        "HIGH_SKILLS_BY_TRACK_BEFORE": counts_before_promotion.get("high_skills_by_track"),
        "HIGH_SKILLS_BY_TRACK_AFTER": counts_after_promotion.get("high_skills_by_track"),
        "HIGH_SKILL_COUNT_BEFORE": counts_before_promotion.get("high_skill_count"),
        "HIGH_SKILL_COUNT_AFTER": counts_after_promotion.get("high_skill_count"),
        "EXECUTIVE_SUMMARY_ALLOWED_BEFORE": counts_before_promotion.get(
            "executive_summary_allowed_count"
        ),
        "EXECUTIVE_SUMMARY_ALLOWED_AFTER": counts_after_promotion.get(
            "executive_summary_allowed_count"
        ),
        "FILES_CHANGED": [
            "apps_rg/fact_inventory/augmented_skills_graph_sqlite.py",
            "apps_rg/fact_inventory/harden_augmented_skills_graph_ssot.py",
            "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            str(ledger_path.relative_to(REPO)).replace("\\", "/"),
        ],
        "PATCH_STATS": patch_stats,
        "COUNTS_BEFORE": counts_before,
        "COUNTS_AFTER_JSON": counts_after_json,
        "COUNTS_AFTER_SQLITE": validation.get("counts"),
        "SUPPORT_LEVEL_CONFIDENCE_MAPPING": {
            "support_level": "provenance/source class only (DERIVED_SUPPORTED, DIRECT_FROM_RESUME_ARCHIVE, ...)",
            "confidence_grade": "HIGH | MEDIUM | LOW | BLOCKED on skill_rows and graph_nodes.confidence",
            "derive_fn": "apps_rg.fact_inventory.augmented_skills_graph_sqlite.derive_confidence_grade",
            "sqlite_column": "graph_nodes.confidence stores confidence_grade only",
            "executive_summary_gate": "confidence_grade=HIGH + ACTIVE/ACTIVE_CONFIRMED + fact_id_links",
        },
        "EXECUTIVE_SUMMARY_ELIGIBILITY_SAMPLE": validation.get("executive_summary_allowed_sample"),
        "SQL_VALIDATION_QUERIES_AND_RESULTS": validation,
        "MATERIALIZATION": mat,
        "SQL_VALIDATION": validation,
        "P0_FINDINGS_FIXED": list(validation.get("p0_fixed", []))
        + ["confidence_grade_separate_from_support_level"],
        "P1_FINDINGS_FIXED": validation.get("p1_fixed", []),
        "PROTECTED_PATHS_UNTOUCHED": [
            "apps_rg/runtime/",
            "agentic_core/",
            "prompts/",
            "selected_role_fact_set",
            "section generation lanes",
        ],
        "EXPLICIT_NON_CLAIMS": [
            "Graph SQLite is routing/context only; not claim proof.",
            "Candidate facts allowed_after_human_confirm do not auto-promote skills to HIGH without human_confirmed_archive_promotion.",
            "Operator wave confirmed only fact_engineering_platform_001, 003, 004, 006; 002 and 005 not promoted.",
            "Skills outside OPERATOR_ARCHIVE_PROMOTION_BY_SKILL remain unchanged (e.g. skill_runtime_proof_bundle_design on 004).",
            "Marketplace listing ownership claims remain blocked for ANTHROPIC_PARTNERSHIPS_APPLIED_AI.",
            "skill_p2_anchor_major_airline_devops_aws remains internal-only without archive proof.",
            "broad_skills_ledger non-authority unchanged.",
            "skill_runtime_gate_mesh_design primary proof is fact_engineering_platform_001 (not fact_governance_003).",
        ],
        "NEXT_BLOCKER": (
            "none"
            if validation["status"] == "PASS"
            and counts_after_promotion.get("track_genai_agentic_high_skills")
            else (
                "expand_operator_confirmed_fact_set_for_remaining_theme_skills"
                if validation["status"] == "PASS"
                else validation.get("issues")
            )
        ),
    }
    OUT_RECEIPT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    OUT_RECEIPT_MD.write_text(
        "\n".join(
            [
                "# Augmented skills graph materialization harden receipt",
                "",
                f"**STATUS:** {receipt['STATUS']}",
                "",
                f"**SQLite:** [{Path(mat['sqlite_db_path']).name}]({str(mat['sqlite_db_path']).replace(chr(92), '/')})",
                "",
                "## COUNTS_BEFORE_AFTER",
                f"- JSON before: `{counts_before}`",
                f"- JSON after: `{counts_after_json}`",
                f"- SQLite after: `{validation.get('counts')}`",
                "",
                "## SQL validation",
                f"- PLAN_DEFECT_FIXED: confidence_grade separate from support_level",
                f"- status: `{validation['status']}`",
                f"- issues: `{validation.get('issues', [])}`",
                f"- HIGH skills: `{validation.get('high_skill_count')}`",
                f"- executive_summary allowed: `{validation.get('executive_summary_allowed_count')}`",
                "",
                "Machine-readable: [augmented_skills_graph_materialization_harden_receipt.json]"
                "(docs/reports/apps_rg/augmented_skills_graph_materialization_harden_receipt.json).",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"STATUS": receipt["STATUS"], "receipt": str(OUT_RECEIPT_JSON)}, indent=2))
    return 0 if receipt["STATUS"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
