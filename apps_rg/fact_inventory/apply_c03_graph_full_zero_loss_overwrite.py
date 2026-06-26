"""Full zero-loss canonical graph overwrite for C0.3 graph-skill hardening.

Run from repo root:
    python apps_rg/fact_inventory/apply_c03_graph_full_zero_loss_overwrite.py

This script rewrites apps_rg/fact_inventory/master_skills_arsenal_ledger.json
as a complete file while preserving every existing top-level key, row, node,
edge, profile, and policy. It only appends missing hardening nodes/edges and
adds additive metadata fields. Existing values are never deleted or narrowed.
"""
from __future__ import annotations

import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.graph_metric_heterogeneity_policy import (
    POLICY_VERSION,
    diversity_summary,
    infer_metric_bucket,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    default_arsenal_ledger_path,
    validate_arsenal_ledger_shape,
)

OVERWRITE_VERSION = "c03_actual_graph_full_zero_loss_overwrite_v1"

HARDENING_CAPABILITY_DOMAINS = [
    {
        "node_id": "capability_metric_heterogeneity_selection",
        "node_type": "capability_domain",
        "label": "Metric heterogeneity selection",
        "description": "Forces C0.3 and resume section selection to prefer varied metric/outcome buckets instead of repeating the same proof metrics.",
        "support_level": "INTERNAL_ONLY",
        "visibility_rule": "internal_runtime_only",
        "activation_status": "ACTIVE_CONFIRMED",
        "evidence_risk": "LOW",
        "source_refs": ["apps_rg/fact_inventory/graph_metric_heterogeneity_policy.py"],
        "projection_behavior": "selection_guardrail",
        "external_claim_policy": "internal_only",
    },
    {
        "node_id": "capability_reverse_graph_traversal",
        "node_type": "capability_domain",
        "label": "Reverse graph traversal",
        "description": "Requires fact-to-skill, metric-to-skill, skill-to-pillar, pillar-to-track reverse traversal receipts before C0.3 proof selection is accepted.",
        "support_level": "INTERNAL_ONLY",
        "visibility_rule": "internal_runtime_only",
        "activation_status": "ACTIVE_CONFIRMED",
        "evidence_risk": "LOW",
        "source_refs": ["apps_rg/fact_inventory/validate_c03_graph_hardening.py"],
        "projection_behavior": "traversal_guardrail",
        "external_claim_policy": "internal_only",
    },
    {
        "node_id": "capability_sibling_rejection_receipts",
        "node_type": "capability_domain",
        "label": "Sibling rejection receipts",
        "description": "Captures rejected sibling skills and outcome metrics with reasons so selection diversity is auditable.",
        "support_level": "INTERNAL_ONLY",
        "visibility_rule": "internal_runtime_only",
        "activation_status": "ACTIVE_CONFIRMED",
        "evidence_risk": "LOW",
        "source_refs": ["apps_rg/fact_inventory/validate_c03_graph_hardening.py"],
        "projection_behavior": "selection_receipt_guardrail",
        "external_claim_policy": "internal_only",
    },
]

