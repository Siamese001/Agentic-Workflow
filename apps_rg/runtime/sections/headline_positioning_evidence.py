"""Headline positioning evidence — C0 consumption + proof-pool attach for the headline lane.

Proof authority is graph positioning bundles plus linked source facts, not flat skill
lists. Base headline is calibration only; competency bundles are positioning source;
JD/briefing are targeting only; E0 examples are style only.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import load_augmented_skills_graph
from apps_rg.runtime.sections.headline_positioning_registry import (
    HEADLINE_SECTION_ID,
    REQUIRED_POSITIONING_FAMILIES,
    get_bundles_for_section,
    validate_bundle,
)

HEADLINE_POSITIONING_EVIDENCE_PACK_MARKER = "HEADLINE_POSITIONING_EVIDENCE_PACK"

# Seniority/specificity floors surfaced into C0 for organic generation.
HEADLINE_SENIORITY_FLOOR = "SVP Engineering"
HEADLINE_TECHNICAL_SPECIFICITY_FLOOR = 2  # >=2 positioning families in X/Y/Z

_AUTHORITY_HEADER_LINES: tuple[str, ...] = (
    "proof_authority = graph_positioning_bundles_plus_linked_source_facts",
    "base_headline_usage = calibration_only",
    "competency_bundle_usage = positioning_source",
    "jd_usage = targeting_only",
    "examples_usage = style_only",
    "flat_skill_list_graph_context = forbidden",
    (
        "Generate the headline organically from positioning bundles. "
        "Do not copy base headline, E0 examples, or JD phrases."
    ),
)

_FORBIDDEN_C0_SUBSTRINGS: tuple[str, ...] = (
    "Lakehouse Microservices Architecture",
    "AI Lifecycle Standardization",
    "SVP IT Strategy",
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _skill_rows_by_id(repo_root: Path | None = None) -> dict[str, dict[str, Any]]:
    graph = load_augmented_skills_graph(repo_root=repo_root or _repo_root())
    out: dict[str, dict[str, Any]] = {}
    for row in graph.get("skill_rows") or []:
        if isinstance(row, dict):
            sid = str(row.get("skill_id") or "").strip()
            if sid:
                out[sid] = row
    return out


def build_headline_positioning_section_packet(
    section_id: str = HEADLINE_SECTION_ID,
    *,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Build machine-readable positioning packet for the headline (proof_pool metadata)."""
    bundles = get_bundles_for_section(section_id)
    skill_index = _skill_rows_by_id(repo_root)
    records: list[dict[str, Any]] = []
    all_skill_ids: list[str] = []
    all_fact_ids: list[str] = []
    all_competency_bundle_ids: list[str] = []
    for bundle in bundles:
        ok, violations = validate_bundle(bundle)
        if not ok:
            raise ValueError(
                f"Invalid headline positioning bundle "
                f"{bundle.get('headline_positioning_bundle_id')}: {violations}"
            )
        skill_nodes: list[dict[str, Any]] = []
        for sid in bundle.get("graph_skill_node_ids") or []:
            row = skill_index.get(str(sid))
            if row:
                skill_nodes.append(
                    {
                        "skill_id": sid,
                        "allowed_phrases": list(row.get("allowed_phrases") or [])[:6],
                        "activation_status": row.get("activation_status"),
                    }
                )
            all_skill_ids.append(str(sid))
        all_fact_ids.extend(str(f) for f in (bundle.get("linked_source_fact_ids") or []))
        all_competency_bundle_ids.extend(
            str(c) for c in (bundle.get("source_competency_bundle_ids") or [])
        )
        records.append(
            {
                "headline_positioning_bundle_id": bundle["headline_positioning_bundle_id"],
                "positioning_family": bundle["positioning_family"],
                "display_phrase_candidate": bundle["display_phrase_candidate"],
                "source_competency_bundle_ids": list(bundle.get("source_competency_bundle_ids") or []),
                "graph_skill_node_ids": list(bundle.get("graph_skill_node_ids") or []),
                "linked_source_fact_ids": list(bundle.get("linked_source_fact_ids") or []),
                "graph_lineage_refs": list(bundle.get("graph_lineage_refs") or []),
                "seniority_signal": bundle.get("seniority_signal"),
                "technical_specificity_signal": bundle.get("technical_specificity_signal"),
                "platform_signal": bundle.get("platform_signal"),
                "governance_signal": bundle.get("governance_signal"),
                "target_relevance_rationale": bundle.get("target_relevance_rationale"),
                "external_claim_policy": bundle.get("external_claim_policy"),
                "bound_skills": skill_nodes,
            }
        )
    return {
        "section_id": section_id,
        "proof_authority": "graph_positioning_bundles_plus_linked_source_facts",
        "base_headline_usage": "calibration_only",
        "competency_bundle_usage": "positioning_source",
        "jd_usage": "targeting_only",
        "examples_usage": "style_only",
        "headline_positioning_bundles": records,
        "headline_positioning_bundle_ids": [r["headline_positioning_bundle_id"] for r in records],
        "competency_bundle_ids": sorted(set(all_competency_bundle_ids)),
        "graph_skill_node_ids": sorted(set(all_skill_ids)),
        "source_fact_ids": sorted(set(all_fact_ids)),
        "seniority_floor": HEADLINE_SENIORITY_FLOOR,
        "technical_specificity_floor": HEADLINE_TECHNICAL_SPECIFICITY_FLOOR,
        "required_positioning_families": list(REQUIRED_POSITIONING_FAMILIES),
        "consumption_mode": "headline_positioning_bundle_required",
        "flat_skill_only_forbidden": True,
    }


