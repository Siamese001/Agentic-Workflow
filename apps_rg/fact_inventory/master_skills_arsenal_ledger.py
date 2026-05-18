"""Master skills arsenal ledger — skills layer beside atomic facts (apps_rg only)."""
from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any

REPO_REL = Path("apps_rg") / "fact_inventory" / "master_skills_arsenal_ledger.json"

REQUIRED_TOP_LEVEL: tuple[str, ...] = (
    "metadata",
    "support_levels",
    "visibility_rules",
    "activation_statuses",
    "pillars",
    "skill_rows",
    "actuarial_career_matrix",
    "partner_gtm_matrix",
    "role_family_projection_profiles",
    "validation_rules",
)

W4A_TOP_LEVEL: tuple[str, ...] = (
    "graph_metadata",
    "graph_layers",
    "graph_nodes",
    "graph_edges",
    "external_claim_policies",
    "agentic_runtime_matrix",
    "agentic_capability_domains",
    "graph_validation_rules",
    "resume_generation_policy",
)

NON_EXTERNAL_CLAIM_POLICIES = frozenset(
    {
        "internal_only",
        "pending_source_internal_only",
        "weak_snippet_internal_only",
        "repo_portfolio_not_resume_default",
    }
)

NON_EXTERNAL_SUPPORT_LEVELS = frozenset(
    {"INTERNAL_ONLY", "REPO_EVIDENCE_PORTFOLIO", "TARGETING_ONLY", "STYLE_ONLY", "BLOCKED"}
)

REQUIRED_SKILL_ROW_FIELDS: tuple[str, ...] = (
    "skill_id",
    "fact_id_links",
    "pillar",
    "subpillar",
    "career_stage",
    "source_resume_files",
    "source_snippets",
    "user_confirmed",
    "support_level",
    "role_family_weights",
    "allowed_phrases",
    "forbidden_phrases",
    "allowed_sections",
    "visibility_rule",
    "evidence_risk",
    "activation_status",
    "human_confirmation_required",
)

PROOF_FORBIDDEN_SUPPORT_LEVELS = frozenset(
    {"TARGETING_ONLY", "STYLE_ONLY", "BLOCKED", "USER_CONFIRMED_PENDING_SOURCE"}
)