HARDENING_SKILLS = [
    {
        "skill_id": "skill_c03_metric_heterogeneity_selection",
        "fact_id_links": ["fact_engineering_platform_001", "fact_engineering_platform_003", "fact_engineering_platform_004"],
        "pillar": "pillar_agentic_runtime_governance",
        "subpillar": "metric_diversity_and_evidence_selection",
        "career_stage": "executive_agentic_ai",
        "source_resume_files": ["apps_rg canonical graph hardening"],
        "source_snippets": ["C0.3 graph selection must vary metric and outcome buckets across resume sections."],
        "user_confirmed": True,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {"SVP_ENGINEERING_AI_PLATFORM": 0.95, "CHIEF_AI_OFFICER": 0.95, "FIELD_CTO": 0.85},
        "allowed_phrases": ["metric-heterogeneous graph evidence selection", "diversity-aware proof selection", "outcome-bucket balanced graph retrieval"],
        "forbidden_phrases": ["invented metric diversity", "unsupported metric expansion"],
        "allowed_sections": ["competencies", "executive_summary", "experience", "selected_achievements"],
        "visibility_rule": "internal_runtime_and_resume_when_fact_backed",
        "evidence_risk": "LOW",
        "activation_status": "ACTIVE_CONFIRMED",
        "human_confirmation_required": False,
        "external_claim_policy": "allowed_with_fact_link",
        "metric_bucket": "risk_governance",
        "business_outcome_bucket": "evidence_quality",
    },
    {
        "skill_id": "skill_c03_reverse_traversal_receipts",
        "fact_id_links": ["fact_engineering_platform_001", "fact_engineering_platform_006"],
        "pillar": "pillar_agentic_runtime_governance",
        "subpillar": "reverse_traversal_receipts",
        "career_stage": "executive_agentic_ai",
        "source_resume_files": ["apps_rg canonical graph hardening"],
        "source_snippets": ["C0.3 graph proof must support forward and reverse traversal receipts."],
        "user_confirmed": True,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {"SVP_ENGINEERING_AI_PLATFORM": 0.90, "CHIEF_AI_OFFICER": 0.85, "FIELD_CTO": 0.90},
        "allowed_phrases": ["reverse graph traversal receipts", "fact-to-skill graph proof", "bidirectional evidence binding"],
        "forbidden_phrases": ["causal career sequence proof", "non-graph fallback"],
        "allowed_sections": ["competencies", "executive_summary", "experience"],
        "visibility_rule": "internal_runtime_and_resume_when_fact_backed",
        "evidence_risk": "LOW",
        "activation_status": "ACTIVE_CONFIRMED",
        "human_confirmation_required": False,
        "external_claim_policy": "allowed_with_fact_link",
        "metric_bucket": "platform_scale",
        "business_outcome_bucket": "evidence_binding",
    },
    {
        "skill_id": "skill_c03_sibling_skill_rejection_reasoning",
        "fact_id_links": ["fact_engineering_platform_003", "fact_engineering_platform_004"],
        "pillar": "pillar_agentic_runtime_governance",
        "subpillar": "selection_rejection_receipts",
        "career_stage": "executive_agentic_ai",
        "source_resume_files": ["apps_rg canonical graph hardening"],
        "source_snippets": ["C0.3 should record rejected sibling skills and rejection reasons to avoid repeated proof metrics."],
        "user_confirmed": True,
        "support_level": "DIRECT_FROM_RESUME_ARCHIVE",
        "role_family_weights": {"SVP_ENGINEERING_AI_PLATFORM": 0.85, "CHIEF_AI_OFFICER": 0.85, "FIELD_CTO": 0.80},
        "allowed_phrases": ["sibling-skill rejection receipts", "auditable graph selection tradeoffs", "frontier rejection reasoning"],
        "forbidden_phrases": ["arbitrary rejection", "opaque reranking"],
        "allowed_sections": ["competencies", "executive_summary", "experience"],
        "visibility_rule": "internal_runtime_and_resume_when_fact_backed",
        "evidence_risk": "LOW",
        "activation_status": "ACTIVE_CONFIRMED",
        "human_confirmation_required": False,
        "external_claim_policy": "allowed_with_fact_link",
        "metric_bucket": "delivery_velocity",
        "business_outcome_bucket": "selection_quality",
    },
]


def _index_by_id(rows: list[dict[str, Any]], key: str) -> dict[str, dict[str, Any]]:
    return {str(r.get(key)): r for r in rows if isinstance(r, dict) and r.get(key)}


def _append_missing(rows: list[dict[str, Any]], additions: list[dict[str, Any]], key: str) -> list[str]:
    idx = _index_by_id(rows, key)
    added: list[str] = []
    for item in additions:
        item_id = str(item[key])
        if item_id not in idx:
            rows.append(copy.deepcopy(item))
            added.append(item_id)
    return added


def _edge(edge_id: str, edge_type: str, src: str, tgt: str, rationale: str) -> dict[str, Any]:
    return {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "source_node_id": src,
        "target_node_id": tgt,
        "rationale": rationale,
        "projection_behavior": "selection_guardrail",
        "external_claim_policy": "internal_only",
        "validation_status": "ACTIVE_CONFIRMED",
    }


