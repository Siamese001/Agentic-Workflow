"""Packet Registry — central template store and builder dispatch.

All packet types MUST be registered here. Building a packet without
going through the registry is forbidden (prevents prompt scatter).

Each PacketTemplate defines:
    - Static blocks (system, policy, abstain, refine)
    - Must-use and optional evidence source types
    - Output schema skeleton
    - Token budget allocation
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenBudget:
    """Token allocation for a packet type."""

    total: int = 6000
    system_policy: int = 800
    task: int = 400
    must_use_evidence: int = 4000
    optional_evidence: int = 800
    contradiction_meta: int = 400

    def to_dict(self) -> dict[str, int]:
        return {
            "total": self.total,
            "system_policy": self.system_policy,
            "task": self.task,
            "must_use_evidence": self.must_use_evidence,
            "optional_evidence": self.optional_evidence,
            "contradiction_meta": self.contradiction_meta,
        }


@dataclass
class PacketTemplate:
    """Static template for a packet type."""

    packet_type: str
    system_block: str
    policy_block: str
    abstain_instructions: str
    refine_instructions: str
    output_schema: dict[str, Any]
    must_use_sources: list[str]
    optional_sources: list[str] = field(default_factory=list)
    token_budget: TokenBudget = field(default_factory=TokenBudget)


# ---------------------------------------------------------------------------
# Policy block shared across all ADG packets
# ---------------------------------------------------------------------------

_SHARED_POLICY = (
    "1. Canonical ADG artifacts (SQLite, JSON reports) are the source of truth.\n"
    "2. Graph DB outputs are augmenting evidence only — never override canonical truth.\n"
    "3. Contradictions between sources MUST be preserved and reported, never hidden.\n"
    "4. Weak evidence MUST be flagged; do not present weak support as strong.\n"
    "5. If evidence is insufficient, abstain or request scope refinement.\n"
    "6. All durable mutations terminate at the Universal Write Gateway (UWG).\n"
    "7. C0 retrieves only; prompt assembly packages only; L0 routes only; L2 executes only."
)

_SHARED_ABSTAIN = (
    "If the evidence is insufficient to answer the task with confidence, "
    "state explicitly what is missing and suggest a refinement query. "
    "Do not fabricate evidence or invent findings not grounded in the provided artifacts."
)

_SHARED_REFINE = (
    "If the evidence bundle has coverage_score < 0.3 or critical gaps, "
    "request: (a) regeneration of the ADG with --force, "
    "(b) a narrower scope (specific layer or file), or "
    "(c) additional artifact types to fill the gap."
)


# ---------------------------------------------------------------------------
# Packet templates — 8 families
# ---------------------------------------------------------------------------

TEMPLATES: dict[str, PacketTemplate] = {
    "determinism_rca": PacketTemplate(
        packet_type="determinism_rca",
        system_block=(
            "You are an ADG determinism analyst. Your role is to diagnose "
            "digest mismatches, node/edge reconciliation failures, and "
            "provenance probe errors from the latest ADG generation run."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "root_cause_hypotheses": {"type": "array", "items": {"type": "string"}},
                "affected_artifacts": {"type": "array", "items": {"type": "string"}},
                "mismatch_details": {"type": "object"},
                "next_diagnostic_steps": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
            },
        },
        must_use_sources=["provenance_report", "closure_report", "sqlite"],
        optional_sources=["graph_db"],
        token_budget=TokenBudget(
            total=8000,
            system_policy=500,
            task=500,
            must_use_evidence=5000,
            optional_evidence=1200,
            contradiction_meta=800,
        ),
    ),
    "p0_failure": PacketTemplate(
        packet_type="p0_failure",
        system_block=(
            "You are an ADG P0 failure analyst. Your role is to diagnose "
            "hard-fail violations (layer violations, circular imports, "
            "dynamic_exec) and identify the minimal repair path."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "rule_id": {"type": "string"},
                "violation_class": {"type": "string"},
                "stage": {"type": "string", "enum": ["preflight", "full"]},
                "offending_files": {"type": "array", "items": {"type": "string"}},
                "offending_path": {"type": "string"},
                "first_illegal_hop": {"type": "string"},
                "candidate_repair_mode": {"type": "string"},
                "safe_next_step": {"type": "string"},
            },
        },
        must_use_sources=["sqlite", "closure_report", "sc_ap_config"],
        optional_sources=["graph_db"],
        token_budget=TokenBudget(
            total=6000,
            system_policy=400,
            task=400,
            must_use_evidence=4000,
            optional_evidence=800,
            contradiction_meta=400,
        ),
    ),
    "ratchet_review": PacketTemplate(
        packet_type="ratchet_review",
        system_block=(
            "You are an ADG ratchet reviewer. Your role is to analyze "
            "P1/P2 anti-pattern counts against baseline ceilings and "
            "recommend fix ordering by structural risk."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "gross_count": {"type": "integer"},
                "net_delta": {"type": "integer"},
                "new_violations": {"type": "integer"},
                "resolved_violations": {"type": "integer"},
                "affected_layers": {"type": "array", "items": {"type": "string"}},
                "critical_path_count": {"type": "integer"},
                "exemptions": {"type": "integer"},
                "recommended_fix_ordering": {"type": "array", "items": {"type": "string"}},
            },
        },
        must_use_sources=["ratchet", "burndown", "sqlite"],
        optional_sources=["structural"],
        token_budget=TokenBudget(
            total=6000,
            system_policy=400,
            task=400,
            must_use_evidence=4000,
            optional_evidence=800,
            contradiction_meta=400,
        ),
    ),
    "unknown_unresolved_triage": PacketTemplate(
        packet_type="unknown_unresolved_triage",
        system_block=(
            "You are an ADG module triage analyst. Your role is to classify "
            "unknown modules and unresolved imports as taxonomy lag vs real "
            "structural gaps, and recommend remediation."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "unknown_modules": {"type": "array", "items": {"type": "object"}},
                "unresolved_imports": {"type": "array", "items": {"type": "object"}},
                "taxonomy_lag_candidates": {"type": "array", "items": {"type": "string"}},
                "real_structural_gaps": {"type": "array", "items": {"type": "string"}},
                "package_concentration": {"type": "object"},
            },
        },
        must_use_sources=["layer_coverage_report", "sqlite"],
        optional_sources=["graph_db"],
        token_budget=TokenBudget(
            total=6000,
            system_policy=400,
            task=400,
            must_use_evidence=4000,
            optional_evidence=800,
            contradiction_meta=400,
        ),
    ),
    "hotspot_investigation": PacketTemplate(
        packet_type="hotspot_investigation",
        system_block=(
            "You are an ADG hotspot analyst. Your role is to identify "
            "high fan-in/fan-out nodes, high-violation files, and "
            "connected risk surfaces for prioritized remediation."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "top_fan_in": {"type": "array", "items": {"type": "object"}},
                "top_fan_out": {"type": "array", "items": {"type": "object"}},
                "top_violation_files": {"type": "array", "items": {"type": "object"}},
                "connected_risk_surfaces": {"type": "array", "items": {"type": "string"}},
                "root_cause_neighborhoods": {"type": "array", "items": {"type": "object"}},
            },
        },
        must_use_sources=["sqlite", "structural"],
        optional_sources=["graph_db"],
        token_budget=TokenBudget(
            total=8000,
            system_policy=500,
            task=500,
            must_use_evidence=5000,
            optional_evidence=1200,
            contradiction_meta=800,
        ),
    ),
    "infrastructure_boundary": PacketTemplate(
        packet_type="infrastructure_boundary",
        system_block=(
            "You are an ADG infrastructure boundary analyst. Your role is to "
            "identify raw infra spread, write-path bypass risks, and "
            "provider/tool/network choke-point failures."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "raw_infra_spread": {"type": "array", "items": {"type": "object"}},
                "write_path_bypass_risks": {"type": "array", "items": {"type": "object"}},
                "choke_point_failures": {"type": "array", "items": {"type": "object"}},
                "approved_surfaces": {"type": "array", "items": {"type": "string"}},
                "miswired_surfaces": {"type": "array", "items": {"type": "string"}},
            },
        },
        must_use_sources=["infra_view", "sqlite"],
        optional_sources=["graph_db"],
        token_budget=TokenBudget(
            total=6000,
            system_policy=400,
            task=400,
            must_use_evidence=4000,
            optional_evidence=800,
            contradiction_meta=400,
        ),
    ),
    "graph_path_explanation": PacketTemplate(
        packet_type="graph_path_explanation",
        system_block=(
            "You are an ADG graph path analyst. Your role is to explain "
            "exact violating paths, first illegal hops, missing choke points, "
            "and blast-radius neighbors."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "violating_path": {"type": "array", "items": {"type": "string"}},
                "first_illegal_hop": {"type": "object"},
                "missing_choke_point": {"type": "string"},
                "blast_radius_neighbors": {"type": "array", "items": {"type": "string"}},
                "cross_snapshot_diff": {"type": "object"},
            },
        },
        must_use_sources=["sqlite"],
        optional_sources=["graph_db", "structural"],
        token_budget=TokenBudget(
            total=6000,
            system_policy=400,
            task=400,
            must_use_evidence=4000,
            optional_evidence=800,
            contradiction_meta=400,
        ),
    ),
    "executive_summary": PacketTemplate(
        packet_type="executive_summary",
        system_block=(
            "You are an ADG executive reviewer. Your role is to produce "
            "a concise one-run summary covering top blockers, likely false "
            "positives, taxonomy mismatches, and recommended next wave."
        ),
        policy_block=_SHARED_POLICY,
        abstain_instructions=_SHARED_ABSTAIN,
        refine_instructions=_SHARED_REFINE,
        output_schema={
            "type": "object",
            "properties": {
                "run_summary": {"type": "string"},
                "top_blockers": {"type": "array", "items": {"type": "string"}},
                "likely_false_positives": {"type": "array", "items": {"type": "string"}},
                "taxonomy_mismatches": {"type": "array", "items": {"type": "string"}},
                "recommended_next_wave": {"type": "string"},
                "uncertainty_disclosure": {"type": "string"},
            },
        },
        must_use_sources=["snapshot", "burndown", "closure_report", "ratchet"],
        optional_sources=["structural", "graph_db"],
        token_budget=TokenBudget(
            total=4000,
            system_policy=400,
            task=300,
            must_use_evidence=2500,
            optional_evidence=500,
            contradiction_meta=300,
        ),
    ),
}


# ---------------------------------------------------------------------------
# Registry API
# ---------------------------------------------------------------------------

VALID_PACKET_TYPES = frozenset(TEMPLATES.keys())


def get_template(packet_type: str) -> PacketTemplate:
    """Get a packet template by type. Raises ValueError if unknown."""
    if packet_type not in TEMPLATES:
        raise ValueError(f"Unknown packet type: {packet_type!r}. Valid types: {sorted(VALID_PACKET_TYPES)}")
    return TEMPLATES[packet_type]


def list_packet_types() -> list[str]:
    """Return sorted list of all registered packet types."""
    return sorted(VALID_PACKET_TYPES)
