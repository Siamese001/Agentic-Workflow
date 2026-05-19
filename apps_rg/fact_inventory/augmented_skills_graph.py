"""Augmented skills graph — authoritative skills/competency source for apps_rg sections.

Canonical artifact: ``master_skills_arsenal_ledger.json`` (W4A graph_nodes/graph_edges).
Candidate fact rows remain claim-evidence substrate via proof-pool resolver; they are not skills authority.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    default_arsenal_ledger_path,
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
    validate_arsenal_ledger_shape,
)

SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH = "augmented_skills_graph"
SKILLS_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH = "augmented_skills_graph"
SKILLS_AUTHORITY_SOURCE_TYPE = "augmented_skills_graph"
CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER = "candidate_fact_ledger"
CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH = "augmented_skills_graph"
CLAIM_EVIDENCE_SOURCE_TYPE_SRFS = "selected_role_fact_set"
CLAIM_EVIDENCE_SOURCE_TYPE_BASE_RESUME = "base_resume_fallback"
LEGACY_SKILLS_LEDGER_ROLE = "deprecated_reference"


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _sha256_hex(text: str | bytes) -> str:
    data = text.encode("utf-8") if isinstance(text, str) else text
    return hashlib.sha256(data).hexdigest()


def default_augmented_skills_graph_path(repo_root: Path | None = None) -> Path:
    return default_arsenal_ledger_path(repo_root)


def augmented_skills_graph_path_explicit(
    path: str | None,
    *,
    repo_root: Path | None = None,
) -> Path:
    env_override = str(os.environ.get("APPS_RG_AUGMENTED_SKILLS_GRAPH_PATH") or "").strip()
    root = repo_root or _repo_root()
    if path and str(path).strip():
        p = Path(path)
        return p if p.is_absolute() else (root / p).resolve()
    if env_override:
        p = Path(env_override)
        return p if p.is_absolute() else (root / p).resolve()
    return default_augmented_skills_graph_path(root)


def load_augmented_skills_graph(
    *,
    repo_root: Path | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    """Load and validate the augmented skills graph (arsenal ledger with W4A graph)."""
    graph_path = path or augmented_skills_graph_path_explicit(None, repo_root=repo_root)
    payload = load_master_skills_arsenal_ledger(path=graph_path)
    validate_arsenal_ledger_shape(payload)
    if not payload.get("graph_metadata"):
        raise ValueError("augmented skills graph missing graph_metadata (W4A required)")
    return payload


def graph_version_from_payload(graph: dict[str, Any]) -> str:
    meta = graph.get("graph_metadata") if isinstance(graph.get("graph_metadata"), dict) else {}
    md = graph.get("metadata") if isinstance(graph.get("metadata"), dict) else {}
    return str(meta.get("schema_version") or md.get("schema_version") or "unknown")


def skills_authority_fields(
    *,
    graph: dict[str, Any] | None,
    graph_ref: str,
    graph_digest: str,
    status: str,
    block_reason: str = "",
) -> dict[str, Any]:
    """Canonical skills-authority dual-source fields."""
    md = (graph or {}).get("metadata") if isinstance((graph or {}).get("metadata"), dict) else {}
    legacy_ref = str(md.get("candidate_fact_ledger_ref") or "").strip()
    present = status == "PASS" and bool(graph)
    out: dict[str, Any] = {
        "skills_authority_source_type": SKILLS_AUTHORITY_SOURCE_TYPE,
        "skills_authority_graph_ref": graph_ref if present else (graph_ref or None),
        "skills_authority_graph_digest": graph_digest if present else "",
        "skills_authority_graph_version": graph_version_from_payload(graph) if graph else "",
        "skills_authority_status": status,
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "skills_source_type": SKILLS_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH,
        "skills_source_authority_status": status,
        "augmented_skills_graph_present": present,
        "augmented_skills_graph_ref": graph_ref if present else (graph_ref or None),
        "augmented_skills_graph_digest": graph_digest if present else "",
        "graph_ref": graph_ref if present else (graph_ref or None),
        "graph_digest": graph_digest if present else "",
        "graph_version": graph_version_from_payload(graph) if graph else "",
        "legacy_skills_ledger_ref": legacy_ref or None,
        "legacy_skills_ledger_role": LEGACY_SKILLS_LEDGER_ROLE,
        "legacy_broad_skills_ledger_skills_authority": False,
        "deprecated_non_authority": True,
    }
    if block_reason:
        out["skills_authority_block_reason"] = block_reason
    return out


def augmented_skills_graph_authority_metadata(
    *,
    graph: dict[str, Any],
    graph_ref: str,
    graph_digest: str,
) -> dict[str, Any]:
    return skills_authority_fields(
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        status="PASS",
    )


def blocked_skills_authority_metadata(
    *,
    reason: str,
    graph_ref: str = "",
    legacy_skills_ledger_ref: str | None = None,
) -> dict[str, Any]:
    meta = skills_authority_fields(
        graph=None,
        graph_ref=graph_ref,
        graph_digest="",
        status="BLOCKED",
        block_reason=reason,
    )
    if legacy_skills_ledger_ref:
        meta["legacy_skills_ledger_ref"] = legacy_skills_ledger_ref
    return meta


def claim_evidence_fields(
    *,
    source_type: str,
    source_ref: str,
    source_digest: str = "",
    substrate_type: str | None = None,
    substrate_ref: str | None = None,
) -> dict[str, Any]:
    """Claim-evidence dual-source fields (distinct from skills authority)."""
    out: dict[str, Any] = {
        "claim_evidence_source_type": source_type,
        "claim_evidence_source_ref": source_ref,
        "claim_evidence_source_digest": source_digest or None,
    }
    if substrate_type and substrate_ref:
        out["claim_evidence_substrate_type"] = substrate_type
        out["claim_evidence_substrate_ref"] = substrate_ref
    return out


def merge_dual_source_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    claim_evidence: dict[str, Any],
    skills_authority: dict[str, Any],
) -> dict[str, Any]:
    """Merge claim + skills dual-source fields into proof_pool_metadata."""
    return {**meta, **claim_evidence, **skills_authority}


def resolve_augmented_skills_graph_authority(
    *,
    repo_root: Path | None = None,
    graph_path: str | None = None,
) -> dict[str, Any]:
    """Load graph authority metadata or fail closed (BLOCKED) — never fall back to candidate fact ledger."""
    root = repo_root or _repo_root()
    path = augmented_skills_graph_path_explicit(graph_path, repo_root=root)
    ref = str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
    try:
        graph = load_augmented_skills_graph(repo_root=root, path=path)
        digest = _sha256_hex(
            json.dumps(graph, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
        )
        return augmented_skills_graph_authority_metadata(
            graph=graph,
            graph_ref=ref,
            graph_digest=digest,
        )
    except (OSError, ValueError, TypeError, json.JSONDecodeError, FileNotFoundError) as exc:
        return blocked_skills_authority_metadata(
            reason=f"augmented_skills_graph_unavailable:{type(exc).__name__}",
            graph_ref=ref,
        )


def build_verified_skill_inventory_projection(
    *,
    section_id: str = "competencies",
    graph: dict[str, Any] | None = None,
    repo_root: Path | None = None,
    allowed_fact_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Graph-authoritative competency scaffolding (not base-resume facts.skills SSOT)."""
    root = repo_root or _repo_root()
    g = graph or load_augmented_skills_graph(repo_root=root)
    allowed = allowed_fact_ids or set()
    skills: list[dict[str, Any]] = []
    for row in g.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        sections = row.get("allowed_sections") or []
        if section_id not in sections and "competencies" not in sections:
            continue
        if not skill_row_eligible_for_external_claim(row):
            continue
        links = [str(x) for x in (row.get("fact_id_links") or []) if str(x).strip()]
        if allowed and not any(lid in allowed or lid.split("_metric_")[0] in allowed for lid in links):
            continue
        skills.append(
            {
                "skill_id": row.get("skill_id"),
                "skill_name": (row.get("allowed_phrases") or [""])[0]
                if isinstance(row.get("allowed_phrases"), list)
                else str(row.get("skill_id") or ""),
                "source_fact_ids": links,
                "evidence_type": "augmented_skills_graph_projection",
                "pillar": row.get("pillar"),
                "subpillar": row.get("subpillar"),
            }
        )
    return {
        "verified_skill_inventory_projection": {"skills": skills},
        "verified_skill_inventory_deprecated": {
            "note": "base resume facts.skills is not skills authority; use projection_from_graph",
            "authority": "deprecated_non_authority",
        },
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "projection_from_graph": True,
        "skills_authority_source_type": SKILLS_AUTHORITY_SOURCE_TYPE,
    }


