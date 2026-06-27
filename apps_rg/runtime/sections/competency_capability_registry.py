"""Competency capability bundle registry — graph-backed bundles for the competencies section.

Loads ``competency_capability_bundles.json`` and exposes typed accessors plus guards.

Authority model (enforced by guards, not weakened):
- Graph skills + linked source facts = content/proof authority.
- Base resume competencies = calibration baseline only (never source prose).
- Archive resumes = candidate signal/provenance only (never hydration).
- JD/briefing = targeting only.
- Generic taxonomy labels = display wrappers only, never proof authority.

Config gate: competencies graph_expansion_allowed may be enabled only when section
generation consumes ``competency_bundle_id`` (graph_expansion_mode=competency_bundle_only),
not flat taxonomy labels or flat skill lists.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

BUNDLES_PATH: Path = (
    Path(__file__).resolve().parents[3]
    / "apps_rg"
    / "fact_inventory"
    / "competency_capability_bundles.json"
)

_BUNDLES_CACHE: dict[str, Any] | None = None

COMPETENCIES_SECTION_ID = "competencies"

# Required + optional capability families (SSOT mirror of data file).
REQUIRED_CAPABILITY_FAMILIES: tuple[str, ...] = (
    "agentic_platforms",
    "runtime_governance",
    "retrieval_context_engineering",
    "llmops_reliability",
    "distributed_systems_engineering",
    "platform_productization",
    "partner_applied_ai_architecture",
    "engineering_leadership",
)

OPTIONAL_CAPABILITY_FAMILIES: tuple[str, ...] = (
    "partnerships_ecosystem_execution",
    "insurance_domain_modernization",
    "data_governance_security",
    "cloud_hpc_modernization",
    "devsecops_delivery_governance",
)

REQUIRED_BUNDLE_FIELDS: frozenset[str] = frozenset({
    "competency_bundle_id",
    "capability_family",
    "display_label_candidate",
    "graph_skill_node_ids",
    "linked_source_fact_ids",
    "employer_bindings",
    "role_episode_bindings",
    "allowed_sections",
    "evidence_strength",
    "external_claim_policy",
    "activation_status",
    "base_rigor_family_match",
    "seniority_signal",
    "technical_density_signal",
    "commercial_or_operating_scope_signal",
    "target_relevance_rationale",
})

# Support classification for competency proof distinction.
SUPPORT_GRAPH_BACKED = "GRAPH_BACKED_BUNDLE"
SUPPORT_GENERIC_TAXONOMY = "GENERIC_TAXONOMY_LABEL"
SUPPORT_JD_ONLY = "JD_ONLY_PHRASE"
SUPPORT_ARCHIVE_OR_BASE_CALIBRATION = "ARCHIVE_OR_BASE_CALIBRATION_TEXT"
SUPPORT_FALLBACK_DEFAULT = "FALLBACK_DEFAULT_SUPPORT"

# Generic taxonomy wrapper labels that must NOT stand alone as proof.
GENERIC_TAXONOMY_LABELS: frozenset[str] = frozenset({
    "technology strategy & innovation",
    "technology strategy and innovation",
    "data & analytics modernization",
    "data and analytics modernization",
    "governance, risk & compliance",
    "governance, risk and compliance",
    "commercial & operating impact",
    "commercial and operating impact",
    "cloud & partner ecosystems",
    "cloud and partner ecosystems",
})


class CompetencyBundleError(ValueError):
    """Competency capability bundle contract violation."""


def _load_bundles(path: Path = BUNDLES_PATH) -> dict[str, Any]:
    global _BUNDLES_CACHE
    if _BUNDLES_CACHE is None:
        with open(path, encoding="utf-8") as fh:
            _BUNDLES_CACHE = json.load(fh)
    return _BUNDLES_CACHE


def get_all_bundles(path: Path = BUNDLES_PATH) -> list[dict[str, Any]]:
    return list(_load_bundles(path).get("bundles", []))


def get_bundle_by_id(bundle_id: str, path: Path = BUNDLES_PATH) -> dict[str, Any] | None:
    for b in get_all_bundles(path):
        if b.get("competency_bundle_id") == bundle_id:
            return b
    return None


def get_bundles_for_section(
    section_id: str = COMPETENCIES_SECTION_ID, path: Path = BUNDLES_PATH
) -> list[dict[str, Any]]:
    return [
        b for b in get_all_bundles(path)
        if section_id in (b.get("allowed_sections") or [])
    ]


def get_bundles_by_family(path: Path = BUNDLES_PATH) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for b in get_all_bundles(path):
        fam = str(b.get("capability_family") or "")
        out.setdefault(fam, []).append(b)
    return out


def required_family_bundles(path: Path = BUNDLES_PATH) -> dict[str, dict[str, Any]]:
    """Return one bundle per required family (first activated bundle per family)."""
    by_fam = get_bundles_by_family(path)
    out: dict[str, dict[str, Any]] = {}
    for fam in REQUIRED_CAPABILITY_FAMILIES:
        for b in by_fam.get(fam, []):
            if str(b.get("activation_status") or "") == "ACTIVE":
                out[fam] = b
                break
    return out


# ---------------------------------------------------------------------------
# Validation + guards
# ---------------------------------------------------------------------------


def validate_competency_bundle(bundle: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a competency capability bundle against required schema and invariants."""
    violations: list[str] = []

    missing = REQUIRED_BUNDLE_FIELDS - set(bundle.keys())
    if missing:
        violations.append(f"Missing required fields: {sorted(missing)}")

    fam = str(bundle.get("capability_family") or "")
    if fam not in REQUIRED_CAPABILITY_FAMILIES and fam not in OPTIONAL_CAPABILITY_FAMILIES:
        violations.append(f"Unknown capability_family: {fam!r}")

    if not bundle.get("graph_skill_node_ids"):
        violations.append("graph_skill_node_ids must not be empty (flat taxonomy-only bundle forbidden)")

    if COMPETENCIES_SECTION_ID not in (bundle.get("allowed_sections") or []):
        violations.append("allowed_sections must include 'competencies'")

    # External claim policy must declare skill projection is not proof on its own.
    ecp = str(bundle.get("external_claim_policy") or "")
    if not ecp:
        violations.append("external_claim_policy required")

    return len(violations) == 0, violations


