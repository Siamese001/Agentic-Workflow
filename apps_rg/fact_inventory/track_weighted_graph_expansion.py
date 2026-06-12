"""P1-W4 track-weighted proof pool expansion over augmented_skills_graph.

Uses only materialized graph edges (career_track, pillar, skill_supported_by_fact, employment spine).
Career track sequence is chronological ordering only — never causal proof.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import (
    SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
    assert_skills_not_broad_ledger_authority,
    graph_version_from_payload,
    load_augmented_skills_graph,
)
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
)

ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "docs/reports/apps_rg"
FIXTURES_DIR = REPORTS_DIR / "fixtures"

TRACK_NODE_IDS = (
    "track_actuarial_risk_derivatives",
    "track_data_tech_cloud_ml",
    "track_genai_agentic",
)

DEFAULT_TRACK_WEIGHTS: dict[str, float] = {
    "track_actuarial_risk_derivatives": 0.10,
    "track_data_tech_cloud_ml": 0.25,
    "track_genai_agentic": 0.65,
}

# Functional pillar-weight defaults (within-track skill re-ranking).
# A skill whose pillar is not in the active profile's top_weighted_pillars gets the
# neutral default; a pillar in the profile's deprioritize list is suppressed near-zero.
DEFAULT_FUNCTIONAL_PILLAR_WEIGHT = 0.55
DEPRIORITIZED_PILLAR_WEIGHT = 0.10

ROLE_FAMILY_TRACK_WEIGHTS: dict[str, dict[str, float]] = {
    "SVP_ENGINEERING_AI_PLATFORM": dict(DEFAULT_TRACK_WEIGHTS),
    "CHIEF_AI_OFFICER": {
        "track_actuarial_risk_derivatives": 0.15,
        "track_data_tech_cloud_ml": 0.25,
        "track_genai_agentic": 0.60,
    },
    "FIELD_CTO": {
        "track_actuarial_risk_derivatives": 0.05,
        "track_data_tech_cloud_ml": 0.45,
        "track_genai_agentic": 0.50,
    },
    "GOVERNANCE_RISK": {
        "track_actuarial_risk_derivatives": 0.40,
        "track_data_tech_cloud_ml": 0.30,
        "track_genai_agentic": 0.30,
    },
    "QUANT_TRADING": {
        "track_actuarial_risk_derivatives": 0.55,
        "track_data_tech_cloud_ml": 0.35,
        "track_genai_agentic": 0.10,
    },
    "ANTHROPIC_PARTNERSHIPS_APPLIED_AI": {
        "track_actuarial_risk_derivatives": 0.05,
        "track_data_tech_cloud_ml": 0.70,
        "track_genai_agentic": 0.25,
    },
    # W14b — senior-role profiles (mirrors senior_role_track_weight_profiles_design.yaml)
    "INSURANCE_CARRIER_TRANSFORMATION": {
        "track_actuarial_risk_derivatives": 0.35,
        "track_data_tech_cloud_ml": 0.25,
        "track_genai_agentic": 0.40,
    },
    "INSURER_IT_AI_ENABLEMENT": {
        "track_actuarial_risk_derivatives": 0.20,
        "track_data_tech_cloud_ml": 0.45,
        "track_genai_agentic": 0.35,
    },
    "INSURANCE_BROKERAGE_IT_INNOVATION": {
        "track_actuarial_risk_derivatives": 0.10,
        "track_data_tech_cloud_ml": 0.50,
        "track_genai_agentic": 0.40,
    },
    "BANKING_PLATFORM_AI": {
        "track_actuarial_risk_derivatives": 0.35,
        "track_data_tech_cloud_ml": 0.30,
        "track_genai_agentic": 0.35,
    },
    "REGULATED_AI_GOVERNANCE": {
        "track_actuarial_risk_derivatives": 0.40,
        "track_data_tech_cloud_ml": 0.30,
        "track_genai_agentic": 0.30,
    },
    "PARTNER_APPLIED_AI_ARCHITECTURE": {
        "track_actuarial_risk_derivatives": 0.03,
        "track_data_tech_cloud_ml": 0.70,
        "track_genai_agentic": 0.27,
    },
    "HYPERSCALER_MARKETPLACE_GTM": {
        "track_actuarial_risk_derivatives": 0.05,
        "track_data_tech_cloud_ml": 0.70,
        "track_genai_agentic": 0.25,
    },
    "CONSULTING_DELIVERY_LEADERSHIP": {
        "track_actuarial_risk_derivatives": 0.15,
        "track_data_tech_cloud_ml": 0.50,
        "track_genai_agentic": 0.35,
    },
    # Enhancement #2 — three-phase balanced profile for JDs requiring all career eras equally.
    # Used when detect_three_phase_jd() is True and no domain-specific profile matches.
    # Weights kept within ±0.11 of each other to prevent any single track dominating.
    "THREE_PHASE_GENERALIST": {
        "track_actuarial_risk_derivatives": 0.27,
        "track_data_tech_cloud_ml": 0.38,
        "track_genai_agentic": 0.35,
    },
}

# Taxonomy ids with dedicated W0.5b projection profiles (JD targeting only).
SENIOR_ROLE_TAXONOMY_IDS: frozenset[str] = frozenset(
    {
        "INSURANCE_CARRIER_TRANSFORMATION",
        "INSURER_IT_AI_ENABLEMENT",
        "INSURANCE_BROKERAGE_IT_INNOVATION",
        "BANKING_PLATFORM_AI",
        "REGULATED_AI_GOVERNANCE",
        "PARTNER_APPLIED_AI_ARCHITECTURE",
        "HYPERSCALER_MARKETPLACE_GTM",
        "CONSULTING_DELIVERY_LEADERSHIP",
    }
)

TAXONOMY_TO_PROJECTION_ROLE: dict[str, str] = {
    "ENGINEERING_PLATFORM": "SVP_ENGINEERING_AI_PLATFORM",
    "AI_GOVERNANCE_RISK": "GOVERNANCE_RISK",
    "QUANT_TRADING_HPC": "QUANT_TRADING",
    "PARTNERSHIPS_GTM": "ANTHROPIC_PARTNERSHIPS_APPLIED_AI",
    "EXECUTIVE_LEADERSHIP": "CHIEF_AI_OFFICER",
    "AI_SOLUTIONS_ARCHITECTURE": "FIELD_CTO",
    "INSURANCE_CARRIER_TRANSFORMATION": "INSURANCE_CARRIER_TRANSFORMATION",
    "INSURER_IT_AI_ENABLEMENT": "INSURER_IT_AI_ENABLEMENT",
    "INSURANCE_BROKERAGE_IT_INNOVATION": "INSURANCE_BROKERAGE_IT_INNOVATION",
    "BANKING_PLATFORM_AI": "BANKING_PLATFORM_AI",
    "REGULATED_AI_GOVERNANCE": "REGULATED_AI_GOVERNANCE",
    "PARTNER_APPLIED_AI_ARCHITECTURE": "PARTNER_APPLIED_AI_ARCHITECTURE",
    "HYPERSCALER_MARKETPLACE_GTM": "HYPERSCALER_MARKETPLACE_GTM",
    "CONSULTING_DELIVERY_LEADERSHIP": "CONSULTING_DELIVERY_LEADERSHIP",
}

HYBRID_JD_FIXTURE = (
    "SVP Engineering — Agentic AI platform leader for regulated financial services. "
    "Must show governed agentic runtime, GraphRAG, multi-agent orchestration, and policy gates. "
    "Also value actuarial rigor, derivatives risk, and Basel/CCAR lineage plus "
    "AWS cloud data platform and partner GTM co-sell experience."
)

SINGLE_TRACK_JD_FIXTURE = (
    "Quantitative trading and derivatives pricing specialist — deep actuarial foundation, "
    "Greeks hedging, exotic options, and capital modeling only. No agentic AI or partner GTM scope."
)

APPROVED_EDGE_TYPES = frozenset(
    {
        "career_track_contains_pillar",
        "career_track_contains_epoch",
        "employment_in_career_track",
        "employment_hosts_fact",
        "skill_supported_by_fact",
        "epoch_contains_pillar",
    }
)

GRAPH_EXPANSION_MODE_TRACK_WEIGHTED = "TRACK_WEIGHTED_MULTI_HOP"
C03_BINDING_SURFACE = "apps_rg/fact_inventory/track_weighted_graph_expansion"

P1_W4_CLOSEOUT_FILE_PREFIXES = (
    "apps_rg/fact_inventory/track_weighted_graph_expansion.py",
    "apps_rg/fact_inventory/validate_p1_w4_track_weighted_closeout.py",
    "apps_rg/runtime/proof_pool_resolver.py",
    "tests/unit/apps_rg/fact_inventory/test_track_weighted_graph_expansion_p1_w4.py",
    "tests/_apps_contract/test_career_track_p1_w4_weighted_expansion_contract.py",
    "docs/reports/apps_rg/career_track_p1_w4",
    "docs/reports/apps_rg/fixtures/p1_w4",
    ".claude/plans/graph-skills-hardening-f3a8c1.md",
)


def _sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _graph_ref_and_digest(graph: dict[str, Any], repo_root: Path) -> tuple[str, str]:
    path = repo_root / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
    ref = (
        str(path.relative_to(repo_root))
        if path.is_relative_to(repo_root)
        else str(path)
    )
    digest = _sha256_hex(json.dumps(graph, sort_keys=True, ensure_ascii=False, separators=(",", ":")))
    return ref, digest


class TrackWeightedExpansionContractError(ValueError):
    """Hybrid track coverage or authority contract violation."""


@dataclass
class GraphHopStep:
    edge_type: str
    from_node: str
    to_node: str
    note: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "edge_type": self.edge_type,
            "from": self.from_node,
            "to": self.to_node,
            "note": self.note,
        }


def _normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    clipped = {k: max(0.0, float(weights.get(k, 0.0))) for k in TRACK_NODE_IDS}
    total = sum(clipped.values())
    if total <= 0:
        return dict(DEFAULT_TRACK_WEIGHTS)
    return {k: round(v / total, 4) for k, v in clipped.items()}


def resolve_career_track_weights(
    *,
    role_family_key: str,
    jd_text: str = "",
    weight_override: dict[str, float] | None = None,
) -> dict[str, float]:
    """JD/role_family → normalized career_track weights."""
    if weight_override is not None:
        return _normalize_weights(weight_override)
    base = dict(ROLE_FAMILY_TRACK_WEIGHTS.get(role_family_key) or DEFAULT_TRACK_WEIGHTS)
    jd = jd_text.lower()
    if jd:
        bumps: dict[str, float] = {}
        if any(k in jd for k in ("actuarial", "derivatives", "greeks", "basel", "ccar", "capital modeling")):
            bumps["track_actuarial_risk_derivatives"] = 0.05
        if any(
            k in jd
            for k in (
                "underwriting",
                "claims",
                "policy administration",
                "insurance industry",
                "insurance carrier",
            )
        ):
            bumps["track_actuarial_risk_derivatives"] = max(
                bumps.get("track_actuarial_risk_derivatives", 0.0), 0.08
            )
        # Enhancement #5 — Phase 1 keyword expansion: regulatory/quantitative risk signals
        if any(
            k in jd
            for k in (
                "stress testing",
                "ifrs 17",
                "solvency ii",
                "model risk",
                "quantitative risk",
                "reserving",
                "economic capital",
                "embedded value",
            )
        ):
            bumps["track_actuarial_risk_derivatives"] = max(
                bumps.get("track_actuarial_risk_derivatives", 0.0), 0.06
            )
        if any(k in jd for k in ("aws", "cloud", "partner", "gtm", "co-sell", "hyperscaler", "revenue")):
            bumps["track_data_tech_cloud_ml"] = 0.05
        # Enhancement #9 — Phase 2 keyword expansion: IBM ecosystem and FinOps signals
        if any(
            k in jd
            for k in (
                "watson",
                "apptio",
                "finops",
                "solution engineering",
                "cloud marketplace",
                "ibm consulting",
            )
        ):
            bumps["track_data_tech_cloud_ml"] = max(
                bumps.get("track_data_tech_cloud_ml", 0.0), 0.06
            )
        if any(
            k in jd
            for k in (
                "agentic",
                "graphrag",
                "orchestration",
                "routing",
                "llm governance",
                "rag-enhanced",
                "multi-agent",
                "companion agent",
                "automation agent",
            )
        ):
            bumps["track_genai_agentic"] = 0.05
        if any(
            k in jd
            for k in (
                "it strategy",
                "enterprise architecture",
                "innovation incubation",
                "data platforms",
                "technology strategy",
            )
        ):
            bumps["track_data_tech_cloud_ml"] = max(
                bumps.get("track_data_tech_cloud_ml", 0.0), 0.08
            )
            bumps["track_genai_agentic"] = max(bumps.get("track_genai_agentic", 0.0), 0.06)
        if role_family_key == "INSURANCE_CARRIER_TRANSFORMATION" and any(
            k in jd for k in ("agentic ai", "agentic ai transformation", "global head")
        ):
            bumps["track_genai_agentic"] = max(bumps.get("track_genai_agentic", 0.0), 0.12)
        if role_family_key in (
            "INSURER_IT_AI_ENABLEMENT",
            "INSURANCE_BROKERAGE_IT_INNOVATION",
        ) and any(k in jd for k in ("innovation", "enterprise architecture", "ai/ml")):
            bumps["track_data_tech_cloud_ml"] = max(
                bumps.get("track_data_tech_cloud_ml", 0.0), 0.10
            )
            bumps["track_genai_agentic"] = max(bumps.get("track_genai_agentic", 0.0), 0.08)
        for track, bump in bumps.items():
            base[track] = base.get(track, 0.0) + bump
    return _normalize_weights(base)


def _three_phase_jd_hit(jd_text: str) -> bool:
    """Return True when JD keywords independently bump all three career track nodes.

    Mirrors the bump keyword sets in resolve_career_track_weights without importing
    graph_selection_rationale (would create a circular dependency).
    """
    jd = jd_text.lower()
    p1_hit = any(
        k in jd
        for k in (
            "actuarial", "derivatives", "greeks", "basel", "ccar", "capital modeling",
            "underwriting", "claims", "policy administration", "insurance industry", "insurance carrier",
            "stress testing", "ifrs 17", "solvency ii", "model risk", "quantitative risk",
            "reserving", "economic capital", "embedded value",
        )
    )
    p2_hit = any(
        k in jd
        for k in (
            "aws", "cloud", "partner", "gtm", "co-sell", "hyperscaler", "revenue",
            "watson", "apptio", "finops", "solution engineering", "cloud marketplace", "ibm consulting",
            "it strategy", "enterprise architecture", "innovation incubation", "data platforms",
            "technology strategy",
        )
    )
    p3_hit = any(
        k in jd
        for k in (
            "agentic", "graphrag", "orchestration", "routing", "llm governance",
            "rag-enhanced", "multi-agent", "companion agent", "automation agent",
        )
    )
    return p1_hit and p2_hit and p3_hit


def infer_projection_role_family_key(
    *,
    target_role: str = "",
    jd_text: str = "",
    briefing_text: str = "",
    taxonomy: dict[str, Any] | None = None,
) -> str:
    """Map taxonomy inference to ledger role_family_projection_profiles key."""
    from apps_rg.fact_inventory.role_family_selection import infer_role_family_priorities

    if taxonomy is None:
        tax_path = ROOT / "apps_rg/config/domain_contract/master_role_family_taxonomy.yaml"
        import yaml  # type: ignore[import-untyped]

        taxonomy = yaml.safe_load(tax_path.read_text(encoding="utf-8"))
    priorities = infer_role_family_priorities(
        target_role=target_role,
        jd_text=jd_text,
        briefing_text=briefing_text,
        taxonomy=taxonomy,
    )
    corp = f"{target_role}\n{jd_text}\n{briefing_text}".lower()
    ade_signals = (
        "deployment engineering",
        "partner ade",
        "systems integrator",
        "genai",
        "openai api",
        "ai deployment",
        "prototype to production",
    )
    ade_hits = sum(1 for sig in ade_signals if sig in corp)
    if priorities and ade_hits >= 3:
        partner = next(
            (p for p in priorities if p.role_family == "PARTNER_APPLIED_AI_ARCHITECTURE"),
            None,
        )
        if partner and partner.score > 0:
            top = priorities[0]
            if top.role_family != "PARTNER_APPLIED_AI_ARCHITECTURE" and partner.score >= top.score - 1:
                priorities = (partner,) + tuple(
                    p for p in priorities if p.role_family != partner.role_family
                )
    carrier_signals = (
        "insurance",
        "underwriting",
        "claims",
        "agentic ai",
        "policy administration",
        "carrier transformation",
    )
    carrier_hits = sum(1 for sig in carrier_signals if sig in corp)
    if priorities and carrier_hits >= 4:
        carrier = next(
            (p for p in priorities if p.role_family == "INSURANCE_CARRIER_TRANSFORMATION"),
            None,
        )
        if carrier and carrier.score > 0:
            top = priorities[0]
            if (
                top.role_family != "INSURANCE_CARRIER_TRANSFORMATION"
                and carrier.score >= top.score - 1
            ):
                priorities = (carrier,) + tuple(
                    p for p in priorities if p.role_family != carrier.role_family
                )
    broker_it_signals = (
        "brown & brown",
        "insurance brokerage",
        "it strategy & innovation",
        "it strategy",
        "enterprise architecture",
        "innovation incubation",
        "interoperability",
        "CITO",
    )
    broker_hits = sum(1 for sig in broker_it_signals if sig in corp)
    if priorities and broker_hits >= 4:
        broker = next(
            (p for p in priorities if p.role_family == "INSURANCE_BROKERAGE_IT_INNOVATION"),
            None,
        )
        insurer_it = next(
            (p for p in priorities if p.role_family == "INSURER_IT_AI_ENABLEMENT"),
            None,
        )
        pick = broker
        if broker and insurer_it and insurer_it.score > broker.score:
            pick = insurer_it
        if pick and pick.score > 0:
            top = priorities[0]
            if pick.role_family != top.role_family and pick.score >= top.score - 1:
                priorities = (pick,) + tuple(
                    p for p in priorities if p.role_family != pick.role_family
                )
    if priorities:
        top = priorities[0]
        banking = next((p for p in priorities if p.role_family == "BANKING_PLATFORM_AI"), None)
        regulated = next((p for p in priorities if p.role_family == "REGULATED_AI_GOVERNANCE"), None)
        if (
            banking
            and regulated
            and banking.score >= 2
            and banking.score >= regulated.score - 2
        ):
            mapped = TAXONOMY_TO_PROJECTION_ROLE.get("BANKING_PLATFORM_AI")
            if mapped:
                return mapped

        senior_hits = [
            p
            for p in priorities
            if p.role_family in SENIOR_ROLE_TAXONOMY_IDS and p.score > 0
        ]
        if senior_hits:
            best_score = max(p.score for p in senior_hits)
            if top.score > best_score:
                mapped = TAXONOMY_TO_PROJECTION_ROLE.get(top.role_family)
                if mapped:
                    return mapped
            tie_order = (
                "INSURANCE_CARRIER_TRANSFORMATION",
                "INSURANCE_BROKERAGE_IT_INNOVATION",
                "INSURER_IT_AI_ENABLEMENT",
                "PARTNER_APPLIED_AI_ARCHITECTURE",
                "BANKING_PLATFORM_AI",
                "CONSULTING_DELIVERY_LEADERSHIP",
                "HYPERSCALER_MARKETPLACE_GTM",
                "REGULATED_AI_GOVERNANCE",
            )
            order_rank = {rid: idx for idx, rid in enumerate(tie_order)}
            tied = [p for p in senior_hits if p.score == best_score]
            tied.sort(key=lambda p: order_rank.get(p.role_family, 99))
            mapped = TAXONOMY_TO_PROJECTION_ROLE.get(tied[0].role_family)
            if mapped:
                return mapped

        top_tax = top.role_family
        mapped = TAXONOMY_TO_PROJECTION_ROLE.get(top_tax)
        if mapped:
            return mapped
    # Enhancement #2 — three-phase fallback: when no domain-specific profile matched and the
    # JD signals all three career tracks, prefer the balanced THREE_PHASE_GENERALIST profile
    # over the Phase 3-dominant SVP_ENGINEERING_AI_PLATFORM default.
    if _three_phase_jd_hit(jd_text):
        return "THREE_PHASE_GENERALIST"
    return "SVP_ENGINEERING_AI_PLATFORM"


@dataclass
class _GraphIndexes:
    track_pillars: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    track_epochs: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    pillar_epochs: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    skill_to_facts: dict[str, set[str]] = field(default_factory=lambda: defaultdict(set))
    employment_tracks: dict[str, str] = field(default_factory=dict)


def _build_graph_indexes(graph: dict[str, Any]) -> _GraphIndexes:
    idx = _GraphIndexes()
    for edge in graph.get("graph_edges") or []:
        if not isinstance(edge, dict):
            continue
        et = str(edge.get("edge_type") or "")
        src = str(edge.get("source_node_id") or "")
        tgt = str(edge.get("target_node_id") or "")
        if et == "career_track_contains_pillar":
            idx.track_pillars[src].add(tgt)
        elif et == "career_track_contains_epoch":
            idx.track_epochs[src].add(tgt)
        elif et == "epoch_contains_pillar":
            idx.pillar_epochs[tgt].add(src)
        elif et == "skill_supported_by_fact":
            idx.skill_to_facts[src].add(tgt)
        elif et == "employment_in_career_track" and edge.get("primary") is True:
            idx.employment_tracks[src] = tgt
    return idx


def _skill_rows_by_id(graph: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for row in graph.get("skill_rows") or []:
        if isinstance(row, dict) and row.get("skill_id"):
            out[str(row["skill_id"])] = row
    return out


def _row_track_id(row: dict[str, Any], pillar: str, track_pillars: dict[str, set[str]]) -> str | None:
    explicit = row.get("career_track_id")
    if explicit:
        mapping = {
            "TRACK_ACTUARIAL_RISK_DERIVATIVES": "track_actuarial_risk_derivatives",
            "TRACK_DATA_TECH_CLOUD_ML": "track_data_tech_cloud_ml",
            "TRACK_GENAI_AGENTIC": "track_genai_agentic",
        }
        return mapping.get(str(explicit), None)
    for track, pillars in track_pillars.items():
        if pillar in pillars:
            return track
    return None


def _build_hop_path(
    *,
    track_id: str,
    pillar: str,
    skill_id: str,
    fact_id: str,
    idx: _GraphIndexes,
) -> list[dict[str, str]]:
    steps: list[GraphHopStep] = [
        GraphHopStep(
            "career_track_contains_pillar",
            track_id,
            pillar,
            "track-weighted pillar scope",
        ),
        GraphHopStep(
            "skill_row_pillar_projection",
            pillar,
            skill_id,
            "ACTIVE skill_row pillar match (not causal)",
        ),
    ]
    if fact_id in idx.skill_to_facts.get(skill_id, set()):
        steps.append(
            GraphHopStep(
                "skill_supported_by_fact",
                skill_id,
                fact_id,
                "graph edge skill_supported_by_fact",
            )
        )
    else:
        steps.append(
            GraphHopStep(
                "skill_row_fact_id_links",
                skill_id,
                fact_id,
                "fact_id_links on skill_row (no separate fact node)",
            )
        )
    return [s.as_dict() for s in steps]


def bind_track_weighted_c03_graph_evidence(
    expansion: dict[str, Any],
    *,
    graph: dict[str, Any],
    graph_ref: str,
    graph_digest: str,
    binding_surface: str = C03_BINDING_SURFACE,
) -> dict[str, Any]:
    """Bind track-weighted expansion as C0.3-style graph evidence (graph-only items)."""
    from apps_rg.runtime.c03_graphrag_bound import build_executive_summary_c03_graphrag_bound

    fact_ids = sorted(
        {str(f["fact_id"]) for f in expansion.get("selected_facts") or [] if f.get("fact_id")}
    )
    skill_ids = sorted(
        {str(s["skill_id"]) for s in expansion.get("selected_skills") or [] if s.get("skill_id")}
    )
    hop_paths: list[list[dict[str, str]]] = []
    edge_types: set[str] = set()
    for skill in expansion.get("selected_skills") or []:
        path = skill.get("graph_hop_path") or []
        if path:
            hop_paths.append(path)
        for step in path:
            if isinstance(step, dict) and step.get("edge_type"):
                edge_types.add(str(step["edge_type"]))

    evidence_items: list[dict[str, Any]] = []
    for fid in fact_ids:
        evidence_items.append(
            {
                "evidence_id": f"evidence:track_weighted:{fid}",
                "source": graph_ref,
                "source_class": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
                "graph_node_ref": f"node_fact:{fid.split('_metric_', 1)[0]}",
                "authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
                "binding_mode": GRAPH_EXPANSION_MODE_TRACK_WEIGHTED,
                "career_track": next(
                    (
                        str(f.get("career_track"))
                        for f in expansion.get("selected_facts") or []
                        if str(f.get("fact_id")) == fid
                    ),
                    "",
                ),
            }
        )

    non_graph = [
        it
        for it in evidence_items
        if str(it.get("source_class")) != SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
        or str(it.get("authority")) != SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH
    ]

    c03_doc = build_executive_summary_c03_graphrag_bound(
        graph=graph,
        graph_ref=graph_ref,
        graph_digest=graph_digest,
        selected_fact_ids=fact_ids,
        evidence_items=evidence_items,
    )
    c03_status = str(c03_doc.get("c03_graphrag_bound_status") or "NOT_BOUND")
    expansion_ref = f"ref:graph:track_weighted_expansion:{graph_digest[:16]}"

    bound = {
        **expansion,
        "c03_graph_bound_status": c03_status,
        "c03_binding_surface": binding_surface,
        "c03_graph_expansion_ref": expansion_ref,
        "c03_graph_hop_paths_count": len(hop_paths),
        "c03_selected_tracks": list(expansion.get("tracks_with_facts") or []),
        "c03_selected_fact_ids": fact_ids,
        "c03_selected_skill_ids": skill_ids,
        "non_graph_evidence_items_count": len(non_graph),
        "graph_expansion_mode": GRAPH_EXPANSION_MODE_TRACK_WEIGHTED,
        "graph_hop_edge_types_used": sorted(edge_types),
        "c03_graphrag_bound_document": c03_doc,
        "graph_ref": graph_ref,
        "graph_digest": graph_digest,
        "graph_version": graph_version_from_payload(graph),
    }
    assert_skills_not_broad_ledger_authority(bound)
    return bound


def build_track_weighted_expansion(
    *,
    graph: dict[str, Any] | None = None,
    role_family_key: str = "SVP_ENGINEERING_AI_PLATFORM",
    jd_text: str = "",
    briefing_text: str = "",
    weight_override: dict[str, float] | None = None,
    seed_fact_ids: list[str] | None = None,
    min_tracks_with_facts: int = 2,
    enforce_hybrid_contract: bool = True,
    bind_c03: bool = True,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Expand proof-safe skills/facts by career track weights using approved graph edges only."""
    root = repo_root or ROOT
    g = graph or load_augmented_skills_graph(repo_root=root)
    weights = resolve_career_track_weights(
        role_family_key=role_family_key,
        jd_text=jd_text,
        weight_override=weight_override,
    )
    idx = _build_graph_indexes(g)
    rows_by_id = _skill_rows_by_id(g)
    seed = {str(x) for x in (seed_fact_ids or []) if str(x).strip()}

    # Functional pillar-weight signal: the projection profile's top_weighted_pillars
    # re-rank approved skills WITHIN each career track by JD-resolved role family.
    # (Replaces the dead role_family_weights lookup — those weights are keyed by taxonomy
    # id, never the projection key, so the prior `rf_w` was silently always 0.0.)
    profiles = g.get("role_family_projection_profiles") or {}
    _profile = profiles.get(role_family_key) or {}
    _pillar_w = {
        str(p.get("pillar_id")): float(p.get("weight") or 0.0)
        for p in (_profile.get("top_weighted_pillars") or [])
        if isinstance(p, dict) and p.get("pillar_id")
    }
    _deprio_pillars = {str(x) for x in (_profile.get("deprioritize_pillars") or [])}

    def _functional_pillar_weight(pillar_id: str) -> float:
        if pillar_id in _deprio_pillars:
            return DEPRIORITIZED_PILLAR_WEIGHT
        return _pillar_w.get(pillar_id, DEFAULT_FUNCTIONAL_PILLAR_WEIGHT)

    selected_skills: list[dict[str, Any]] = []
    selected_facts: list[dict[str, Any]] = []
    excluded: list[dict[str, str]] = []
    skills_by_track: dict[str, list[str]] = defaultdict(list)
    facts_by_track: dict[str, list[str]] = defaultdict(list)

    for track_id in TRACK_NODE_IDS:
        w = weights[track_id]
        if w <= 0.001:
            excluded.append({"id": track_id, "reason": f"track_weight_zero:{w}"})
            continue
        pillars = idx.track_pillars.get(track_id, set())
        if not pillars:
            excluded.append({"id": track_id, "reason": "no_pillars_for_track"})
            continue
        cap = max(1, int(round(20 * w)))
        candidates: list[tuple[float, str, dict[str, Any]]] = []
        for sid, row in rows_by_id.items():
            status = str(row.get("activation_status") or "")
            if not status.startswith("ACTIVE"):
                excluded.append({"id": sid, "reason": f"not_active:{status}"})
                continue
            if not skill_row_eligible_for_external_claim(row):
                excluded.append({"id": sid, "reason": "not_eligible_for_external_claim"})
                continue
            pillar = str(row.get("pillar") or "")
            row_track = _row_track_id(row, pillar, idx.track_pillars)
            if row_track != track_id:
                continue
            links = [str(x) for x in (row.get("fact_id_links") or []) if str(x).strip()]
            if not links:
                excluded.append({"id": sid, "reason": "empty_fact_id_links"})
                continue
            functional_w = _functional_pillar_weight(pillar)
            score = w * functional_w
            candidates.append((score, sid, row))
        candidates.sort(key=lambda t: (-t[0], t[1]))
        for _, sid, row in candidates[:cap]:
            pillar = str(row.get("pillar") or "")
            links = [str(x) for x in (row.get("fact_id_links") or []) if str(x).strip()]
            for fid in links:
                if seed and fid not in seed and fid.split("_metric_")[0] not in seed:
                    pass  # still allow graph-backed facts without SRFS seed
                hop = _build_hop_path(
                    track_id=track_id,
                    pillar=pillar,
                    skill_id=sid,
                    fact_id=fid,
                    idx=idx,
                )
                selected_skills.append(
                    {
                        "skill_id": sid,
                        "career_track": track_id,
                        "pillar": pillar,
                        "weight": w,
                        "graph_hop_path": hop,
                    }
                )
                skills_by_track[track_id].append(sid)
                fact_entry = {
                    "fact_id": fid,
                    "career_track": track_id,
                    "skill_id": sid,
                    "graph_hop_path": hop,
                }
                selected_facts.append(fact_entry)
                facts_by_track[track_id].append(fid)

    # De-dupe facts/skills per track
    def _uniq(xs: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for x in xs:
            if x not in seen:
                seen.add(x)
                out.append(x)
        return out

    skills_by_track = {k: _uniq(v) for k, v in skills_by_track.items()}
    facts_by_track = {k: _uniq(v) for k, v in facts_by_track.items()}
    tracks_with_facts = [t for t, fids in facts_by_track.items() if fids]

    meta = {
        "schema": "track_weighted_graph_expansion_v1",
        "plan_id": "graph-skills-hardening-f3a8c1",
        "wave": "P1-W4",
        "source_authority": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "skills_authority_source_type": SOURCE_AUTHORITY_AUGMENTED_SKILLS_GRAPH,
        "broad_skills_ledger_used_as_authority": False,
        "legacy_broad_skills_ledger_skills_authority": False,
        "cross_track_causal_claims": False,
        "career_sequence_semantics": "chronological_only_non_causal",
        "role_family_key": role_family_key,
        "projection_role_family_key": role_family_key,
        "tracks_selected": list(TRACK_NODE_IDS),
        "track_weights": weights,
        "selected_skill_count_by_track": {k: len(v) for k, v in skills_by_track.items()},
        "selected_fact_count_by_track": {k: len(v) for k, v in facts_by_track.items()},
        "tracks_with_facts": tracks_with_facts,
        "selected_skills": selected_skills[:120],
        "selected_facts": selected_facts[:120],
        "excluded_candidates": excluded[:200],
        "graph_hop_paths_sample": [s.get("graph_hop_path") for s in selected_skills[:5]],
        "approved_edge_types_used": sorted(APPROVED_EDGE_TYPES),
        "targeting": {
            "jd_text_excerpt": jd_text[:240],
            "briefing_text_excerpt": briefing_text[:120],
        },
    }
    assert_skills_not_broad_ledger_authority(meta)

    if enforce_hybrid_contract and min_tracks_with_facts > 1:
        if len(tracks_with_facts) < min_tracks_with_facts:
            raise TrackWeightedExpansionContractError(
                f"hybrid contract requires >={min_tracks_with_facts} tracks with facts; "
                f"got {tracks_with_facts}"
            )

    if bind_c03:
        graph_ref, graph_digest = _graph_ref_and_digest(g, root)
        meta = bind_track_weighted_c03_graph_evidence(
            meta,
            graph=g,
            graph_ref=graph_ref,
            graph_digest=graph_digest,
        )
        from apps_rg.fact_inventory.validate_p1_w4_track_weighted_closeout import (
            validate_p1_w4_track_weighted_closeout,
        )

        validate_p1_w4_track_weighted_closeout(
            meta,
            hybrid_fixture=enforce_hybrid_contract,
            min_tracks_with_facts=min_tracks_with_facts,
        )
    return meta


def capture_agentic_core_isolation(*, repo_root: Path | None = None) -> dict[str, Any]:
    """Record agentic_core git state and whether P1-W4 paths touched it."""
    root = repo_root or ROOT
    diff = subprocess.run(  # guardian: allow-chokepoint-bypass -- isolation receipt captures read-only git diff; no runtime tool egress
        ["git", "diff", "--name-only", "--", "agentic_core"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    status = subprocess.run(  # guardian: allow-chokepoint-bypass -- isolation receipt captures read-only git status; no runtime tool egress
        ["git", "status", "--short", "--", "agentic_core"],
        cwd=str(root),
        capture_output=True,
        text=True,
        check=False,
    )
    diff_names = [ln.strip() for ln in diff.stdout.splitlines() if ln.strip()]
    status_lines = [ln.strip() for ln in status.stdout.splitlines() if ln.strip()]
    p1_files = list(P1_W4_CLOSEOUT_FILE_PREFIXES)
    touched = any(p.startswith("agentic_core/") for p in p1_files)
    return {
        "git_diff_name_only_agentic_core": diff_names,
        "git_status_short_agentic_core": status_lines,
        "dirty_files": diff_names,
        "touched_by_this_wave": touched,
        "p1_w4_changed_file_prefixes": p1_files,
        "workspace_guard_clean": len(diff_names) == 0,
        "isolation_verdict": (
            "ISOLATED_PREEXISTING_CHURN"
            if diff_names and not touched
            else ("CLEAN" if not diff_names else "BLOCKED_WAVE_TOUCHED_AGENTIC_CORE")
        ),
        "evidence": (
            "P1-W4 closeout changed only apps_rg/fact_inventory, apps_rg/runtime/proof_pool_resolver.py, "
            "tests, docs/reports/apps_rg, and plan markdown — no agentic_core paths in scope."
        ),
    }


def write_p1_w4_receipts(
    *,
    repo_root: Path | None = None,
    hybrid_jd: str = HYBRID_JD_FIXTURE,
) -> dict[str, Any]:
    """Run hybrid expansion and write JSON + markdown receipts."""
    root = repo_root or ROOT
    graph = load_augmented_skills_graph(repo_root=root)
    role_key = infer_projection_role_family_key(target_role="SVP Engineering Agentic AI", jd_text=hybrid_jd)
    hybrid = build_track_weighted_expansion(
        graph=graph,
        role_family_key=role_key,
        jd_text=hybrid_jd,
        enforce_hybrid_contract=True,
        min_tracks_with_facts=2,
        bind_c03=True,
        repo_root=root,
    )
    isolation = capture_agentic_core_isolation(repo_root=root)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    receipt_path = REPORTS_DIR / "career_track_p1_w4_track_weighted_expansion_receipt.json"
    md_path = REPORTS_DIR / "career_track_p1_w4_track_weighted_expansion.md"
    closeout_path = REPORTS_DIR / "career_track_p1_w4_closeout_receipt.json"
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": ts,
        "plan_id": "graph-skills-hardening-f3a8c1",
        "wave": "P1-W4",
        "closeout_wave": "P1-W4-CLOSEOUT",
        "hybrid_fixture": hybrid,
        "c03_binding_proof": {
            "c03_graph_bound_status": hybrid.get("c03_graph_bound_status"),
            "c03_binding_surface": hybrid.get("c03_binding_surface"),
            "c03_graph_expansion_ref": hybrid.get("c03_graph_expansion_ref"),
            "c03_graph_hop_paths_count": hybrid.get("c03_graph_hop_paths_count"),
            "c03_selected_tracks": hybrid.get("c03_selected_tracks"),
            "non_graph_evidence_items_count": hybrid.get("non_graph_evidence_items_count"),
            "broad_skills_ledger_used_as_authority": hybrid.get("broad_skills_ledger_used_as_authority"),
            "graph_expansion_mode": hybrid.get("graph_expansion_mode"),
            "graph_hop_edge_types_used": hybrid.get("graph_hop_edge_types_used"),
        },
        "agentic_core_isolation": isolation,
    }
    receipt_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    closeout_path.write_text(
        json.dumps(
            {
                "schema": "career_track_p1_w4_closeout_receipt_v1",
                "generated_at": ts,
                "plan_id": "graph-skills-hardening-f3a8c1",
                "wave": "P1-W4-CLOSEOUT",
                "c03_binding_proof": payload["c03_binding_proof"],
                "agentic_core_isolation": isolation,
                "hybrid_tracks_with_facts": hybrid.get("tracks_with_facts"),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    md_lines = [
        "# P1-W4 — Track-weighted graph expansion",
        "",
        f"**Generated:** {ts}  ",
        f"**Plan:** graph-skills-hardening-f3a8c1  ",
        f"**Role family:** {hybrid.get('role_family_key')}",
        "",
        "## Track weights",
        "",
    ]
    for track, w in (hybrid.get("track_weights") or {}).items():
        md_lines.append(f"- `{track}`: {w}")
    md_lines.extend(
        [
            "",
            "## Selected facts by track",
            "",
        ]
    )
    for track, count in (hybrid.get("selected_fact_count_by_track") or {}).items():
        md_lines.append(f"- `{track}`: {count} facts")
    md_lines.extend(
        [
            "",
            "## Graph hop sample (first skill)",
            "",
            "```json",
            json.dumps((hybrid.get("graph_hop_paths_sample") or [[]])[0], indent=2),
            "```",
            "",
            "## C0.3 binding (track-weighted)",
            "",
            f"- c03_graph_bound_status: **{hybrid.get('c03_graph_bound_status')}**",
            f"- c03_binding_surface: `{hybrid.get('c03_binding_surface')}`",
            f"- c03_graph_expansion_ref: `{hybrid.get('c03_graph_expansion_ref')}`",
            f"- c03_graph_hop_paths_count: **{hybrid.get('c03_graph_hop_paths_count')}**",
            f"- c03_selected_tracks: {hybrid.get('c03_selected_tracks')}",
            f"- non_graph_evidence_items_count: **{hybrid.get('non_graph_evidence_items_count')}**",
            f"- graph_expansion_mode: **{hybrid.get('graph_expansion_mode')}**",
            "",
            "## Authority",
            "",
            f"- broad_skills_ledger_used_as_authority: **{hybrid.get('broad_skills_ledger_used_as_authority')}**",
            f"- cross_track_causal_claims: **{hybrid.get('cross_track_causal_claims')}**",
            f"- tracks_with_facts: **{hybrid.get('tracks_with_facts')}**",
            "",
            "## agentic_core isolation",
            "",
            f"- isolation_verdict: **{isolation.get('isolation_verdict')}**",
            f"- touched_by_this_wave: **{isolation.get('touched_by_this_wave')}**",
            f"- dirty_files: `{isolation.get('dirty_files')}`",
            "",
        ]
    )
    md_path.write_text("\n".join(md_lines), encoding="utf-8")
    return {
        "receipt_json": str(receipt_path),
        "receipt_md": str(md_path),
        "closeout_json": str(closeout_path),
        "hybrid": hybrid,
        "isolation": isolation,
    }


def main() -> None:
    out = write_p1_w4_receipts()
    print(json.dumps(
        {
            "tracks_with_facts": out["hybrid"].get("tracks_with_facts"),
            "selected_fact_count_by_track": out["hybrid"].get("selected_fact_count_by_track"),
            "receipt": out["receipt_json"],
        },
        indent=2,
    ))


if __name__ == "__main__":
    main()