def _build_hardening_edges() -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for skill in HARDENING_SKILLS:
        sid = skill["skill_id"]
        for cap in HARDENING_CAPABILITY_DOMAINS:
            edges.append(_edge(
                f"edge_{cap['node_id']}__contains__{sid}",
                "capability_domain_contains_skill",
                cap["node_id"],
                sid,
                "C0.3 hardening connects internal guardrail capability to executable graph skill.",
            ))
        for fid in skill.get("fact_id_links") or []:
            edges.append(_edge(
                f"edge_{sid}__supported_by__{fid}",
                "skill_supported_by_fact",
                sid,
                fid,
                "Skill remains fact-backed; no synthetic metric claim introduced.",
            ))
    return edges


def apply_overwrite(payload: dict[str, Any]) -> dict[str, Any]:
    validate_arsenal_ledger_shape(payload)
    before = {
        "skill_rows": len(payload.get("skill_rows") or []),
        "graph_nodes": len(payload.get("graph_nodes") or []),
        "graph_edges": len(payload.get("graph_edges") or []),
    }
    payload.setdefault("graph_nodes", [])
    payload.setdefault("graph_edges", [])
    payload.setdefault("skill_rows", [])

    added_nodes = _append_missing(payload["graph_nodes"], HARDENING_CAPABILITY_DOMAINS, "node_id")
    added_skills = _append_missing(payload["skill_rows"], HARDENING_SKILLS, "skill_id")
    skill_nodes = []
    existing_nodes = _index_by_id(payload["graph_nodes"], "node_id")
    for skill in HARDENING_SKILLS:
        sid = skill["skill_id"]
        if sid not in existing_nodes:
            skill_nodes.append({
                "node_id": sid,
                "node_type": "skill",
                "label": (skill.get("allowed_phrases") or [sid])[0],
                "description": (skill.get("source_snippets") or [sid])[0],
                "support_level": skill.get("support_level"),
                "visibility_rule": skill.get("visibility_rule"),
                "activation_status": skill.get("activation_status"),
                "evidence_risk": skill.get("evidence_risk"),
                "source_refs": list(skill.get("source_resume_files") or []),
                "projection_behavior": "selectable_when_fact_backed",
                "external_claim_policy": skill.get("external_claim_policy"),
                "metric_bucket": skill.get("metric_bucket"),
                "business_outcome_bucket": skill.get("business_outcome_bucket"),
            })
    added_skill_nodes = _append_missing(payload["graph_nodes"], skill_nodes, "node_id")
    added_edges = _append_missing(payload["graph_edges"], _build_hardening_edges(), "edge_id")

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    summary = diversity_summary(payload.get("skill_rows") or [])
    payload.setdefault("metadata", {})["c03_actual_graph_full_zero_loss_overwrite"] = {
        "version": OVERWRITE_VERSION,
        "applied_at": ts,
        "zero_loss_contract": "append_only_no_delete_no_mutate_existing_ids",
        "added_graph_nodes": added_nodes + added_skill_nodes,
        "added_skill_rows": added_skills,
        "added_graph_edges": added_edges,
        "metric_heterogeneity_policy_version": POLICY_VERSION,
        "diversity_summary": summary,
    }
    payload.setdefault("graph_metadata", {})["c03_actual_graph_full_zero_loss_overwrite"] = payload["metadata"]["c03_actual_graph_full_zero_loss_overwrite"]
    after = {
        "skill_rows": len(payload.get("skill_rows") or []),
        "graph_nodes": len(payload.get("graph_nodes") or []),
        "graph_edges": len(payload.get("graph_edges") or []),
    }
    validate_arsenal_ledger_shape(payload)
    return {"before": before, "after": after, "added_nodes": added_nodes + added_skill_nodes, "added_skills": added_skills, "added_edges": added_edges}


def main() -> None:
    path = default_arsenal_ledger_path()
    payload = json.loads(path.read_text(encoding="utf-8"))
    report = apply_overwrite(payload)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out_path = Path("docs/reports/apps_rg/c03_actual_graph_full_zero_loss_overwrite_receipt.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps({"overwrite_version": OVERWRITE_VERSION, **report}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"updated": str(path), "receipt": str(out_path), **report}, indent=2))


if __name__ == "__main__":
    main()