def assert_competency_bundle_id_present(context: dict[str, Any]) -> None:
    """Raise if competency_bundle_id absent. Competencies may not consume graph context flat."""
    bid = context.get("competency_bundle_id")
    if not bid:
        raise CompetencyBundleError(
            "Competencies graph context requires competency_bundle_id. "
            "Consuming flat taxonomy labels or flat skill lists without bundle_id binding is forbidden. "
            "Config gate: competencies graph_expansion_allowed enabled only in "
            "graph_expansion_mode=competency_bundle_only."
        )


def reject_flat_taxonomy_only_bundle(context: dict[str, Any]) -> None:
    """Reject a 'bundle' that is only a generic taxonomy label with no graph skill node ids."""
    label = str(context.get("display_label_candidate") or context.get("category_label") or "").strip().lower()
    has_graph = bool(context.get("graph_skill_node_ids"))
    if not has_graph and label in GENERIC_TAXONOMY_LABELS:
        raise CompetencyBundleError(
            f"Flat taxonomy-only bundle rejected: '{label}' has no graph_skill_node_ids. "
            "Generic taxonomy labels are display wrappers only, not proof authority."
        )
    if not has_graph:
        raise CompetencyBundleError(
            "Bundle has no graph_skill_node_ids; flat skill/label-only support is not proof."
        )


def reject_default_fid_only_support(term: dict[str, Any]) -> None:
    """Reject a term whose only support is default_fid backfill."""
    if not isinstance(term, dict):
        return
    proof_source = str(term.get("proof_source") or "")
    skill_ids = term.get("graph_skill_node_ids") or term.get("source_skill_ids") or []
    if proof_source == "default_fid_backfill" and not skill_ids:
        raise CompetencyBundleError(
            "default_fid-only support rejected: a taxonomy term cannot pass solely because it "
            "is attached to default_fid. Require graph_skill_node_ids or graph lineage."
        )