def assert_skills_not_broad_ledger_authority(metadata: dict[str, Any] | None) -> None:
    """Raise if metadata treats broad_skills_ledger as active skills authority."""
    meta = metadata or {}
    if meta.get("legacy_broad_skills_ledger_skills_authority") is True:
        raise ValueError("broad_skills_ledger must not be skills authority")
    if meta.get("broad_skills_ledger_skills_authority") is True:
        raise ValueError("broad_skills_ledger_skills_authority must be false")
    st = str(meta.get("skills_authority_source_type") or meta.get("skills_source_type") or "")
    if st == "broad_skills_ledger":
        raise ValueError("skills_authority_source_type cannot be broad_skills_ledger")


__all__ = [
    "CLAIM_EVIDENCE_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH",
    "CLAIM_EVIDENCE_SOURCE_TYPE_BASE_RESUME",
    "CLAIM_EVIDENCE_SOURCE_TYPE_CANDIDATE_FACT_LEDGER",
    "CLAIM_EVIDENCE_SOURCE_TYPE_SRFS",
    "LEGACY_SKILLS_LEDGER_ROLE",
    "SKILLS_AUTHORITY_SOURCE_TYPE",
    "SKILLS_SOURCE_TYPE_AUGMENTED_SKILLS_GRAPH",
    "SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH",
    "assert_skills_not_broad_ledger_authority",
    "augmented_skills_graph_authority_metadata",
    "augmented_skills_graph_path_explicit",
    "blocked_skills_authority_metadata",
    "build_verified_skill_inventory_projection",
    "claim_evidence_fields",
    "default_augmented_skills_graph_path",
    "graph_version_from_payload",
    "load_augmented_skills_graph",
    "merge_dual_source_proof_pool_metadata",
    "resolve_augmented_skills_graph_authority",
    "skills_authority_fields",
]
