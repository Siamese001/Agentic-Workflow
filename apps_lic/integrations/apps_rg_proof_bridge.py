"""apps_lic <-> apps_rg shared candidate-proof bridge (W2).

Plan: apps-lic-completeness-graph-grounding-ssot-e7b2c4 (W2).

The source-of-record for apps_lic outbound proof points is the apps_rg
``augmented_skills_graph`` (the shared candidate-proof SSOT). This module loads
that shared graph once and projects approved skill proof-points + their fact
lineage so two apps_lic surfaces stop drifting from the resume proof:

  * the C0.3 ``LicGraphAdapter`` returns real neighbours (W2.1); and
  * the live sender-proof packet carries apps_rg SSOT provenance (W2.2).

Fail-soft by construction: if apps_rg is unavailable (import error or missing
artifact), the index is empty and ``available`` is False — apps_lic never hard
-fails on a missing shared artifact, it simply reports no SSOT provenance.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any, Mapping

APPS_RG_GRAPH_SOURCE = "apps_rg.augmented_skills_graph.v1"

# A skill is externally claimable proof only when activated and not blocked.
_APPROVED_ACTIVATION = frozenset({"ACTIVE", "ACTIVE_CONFIRMED"})
_BLOCK_TOKENS = ("block", "forbid", "deny", "hold")

PERMISSION_ALLOW = "allow"
PERMISSION_BLOCKED = "blocked"


@dataclass(frozen=True)
class ApprovedSkillProof:
    """One apps_rg skill projected as an approved proof-point with lineage."""

    skill_id: str
    node_id: str
    capability: str
    fact_id_links: tuple[str, ...]
    activation_status: str
    support_level: str
    confidence_grade: str
    external_claim_policy: str
    permission: str
    # W3 recipient-fit weighting (graph-derived): apps_rg per-skill role-family
    # weights + taxonomy placement.
    role_family_weights: Mapping[str, float] = field(default_factory=dict)
    pillar: str = ""
    domain: str = ""

    def to_packet(self) -> dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "node_id": self.node_id,
            "capability": self.capability,
            "fact_id_links": list(self.fact_id_links),
            "activation_status": self.activation_status,
            "support_level": self.support_level,
            "confidence_grade": self.confidence_grade,
            "external_claim_policy": self.external_claim_policy,
            "permission": self.permission,
            "role_family_weights": dict(self.role_family_weights),
            "pillar": self.pillar,
            "domain": self.domain,
        }


@dataclass(frozen=True)
class AppsRgProofIndex:
    """Loaded, indexed projection of the apps_rg shared proof graph."""

    available: bool
    graph_source: str
    graph_version: str
    graph_digest: str
    skills_by_id: Mapping[str, ApprovedSkillProof] = field(default_factory=dict)
    fact_to_node: Mapping[str, str] = field(default_factory=dict)
    skill_to_node: Mapping[str, str] = field(default_factory=dict)
    adjacency: Mapping[str, tuple[tuple[str, str, str, str], ...]] = field(default_factory=dict)
    fact_to_skills: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    load_error: str = ""

    @property
    def snapshot_pointer(self) -> str:
        return f"apps_rg::augmented_skills_graph::{self.graph_digest or 'unavailable'}"


# W3 — recipient_class -> apps_rg role families it screens for. Technical
# evaluators (recruiter/TA/hiring-owner/eng-leaders) weight role/req-fit proof;
# executives weight business-outcome / GTM / revenue proof.
_TECHNICAL_FAMILIES = (
    "ENGINEERING_PLATFORM",
    "AI_SOLUTIONS_ARCHITECTURE",
    "AI_GOVERNANCE_RISK",
    "QUANT_TRADING_HPC",
)
_BUSINESS_FAMILIES = (
    "EXECUTIVE_LEADERSHIP",
    "PARTNERSHIPS_GTM",
    "REVENUE_OPERATIONS",
    "STRATEGIC_FINANCE",
)
RECIPIENT_ROLE_FAMILIES: Mapping[str, tuple[str, ...]] = {
    "RECRUITER": _TECHNICAL_FAMILIES,
    "SENIOR_TA": _TECHNICAL_FAMILIES,
    "HIRING_MANAGER": _TECHNICAL_FAMILIES,
    "VP_ENG": _TECHNICAL_FAMILIES,
    "CTO": (*_TECHNICAL_FAMILIES, *_BUSINESS_FAMILIES),
    "EXECUTIVE": _BUSINESS_FAMILIES,
    "C_LEVEL": _BUSINESS_FAMILIES,
    "CEO": _BUSINESS_FAMILIES,
}


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _permission_for(activation_status: str, external_claim_policy: str) -> str:
    activated = str(activation_status or "").strip().upper() in _APPROVED_ACTIVATION
    policy = str(external_claim_policy or "").strip().lower()
    blocked = any(token in policy for token in _BLOCK_TOKENS)
    return PERMISSION_ALLOW if (activated and not blocked) else PERMISSION_BLOCKED


def _empty_index(load_error: str = "") -> AppsRgProofIndex:
    return AppsRgProofIndex(
        available=False,
        graph_source=APPS_RG_GRAPH_SOURCE,
        graph_version="unavailable",
        graph_digest="",
        load_error=load_error,
    )


@lru_cache(maxsize=1)
def load_apps_rg_proof_index() -> AppsRgProofIndex:
    """Load + index the apps_rg shared proof graph (cached; fail-soft)."""
    try:
        from apps_rg.fact_inventory.augmented_skills_graph import (  # noqa: PLC0415
            graph_version_from_payload,
            load_augmented_skills_graph,
        )

        graph = load_augmented_skills_graph()
    except Exception as exc:  # guardian: allow-broad-exception -- shared apps_rg SSOT is optional; any load failure degrades to an empty (unavailable) index rather than breaking apps_lic
        return _empty_index(load_error=f"{type(exc).__name__}: {exc}")

    # The proof lineage lives in skill_rows.fact_id_links (skill <-> fact), not in
    # the taxonomy graph_edges. Node ids are the skill_id / fact_id directly
    # (already namespaced "skill_*" / "fact_*"); the proof adjacency is the
    # skill<->fact evidence relation.
    skills_by_id: dict[str, ApprovedSkillProof] = {}
    fact_to_node: dict[str, str] = {}
    skill_to_node: dict[str, str] = {}
    fact_to_skills: dict[str, list[str]] = {}
    adjacency: dict[str, list[tuple[str, str, str, str]]] = {}

    for row in graph.get("skill_rows") or []:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("skill_id") or "").strip()
        if not sid:
            continue
        skill_to_node[sid] = sid
        fact_links = tuple(
            str(fid).strip() for fid in row.get("fact_id_links") or [] if str(fid).strip()
        )
        for fid in fact_links:
            fact_to_node[fid] = fid
            fact_to_skills.setdefault(fid, []).append(sid)
            adjacency.setdefault(sid, []).append((fid, "EVIDENCE", f"{sid}->{fid}", "out"))
            adjacency.setdefault(fid, []).append((sid, "SUPPORTS", f"{fid}->{sid}", "in"))
        activation = str(row.get("activation_status") or "")
        external_policy = str(row.get("external_claim_policy") or "")
        raw_weights = row.get("role_family_weights")
        role_weights = (
            {str(k): float(v) for k, v in raw_weights.items() if _is_number(v)}
            if isinstance(raw_weights, Mapping)
            else {}
        )
        skills_by_id[sid] = ApprovedSkillProof(
            skill_id=sid,
            node_id=sid,
            capability=str(row.get("capability") or row.get("domain") or ""),
            fact_id_links=fact_links,
            activation_status=activation,
            support_level=str(row.get("support_level") or ""),
            confidence_grade=str(
                row.get("confidence_grade") or row.get("confidence_grade_derived") or ""
            ),
            external_claim_policy=external_policy,
            permission=_permission_for(activation, external_policy),
            role_family_weights=role_weights,
            pillar=str(row.get("pillar") or ""),
            domain=str(row.get("domain") or ""),
        )

    digest = _sha16(json.dumps(graph.get("graph_metadata") or {}, sort_keys=True, default=str))
    return AppsRgProofIndex(
        available=True,
        graph_source=APPS_RG_GRAPH_SOURCE,
        graph_version=graph_version_from_payload(graph),
        graph_digest=digest,
        skills_by_id=skills_by_id,
        fact_to_node=fact_to_node,
        skill_to_node=skill_to_node,
        adjacency={k: tuple(v) for k, v in adjacency.items()},
        fact_to_skills={k: tuple(dict.fromkeys(v)) for k, v in fact_to_skills.items()},
    )


def proof_provenance_for(
    *,
    source_ids: tuple[str, ...] | list[str] = (),
    skill_tags: tuple[str, ...] | list[str] = (),
    apps_rg_skill_ids: tuple[str, ...] | list[str] = (),
) -> dict[str, Any]:
    """Resolve apps_rg SSOT provenance for one apps_lic proof point.

    ``apps_rg_skill_ids`` is the authoritative linkage: explicit apps_rg skill
    IDs the proof point claims as its shared-SSOT backing. ``source_ids`` /
    ``skill_tags`` are also tried (apps_rg fact ids / skill ids that happen to
    match). Returns a serialisable provenance block: which references resolve to
    real apps_rg graph nodes, the union approval permission, and the shared graph
    ref/version/digest. When the shared SSOT is unavailable, ``ssot_available`` is
    False and nothing is claimed as grounded.
    """
    idx = load_apps_rg_proof_index()
    src = tuple(str(s).strip() for s in source_ids if str(s).strip())
    explicit = tuple(str(s).strip() for s in apps_rg_skill_ids if str(s).strip())
    tags = tuple((*explicit, *(str(t).strip() for t in skill_tags if str(t).strip())))
    if not idx.available:
        return {
            "ssot_available": False,
            "graph_source": idx.graph_source,
            "graph_version": idx.graph_version,
            "resolved_fact_ids": [],
            "resolved_skill_ids": [],
            "permission": PERMISSION_BLOCKED,
            "load_error": idx.load_error,
        }
    resolved_facts = [fid for fid in src if fid in idx.fact_to_node]
    # The proof point's OWN declared skills (skill_tags) drive permission.
    own_skills = [sid for sid in tags if sid in idx.skills_by_id]
    # A source_id can be an apps_rg fact id implying skills via lineage (breadth).
    lineage_skills = [
        sid
        for fid in resolved_facts
        for sid in idx.fact_to_skills.get(fid, ())
        if sid not in own_skills
    ]
    resolved_skills = list(dict.fromkeys((*own_skills, *lineage_skills)))

    def _allow(sids: list[str]) -> bool:
        return bool(sids) and all(
            idx.skills_by_id[sid].permission == PERMISSION_ALLOW for sid in sids
        )

    if own_skills:
        # Declared skills must all be approved in the shared SSOT.
        permission = PERMISSION_ALLOW if _allow(own_skills) else PERMISSION_BLOCKED
    elif lineage_skills:
        # Grounded only via fact lineage: allow if any approved skill backs it.
        permission = (
            PERMISSION_ALLOW
            if any(idx.skills_by_id[sid].permission == PERMISSION_ALLOW for sid in lineage_skills)
            else PERMISSION_BLOCKED
        )
    else:
        permission = PERMISSION_BLOCKED
    grounded = bool(resolved_facts or resolved_skills)
    return {
        "ssot_available": True,
        "ssot_grounded": grounded,
        "graph_source": idx.graph_source,
        "graph_version": idx.graph_version,
        "graph_digest": idx.graph_digest,
        "snapshot_pointer": idx.snapshot_pointer,
        "resolved_fact_ids": resolved_facts,
        "resolved_skill_ids": resolved_skills,
        "permission": permission,
    }


def recipient_fit_weight(
    *,
    apps_rg_skill_ids: tuple[str, ...] | list[str],
    recipient_class: str,
) -> dict[str, Any]:
    """Graph-derived recipient fit for a proof point (W3).

    Maps the recipient class to the apps_rg role families it screens for, then
    returns the best ``role_family_weights`` value across the proof point's
    linked apps_rg skills for those families. ``weight`` is 0.0 when the SSOT is
    unavailable, the recipient class is unknown, or no skill weights match.
    """
    idx = load_apps_rg_proof_index()
    families = RECIPIENT_ROLE_FAMILIES.get(str(recipient_class or "").strip().upper(), ())
    if not idx.available or not families:
        return {"weight": 0.0, "families": list(families), "matched_family": "", "matched_skill": ""}
    best = 0.0
    best_family = ""
    best_skill = ""
    for sid in apps_rg_skill_ids:
        proof = idx.skills_by_id.get(str(sid).strip())
        if proof is None:
            continue
        for family in families:
            weight = float(proof.role_family_weights.get(family, 0.0))
            if weight > best:
                best, best_family, best_skill = weight, family, proof.skill_id
    return {
        "weight": round(best, 4),
        "families": list(families),
        "matched_family": best_family,
        "matched_skill": best_skill,
    }


def graph_weighted_skill_ids(
    *,
    recipient_class: str,
    top_n: int = 8,
    min_weight: float = 0.6,
) -> tuple[str, ...]:
    """Top apps_rg skill ids by recipient role-family fit (W3).

    Replaces flat hand-authored ``candidate_skills`` lists with a graph-weighted
    selection. Returns approved (allow-permission) apps_rg skill ids ranked by
    their best role-family weight for the recipient class.
    """
    idx = load_apps_rg_proof_index()
    families = RECIPIENT_ROLE_FAMILIES.get(str(recipient_class or "").strip().upper(), ())
    if not idx.available or not families:
        return ()
    scored: list[tuple[float, str]] = []
    for sid, proof in idx.skills_by_id.items():
        if proof.permission != PERMISSION_ALLOW:
            continue
        best = max((float(proof.role_family_weights.get(f, 0.0)) for f in families), default=0.0)
        if best >= min_weight:
            scored.append((best, sid))
    scored.sort(key=lambda item: (-item[0], item[1]))
    return tuple(sid for _weight, sid in scored[: max(0, top_n)])


__all__ = [
    "APPS_RG_GRAPH_SOURCE",
    "PERMISSION_ALLOW",
    "PERMISSION_BLOCKED",
    "RECIPIENT_ROLE_FAMILIES",
    "ApprovedSkillProof",
    "AppsRgProofIndex",
    "graph_weighted_skill_ids",
    "load_apps_rg_proof_index",
    "proof_provenance_for",
    "recipient_fit_weight",
]