def attach_headline_positioning_bundles_to_proof_pool_metadata(
    meta: dict[str, Any],
    *,
    section_id: str = HEADLINE_SECTION_ID,
    repo_root: Path | None = None,
) -> dict[str, Any]:
    """Merge positioning packet into proof_pool_metadata (headline only)."""
    if section_id != HEADLINE_SECTION_ID:
        return meta
    packet = build_headline_positioning_section_packet(section_id, repo_root=repo_root)
    out = dict(meta)
    out["headline_positioning_bundle_consumption"] = True
    out["headline_positioning_bundle_consumption_mode"] = "headline_positioning_bundle_required"
    out["headline_positioning_bundles"] = packet["headline_positioning_bundles"]
    out["headline_positioning_bundle_ids"] = packet["headline_positioning_bundle_ids"]
    out["headline_positioning_section_packet"] = packet
    out["graph_expansion_consumes_headline_positioning_bundles"] = True
    out["flat_skill_only_graph_context_forbidden"] = True
    return out


def assert_headline_positioning_evidence_pack_has_no_forbidden_leaks(pack_text: str) -> None:
    blob = str(pack_text or "")
    hits = [s for s in _FORBIDDEN_C0_SUBSTRINGS if s in blob]
    if hits:
        raise ValueError(
            f"Headline positioning evidence pack contains forbidden demotion leakage: {hits}"
        )


def format_headline_positioning_evidence_pack(
    runtime_payload: dict[str, Any],
    *,
    section_id: str = HEADLINE_SECTION_ID,
) -> str:
    """C0 body: headline positioning bundles as proof authority."""
    packet = build_headline_positioning_section_packet(section_id)
    runtime_payload["headline_positioning_section_packet"] = packet
    runtime_payload["headline_positioning_bundle_ids"] = packet["headline_positioning_bundle_ids"]

    jd = str(runtime_payload.get("jd_text") or "").strip()

    header_lines = [
        f"{HEADLINE_POSITIONING_EVIDENCE_PACK_MARKER} "
        "(proof substrate — compose SVP Engineering | X | Y | Z from positioning bundles):",
        *_AUTHORITY_HEADER_LINES,
        f"- seniority_floor: {packet['seniority_floor']} (segment 0 must be exactly this).",
        f"- technical_specificity_floor: >= {packet['technical_specificity_floor']} positioning families across X/Y/Z.",
        "- governance_floor: at least one of X/Y/Z MUST carry a governance or regulated-AI signal "
        "(vocabulary: governance, governed, runtime, gates, policy, deterministic, regulated, "
        "regulatory, compliance) drawn from a bundle with governance_signal: true.",
        "- narrowing_guard: avoid generic IT-strategy, modernization, transformation, "
        "innovation-leadership, lifecycle-standardization, vendor/partner-ecosystem, and "
        "contract-value style program labels in X/Y/Z — even when such phrases appear in the "
        "evidence, they demote the posture. Position every segment as senior platform/engineering "
        "leadership using the positioning-family vocabulary above.",
        "- Each positioning theme MUST bind to a headline_positioning_bundle_id with graph_skill_node_ids.",
        "- skill_id alone is not proof; linked_source_fact_ids or graph_lineage_refs bind positioning.",
    ]
    if jd:
        header_lines.append(
            "- JD/briefing select which fact-supported positioning families to foreground (targeting only)."
        )

    blocks: list[str] = []
    for rec in packet["headline_positioning_bundles"]:
        lines = [
            f"POSITIONING_BUNDLE {rec['headline_positioning_bundle_id']} "
            f"({rec['positioning_family']}):",
            f"  display_phrase_candidate: {rec['display_phrase_candidate']}",
            f"  source_competency_bundle_ids: {rec['source_competency_bundle_ids']}",
            f"  graph_skill_node_ids: {rec['graph_skill_node_ids']}",
            f"  linked_source_fact_ids: {rec['linked_source_fact_ids']}",
            f"  graph_lineage_refs: {rec['graph_lineage_refs']}",
            f"  seniority_signal: {rec['seniority_signal']} | platform_signal: {rec['platform_signal']} "
            f"| governance_signal: {rec['governance_signal']}",
            "  bound_skills (graph authority — vocabulary anchors only, not proof on their own):",
        ]
        _bound = list(rec.get("bound_skills") or [])
        if not _bound:
            lines.append("    - (none materialized)")
        for s in _bound:
            if not isinstance(s, dict):
                continue
            sid = s.get("skill_id")
            phrases = ", ".join(list(s.get("allowed_phrases") or [])[:5])
            if phrases:
                lines.append(f"    - {sid} | allowed_phrases: {phrases}")
            else:
                lines.append(f"    - {sid}")
        lines.append(f"  target_relevance_rationale: {rec['target_relevance_rationale']}")
        blocks.append("\n".join(lines))

    out = "\n".join(header_lines) + "\n\n" + "\n\n".join(blocks)
    assert_headline_positioning_evidence_pack_has_no_forbidden_leaks(out)
    return out


def is_flat_skill_only_packet(packet: dict[str, Any]) -> bool:
    from apps_rg.runtime.sections.cross_section_signal_guards import (
        is_flat_skill_only_graph_packet,
    )

    if isinstance(packet, dict) and packet.get("headline_positioning_section_packet"):
        return False
    return is_flat_skill_only_graph_packet(packet)


__all__ = [
    "HEADLINE_POSITIONING_EVIDENCE_PACK_MARKER",
    "HEADLINE_SENIORITY_FLOOR",
    "HEADLINE_TECHNICAL_SPECIFICITY_FLOOR",
    "assert_headline_positioning_evidence_pack_has_no_forbidden_leaks",
    "attach_headline_positioning_bundles_to_proof_pool_metadata",
    "build_headline_positioning_section_packet",
    "format_headline_positioning_evidence_pack",
    "is_flat_skill_only_packet",
]