def reject_jd_only_skill(term: dict[str, Any], *, jd_text: str) -> None:
    """Reject a term lifted from JD text with no graph/source support."""
    if not isinstance(term, dict):
        return
    phrase = str(term.get("term") or term.get("text") or "").strip().lower()
    skill_ids = term.get("graph_skill_node_ids") or term.get("source_skill_ids") or []
    fact_ids = term.get("source_fact_ids") or []
    jd_low = str(jd_text or "").lower()
    if phrase and phrase in jd_low and not skill_ids and not fact_ids:
        raise CompetencyBundleError(
            f"JD-only skill rejected: '{phrase}' appears in JD with no graph/source support. "
            "JD/briefing are targeting only, never proof."
        )


_PROSE_SENTENCE_RE = re.compile(r"[a-z],?\s+(?:and|with|to|for|by|that|which)\s+", re.IGNORECASE)


def _looks_like_prose(text: str) -> bool:
    s = str(text or "").strip()
    if not s:
        return False
    if s.endswith(".") and len(s.split()) > 8:
        return True
    if len(s.split()) > 9:
        return True
    if _PROSE_SENTENCE_RE.search(s) and len(s.split()) > 7:
        return True
    return False


def reject_archive_prose_hydration(text: str) -> None:
    """Reject archive resume prose being hydrated as a competency term/label."""
    if _looks_like_prose(text):
        raise CompetencyBundleError(
            f"Archive prose hydration rejected: '{str(text)[:80]}' looks like resume prose. "
            "Archive resumes are provenance only, never source text."
        )


def reject_base_resume_prose_hydration(text: str) -> None:
    """Reject base resume competency prose being hydrated as a competency term/label."""
    if _looks_like_prose(text):
        raise CompetencyBundleError(
            f"Base resume prose hydration rejected: '{str(text)[:80]}' looks like base resume prose. "
            "Base resume competencies are calibration baseline only, never source prose."
        )


def classify_support(
    term: dict[str, Any],
    *,
    jd_text: str = "",
    base_or_archive_blob_lower: str = "",
) -> str:
    """Distinguish graph-backed / generic taxonomy / JD-only / calibration / fallback support."""
    if not isinstance(term, dict):
        return SUPPORT_FALLBACK_DEFAULT
    skill_ids = term.get("graph_skill_node_ids") or term.get("source_skill_ids") or []
    bundle_id = term.get("competency_bundle_id")
    if skill_ids or bundle_id:
        return SUPPORT_GRAPH_BACKED
    proof_source = str(term.get("proof_source") or "")
    if proof_source == "default_fid_backfill":
        return SUPPORT_FALLBACK_DEFAULT
    phrase = str(term.get("term") or term.get("text") or "").strip().lower()
    if phrase and base_or_archive_blob_lower and phrase in base_or_archive_blob_lower:
        return SUPPORT_ARCHIVE_OR_BASE_CALIBRATION
    if phrase and jd_text and phrase in str(jd_text or "").lower():
        return SUPPORT_JD_ONLY
    if phrase in GENERIC_TAXONOMY_LABELS:
        return SUPPORT_GENERIC_TAXONOMY
    fact_ids = term.get("source_fact_ids") or []
    if fact_ids:
        return SUPPORT_GRAPH_BACKED
    return SUPPORT_FALLBACK_DEFAULT


__all__ = [
    "BUNDLES_PATH",
    "COMPETENCIES_SECTION_ID",
    "CompetencyBundleError",
    "GENERIC_TAXONOMY_LABELS",
    "OPTIONAL_CAPABILITY_FAMILIES",
    "REQUIRED_BUNDLE_FIELDS",
    "REQUIRED_CAPABILITY_FAMILIES",
    "SUPPORT_ARCHIVE_OR_BASE_CALIBRATION",
    "SUPPORT_FALLBACK_DEFAULT",
    "SUPPORT_GENERIC_TAXONOMY",
    "SUPPORT_GRAPH_BACKED",
    "SUPPORT_JD_ONLY",
    "assert_competency_bundle_id_present",
    "classify_support",
    "get_all_bundles",
    "get_bundle_by_id",
    "get_bundles_by_family",
    "get_bundles_for_section",
    "reject_archive_prose_hydration",
    "reject_base_resume_prose_hydration",
    "reject_default_fid_only_support",
    "reject_flat_taxonomy_only_bundle",
    "reject_jd_only_skill",
    "required_family_bundles",
    "validate_competency_bundle",
]