JD_BRIEFING_FORBIDDEN_FACT_ID_PREFIXES = frozenset(
    {"jd", "briefing", "job_description", "targeting_jd", "targeting_briefing"}
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_arsenal_ledger_path(repo_root: Path | None = None) -> Path:
    return (repo_root or _repo_root()) / REPO_REL


def load_master_skills_arsenal_ledger(
    *,
    repo_root: Path | None = None,
    path: Path | None = None,
) -> dict[str, Any]:
    ledger_path = path or default_arsenal_ledger_path(repo_root)
    payload = json.loads(ledger_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise TypeError("arsenal ledger must be object")
    validate_arsenal_ledger_shape(payload)
    return payload


def arsenal_skill_ids(ledger: dict[str, Any]) -> list[str]:
    rows = ledger.get("skill_rows") or []
    return [str(r["skill_id"]) for r in rows if isinstance(r, dict) and r.get("skill_id")]


def validate_skill_row_shape(row: dict[str, Any]) -> None:
    for field in REQUIRED_SKILL_ROW_FIELDS:
        if field not in row:
            raise ValueError(f"skill_row missing {field}")
    if not isinstance(row["fact_id_links"], list):
        raise TypeError("fact_id_links must be list")
    if not isinstance(row["allowed_phrases"], list):
        raise TypeError("allowed_phrases must be list")
    if not isinstance(row["forbidden_phrases"], list):
        raise TypeError("forbidden_phrases must be list")


def _phrase_overlap(allowed: list[str], forbidden: list[str]) -> list[str]:
    overlaps: list[str] = []
    for a in allowed:
        al = a.lower()
        for f in forbidden:
            fl = f.lower()
            if fl in al or al in fl:
                overlaps.append(a)
                break
    return overlaps


def _is_jd_briefing_fact_id(fact_id: str) -> bool:
    low = fact_id.lower()
    return any(low.startswith(p) or p in low for p in JD_BRIEFING_FORBIDDEN_FACT_ID_PREFIXES)


def skill_row_eligible_for_external_claim(row: dict[str, Any]) -> bool:
    """Whether a skill row may anchor external resume claims (not internal ranking only)."""
    support = str(row.get("support_level") or "")
    policy = str(row.get("external_claim_policy") or "")
    if support in NON_EXTERNAL_SUPPORT_LEVELS:
        return False
    if policy in NON_EXTERNAL_CLAIM_POLICIES:
        return False
    if support == "BLOCKED":
        return False
    if support in ("TARGETING_ONLY", "STYLE_ONLY"):
        return False
    if support == "USER_CONFIRMED_PENDING_SOURCE":
        if row.get("human_confirmation_required", True):
            return False
        if str(row.get("activation_status")) != "ACTIVE_CONFIRMED":
            return False
    if support == "DERIVED_SUPPORTED" and not (row.get("fact_id_links") or []):
        return False
    if support == "REPO_EVIDENCE_PORTFOLIO":
        return False
    snippets = row.get("source_snippets") or []
    facts = row.get("fact_id_links") or []
    if not snippets and not facts:
        return False
    if snippets and all(len(str(s).strip()) < 24 for s in snippets):
        return False
    for fid in facts:
        if _is_jd_briefing_fact_id(str(fid)):
            return False
        if _is_skill_id(str(fid)):
            return False
    if _phrase_overlap(list(row.get("allowed_phrases") or []), list(row.get("forbidden_phrases") or [])):
        return False
    return True


def _is_skill_id(value: str) -> bool:
    return value.startswith("skill_")


def skill_row_eligible_for_internal_ranking(row: dict[str, Any]) -> bool:
    if str(row.get("support_level")) == "BLOCKED":
        return False
    return True


def validate_skill_row_for_external_output(row: dict[str, Any]) -> list[str]:
    """Return violation messages; empty list means eligible for external claim use."""
    violations: list[str] = []
    validate_skill_row_shape(row)
    support = str(row.get("support_level") or "")
    if support == "BLOCKED":
        violations.append("BLOCKED cannot be selected for external output")
    if support in ("TARGETING_ONLY", "STYLE_ONLY"):
        violations.append(f"{support} cannot be used as proof")
    if support == "USER_CONFIRMED_PENDING_SOURCE":
        if row.get("human_confirmation_required", True):
            violations.append("USER_CONFIRMED_PENDING_SOURCE requires human confirmation")
        elif str(row.get("activation_status")) != "ACTIVE_CONFIRMED":
            violations.append("USER_CONFIRMED_PENDING_SOURCE requires ACTIVE_CONFIRMED")
    if support == "DERIVED_SUPPORTED" and not (row.get("fact_id_links") or []):
        violations.append("DERIVED_SUPPORTED requires fact_id_links")
    snippets = row.get("source_snippets") or []
    facts = row.get("fact_id_links") or []
    if not snippets and not facts:
        violations.append("external claim requires source_snippets or fact_id_links")
    for fid in facts:
        if _is_jd_briefing_fact_id(str(fid)):
            violations.append(f"JD/briefing cannot appear as fact_id_links: {fid}")
    overlaps = _phrase_overlap(
        list(row.get("allowed_phrases") or []),
        list(row.get("forbidden_phrases") or []),
    )
    if overlaps:
        violations.append(f"allowed_phrases overlap forbidden: {overlaps[:3]}")
    return violations


def validate_w4a_graph_shape(ledger: dict[str, Any]) -> None:
    if not ledger.get("metadata", {}).get("w4a_hardened"):
        return
    for key in W4A_TOP_LEVEL:
        if key not in ledger:
            raise ValueError(f"W4A arsenal ledger missing top-level key: {key}")
    nodes = ledger.get("graph_nodes") or []
    edges = ledger.get("graph_edges") or []
    if not isinstance(nodes, list) or not nodes:
        raise ValueError("graph_nodes must be non-empty list when w4a_hardened")
    if not isinstance(edges, list) or not edges:
        raise ValueError("graph_edges must be non-empty list when w4a_hardened")
    for node in nodes:
        for field in (
            "node_id",
            "node_type",
            "label",
            "description",
            "support_level",
            "visibility_rule",
            "activation_status",
            "evidence_risk",
            "source_refs",
            "projection_behavior",
            "external_claim_policy",
        ):
            if field not in node:
                raise ValueError(f"graph node {node.get('node_id')} missing {field}")
    for edge in edges:
        for field in (
            "edge_id",
            "edge_type",
            "source_node_id",
            "target_node_id",
            "rationale",
            "projection_behavior",
            "external_claim_policy",
            "validation_status",
        ):
            if field not in edge:
                raise ValueError(f"graph edge {edge.get('edge_id')} missing {field}")


def validate_arsenal_ledger_shape(ledger: dict[str, Any]) -> None:
    for key in REQUIRED_TOP_LEVEL:
        if key not in ledger:
            raise ValueError(f"arsenal ledger missing top-level key: {key}")
    validate_w4a_graph_shape(ledger)
    rows = ledger.get("skill_rows")
    if not isinstance(rows, list):
        raise TypeError("skill_rows must be list")
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise TypeError("skill_row must be dict")
        validate_skill_row_shape(row)
        sid = str(row["skill_id"])
        if sid in seen:
            raise ValueError(f"duplicate skill_id: {sid}")
        seen.add(sid)
        support_levels = ledger.get("support_levels") or []
        if row["support_level"] not in support_levels:
            raise ValueError(f"unknown support_level on {sid}: {row['support_level']}")
        act = str(row.get("activation_status"))
        if act not in (ledger.get("activation_statuses") or []):
            raise ValueError(f"unknown activation_status on {sid}: {act}")


def assert_no_jd_briefing_as_proof_fact_ids(fact_ids: Iterable[str]) -> None:
    for fid in fact_ids:
        if _is_jd_briefing_fact_id(str(fid)):
            raise ValueError(f"JD/briefing cannot be proof fact id: {fid}")

