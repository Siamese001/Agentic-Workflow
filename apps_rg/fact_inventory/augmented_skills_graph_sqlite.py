"""Materialize augmented_skills_graph (JSON ledger) into SQLite for C0.3 context lookup.

Graph rows organize/rout capabilities — they are not claim proof. Facts remain proof substrate.
"""
from __future__ import annotations

import hashlib
import json
import os
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import (
    graph_version_from_payload,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
    validate_arsenal_ledger_shape,
)
from apps_rg.fact_inventory.track_weighted_graph_expansion import (
    ROLE_FAMILY_TRACK_WEIGHTS,
    SENIOR_ROLE_TAXONOMY_IDS,
)

REPO_REL_DB = Path("artifacts/apps_rg/fact_inventory/augmented_skills_graph.sqlite")

CANONICAL_NODE_TYPES = frozenset(
    {
        "pillar",
        "skill",
        "fact",
        "role_family",
        "career_track",
        "career_epoch",
        "capability_domain",
        "employment",
        "locked_bullet",
        "certification",
        "section",
        "concept",
        "repo_evidence",
        "policy",
        "policy_rule",
        "graph_ref",
        # W2.0 (typed-edge-role-facet-guardrails-a6f3d2): first-class metric_outcome
        # nodes materialized from role_episode_bundle metric_outcome_nodes dicts.
        "metric_outcome",
    }
)

RAW_TO_CANONICAL_NODE_TYPE: dict[str, str] = {
    "domain_pillar": "pillar",
    "skill_row": "skill",
    "career_track": "career_track",
    "career_epoch": "career_epoch",
    "capability_domain": "capability_domain",
    "identity_north_star": "role_family",
    "employment": "employment",
    "locked_bullet": "locked_bullet",
    "certification": "certification",
    "section": "section",
    "concept": "concept",
    "repo_evidence": "repo_evidence",
    "policy": "policy",
    "policy_rule": "policy_rule",
}

POLICY_EDGE_SOURCE_KEYS = frozenset(
    {
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
)

FORBIDDEN_SKILL_NODE_IDS = frozenset(
    {
        "skill_projection_not_proof",
        "skill_id_never_source_fact_id",
    }
)

NON_PROMOTE_ACTIVATION = frozenset(
    {"DRAFT", "INTERNAL_ONLY", "DO_NOT_PROMOTE", "BLOCKED", "USER_CONFIRMED_PENDING_SOURCE"}
)

EXTERNAL_ACTIVE_STATUSES = frozenset({"ACTIVE", "ACTIVE_CONFIRMED"})

CONFIDENCE_GRADES = frozenset({"HIGH", "MEDIUM", "LOW", "BLOCKED"})

BLOCKED_SUPPORT_LEVELS = frozenset(
    {
        "INTERNAL_ONLY",
        "USER_CONFIRMED_PENDING_SOURCE",
        "REPO_EVIDENCE_PORTFOLIO",
        "BLOCKED",
        "TARGETING_ONLY",
        "STYLE_ONLY",
    }
)

BLOCKED_EXTERNAL_CLAIM_POLICIES = frozenset(
    {
        "pending_source_internal_only",
        "weak_snippet_internal_only",
        "repo_portfolio_not_resume_default",
        "internal_traversal_only",
        "skill_projection_not_proof",
    }
)

CONFIDENCE_GRADE_RANK: dict[str, int] = {
    "BLOCKED": 0,
    "LOW": 1,
    "MEDIUM": 2,
    "HIGH": 3,
}

CANDIDATE_LEDGER_REL_PATH = Path(
    "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
)

ENGINEERING_PLATFORM_CANDIDATE_FACT_IDS = frozenset(
    {
        "fact_engineering_platform_001",
        "fact_engineering_platform_002",
        "fact_engineering_platform_003",
        "fact_engineering_platform_004",
        "fact_engineering_platform_005",
        "fact_engineering_platform_006",
    }
)

HUMAN_CONFIRM_REQUIRED_ALLOWED_RESUME_USE = frozenset({"allowed_after_human_confirm"})

THEME_AGENTIC_SKILL_IDS = frozenset(
    {
        "skill_governed_agentic_systems_architecture",
        "skill_runtime_gate_mesh_design",
        "skill_prompt_assembly_architecture",
        "skill_context_engineering",
        "skill_evidence_contract_design",
        "skill_dense_sparse_exact_retrieval_design",
        "skill_graph_aware_relationship_grounding",
        "skill_audit_grade_observability",
        "skill_ai_governance_certification",
        "skill_reusable_agentic_platform_architecture",
        "skill_agentic_platform_productization",
        "skill_runtime_proof_bundle_design",
    }
)

OPERATOR_CONFIRMED_ARCHIVE_FACT_IDS = frozenset(
    {
        "fact_engineering_platform_001",
        "fact_engineering_platform_003",
        "fact_engineering_platform_004",
        "fact_engineering_platform_006",
    }
)

OPERATOR_ARCHIVE_PROMOTION_BY_SKILL: dict[str, list[str]] = {
    "skill_governed_agentic_systems_architecture": ["fact_engineering_platform_001"],
    "skill_runtime_gate_mesh_design": ["fact_engineering_platform_001"],
    "skill_context_engineering": ["fact_engineering_platform_003"],
    "skill_prompt_assembly_architecture": ["fact_engineering_platform_003"],
    "skill_dense_sparse_exact_retrieval_design": ["fact_engineering_platform_001"],
    "skill_graph_aware_relationship_grounding": ["fact_engineering_platform_001"],
    "skill_audit_grade_observability": [
        "fact_engineering_platform_003",
        "fact_engineering_platform_004",
    ],
    "skill_reusable_agentic_platform_architecture": ["fact_engineering_platform_006"],
    "skill_agentic_platform_productization": ["fact_engineering_platform_006"],
}

FORBIDDEN_PROMOTION_SKILL_SUBSTRINGS = (
    "airline",
    "brokerage",
    "underwriting",
    "claims",
    "marketplace",
)

DDL_STATEMENTS: tuple[str, ...] = (
    """
    CREATE TABLE IF NOT EXISTS graph_nodes (
        node_id TEXT PRIMARY KEY,
        node_type TEXT NOT NULL,
        label TEXT NOT NULL,
        description TEXT NOT NULL DEFAULT '',
        activation_status TEXT NOT NULL DEFAULT '',
        support_level TEXT NOT NULL DEFAULT '',
        confidence TEXT NOT NULL DEFAULT '',
        external_eligible INTEGER NOT NULL DEFAULT 0,
        source_authority TEXT NOT NULL DEFAULT 'augmented_skills_graph',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS graph_edges (
        edge_id TEXT PRIMARY KEY,
        source_node_id TEXT NOT NULL,
        target_node_id TEXT NOT NULL,
        edge_family TEXT NOT NULL DEFAULT '',
        edge_type TEXT NOT NULL,
        weight REAL NOT NULL DEFAULT 1.0,
        confidence TEXT NOT NULL DEFAULT '',
        directional INTEGER NOT NULL DEFAULT 1,
        evidence_status TEXT NOT NULL DEFAULT '',
        section_fit TEXT NOT NULL DEFAULT '',
        source_authority TEXT NOT NULL DEFAULT 'augmented_skills_graph'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS skill_fact_links (
        skill_id TEXT NOT NULL,
        fact_id TEXT NOT NULL,
        support_level TEXT NOT NULL DEFAULT '',
        claim_eligibility INTEGER NOT NULL DEFAULT 0,
        source_trace TEXT NOT NULL DEFAULT '',
        archive_trace TEXT NOT NULL DEFAULT '',
        human_confirmed INTEGER NOT NULL DEFAULT 0,
        external_eligible INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (skill_id, fact_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS section_eligibility (
        node_id TEXT NOT NULL,
        section_id TEXT NOT NULL,
        allowed INTEGER NOT NULL DEFAULT 0,
        claim_policy TEXT NOT NULL DEFAULT '',
        reason TEXT NOT NULL DEFAULT '',
        blocked_reason TEXT NOT NULL DEFAULT '',
        PRIMARY KEY (node_id, section_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS role_family_projection (
        role_family_id TEXT PRIMARY KEY,
        projection_role_family_key TEXT NOT NULL,
        track_weight_profile TEXT NOT NULL DEFAULT '{}',
        taxonomy_source TEXT NOT NULL DEFAULT '',
        targeting_keywords TEXT NOT NULL DEFAULT '[]',
        proof_policy_note TEXT NOT NULL DEFAULT 'graph_routing_not_claim_proof'
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS graph_metadata (
        graph_version TEXT PRIMARY KEY,
        materialized_from TEXT NOT NULL,
        materialized_at TEXT NOT NULL,
        ledger_hash TEXT NOT NULL,
        graph_count_summary TEXT NOT NULL DEFAULT '{}',
        authority_status TEXT NOT NULL DEFAULT 'augmented_skills_graph_authoritative'
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_graph_nodes_type ON graph_nodes(node_type)",
    "CREATE INDEX IF NOT EXISTS idx_graph_edges_type ON graph_edges(edge_type)",
    "CREATE INDEX IF NOT EXISTS idx_graph_edges_src ON graph_edges(source_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_graph_edges_tgt ON graph_edges(target_node_id)",
    "CREATE INDEX IF NOT EXISTS idx_section_eligibility_section ON section_eligibility(section_id)",
    "CREATE INDEX IF NOT EXISTS idx_skill_fact_links_fact ON skill_fact_links(fact_id)",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256_hex(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def default_graph_sqlite_path(repo_root: Path | None = None) -> Path:
    root = repo_root or _repo_root()
    env = str(os.environ.get("APPS_RG_AUGMENTED_SKILLS_GRAPH_SQLITE_PATH") or "").strip()
    if env:
        p = Path(env)
        return p if p.is_absolute() else (root / p).resolve()
    return (root / REPO_REL_DB).resolve()


def infer_node_type_from_id(node_id: str) -> str:
    nid = str(node_id or "").strip()
    if not nid:
        return "graph_ref"
    if nid.startswith("policy_rule_") or nid in POLICY_EDGE_SOURCE_KEYS:
        return "policy_rule"
    if nid.startswith("policy_"):
        return "policy"
    if nid.startswith("section_"):
        return "section"
    if nid.startswith("concept_"):
        return "concept"
    if nid.startswith("repo_"):
        return "repo_evidence"
    if nid.startswith("domain_"):
        return "capability_domain"
    if nid.startswith("employment_") or nid.startswith("exp_"):
        return "employment"
    if nid.startswith("bul_"):
        return "locked_bullet"
    if nid.startswith("cert_"):
        return "certification"
    if nid.startswith("fact_") or nid.startswith("node_fact_"):
        return "fact"
    # W2.0: metric_outcome IDs are minted as ``metric_<employer>_<...>`` in
    # role_episode_bundle files. Inference precedes the skill_ branch because
    # neither prefix collides with the other.
    if nid.startswith("metric_"):
        return "metric_outcome"
    if nid.startswith("skill_"):
        return "skill"
    if nid.startswith("pillar_"):
        return "pillar"
    if nid.startswith("track_"):
        return "career_track"
    if nid.startswith("epoch_"):
        return "career_epoch"
    return "graph_ref"


def resolve_node_type(node_id: str, raw_type: str) -> str:
    nid = str(node_id or "").strip()
    low = str(raw_type or "").strip()
    if nid in FORBIDDEN_SKILL_NODE_IDS:
        return "policy_rule"
    if low in CANONICAL_NODE_TYPES and low != nid:
        return low
    mapped = RAW_TO_CANONICAL_NODE_TYPE.get(low)
    if mapped and mapped != nid:
        return mapped
    inferred = infer_node_type_from_id(nid)
    if inferred != "graph_ref":
        return inferred
    if low and low != nid:
        return low
    return inferred


def canonical_node_type(raw: str, *, node_id: str = "") -> str:
    if node_id:
        return resolve_node_type(node_id, raw)
    r = str(raw or "").strip()
    if r in CANONICAL_NODE_TYPES or r in RAW_TO_CANONICAL_NODE_TYPE:
        return resolve_node_type("", r)
    return resolve_node_type(r, "")


def _is_skill_id(value: str) -> bool:
    return str(value or "").startswith("skill_")


def derive_confidence_grade(
    row: dict[str, Any],
    *,
    has_fact_link: bool = False,
) -> str:
    """Map provenance support_level + activation to confidence_grade (not support_level overload)."""
    visibility = str(row.get("visibility_rule") or "").strip()
    if visibility == "never_external":
        return "BLOCKED"
    policy = str(row.get("external_claim_policy") or "").strip()
    if policy in BLOCKED_EXTERNAL_CLAIM_POLICIES:
        return "BLOCKED"
    support = str(row.get("support_level") or "").strip()
    if support in BLOCKED_SUPPORT_LEVELS:
        return "BLOCKED"
    status = str(row.get("activation_status") or "").strip()
    if status in ("BLOCKED", "DO_NOT_PROMOTE"):
        return "BLOCKED"
    links = row.get("fact_id_links") or []
    has_link = has_fact_link or bool(links)

    if status == "ACTIVE_CONFIRMED" and has_link:
        if support == "DIRECT_FROM_RESUME_ARCHIVE":
            return "HIGH"
        if support == "BUNDLE_SUPPORTED" and skill_row_eligible_for_external_claim(row):
            return "HIGH"
    if status == "ACTIVE" and support == "DERIVED_SUPPORTED" and has_link:
        return "MEDIUM"
    if status == "DRAFT" and support in ("DIRECT_FROM_RESUME_ARCHIVE", "DERIVED_SUPPORTED"):
        return "LOW"
    if status == "ACTIVE" and support == "DIRECT_FROM_RESUME_ARCHIVE" and has_link:
        return "MEDIUM"
    if status == "ACTIVE_CONFIRMED" and support == "DERIVED_SUPPORTED" and has_link:
        return "MEDIUM"
    return "BLOCKED"


def default_candidate_fact_ledger_path(repo_root: Path | None = None) -> Path:
    root = repo_root or _repo_root()
    return (root / CANDIDATE_LEDGER_REL_PATH).resolve()


def load_candidate_fact_promotion_registry(
    repo_root: Path | None = None,
) -> dict[str, dict[str, Any]]:
    """Load candidate-fact promotion metadata; does not auto-promote skills."""
    path = default_candidate_fact_ledger_path(repo_root)
    if not path.is_file():
        return {}
    payload = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for raw in payload.get("candidate_facts") or []:
        if not isinstance(raw, dict):
            continue
        fid = str(raw.get("candidate_fact_id") or "").strip()
        if not fid:
            continue
        allowed = str(raw.get("allowed_resume_use") or "").strip()
        human_records = raw.get("human_confirmed_archive_promotions") or []
        has_human = bool(
            raw.get("human_confirmed_archive_promotion")
            or (isinstance(human_records, list) and human_records)
        )
        out[fid] = {
            "candidate_fact_id": fid,
            "candidate_confidence": str(raw.get("confidence") or ""),
            "allowed_resume_use": allowed,
            "source_resume_variants": list(raw.get("source_resume_variants") or []),
            "capability_tags": list(raw.get("capability_tags") or []),
            "claim_text": str(raw.get("claim_text") or ""),
            "ledger_status": str(payload.get("status") or ""),
            "has_explicit_human_confirmation": has_human,
            "promotion_status": (
                "PROMOTE_NOW"
                if has_human
                else "PROMOTION_READY_NEEDS_HUMAN_CONFIRM"
                if allowed in HUMAN_CONFIRM_REQUIRED_ALLOWED_RESUME_USE
                else "NEEDS_REVIEW"
            ),
        }
    return out


def parse_human_confirmed_archive_promotion(row: dict[str, Any]) -> dict[str, Any] | None:
    promo = row.get("human_confirmed_archive_promotion")
    if not isinstance(promo, dict):
        return None
    required = (
        "human_confirmed_by",
        "human_confirmed_at",
        "source_fact_ids",
        "override_reason",
    )
    if not all(str(promo.get(k) or "").strip() for k in required):
        return None
    source_ids = promo.get("source_fact_ids")
    if not isinstance(source_ids, list) or not source_ids:
        return None
    return promo


def has_valid_human_confirmed_archive_promotion(row: dict[str, Any]) -> bool:
    return parse_human_confirmed_archive_promotion(row) is not None


def skill_links_only_engineering_candidate_pending_confirm(
    row: dict[str, Any],
    candidate_registry: dict[str, dict[str, Any]] | None,
) -> bool:
    """True when every linked fact is an engineering-platform candidate awaiting human confirm.

    Does not cap skills anchored to governance/GTM/archive facts that already meet HIGH derivation.
    """
    if has_valid_human_confirmed_archive_promotion(row):
        return False
    registry = candidate_registry or {}
    links = [str(x).strip() for x in (row.get("fact_id_links") or []) if str(x).strip()]
    if not links:
        return False
    if not all(fid in ENGINEERING_PLATFORM_CANDIDATE_FACT_IDS for fid in links):
        return False
    return all(
        registry.get(fid, {}).get("promotion_status")
        == "PROMOTION_READY_NEEDS_HUMAN_CONFIRM"
        for fid in links
    )


def cap_derived_grade_for_candidate_facts(
    row: dict[str, Any],
    derived: str,
    *,
    candidate_registry: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Prevent candidate-only facts from yielding HIGH without human confirmation."""
    if derived != "HIGH":
        return derived
    if skill_links_only_engineering_candidate_pending_confirm(row, candidate_registry):
        return "MEDIUM"
    return derived


def resolve_confidence_grade(
    row: dict[str, Any],
    *,
    has_fact_link: bool = False,
    candidate_registry: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Resolve effective grade with override guardrails and candidate-fact cap."""
    derived = derive_confidence_grade(row, has_fact_link=has_fact_link)
    derived = cap_derived_grade_for_candidate_facts(
        row, derived, candidate_registry=candidate_registry
    )
    preset = str(row.get("confidence_grade") or "").strip().upper()
    override_blocked_reason = ""
    effective = derived
    if preset in CONFIDENCE_GRADES:
        preset_rank = CONFIDENCE_GRADE_RANK.get(preset, -1)
        derived_rank = CONFIDENCE_GRADE_RANK.get(derived, -1)
        if preset_rank > derived_rank:
            if has_valid_human_confirmed_archive_promotion(row):
                effective = preset
            else:
                effective = derived
                override_blocked_reason = (
                    "confidence_override_blocked_missing_human_confirmation"
                )
        else:
            # Stale lower presets must not suppress proof-derived grades.
            effective = derived
    return {
        "derived_grade": derived,
        "effective_grade": effective,
        "preset_grade": preset if preset in CONFIDENCE_GRADES else "",
        "override_blocked_reason": override_blocked_reason,
        "human_confirmed_archive_promotion": has_valid_human_confirmed_archive_promotion(row),
        "candidate_pending_only": skill_links_only_engineering_candidate_pending_confirm(
            row, candidate_registry
        ),
    }


def confidence_grade_for_skill_row(
    row: dict[str, Any],
    *,
    has_fact_link: bool = False,
    candidate_registry: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Effective confidence_grade: derived proof or explicit human-confirmed override only."""
    return resolve_confidence_grade(
        row,
        has_fact_link=has_fact_link,
        candidate_registry=candidate_registry,
    )["effective_grade"]


def audit_candidate_fact_promotions(
    payload: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> list[dict[str, Any]]:
    """Graph-only promotion plan for engineering-platform candidate facts."""
    registry = load_candidate_fact_promotion_registry(repo_root)
    skill_rows = {
        str(r["skill_id"]): r
        for r in payload.get("skill_rows") or []
        if isinstance(r, dict) and r.get("skill_id")
    }
    for r in payload.get("agentic_runtime_matrix") or []:
        if isinstance(r, dict) and r.get("skill_id"):
            sid = str(r["skill_id"])
            if sid not in skill_rows:
                skill_rows[sid] = r
            else:
                links = set(skill_rows[sid].get("fact_id_links") or [])
                links.update(r.get("fact_id_links") or [])
                skill_rows[sid]["fact_id_links"] = sorted(links)
    audits: list[dict[str, Any]] = []
    for fid in sorted(ENGINEERING_PLATFORM_CANDIDATE_FACT_IDS):
        meta = registry.get(fid, {})
        linked = sorted(
            sid
            for sid, row in skill_rows.items()
            if fid in (row.get("fact_id_links") or [])
        )
        audits.append(
            {
                "candidate_fact_id": fid,
                "candidate_confidence": meta.get("candidate_confidence", ""),
                "allowed_resume_use": meta.get("allowed_resume_use", ""),
                "source_resume_variants": meta.get("source_resume_variants", []),
                "capability_tags": meta.get("capability_tags", []),
                "eligible_linked_skills": linked,
                "promotion_decision": meta.get("promotion_status", "UNKNOWN"),
                "PROMOTE_NOW": meta.get("promotion_status") == "PROMOTE_NOW",
                "PROMOTION_READY_NEEDS_HUMAN_CONFIRM": meta.get(
                    "promotion_status"
                )
                == "PROMOTION_READY_NEEDS_HUMAN_CONFIRM",
            }
        )
    return audits


def classify_skill_archive_promotion(
    row: dict[str, Any],
    *,
    candidate_registry: dict[str, dict[str, Any]] | None = None,
) -> str:
    """Promotion decision enum for governed agentic/platform skills."""
    sid = str(row.get("skill_id") or "")
    support = str(row.get("support_level") or "")
    activation = str(row.get("activation_status") or "")
    links = list(row.get("fact_id_links") or [])

    if has_valid_human_confirmed_archive_promotion(row):
        return "PROMOTE_NOW_HUMAN_CONFIRMED"
    if support in BLOCKED_SUPPORT_LEVELS or activation in NON_PROMOTE_ACTIVATION:
        if support == "REPO_EVIDENCE_PORTFOLIO" or (
            activation == "DRAFT" and not links
        ):
            return "KEEP_BLOCKED_REPO_ONLY"
        return "KEEP_BLOCKED_REPO_ONLY"
    if sid == "skill_runtime_gate_mesh_design":
        primary = str(row.get("primary_fact_id") or "")
        if primary == "fact_engineering_platform_001":
            return "SEMANTIC_REWIRE_ONLY"
        if "fact_governance_003" in links and "fact_engineering_platform_001" not in links:
            return "SEMANTIC_REWIRE_READY"
    if not links:
        return "KEEP_MEDIUM_NEEDS_ARCHIVE_LINK"
    if skill_links_only_engineering_candidate_pending_confirm(row, candidate_registry):
        return "PROMOTION_READY_NEEDS_HUMAN_CONFIRM"
    return "KEEP_MEDIUM_NEEDS_ARCHIVE_LINK"


def audit_theme_skill_promotion_decisions(
    payload: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> list[dict[str, Any]]:
    registry = load_candidate_fact_promotion_registry(repo_root)
    skill_rows = {
        str(r["skill_id"]): r
        for r in payload.get("skill_rows") or []
        if isinstance(r, dict) and r.get("skill_id")
    }
    for r in payload.get("agentic_runtime_matrix") or []:
        if isinstance(r, dict) and r.get("skill_id"):
            skill_rows.setdefault(str(r["skill_id"]), r)
    out: list[dict[str, Any]] = []
    for sid in sorted(THEME_AGENTIC_SKILL_IDS):
        row = skill_rows.get(sid)
        if not row:
            out.append({"skill_id": sid, "decision": "MISSING_SKILL_ROW"})
            continue
        resolved = resolve_confidence_grade(
            row,
            has_fact_link=bool(row.get("fact_id_links")),
            candidate_registry=registry,
        )
        out.append(
            {
                "skill_id": sid,
                "decision": classify_skill_archive_promotion(
                    row, candidate_registry=registry
                ),
                "confidence_grade_derived": resolved["derived_grade"],
                "confidence_grade_effective": resolved["effective_grade"],
                "activation_status": row.get("activation_status"),
                "support_level": row.get("support_level"),
                "fact_id_links": list(row.get("fact_id_links") or []),
                "primary_fact_id": row.get("primary_fact_id"),
                "override_blocked_reason": resolved["override_blocked_reason"],
            }
        )
    return out


def build_skill_rows_by_id(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Merge skill_rows SSOT with agentic_runtime_matrix (agentic wins on collision)."""
    out: dict[str, dict[str, Any]] = {}
    for r in payload.get("skill_rows") or []:
        if isinstance(r, dict) and r.get("skill_id"):
            out[str(r["skill_id"])] = r
    for r in payload.get("agentic_runtime_matrix") or []:
        if isinstance(r, dict) and r.get("skill_id"):
            out[str(r["skill_id"])] = r
    return out


def _reject_operator_promotion_reason(row: dict[str, Any], fact_ids: list[str]) -> str:
    sid = str(row.get("skill_id") or "")
    if any(tok in sid.lower() for tok in FORBIDDEN_PROMOTION_SKILL_SUBSTRINGS):
        return f"forbidden_skill_id_pattern:{sid}"
    support = str(row.get("support_level") or "")
    activation = str(row.get("activation_status") or "")
    if support in BLOCKED_SUPPORT_LEVELS:
        return f"blocked_support_level:{support}"
    if activation in NON_PROMOTE_ACTIVATION:
        return f"blocked_activation_status:{activation}"
    if str(row.get("visibility_rule") or "") == "never_external":
        return "never_external_visibility"
    policy = str(row.get("external_claim_policy") or "")
    if policy in BLOCKED_EXTERNAL_CLAIM_POLICIES:
        return f"blocked_external_claim_policy:{policy}"
    if not fact_ids:
        return "missing_confirmed_fact_ids"
    for fid in fact_ids:
        if fid not in OPERATOR_CONFIRMED_ARCHIVE_FACT_IDS:
            return f"fact_not_operator_confirmed:{fid}"
    if any(_is_skill_id(str(x)) for x in fact_ids):
        return "invalid_fact_id_links_skill_id_shape"
    return ""


def _sync_skill_row_to_payload_collections(
    payload: dict[str, Any],
    row: dict[str, Any],
) -> None:
    """Keep graph_nodes / agentic_runtime_matrix / skill_rows aligned for one skill."""
    sid = str(row.get("skill_id") or "")
    if not sid:
        return
    for collection, key in (
        ("agentic_runtime_matrix", "skill_id"),
        ("graph_nodes", "node_id"),
    ):
        for existing in payload.get(collection) or []:
            if isinstance(existing, dict) and str(existing.get(key)) == sid:
                existing.update(row)
    skill_rows = payload.setdefault("skill_rows", [])
    found = False
    for i, existing in enumerate(skill_rows):
        if isinstance(existing, dict) and str(existing.get("skill_id")) == sid:
            skill_rows[i] = {**existing, **row}
            found = True
            break
    if not found:
        skill_rows.append(dict(row))


def _rewire_skill_fact_edges(
    payload: dict[str, Any],
    skill_id: str,
    fact_ids: list[str],
) -> int:
    """Ensure skill_supported_by_fact edges target operator-confirmed facts only."""
    rewritten = 0
    primary = fact_ids[0] if fact_ids else ""
    keep_ids = set(fact_ids)
    edges = payload.get("graph_edges") or []
    for edge in edges:
        if not isinstance(edge, dict):
            continue
        if str(edge.get("edge_type")) != "skill_supported_by_fact":
            continue
        if str(edge.get("source_node_id")) != skill_id:
            continue
        tgt = str(edge.get("target_node_id") or "")
        if tgt in keep_ids:
            continue
        if primary:
            edge["target_node_id"] = primary
            edge["edge_id"] = f"edge_skill_fact_{skill_id}_{primary}"
            edge["rationale"] = "Operator-confirmed archive promotion anchor"
            rewritten += 1
    for fid in fact_ids:
        eid = f"edge_skill_fact_{skill_id}_{fid}"
        if any(
            isinstance(e, dict)
            and str(e.get("edge_id")) == eid
            for e in edges
        ):
            continue
        edges.append(
            {
                "edge_id": eid,
                "edge_type": "skill_supported_by_fact",
                "source_node_id": skill_id,
                "target_node_id": fid,
                "rationale": "Operator-confirmed archive promotion anchor",
                "projection_behavior": "graph_traversal",
                "external_claim_policy": "atomic_fact_default_external_proof",
                "validation_status": "validated",
            }
        )
        rewritten += 1
    return rewritten


def apply_operator_archive_promotions(
    payload: dict[str, Any],
    *,
    human_confirmed_by: str = "Amit Ayer",
    human_confirmed_at: str | None = None,
) -> dict[str, Any]:
    """Apply bounded operator-confirmed archive promotions (graph metadata only)."""
    ts = human_confirmed_at or _utc_now()
    rows_by_id = build_skill_rows_by_id(payload)
    promoted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    human_records: list[dict[str, Any]] = []

    for skill_id, fact_ids in OPERATOR_ARCHIVE_PROMOTION_BY_SKILL.items():
        row = rows_by_id.get(skill_id)
        if not row:
            rejected.append({"skill_id": skill_id, "reason": "missing_skill_row"})
            continue
        clean_facts = [str(x).strip() for x in fact_ids if str(x).strip()]
        reason = _reject_operator_promotion_reason(row, clean_facts)
        if reason:
            rejected.append({"skill_id": skill_id, "reason": reason})
            continue

        record = {
            "human_confirmed_by": human_confirmed_by,
            "human_confirmed_at": ts,
            "source_fact_ids": clean_facts,
            "override_reason": "archive_snippet_verified_by_operator",
        }
        row["human_confirmed_archive_promotion"] = record
        row["fact_id_links"] = clean_facts
        row["primary_fact_id"] = clean_facts[0]
        row["activation_status"] = "ACTIVE_CONFIRMED"
        row["support_level"] = "DIRECT_FROM_RESUME_ARCHIVE"
        row["user_confirmed"] = True
        row["operator_archive_promotion_applied_at"] = ts
        row.pop("confidence_override_blocked", None)
        row.pop("confidence_grade_override_attempted", None)
        row.pop("confidence_override_blocked_reason", None)

        registry = load_candidate_fact_promotion_registry()
        resolved = resolve_confidence_grade(
            row, has_fact_link=True, candidate_registry=registry
        )
        row["confidence_grade_derived"] = resolved["derived_grade"]
        row["confidence_grade"] = resolved["effective_grade"]

        _sync_skill_row_to_payload_collections(payload, row)
        edge_n = _rewire_skill_fact_edges(payload, skill_id, clean_facts)
        rows_by_id[skill_id] = row

        promoted.append(
            {
                "skill_id": skill_id,
                "fact_id_links": clean_facts,
                "confidence_grade": row["confidence_grade"],
                "activation_status": row["activation_status"],
                "support_level": row["support_level"],
                "edges_rewired": edge_n,
            }
        )
        human_records.append({"skill_id": skill_id, **record})

    gm = payload.setdefault("graph_metadata", {})
    if isinstance(gm, dict):
        gm["operator_archive_promotion_wave"] = {
            "applied_at": ts,
            "human_confirmed_by": human_confirmed_by,
            "confirmed_fact_ids": sorted(OPERATOR_CONFIRMED_ARCHIVE_FACT_IDS),
            "promoted_skill_count": len(promoted),
            "rejected_skill_count": len(rejected),
        }

    return {
        "promoted": promoted,
        "rejected": rejected,
        "human_confirmation_records": human_records,
    }


def collect_high_and_exec_summary_counts(
    payload: dict[str, Any],
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Before/after style counts from merged skill rows (no SQLite required)."""
    registry = load_candidate_fact_promotion_registry(repo_root)
    track_high: Counter[str] = Counter()
    exec_allowed = 0
    high_total = 0
    genai_high_skills: list[str] = []
    for sid, row in build_skill_rows_by_id(payload).items():
        if sid in FORBIDDEN_SKILL_NODE_IDS:
            continue
        has_link = bool(row.get("fact_id_links"))
        grade = confidence_grade_for_skill_row(
            row, has_fact_link=has_link, candidate_registry=registry
        )
        if grade == "HIGH":
            high_total += 1
            epoch = str(row.get("career_epoch") or "")
            pillar = str(row.get("pillar") or "")
            if "agentic" in epoch or pillar == "pillar_agentic_ai_platforms":
                track_high["track_genai_agentic"] += 1
                genai_high_skills.append(sid)
            elif "partner" in pillar or "gtm" in pillar or "presales" in pillar:
                track_high["track_data_tech_cloud_ml"] += 1
            elif "actuarial" in pillar or "capital" in pillar or "derivatives" in pillar:
                track_high["track_actuarial_risk_derivatives"] += 1
            else:
                track_high["track_data_tech_cloud_ml"] += 1
        elig = _executive_summary_eligibility(
            {**row, "confidence_grade": grade},
            has_fact_link=has_link,
            candidate_registry=registry,
        )
        if elig.get("allowed") == 1:
            exec_allowed += 1
    return {
        "high_skill_count": high_total,
        "high_skills_by_track": dict(track_high),
        "executive_summary_allowed_count": exec_allowed,
        "track_genai_agentic_high_skills": sorted(genai_high_skills),
    }


def _confidence_from_skill_row(
    row: dict[str, Any] | None,
    *,
    has_fact_link: bool = False,
    candidate_registry: dict[str, dict[str, Any]] | None = None,
) -> str:
    if not row:
        return ""
    return confidence_grade_for_skill_row(
        row,
        has_fact_link=has_fact_link,
        candidate_registry=candidate_registry,
    )


def _confidence_from_node(
    node: dict[str, Any],
    *,
    skill_row: dict[str, Any] | None = None,
    has_fact_link: bool = False,
    candidate_registry: dict[str, dict[str, Any]] | None = None,
) -> str:
    if skill_row is not None:
        return confidence_grade_for_skill_row(
            skill_row,
            has_fact_link=has_fact_link,
            candidate_registry=candidate_registry,
        )
    preset = str(node.get("confidence_grade") or node.get("confidence") or "").strip().upper()
    if preset in CONFIDENCE_GRADES:
        return preset
    ntype = str(node.get("node_type") or "")
    if ntype in ("policy", "policy_rule"):
        return ""
    if ntype == "fact":
        return "HIGH"
    return ""


def _policy_rule_node_id(policy_key: str) -> str:
    key = str(policy_key or "").strip()
    if key.startswith("policy_rule_"):
        return key
    return f"policy_rule_{key}"


def _redirect_edge_source(src: str) -> str:
    s = str(src or "").strip()
    if s in POLICY_EDGE_SOURCE_KEYS:
        return _policy_rule_node_id(s)
    return s


def _dedupe_edge_rows(edge_by_id: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    seen_triple: set[tuple[str, str, str]] = set()
    out: list[dict[str, Any]] = []
    for row in edge_by_id.values():
        triple = (
            str(row["source_node_id"]),
            str(row["target_node_id"]),
            str(row["edge_type"]),
        )
        if triple in seen_triple:
            continue
        seen_triple.add(triple)
        out.append(row)
    return out


def _ensure_policy_nodes(
    node_rows: dict[str, dict[str, Any]],
    payload: dict[str, Any],
    *,
    ts: str,
) -> None:
    policies = payload.get("external_claim_policies") or {}
    seeds: list[tuple[str, str, str]] = [
        ("policy_external_claim_policy", "policy", "External claim policy anchor"),
        (
            "policy_executive_summary_high_confidence_only",
            "policy",
            "executive_summary: confidence_grade=HIGH + ACTIVE/ACTIVE_CONFIRMED + fact-backed skills only",
        ),
    ]
    if isinstance(policies, dict):
        for key, body in policies.items():
            if not isinstance(key, str) or not key.strip():
                continue
            desc = ""
            if isinstance(body, dict):
                desc = str(body.get("description") or key)
            seeds.append((_policy_rule_node_id(key), "policy_rule", desc or key))
    for nid, ntype, desc in seeds:
        if nid in node_rows:
            continue
        node_rows[nid] = {
            "node_id": nid,
            "node_type": ntype,
            "label": nid,
            "description": desc,
            "activation_status": "ACTIVE",
            "support_level": "POLICY",
            "confidence": "",
            "external_eligible": 0,
            "source_authority": "augmented_skills_graph",
            "created_at": ts,
            "updated_at": ts,
        }


def _executive_summary_eligibility(
    skill_row: dict[str, Any],
    *,
    has_fact_link: bool = False,
    candidate_registry: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    sid = str(skill_row.get("skill_id") or "")
    grade = confidence_grade_for_skill_row(
        skill_row,
        has_fact_link=has_fact_link,
        candidate_registry=candidate_registry,
    )
    status = str(skill_row.get("activation_status") or "")
    support = str(skill_row.get("support_level") or "")
    has_links = has_fact_link or bool(skill_row.get("fact_id_links"))

    blocked_activation = status in NON_PROMOTE_ACTIVATION or status == "DRAFT"
    blocked_support = support in BLOCKED_SUPPORT_LEVELS

    if (
        grade == "HIGH"
        and status in EXTERNAL_ACTIVE_STATUSES
        and not blocked_activation
        and not blocked_support
        and has_links
        and skill_row_eligible_for_external_claim(skill_row)
    ):
        return {
            "node_id": sid,
            "section_id": "executive_summary",
            "allowed": 1,
            "claim_policy": "executive_summary_high_confidence_grade_fact_backed",
            "reason": "confidence_grade=HIGH with fact_id_links",
            "blocked_reason": "",
        }
    if not grade or grade not in CONFIDENCE_GRADES:
        return {
            "node_id": sid,
            "section_id": "executive_summary",
            "allowed": 0,
            "claim_policy": "executive_summary_missing_confidence_grade",
            "reason": "Missing confidence_grade (support_level is provenance only)",
            "blocked_reason": "missing_confidence_grade",
        }
    return {
        "node_id": sid,
        "section_id": "executive_summary",
        "allowed": 0,
        "claim_policy": f"executive_summary_blocked_{grade.lower()}",
        "reason": f"executive_summary requires confidence_grade=HIGH; got {grade}",
        "blocked_reason": f"blocked_{grade.lower()}",
    }


def collect_graph_counts(payload: dict[str, Any]) -> dict[str, Any]:
    nodes = [n for n in payload.get("graph_nodes") or [] if isinstance(n, dict)]
    edges = [e for e in payload.get("graph_edges") or [] if isinstance(e, dict)]
    skills = [r for r in payload.get("skill_rows") or [] if isinstance(r, dict)]
    pillars = sum(1 for n in nodes if str(n.get("node_type")) in ("pillar", "domain_pillar"))
    active = sum(
        1
        for r in skills
        if str(r.get("activation_status")) in EXTERNAL_ACTIVE_STATUSES
    )
    draft = sum(1 for r in skills if str(r.get("activation_status")) == "DRAFT")
    bridges = sum(1 for e in edges if str(e.get("edge_type")) == "pillar_phase_bridge")
    grade_dist = Counter(
        str(r.get("confidence_grade") or derive_confidence_grade(r)).upper() for r in skills
    )
    return {
        "nodes": len(nodes),
        "edges": len(edges),
        "pillars": pillars,
        "skills": len(skills),
        "active_skills": active,
        "draft_skills": draft,
        "phase_bridges": bridges,
        "confidence_grade": dict(grade_dist),
    }


def _skill_external_eligible(
    skill_row: dict[str, Any],
    *,
    has_fact_link: bool,
) -> bool:
    if str(skill_row.get("skill_id") or "") in FORBIDDEN_SKILL_NODE_IDS:
        return False
    status = str(skill_row.get("activation_status") or "")
    if status not in EXTERNAL_ACTIVE_STATUSES:
        return False
    if status in NON_PROMOTE_ACTIVATION:
        return False
    if not has_fact_link:
        return False
    return skill_row_eligible_for_external_claim(skill_row)


def _external_eligible_node(
    node: dict[str, Any],
    *,
    skill_row: dict[str, Any] | None = None,
    has_fact_link: bool = False,
) -> bool:
    nid = str(node.get("node_id") or "")
    if nid in FORBIDDEN_SKILL_NODE_IDS:
        return False
    ntype = str(node.get("node_type") or "")
    if ntype in ("policy", "policy_rule", "section", "concept", "graph_ref"):
        return False
    if skill_row is not None:
        return _skill_external_eligible(skill_row, has_fact_link=has_fact_link)
    policy = str(node.get("external_claim_policy") or "")
    if policy in (
        "pending_source_internal_only",
        "weak_snippet_internal_only",
        "repo_portfolio_not_resume_default",
        "skill_projection_not_proof",
        "internal_traversal_only",
    ):
        return False
    status = str(node.get("activation_status") or "")
    if status in NON_PROMOTE_ACTIVATION:
        return False
    return False


def _parse_section_id(target: str) -> str:
    tgt = str(target or "").strip()
    if tgt.startswith("section_"):
        return tgt.removeprefix("section_")
    return tgt


def _ensure_fact_node(
    nodes: dict[str, dict[str, Any]],
    fact_id: str,
    *,
    ts: str,
) -> None:
    fid = str(fact_id or "").strip()
    if not fid or fid in nodes:
        return
    nodes[fid] = {
        "node_id": fid,
        "node_type": "fact",
        "label": fid,
        "description": "Atomic proof fact node (routing only; proof via SRFS/candidate ledger)",
        "activation_status": "ACTIVE",
        "support_level": "FACT_SUBSTRATE",
        "confidence": "HIGH",
        "external_eligible": 0,
        "source_authority": "augmented_skills_graph",
        "created_at": ts,
        "updated_at": ts,
    }


def materialize_augmented_skills_graph_sqlite(
    *,
    graph: dict[str, Any] | None = None,
    repo_root: Path | None = None,
    db_path: Path | None = None,
    json_source_path: Path | None = None,
) -> dict[str, Any]:
    """Build SQLite DB from augmented skills graph JSON. Returns materialization summary."""
    root = repo_root or _repo_root()
    payload = graph or load_augmented_skills_graph(repo_root=root)
    validate_arsenal_ledger_shape(payload)
    src_path = json_source_path or (root / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json")
    ledger_hash = _sha256_hex(
        json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    )
    gver = graph_version_from_payload(payload)
    ts = _utc_now()
    out_path = db_path or default_graph_sqlite_path(root)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    skill_rows_by_id = build_skill_rows_by_id(payload)
    candidate_registry = load_candidate_fact_promotion_registry(root)

    node_rows: dict[str, dict[str, Any]] = {}
    for raw in payload.get("graph_nodes") or []:
        if not isinstance(raw, dict):
            continue
        nid = str(raw.get("node_id") or "").strip()
        if not nid or nid in FORBIDDEN_SKILL_NODE_IDS:
            continue
        ntype = resolve_node_type(nid, str(raw.get("node_type") or ""))
        skill_row = skill_rows_by_id.get(nid) if ntype == "skill" else None
        node_rows[nid] = {
            "node_id": nid,
            "node_type": ntype,
            "label": str(raw.get("label") or nid),
            "description": str(raw.get("description") or ""),
            "activation_status": str(raw.get("activation_status") or ""),
            "support_level": str(raw.get("support_level") or ""),
            "confidence": (
                confidence_grade_for_skill_row(
                    skill_row, candidate_registry=candidate_registry
                )
                if skill_row
                else _confidence_from_node(raw, candidate_registry=candidate_registry)
            ),
            "external_eligible": 0,
            "source_authority": "augmented_skills_graph",
            "created_at": ts,
            "updated_at": ts,
        }

    _ensure_policy_nodes(node_rows, payload, ts=ts)

    for profile_key in (payload.get("role_family_projection_profiles") or {}):
        if profile_key in node_rows:
            continue
        node_rows[profile_key] = {
            "node_id": profile_key,
            "node_type": "role_family",
            "label": profile_key,
            "description": "Role family projection profile anchor",
            "activation_status": "ACTIVE",
            "support_level": "PROJECTION",
            "confidence": "",
            "external_eligible": 0,
            "source_authority": "augmented_skills_graph",
            "created_at": ts,
            "updated_at": ts,
        }

    edge_by_id: dict[str, dict[str, Any]] = {}
    section_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    skill_fact_rows: list[dict[str, Any]] = []

    for raw in payload.get("graph_edges") or []:
        if not isinstance(raw, dict):
            continue
        eid = str(raw.get("edge_id") or "").strip()
        src = _redirect_edge_source(str(raw.get("source_node_id") or raw.get("source") or "").strip())
        tgt = str(raw.get("target_node_id") or raw.get("target") or "").strip()
        et = str(raw.get("edge_type") or "").strip()
        if not eid or not src or not tgt or not et:
            continue
        if src in FORBIDDEN_SKILL_NODE_IDS:
            continue

        def _ensure_endpoint(endpoint_id: str) -> None:
            eid_s = str(endpoint_id or "").strip()
            if not eid_s or eid_s in node_rows or eid_s in FORBIDDEN_SKILL_NODE_IDS:
                return
            skill_row = skill_rows_by_id.get(eid_s)
            ntype = resolve_node_type(
                eid_s,
                "skill" if skill_row else infer_node_type_from_id(eid_s),
            )
            node_rows[eid_s] = {
                "node_id": eid_s,
                "node_type": ntype,
                "label": str(skill_row.get("capability") if skill_row else eid_s),
                "description": "",
                "activation_status": str(skill_row.get("activation_status") if skill_row else ""),
                "support_level": str(skill_row.get("support_level") if skill_row else ""),
                "confidence": _confidence_from_node({}, skill_row=skill_row) if skill_row else "",
                "external_eligible": 0,
                "source_authority": "augmented_skills_graph",
                "created_at": ts,
                "updated_at": ts,
            }

        _ensure_endpoint(src)
        _ensure_endpoint(tgt)
        weight = float(raw.get("weight") or 1.0)
        edge_by_id[eid] = {
            "edge_id": eid,
            "source_node_id": src,
            "target_node_id": tgt,
            "edge_family": str(raw.get("bridge_edge_family") or ""),
            "edge_type": et,
            "weight": weight,
            "confidence": str(raw.get("validation_status") or "validated"),
            "directional": 1 if str(raw.get("direction") or "forward") != "bidirectional" else 0,
            "evidence_status": str(raw.get("validation_status") or ""),
            "section_fit": _parse_section_id(tgt) if tgt.startswith("section_") else "",
            "source_authority": "augmented_skills_graph",
        }
        edge_row = edge_by_id[eid]
        et = edge_row["edge_type"]
        def _upsert_section(row: dict[str, Any]) -> None:
            key = (str(row["node_id"]), str(row["section_id"]))
            prior = section_by_key.get(key)
            if prior is None:
                section_by_key[key] = row
                return
            if int(row.get("allowed") or 0) == 0:
                section_by_key[key] = row
            elif int(prior.get("allowed") or 0) == 0:
                return
            section_by_key[key] = row

        if et == "skill_allowed_in_section":
            sec = _parse_section_id(tgt)
            row = skill_rows_by_id.get(src, {})
            if sec == "executive_summary" and row:
                link_n = sum(
                    1
                    for fid in row.get("fact_id_links") or []
                    if str(fid).strip() and not _is_skill_id(str(fid))
                )
                _upsert_section(_executive_summary_eligibility(row, has_fact_link=link_n > 0))
            else:
                blocked = str(row.get("activation_status") or "") in NON_PROMOTE_ACTIVATION
                _upsert_section(
                    {
                        "node_id": src,
                        "section_id": sec,
                        "allowed": 0 if blocked else 1,
                        "claim_policy": str(raw.get("external_claim_policy") or "skill_projection_not_proof"),
                        "reason": str(raw.get("rationale") or "skill_allowed_in_section"),
                        "blocked_reason": "activation_blocked" if blocked else "",
                    }
                )
        elif et == "pillar_section_eligibility":
            sec = _parse_section_id(tgt)
            pillar_allowed = 0 if sec == "executive_summary" else 1
            _upsert_section(
                {
                    "node_id": src,
                    "section_id": sec,
                    "allowed": pillar_allowed,
                    "claim_policy": str(raw.get("external_claim_policy") or "internal_traversal_only"),
                    "reason": str(raw.get("rationale") or "pillar_section_eligibility"),
                    "blocked_reason": "executive_summary_skills_high_only" if sec == "executive_summary" else "",
                }
            )
        elif et in (
            "projection_excludes_blocked_skill",
            "section_blocks_pending_source_skill",
            "section_blocks_skill_without_fact",
        ):
            sec = "executive_summary" if "executive" in eid else ""
            _upsert_section(
                {
                    "node_id": src,
                    "section_id": sec or "*",
                    "allowed": 0,
                    "claim_policy": str(raw.get("external_claim_policy") or "blocked"),
                    "reason": str(raw.get("rationale") or et),
                    "blocked_reason": et,
                }
            )

    skill_link_counts: dict[str, int] = {}
    for sid, row in skill_rows_by_id.items():
        if sid in FORBIDDEN_SKILL_NODE_IDS:
            continue
        if sid not in node_rows:
            node_rows[sid] = {
                "node_id": sid,
                "node_type": "skill",
                "label": str(row.get("capability") or sid),
                "description": "",
                "activation_status": str(row.get("activation_status") or ""),
                "support_level": str(row.get("support_level") or ""),
                "confidence": _confidence_from_node(row, skill_row=row),
                "external_eligible": 0,
                "source_authority": "augmented_skills_graph",
                "created_at": ts,
                "updated_at": ts,
            }
        for fid in row.get("fact_id_links") or []:
            fid_s = str(fid).strip()
            if not fid_s or _is_skill_id(fid_s):
                continue
            _ensure_fact_node(node_rows, fid_s, ts=ts)
            skill_link_counts[sid] = skill_link_counts.get(sid, 0) + 1
            claim_ok = _skill_external_eligible(row, has_fact_link=True)
            skill_fact_rows.append(
                {
                    "skill_id": sid,
                    "fact_id": fid_s,
                    "support_level": str(row.get("support_level") or ""),
                    "claim_eligibility": 1 if claim_ok else 0,
                    "source_trace": json.dumps(list(row.get("source_resume_files") or [])[:3]),
                    "archive_trace": "",
                    "human_confirmed": (
                        1
                        if row.get("user_confirmed")
                        or has_valid_human_confirmed_archive_promotion(row)
                        else 0
                    ),
                    "external_eligible": 1 if claim_ok else 0,
                }
            )

    for sid, row in skill_rows_by_id.items():
        if sid in FORBIDDEN_SKILL_NODE_IDS:
            continue
        has_link = skill_link_counts.get(sid, 0) > 0
        grade = confidence_grade_for_skill_row(
            row, has_fact_link=has_link, candidate_registry=candidate_registry
        )
        if sid not in node_rows:
            node_rows[sid] = {
                "node_id": sid,
                "node_type": "skill",
                "label": str(row.get("capability") or sid),
                "description": "",
                "activation_status": str(row.get("activation_status") or ""),
                "support_level": str(row.get("support_level") or ""),
                "confidence": grade,
                "external_eligible": 0,
                "source_authority": "augmented_skills_graph",
                "created_at": ts,
                "updated_at": ts,
            }
        else:
            node_rows[sid]["confidence"] = grade
            node_rows[sid]["support_level"] = str(row.get("support_level") or "")
            node_rows[sid]["activation_status"] = str(row.get("activation_status") or "")
        node_rows[sid]["external_eligible"] = (
            1 if _skill_external_eligible(row, has_fact_link=has_link) else 0
        )
        section_by_key[(sid, "executive_summary")] = _executive_summary_eligibility(
            row,
            has_fact_link=has_link,
            candidate_registry=candidate_registry,
        )

    edge_rows = _dedupe_edge_rows(edge_by_id)

    # W2.0 (typed-edge-role-facet-guardrails-a6f3d2): materialize first-class
    # metric_outcome nodes + edges from role_episode_bundle JSON files. New rows
    # are net-additive (node_type="metric_outcome" + 3 new edge_types in
    # METRIC_OUTCOME_EDGE_TYPES) — existing node_type/edge_type queries are
    # unaffected. Validators do not consume these yet; W2.2 migrates consumers
    # to the resolver in metric_outcome_materializer.resolve_metric_outcome_graph_node.
    from apps_rg.fact_inventory.metric_outcome_materializer import (
        metric_outcome_node_and_edge_rows,
    )

    _mo_node_rows, _mo_edge_rows = metric_outcome_node_and_edge_rows(
        root, ts=ts, known_node_ids=set(node_rows.keys())
    )
    for _row in _mo_node_rows:
        _nid = _row["node_id"]
        # Behavior-neutral guard: never overwrite an existing node row. If a
        # metric ID collides with a pre-existing graph node, the bundle JSON is
        # malformed and W2.0 fails closed at materialization.
        if _nid in node_rows:
            raise ValueError(
                f"metric_outcome materialization: id collision with existing graph_node {_nid!r}"
            )
        node_rows[_nid] = _row
    for _edge in _mo_edge_rows:
        _ensure_endpoint(str(_edge.get("source_node_id") or ""))
        _ensure_endpoint(str(_edge.get("target_node_id") or ""))
    edge_rows.extend(_mo_edge_rows)

    section_rows = list(section_by_key.values())
    projection_rows: list[dict[str, Any]] = []
    profiles = payload.get("role_family_projection_profiles") or {}
    from apps_rg.fact_inventory.candidate_fact_ledger import load_master_role_family_taxonomy
    from apps_rg.runtime.c0.c03_role_family import resolve_c0_pillar_hints

    tax = load_master_role_family_taxonomy(repo_root=repo_root)
    for rf_key in ROLE_FAMILY_TRACK_WEIGHTS:
        if rf_key in profiles:
            continue
        if rf_key not in SENIOR_ROLE_TAXONOMY_IDS:
            continue
        pillar_ids = list(resolve_c0_pillar_hints(rf_key, taxonomy=tax, repo_root=repo_root))
        weights = ROLE_FAMILY_TRACK_WEIGHTS.get(rf_key, {})
        profiles[rf_key] = {
            "label": rf_key.replace("_", " ").title(),
            "taxonomy_ids": [rf_key],
            "top_weighted_pillars": [
                {"pillar_id": pid, "weight": round(1.0 - (i * 0.08), 2)}
                for i, pid in enumerate(pillar_ids[:6])
            ],
            "synthesized_for_sqlite": True,
        }
    for rf_key, prof in profiles.items():
        if not isinstance(prof, dict):
            continue
        weights = ROLE_FAMILY_TRACK_WEIGHTS.get(rf_key, {})
        note = "graph_routing_not_claim_proof"
        if rf_key == "ANTHROPIC_PARTNERSHIPS_APPLIED_AI":
            note = (
                "graph_routing_not_claim_proof;"
                " marketplace_listing_claims_blocked;"
                " pillars_include_hyperscaler_marketplace_and_applied_ai_partner_architecture"
            )
        projection_rows.append(
            {
                "role_family_id": rf_key,
                "projection_role_family_key": rf_key,
                "track_weight_profile": json.dumps(weights, sort_keys=True),
                "taxonomy_source": json.dumps(list(prof.get("taxonomy_ids") or [])),
                "targeting_keywords": json.dumps(list(prof.get("top_weighted_pillars") or [])[:8]),
                "proof_policy_note": note,
            }
        )

    gm = payload.get("graph_metadata") if isinstance(payload.get("graph_metadata"), dict) else {}
    summary = {
        "node_count_json": gm.get("node_count"),
        "edge_count_json": gm.get("edge_count"),
        "node_count_sqlite": len(node_rows),
        "edge_count_sqlite": len(edge_rows),
        "skill_fact_link_count": len(skill_fact_rows),
        "section_eligibility_count": len(section_rows),
        "role_family_projection_count": len(projection_rows),
    }

    if out_path.exists():
        out_path.unlink()  # guardian: allow-missing-hitl-on-irreversible -- rebuild overwrites prior materialized sqlite artifact in reports path
    conn = sqlite3.connect(str(out_path), timeout=30)
    try:
        for stmt in DDL_STATEMENTS:
            conn.execute(stmt)
        conn.executemany(
            """
            INSERT INTO graph_nodes (
                node_id, node_type, label, description, activation_status, support_level,
                confidence, external_eligible, source_authority, created_at, updated_at
            ) VALUES (
                :node_id, :node_type, :label, :description, :activation_status, :support_level,
                :confidence, :external_eligible, :source_authority, :created_at, :updated_at
            )
            """,
            list(node_rows.values()),
        )
        conn.executemany(
            """
            INSERT INTO graph_edges (
                edge_id, source_node_id, target_node_id, edge_family, edge_type, weight,
                confidence, directional, evidence_status, section_fit, source_authority
            ) VALUES (
                :edge_id, :source_node_id, :target_node_id, :edge_family, :edge_type, :weight,
                :confidence, :directional, :evidence_status, :section_fit, :source_authority
            )
            """,
            edge_rows,
        )
        conn.executemany(
            """
            INSERT INTO skill_fact_links (
                skill_id, fact_id, support_level, claim_eligibility, source_trace,
                archive_trace, human_confirmed, external_eligible
            ) VALUES (
                :skill_id, :fact_id, :support_level, :claim_eligibility, :source_trace,
                :archive_trace, :human_confirmed, :external_eligible
            )
            """,
            skill_fact_rows,
        )
        conn.executemany(
            """
            INSERT INTO section_eligibility (
                node_id, section_id, allowed, claim_policy, reason, blocked_reason
            ) VALUES (
                :node_id, :section_id, :allowed, :claim_policy, :reason, :blocked_reason
            )
            """,
            section_rows,
        )
        conn.executemany(
            """
            INSERT INTO role_family_projection (
                role_family_id, projection_role_family_key, track_weight_profile,
                taxonomy_source, targeting_keywords, proof_policy_note
            ) VALUES (
                :role_family_id, :projection_role_family_key, :track_weight_profile,
                :taxonomy_source, :targeting_keywords, :proof_policy_note
            )
            """,
            projection_rows,
        )
        conn.execute(
            """
            INSERT INTO graph_metadata (
                graph_version, materialized_from, materialized_at, ledger_hash,
                graph_count_summary, authority_status
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                gver,
                str(src_path.relative_to(root)) if src_path.is_relative_to(root) else str(src_path),
                ts,
                ledger_hash,
                json.dumps(summary, sort_keys=True),
                "augmented_skills_graph_authoritative",
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "sqlite_db_path": str(out_path),
        "graph_version": gver,
        "graph_hash": ledger_hash,
        "materialized_at": ts,
        "materialized_from": str(src_path),
        **summary,
        "tables_created": [
            "graph_nodes",
            "graph_edges",
            "skill_fact_links",
            "section_eligibility",
            "role_family_projection",
            "graph_metadata",
        ],
    }


def open_graph_sqlite(
    *,
    repo_root: Path | None = None,
    db_path: Path | None = None,
    read_only: bool = True,
) -> sqlite3.Connection:
    path = db_path or default_graph_sqlite_path(repo_root)
    if not path.is_file():
        raise FileNotFoundError(f"augmented skills graph sqlite missing: {path}")
    uri = f"file:{path.as_posix()}?mode=ro" if read_only else f"file:{path.as_posix()}"
    return sqlite3.connect(uri, uri=True, timeout=15)


def load_graph_metadata_row(conn: sqlite3.Connection) -> dict[str, Any]:
    row = conn.execute(
        """
        SELECT graph_version, materialized_from, materialized_at, ledger_hash,
               graph_count_summary, authority_status
        FROM graph_metadata
        ORDER BY materialized_at DESC
        LIMIT 1
        """
    ).fetchone()
    if not row:
        raise ValueError("graph_metadata empty")
    summary = json.loads(row[4] or "{}")
    return {
        "graph_version": row[0],
        "materialized_from": row[1],
        "materialized_at": row[2],
        "ledger_hash": row[3],
        "graph_count_summary": summary,
        "authority_status": row[5],
    }


def validate_materialized_sqlite(
    *,
    graph: dict[str, Any] | None = None,
    repo_root: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Integrity checks: counts, duplicate IDs, FK-like edge/link refs."""
    root = repo_root or _repo_root()
    payload = graph or load_augmented_skills_graph(repo_root=root)
    path = db_path or default_graph_sqlite_path(root)
    if not path.is_file():
        return {"status": "FAIL", "reason": "sqlite_missing", "sqlite_db_path": str(path)}

    gm = payload.get("graph_metadata") if isinstance(payload.get("graph_metadata"), dict) else {}
    expected_nodes = int(gm.get("node_count") or 0)
    expected_edges_meta = int(gm.get("edge_count") or 0)
    expected_edges = len(
        {
            str(e.get("edge_id"))
            for e in payload.get("graph_edges") or []
            if isinstance(e, dict) and e.get("edge_id")
        }
    ) or expected_edges_meta

    conn = open_graph_sqlite(repo_root=root, db_path=path)
    try:
        meta = load_graph_metadata_row(conn)
        meta_summary = meta.get("graph_count_summary") if isinstance(meta.get("graph_count_summary"), dict) else {}
        expected_edges = int(meta_summary.get("edge_count_sqlite") or expected_edges)
        node_count = conn.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0]
        edge_count = conn.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0]
        dup_nodes = conn.execute(
            "SELECT node_id, COUNT(*) c FROM graph_nodes GROUP BY node_id HAVING c > 1"
        ).fetchall()
        dup_edges = conn.execute(
            "SELECT edge_id, COUNT(*) c FROM graph_edges GROUP BY edge_id HAVING c > 1"
        ).fetchall()
        broken_edges = conn.execute(
            """
            SELECT e.edge_id, e.source_node_id, e.target_node_id FROM graph_edges e
            LEFT JOIN graph_nodes s ON s.node_id = e.source_node_id
            LEFT JOIN graph_nodes t ON t.node_id = e.target_node_id
            WHERE s.node_id IS NULL OR t.node_id IS NULL
            """
        ).fetchall()
        dup_triple = conn.execute(
            """
            SELECT source_node_id, target_node_id, edge_type, COUNT(*) c
            FROM graph_edges
            GROUP BY source_node_id, target_node_id, edge_type
            HAVING c > 1
            """
        ).fetchall()
        node_type_eq_id = conn.execute(
            "SELECT node_id FROM graph_nodes WHERE node_type = node_id"
        ).fetchall()
        bogus_skill_nodes = conn.execute(
            """
            SELECT node_id FROM graph_nodes
            WHERE node_id IN ('skill_id_never_source_fact_id', 'skill_projection_not_proof')
            """
        ).fetchall()
        draft_external = conn.execute(
            """
            SELECT node_id, activation_status FROM graph_nodes
            WHERE node_type = 'skill' AND external_eligible = 1
              AND activation_status IN (
                'DRAFT','INTERNAL_ONLY','USER_CONFIRMED_PENDING_SOURCE',
                'DO_NOT_PROMOTE','BLOCKED'
              )
            """
        ).fetchall()
        active_ext_no_link = conn.execute(
            """
            SELECT n.node_id FROM graph_nodes n
            WHERE n.node_type = 'skill' AND n.external_eligible = 1
              AND n.activation_status IN ('ACTIVE','ACTIVE_CONFIRMED')
              AND NOT EXISTS (
                SELECT 1 FROM skill_fact_links l WHERE l.skill_id = n.node_id
              )
            """
        ).fetchall()
        exec_summary_bad = conn.execute(
            """
            SELECT se.node_id, se.allowed, se.blocked_reason, n.confidence, n.support_level
            FROM section_eligibility se
            JOIN graph_nodes n ON n.node_id = se.node_id
            WHERE se.section_id = 'executive_summary' AND se.allowed = 1
              AND n.node_type = 'skill'
              AND (
                n.confidence IS NULL OR n.confidence = '' OR n.confidence = 'MEDIUM'
                OR n.confidence NOT IN ('HIGH')
              )
            """
        ).fetchall()
        exec_summary_medium_allowed = conn.execute(
            """
            SELECT node_id FROM section_eligibility
            WHERE section_id = 'executive_summary' AND allowed = 1
              AND claim_policy LIKE '%medium%'
              AND claim_policy NOT LIKE '%hitl_approved%'
            """
        ).fetchall()
        broad_ref = conn.execute(
            """
            SELECT node_id FROM graph_nodes
            WHERE source_authority LIKE '%broad_skills_ledger%'
            """
        ).fetchall()
        exec_summary_non_high_blocked = conn.execute(
            """
            SELECT se.node_id, n.confidence FROM section_eligibility se
            JOIN graph_nodes n ON n.node_id = se.node_id
            WHERE se.section_id = 'executive_summary' AND se.allowed = 1
              AND n.node_type = 'skill'
              AND n.confidence IN ('MEDIUM', 'LOW', 'BLOCKED')
            """
        ).fetchall()
        exec_summary_allowed_count = conn.execute(
            """
            SELECT COUNT(*) FROM section_eligibility se
            JOIN graph_nodes n ON n.node_id = se.node_id
            WHERE se.section_id = 'executive_summary' AND se.allowed = 1
              AND n.node_type = 'skill'
            """
        ).fetchone()[0]
        skill_confidence_dist = conn.execute(
            """
            SELECT confidence, COUNT(*) FROM graph_nodes
            WHERE node_type = 'skill' GROUP BY confidence ORDER BY 2 DESC
            """
        ).fetchall()
        skill_support_dist = conn.execute(
            """
            SELECT support_level, COUNT(*) FROM graph_nodes
            WHERE node_type = 'skill' GROUP BY support_level ORDER BY 2 DESC
            """
        ).fetchall()
        broken_links = conn.execute(
            """
            SELECT l.skill_id, l.fact_id FROM skill_fact_links l
            LEFT JOIN graph_nodes sk ON sk.node_id = l.skill_id
            LEFT JOIN graph_nodes fa ON fa.node_id = l.fact_id
            WHERE sk.node_id IS NULL OR fa.node_id IS NULL
            """
        ).fetchall()
        skill_fact_count = conn.execute("SELECT COUNT(*) FROM skill_fact_links").fetchone()[0]
        section_elig_count = conn.execute("SELECT COUNT(*) FROM section_eligibility").fetchone()[0]
        rf_count = conn.execute("SELECT COUNT(*) FROM role_family_projection").fetchone()[0]
    finally:
        conn.close()

    issues: list[str] = []
    if dup_nodes:
        issues.append(f"duplicate_node_ids:{len(dup_nodes)}")
    if dup_edges:
        issues.append(f"duplicate_edge_ids:{len(dup_edges)}")
    if dup_triple:
        issues.append(f"duplicate_edge_triples:{len(dup_triple)}")
    if broken_edges:
        issues.append(f"broken_edge_refs:{len(broken_edges)}")
    if broken_links:
        issues.append(f"broken_skill_fact_links:{len(broken_links)}")
    if node_type_eq_id:
        issues.append(f"node_type_equals_node_id:{len(node_type_eq_id)}")
    if bogus_skill_nodes:
        issues.append(f"bogus_policy_skill_nodes:{len(bogus_skill_nodes)}")
    if draft_external:
        issues.append(f"draft_external_eligible:{len(draft_external)}")
    if active_ext_no_link:
        issues.append(f"active_external_without_fact_link:{len(active_ext_no_link)}")
    if exec_summary_bad:
        issues.append(f"executive_summary_non_high_allowed:{len(exec_summary_bad)}")
    if exec_summary_medium_allowed:
        issues.append(f"executive_summary_medium_without_hitl:{len(exec_summary_medium_allowed)}")
    if exec_summary_non_high_blocked:
        issues.append(f"executive_summary_non_high_grade_allowed:{len(exec_summary_non_high_blocked)}")
    if broad_ref:
        issues.append(f"broad_skills_ledger_authority_leak:{len(broad_ref)}")
    if edge_count != expected_edges:
        issues.append(f"edge_count_mismatch:{edge_count}!={expected_edges}")

    status = "PASS" if not issues else "FAIL"
    return {
        "status": status,
        "issues": issues,
        "sqlite_db_path": str(path),
        "graph_version": meta["graph_version"],
        "graph_hash": meta["ledger_hash"],
        "node_count": node_count,
        "edge_count": edge_count,
        "expected_node_count_json": expected_nodes,
        "expected_edge_count_json": expected_edges,
        "expected_edge_count_metadata": expected_edges_meta,
        "skill_fact_link_count": skill_fact_count,
        "section_eligibility_count": section_elig_count,
        "role_family_projection_count": rf_count,
        "broad_skills_ledger_status": "non_authority",
        "dup_triple_count": len(dup_triple),
        "orphan_edge_count": len(broken_edges),
    }


def validate_hardened_materialized_sqlite(
    *,
    graph: dict[str, Any] | None = None,
    repo_root: Path | None = None,
    db_path: Path | None = None,
) -> dict[str, Any]:
    """Strict post-harden validation with SQL assertions required by materialization receipt."""
    root = repo_root or _repo_root()
    payload = graph or load_augmented_skills_graph(repo_root=root)
    base = validate_materialized_sqlite(graph=payload, repo_root=root, db_path=db_path)
    path = Path(str(base["sqlite_db_path"]))
    conn = open_graph_sqlite(repo_root=root, db_path=path)
    try:
        counts = {
            "nodes": conn.execute("SELECT COUNT(*) FROM graph_nodes").fetchone()[0],
            "edges": conn.execute("SELECT COUNT(*) FROM graph_edges").fetchone()[0],
            "pillars": conn.execute(
                "SELECT COUNT(*) FROM graph_nodes WHERE node_type IN ('pillar','capability_domain')"
            ).fetchone()[0],
            "skills": conn.execute(
                "SELECT COUNT(*) FROM graph_nodes WHERE node_type = 'skill'"
            ).fetchone()[0],
            "active_skills": conn.execute(
                """
                SELECT COUNT(*) FROM graph_nodes
                WHERE node_type='skill' AND activation_status IN ('ACTIVE','ACTIVE_CONFIRMED')
                """
            ).fetchone()[0],
            "draft_skills": conn.execute(
                "SELECT COUNT(*) FROM graph_nodes WHERE node_type='skill' AND activation_status='DRAFT'"
            ).fetchone()[0],
            "phase_bridges": conn.execute(
                "SELECT COUNT(*) FROM graph_edges WHERE edge_type='pillar_phase_bridge'"
            ).fetchone()[0],
        }
        anthropic = conn.execute(
            """
            SELECT proof_policy_note, targeting_keywords FROM role_family_projection
            WHERE role_family_id = 'ANTHROPIC_PARTNERSHIPS_APPLIED_AI'
            """
        ).fetchone()
    finally:
        conn.close()

    p0_fixed = [
        "orphan_policy_targets_materialized",
        "canonical_node_type_inference",
        "bogus_policy_strings_not_skill_nodes",
        "executive_summary_high_confidence_gate",
    ]
    p1_fixed = [
        "dedupe_edge_id_and_triple",
        "external_eligible_requires_active_and_fact_link",
        "fact_ref_node_typing_exp_bul_cert",
        "anthropic_role_family_pillar_profile",
        "customer_stakeholder_cs_primary_guardrails",
        "airline_anchor_internal_only",
    ]
    conn = open_graph_sqlite(repo_root=root, db_path=path)
    try:
        exec_allowed_sample = conn.execute(
            """
            SELECT se.node_id, n.confidence, n.support_level, n.activation_status,
                   n.external_eligible,
                   (SELECT COUNT(*) FROM skill_fact_links l WHERE l.skill_id = n.node_id) AS fact_links
            FROM section_eligibility se
            JOIN graph_nodes n ON n.node_id = se.node_id
            WHERE se.section_id = 'executive_summary' AND se.allowed = 1
              AND n.node_type = 'skill'
            ORDER BY se.node_id
            LIMIT 25
            """
        ).fetchall()
        skill_support_dist = conn.execute(
            """
            SELECT support_level, COUNT(*) FROM graph_nodes
            WHERE node_type = 'skill' GROUP BY support_level ORDER BY 2 DESC
            """
        ).fetchall()
        skill_confidence_dist = conn.execute(
            """
            SELECT confidence, COUNT(*) FROM graph_nodes
            WHERE node_type = 'skill' GROUP BY confidence ORDER BY 2 DESC
            """
        ).fetchall()
        high_skill_count = conn.execute(
            "SELECT COUNT(*) FROM graph_nodes WHERE node_type='skill' AND confidence='HIGH'"
        ).fetchone()[0]
        exec_allowed_count = conn.execute(
            """
            SELECT COUNT(*) FROM section_eligibility se
            JOIN graph_nodes n ON n.node_id = se.node_id
            WHERE se.section_id='executive_summary' AND se.allowed=1 AND n.node_type='skill'
            """
        ).fetchone()[0]
        forbidden_high = conn.execute(
            """
            SELECT node_id, activation_status, support_level FROM graph_nodes
            WHERE node_type='skill' AND confidence='HIGH'
              AND (
                activation_status IN (
                  'DRAFT','INTERNAL_ONLY','USER_CONFIRMED_PENDING_SOURCE'
                )
                OR support_level IN (
                  'REPO_EVIDENCE_PORTFOLIO','INTERNAL_ONLY',
                  'USER_CONFIRMED_PENDING_SOURCE'
                )
              )
            """
        ).fetchall()
        high_without_fact_link = conn.execute(
            """
            SELECT n.node_id FROM graph_nodes n
            WHERE n.node_type='skill' AND n.confidence='HIGH'
              AND NOT EXISTS (
                SELECT 1 FROM skill_fact_links l WHERE l.skill_id = n.node_id
              )
            """
        ).fetchall()
    finally:
        conn.close()

    override_violations: list[dict[str, Any]] = []
    registry = load_candidate_fact_promotion_registry(root)
    for row in payload.get("skill_rows") or []:
        if not isinstance(row, dict) or not row.get("skill_id"):
            continue
        resolved = resolve_confidence_grade(
            row,
            has_fact_link=bool(row.get("fact_id_links")),
            candidate_registry=registry,
        )
        derived = str(
            row.get("confidence_grade_derived") or resolved["derived_grade"] or ""
        ).upper()
        effective = str(row.get("confidence_grade") or resolved["effective_grade"] or "").upper()
        if (
            derived
            and effective
            and CONFIDENCE_GRADE_RANK.get(effective, -1)
            > CONFIDENCE_GRADE_RANK.get(derived, -1)
            and not resolved["human_confirmed_archive_promotion"]
        ):
            override_violations.append(
                {
                    "skill_id": row.get("skill_id"),
                    "derived": derived,
                    "effective": effective,
                    "reason": "effective_exceeds_derived_without_human_confirmation",
                }
            )

    issues = list(base.get("issues") or [])
    if high_skill_count > 0 and exec_allowed_count == 0:
        issues.append("executive_summary_allowed_empty_despite_high_skills")
    if anthropic and "hyperscaler_marketplace" not in str(anthropic[0]):
        issues.append("anthropic_profile_missing_marketplace_note")
    if anthropic and "pillar_applied_ai_partner_architecture" not in str(anthropic[1]):
        issues.append("anthropic_profile_missing_applied_ai_pillar")
    if forbidden_high:
        issues.append(f"forbidden_high_skill_promotions:{len(forbidden_high)}")
    if high_without_fact_link:
        issues.append(f"high_skills_without_fact_links:{len(high_without_fact_link)}")
    if override_violations:
        issues.append(
            f"confidence_override_without_human_confirm:{len(override_violations)}"
        )

    status = "PASS" if not issues else "FAIL"
    return {
        **base,
        "status": status,
        "issues": issues,
        "confidence_override_guardrail": {
            "violations_count": len(override_violations),
            "violations_sample": override_violations[:10],
            "candidate_facts_do_not_auto_promote": True,
            "rule": (
                "explicit confidence_grade above derived requires "
                "human_confirmed_archive_promotion metadata"
            ),
        },
        "forbidden_high_skill_promotions": forbidden_high,
        "high_skills_without_fact_links": high_without_fact_link,
        "counts": counts,
        "counts_json": collect_graph_counts(payload),
        "p0_fixed": p0_fixed,
        "p1_fixed": p1_fixed,
        "next_blocker": issues[0] if issues else "none",
        "sql_validation_queries_run": [
            "orphan_edges_zero",
            "duplicate_edge_id_zero",
            "duplicate_edge_triple_zero",
            "node_type_not_equal_node_id",
            "no_bogus_policy_skill_nodes",
            "no_draft_external_eligible",
            "active_external_has_skill_fact_link",
            "executive_summary_high_confidence_grade_only",
            "executive_summary_medium_low_blocked",
            "no_broad_skills_ledger_authority",
            "no_forbidden_high_skill_promotions",
            "no_high_without_fact_links",
            "confidence_override_guardrail_enforced",
        ],
        "skill_support_level_dist": skill_support_dist,
        "skill_confidence_grade_dist": skill_confidence_dist,
        "executive_summary_allowed_count": exec_allowed_count,
        "executive_summary_allowed_sample": [
            {
                "node_id": r[0],
                "confidence_grade": r[1],
                "support_level": r[2],
                "activation_status": r[3],
                "external_eligible": r[4],
                "fact_link_count": r[5],
            }
            for r in exec_allowed_sample
        ],
        "high_skill_count": high_skill_count,
    }


__all__ = [
    "CANONICAL_NODE_TYPES",
    "DDL_STATEMENTS",
    "CONFIDENCE_GRADES",
    "ENGINEERING_PLATFORM_CANDIDATE_FACT_IDS",
    "OPERATOR_ARCHIVE_PROMOTION_BY_SKILL",
    "OPERATOR_CONFIRMED_ARCHIVE_FACT_IDS",
    "THEME_AGENTIC_SKILL_IDS",
    "apply_operator_archive_promotions",
    "audit_candidate_fact_promotions",
    "audit_theme_skill_promotion_decisions",
    "build_skill_rows_by_id",
    "canonical_node_type",
    "classify_skill_archive_promotion",
    "collect_high_and_exec_summary_counts",
    "confidence_grade_for_skill_row",
    "default_candidate_fact_ledger_path",
    "default_graph_sqlite_path",
    "derive_confidence_grade",
    "has_valid_human_confirmed_archive_promotion",
    "load_candidate_fact_promotion_registry",
    "load_graph_metadata_row",
    "materialize_augmented_skills_graph_sqlite",
    "open_graph_sqlite",
    "collect_graph_counts",
    "resolve_confidence_grade",
    "validate_hardened_materialized_sqlite",
    "validate_materialized_sqlite",
]
