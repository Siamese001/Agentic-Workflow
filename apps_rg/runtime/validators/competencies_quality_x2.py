"""Competencies authority X2 gate helpers (Headline/Competencies/Narrative Rigor plan).

Implements deterministic proxy gates enforcing graph-backed competencies proof:
- x2_competencies_capability_family_coverage: ≥5 of 7 capability families present
- x2_competencies_no_default_fid_proof: default_fid backfill cannot be the sole support
- x2_competencies_generic_category_blocked_without_graph: generic categories need graph terms
- x2_competencies_e0_ngram_overlap: anti-leakage gate for E0 example text
- x2_competencies_base_ngram_overlap: anti-hydration gate for base resume competencies

These gates catch competencies output that relies on laundered proof via default_fid
backfill or contains only generic taxonomy categories without graph-skill grounding.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
    compute_max_ngram_overlap_multi_reference,
)

# ---------------------------------------------------------------------------
# Capability families required for SVP Engineering posture
# ---------------------------------------------------------------------------

REQUIRED_CAPABILITY_FAMILIES: dict[str, frozenset[str]] = {
    "agentic_platform": frozenset({
        "agentic", "llm", "agent", "orchestration", "rag", "graphrag",
        "multi-agent", "multiagent", "langgraph", "langchain",
    }),
    "runtime_governance": frozenset({
        "governance", "runtime", "gate", "gates", "policy", "sandbox",
        "deterministic", "guardrail", "guardrails",
    }),
    "retrieval_context": frozenset({
        "retrieval", "context", "vector", "embedding", "search",
        "rag", "indexing", "chunking",
    }),
    "llmops": frozenset({
        "evaluation", "eval", "reliability", "llmops", "telemetry",
        "monitoring", "observability", "tracing",
    }),
    "distributed_infra": frozenset({
        "distributed", "cloud", "microservices", "databricks", "lakehouse",
        "kubernetes", "k8s", "spark", "streaming",
    }),
    "productization": frozenset({
        "productization", "commercialization", "saas", "roadmap",
        "alliance", "go-to-market", "gtm", "pricing",
    }),
    "engineering_leadership": frozenset({
        "engineering", "leadership", "organization", "operating", "model",
        "talent", "hiring", "recruiting", "team", "staff",
    }),
}

CAPABILITY_BUNDLE_FAMILY_TO_GATE_FAMILY: dict[str, str] = {
    "agentic_platforms": "agentic_platform",
    "runtime_governance": "runtime_governance",
    "retrieval_context_engineering": "retrieval_context",
    "llmops_reliability": "llmops",
    "distributed_systems_engineering": "distributed_infra",
    "platform_productization": "productization",
    "engineering_leadership": "engineering_leadership",
}

# ---------------------------------------------------------------------------
# Generic category labels that MUST be backed by graph-derived terms
# ---------------------------------------------------------------------------

GENERIC_CATEGORIES_REQUIRING_GRAPH: frozenset[str] = frozenset({
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

# Minimum number of graph-backed terms a generic category must have
GENERIC_CATEGORY_MIN_GRAPH_TERMS = 3

# n-gram gate thresholds
BASE_NGRAM_THRESHOLD = 0.25
E0_NGRAM_THRESHOLD = 0.20
NGRAM_SIZE = 4

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class CompQualityResult:
    gate_id: str
    passed: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None
    signals: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-z0-9-]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _term_tokens(term_obj: Any) -> set[str]:
    """Extract lowercase tokens from a term dict or string."""
    if isinstance(term_obj, dict):
        phrase = str(term_obj.get("term") or term_obj.get("text") or "")
    else:
        phrase = str(term_obj or "")
    return set(_tokenize(phrase))


def _category_label(cat: Any) -> str:
    if isinstance(cat, dict):
        return str(cat.get("category_label") or cat.get("label") or "").lower().strip()
    return ""


def _category_terms(cat: Any) -> list[Any]:
    if isinstance(cat, dict):
        return cat.get("terms") or []
    return []


def _is_graph_backed(term: Any) -> bool:
    """Term is graph-backed when it carries explicit skill or fact support."""
    if not isinstance(term, dict):
        return False
    if term.get("proof_source") == "default_fid_backfill":
        return False
    skill_ids = term.get("graph_skill_node_ids") or term.get("source_skill_ids") or []
    if skill_ids:
        return True
    fact_ids = term.get("source_fact_ids") or []
    return bool(fact_ids)


def _cat_graph_skill_ids(cat: Any) -> list[str]:
    if not isinstance(cat, dict):
        return []
    raw = cat.get("graph_skill_node_ids") or cat.get("source_skill_ids") or []
    if isinstance(raw, str):
        raw = [raw]
    return [str(item).strip() for item in raw if str(item).strip()]


def _term_support_ids(term: Any) -> list[str]:
    if not isinstance(term, dict):
        return []
    raw = (
        term.get("graph_skill_node_ids")
        or term.get("source_skill_ids")
        or term.get("source_fact_ids")
        or []
    )
    if isinstance(raw, str):
        raw = [raw]
    return [str(item).strip() for item in raw if str(item).strip()]


# ---------------------------------------------------------------------------
# Gate: capability family coverage
# ---------------------------------------------------------------------------


def check_competencies_capability_family_coverage(
    competencies: list[Any],
    min_families: int = 5,
) -> CompQualityResult:
    """Require ≥min_families capability families, preferring bundle metadata over token proxies."""
    all_tokens: set[str] = set()
    bundle_matched_families: set[str] = set()
    for cat in (competencies or []):
        if isinstance(cat, dict):
            family = str(cat.get("capability_family") or "").strip()
            gate_family = CAPABILITY_BUNDLE_FAMILY_TO_GATE_FAMILY.get(family, family)
            if gate_family in REQUIRED_CAPABILITY_FAMILIES:
                bundle_matched_families.add(gate_family)
        for term in _category_terms(cat):
            all_tokens |= _term_tokens(term)
        all_tokens.update(_tokenize(_category_label(cat)))

    token_matched_families: list[str] = []
    for family_name, signals in REQUIRED_CAPABILITY_FAMILIES.items():
        if signals & all_tokens:
            token_matched_families.append(family_name)

    matched_families = sorted(bundle_matched_families) if bundle_matched_families else token_matched_families

    passed = len(matched_families) >= min_families
    return CompQualityResult(
        gate_id="x2_competencies_capability_family_coverage",
        passed=passed,
        observed_value={
            "bundle_families": sorted(bundle_matched_families),
            "token_families": token_matched_families,
            "matched_families": matched_families,
        },
        threshold=f">={min_families} of {len(REQUIRED_CAPABILITY_FAMILIES)} capability families",
        failure_reason=(
            None
            if passed
            else (
                f"Only {len(matched_families)}/{len(REQUIRED_CAPABILITY_FAMILIES)} capability families "
                f"detected (need {min_families}): {matched_families}. "
                "SVP Engineering competencies must cover Agentic Platform, Runtime Governance, "
                "Retrieval Context, LLMOps, Distributed Infra, Productization, Engineering Leadership."
            )
        ),
        signals=matched_families,
    )


# ---------------------------------------------------------------------------
# Gate: no default_fid laundered proof as sole support
# ---------------------------------------------------------------------------


def check_competencies_no_default_fid_proof(
    competencies: list[Any],
    proof_pool_fact_ids: set[str] | None = None,
) -> CompQualityResult:
    """Fail if any term relies solely on default_fid backfill (proof_source == 'default_fid_backfill')."""
    laundered_terms: list[str] = []
    for cat in (competencies or []):
        for term in _category_terms(cat):
            if not isinstance(term, dict):
                continue
            if term.get("proof_source") == "default_fid_backfill":
                phrase = str(term.get("term") or term.get("text") or "unknown")
                laundered_terms.append(phrase)

    passed = len(laundered_terms) == 0
    return CompQualityResult(
        gate_id="x2_competencies_no_default_fid_proof",
        passed=passed,
        observed_value=laundered_terms if laundered_terms else "none",
        threshold="zero default_fid backfill-only terms",
        failure_reason=(
            None
            if passed
            else (
                f"{len(laundered_terms)} term(s) backed only by default_fid backfill: "
                f"{laundered_terms[:5]}. "
                "Terms must have genuine graph_skill_node_ids or verified source_fact_ids."
            )
        ),
        signals=[f"laundered:{t}" for t in laundered_terms[:5]],
    )


# ---------------------------------------------------------------------------
# Gate: generic category must have graph-backed terms
# ---------------------------------------------------------------------------


def check_competencies_generic_category_has_graph_terms(
    competencies: list[Any],
    min_graph_terms: int = GENERIC_CATEGORY_MIN_GRAPH_TERMS,
) -> CompQualityResult:
    """Generic category labels must have ≥min_graph_terms graph-backed specific terms."""
    violations: list[dict[str, Any]] = []
    for cat in (competencies or []):
        label = _category_label(cat)
        if label not in GENERIC_CATEGORIES_REQUIRING_GRAPH:
            continue
        terms = _category_terms(cat)
        graph_term_count = sum(1 for t in terms if _is_graph_backed(t))
        if graph_term_count < min_graph_terms:
            violations.append({
                "category": label,
                "graph_terms": graph_term_count,
                "required": min_graph_terms,
            })

    passed = len(violations) == 0
    return CompQualityResult(
        gate_id="x2_competencies_generic_category_blocked_without_graph",
        passed=passed,
        observed_value=violations if violations else "none",
        threshold=f">={min_graph_terms} graph-backed terms per generic category",
        failure_reason=(
            None
            if passed
            else (
                f"Generic category(ies) lack graph-backed terms: {violations}. "
                "Generic taxonomy labels require ≥3 graph-skill or source-fact-backed terms "
                "to pass the proof authority gate."
            )
        ),
        signals=[v["category"] for v in violations],
    )


# ---------------------------------------------------------------------------
# Gate: E0 n-gram overlap (anti-leakage)
# ---------------------------------------------------------------------------


def check_competencies_e0_ngram_overlap(
    competencies_text: str,
    e0_texts: list[str],
    *,
    threshold: float = E0_NGRAM_THRESHOLD,
    warn_only: bool = True,
) -> CompQualityResult:
    """Fail if competencies text has > threshold 4-gram overlap with E0 examples."""
    if not e0_texts:
        return CompQualityResult(
            gate_id="x2_competencies_e0_ngram_overlap",
            passed=True,
            observed_value=0.0,
            threshold=f"<={threshold:.0%} 4-gram overlap with E0 examples",
            failure_reason=None,
            signals=[],
        )
    overlap = compute_max_ngram_overlap_multi_reference(
        competencies_text, e0_texts, n=NGRAM_SIZE
    )
    passed_gate = overlap <= threshold
    passed = passed_gate or warn_only
    return CompQualityResult(
        gate_id="x2_competencies_e0_ngram_overlap",
        passed=passed,
        observed_value=round(overlap, 4),
        threshold=f"<={threshold:.0%} 4-gram overlap with E0 examples (WARN={'Y' if warn_only else 'N'})",
        failure_reason=(
            None
            if passed_gate
            else (
                f"E0 n-gram overlap {overlap:.1%} exceeds threshold {threshold:.0%}. "
                "Competencies appear to reuse E0 example phrasing."
            )
        ),
        signals=["warn_mode"] if (warn_only and not passed_gate) else [],
    )


# ---------------------------------------------------------------------------
# Gate: base resume competencies n-gram overlap (anti-hydration)
# ---------------------------------------------------------------------------


def check_competencies_base_ngram_overlap(
    competencies_text: str,
    base_competencies_texts: list[str],
    *,
    threshold: float = BASE_NGRAM_THRESHOLD,
    warn_only: bool = True,
) -> CompQualityResult:
    """Fail if competencies text has > threshold 4-gram overlap with base resume competencies."""
    if not base_competencies_texts:
        return CompQualityResult(
            gate_id="x2_competencies_base_ngram_overlap",
            passed=True,
            observed_value=0.0,
            threshold=f"<={threshold:.0%} 4-gram overlap with base competencies",
            failure_reason=None,
            signals=[],
        )
    overlap = compute_max_ngram_overlap_multi_reference(
        competencies_text, base_competencies_texts, n=NGRAM_SIZE
    )
    passed_gate = overlap <= threshold
    passed = passed_gate or warn_only
    return CompQualityResult(
        gate_id="x2_competencies_base_ngram_overlap",
        passed=passed,
        observed_value=round(overlap, 4),
        threshold=f"<={threshold:.0%} 4-gram overlap with base resume competencies (WARN={'Y' if warn_only else 'N'})",
        failure_reason=(
            None
            if passed_gate
            else (
                f"Base resume n-gram overlap {overlap:.1%} exceeds threshold {threshold:.0%}. "
                "Competencies must be organically generated from graph proof, not from base resume."
            )
        ),
        signals=["warn_mode"] if (warn_only and not passed_gate) else [],
    )


# ---------------------------------------------------------------------------
# Competency capability bundle gates (graph-backed rigor wiring)
# ---------------------------------------------------------------------------

# Technical-density signal tokens (substantive engineering vocabulary).
_TECHNICAL_DENSITY_TOKENS: frozenset[str] = frozenset({
    "agentic", "orchestration", "runtime", "governance", "gate", "gates",
    "retrieval", "context", "vector", "graphrag", "grounding", "evaluation",
    "observability", "telemetry", "reliability", "llmops", "microservices",
    "distributed", "cloud", "lakehouse", "streaming", "kubernetes", "pipeline",
    "platform", "architecture", "commercialization", "productization",
    "alliance", "co-sell", "lineage", "rbac", "devsecops", "policy",
    "deterministic", "calibration", "judge", "accelerator",
})


def competency_bundle_consumption_active(
    proof_pool_metadata: dict[str, Any] | None,
) -> bool:
    return bool(
        isinstance(proof_pool_metadata, dict)
        and proof_pool_metadata.get("competency_capability_bundle_consumption")
    )


def selected_graph_evidence_depth_result(
    proof_pool_metadata: dict[str, Any] | None,
) -> CompQualityResult | None:
    """Return a hard fail when the selected graph evidence packet is thin."""
    if not isinstance(proof_pool_metadata, dict):
        return None
    report = proof_pool_metadata.get("graph_evidence_depth_report")
    if not isinstance(report, dict) or not report:
        return None
    status = str(report.get("status") or "").strip().lower()
    thin_item_ids = [str(x).strip() for x in (report.get("thin_item_ids") or []) if str(x).strip()]
    weakest = report.get("weakest_link") or {}
    passed = status == "judge_grade" and not thin_item_ids
    return CompQualityResult(
        gate_id="x2_competencies_selected_graph_evidence_depth_sufficient",
        passed=passed,
        observed_value={
            "status": status or "unknown",
            "summary": report.get("summary"),
            "thin_item_ids": thin_item_ids,
        },
        threshold="selected_graph_evidence_plan must be judge_grade with no thin items",
        failure_reason=(
            None
            if passed
            else (
                f"selected graph evidence packet is thin: {report.get('summary')} "
                f"thin_items=[{', '.join(thin_item_ids)}] weakest_link={weakest!r}"
            )
        ),
        signals=thin_item_ids[:6],
    )


def check_capability_bundles_in_proof_pool(
    proof_pool_metadata: dict[str, Any] | None,
) -> CompQualityResult:
    bundles = []
    if isinstance(proof_pool_metadata, dict):
        bundles = proof_pool_metadata.get("competency_capability_bundles") or []
    passed = len(bundles) > 0
    return CompQualityResult(
        gate_id="x2_competencies_capability_bundles_in_proof_pool",
        passed=passed,
        observed_value=len(bundles),
        threshold=">=1 competency capability bundle in proof pool",
        failure_reason=None if passed else "No competency capability bundles in proof pool metadata.",
        signals=[],
    )


def _cat_bundle_id(cat: Any) -> str:
    if isinstance(cat, dict):
        return str(cat.get("competency_bundle_id") or "").strip()
    return ""


def _cat_graph_nodes(cat: Any) -> list[str]:
    if isinstance(cat, dict):
        return [str(x) for x in (cat.get("graph_skill_node_ids") or []) if str(x).strip()]
    return []


def _cat_source_fact_ids(cat: Any) -> list[str]:
    out: list[str] = []
    if isinstance(cat, dict):
        for fid in cat.get("source_fact_ids") or []:
            if str(fid).strip():
                out.append(str(fid))
    return out


def _category_and_term_source_fact_ids(cat: Any) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for fid in _cat_source_fact_ids(cat):
        fid_s = str(fid).strip()
        if fid_s and fid_s not in seen:
            seen.add(fid_s)
            out.append(fid_s)
    for term in _category_terms(cat):
        if not isinstance(term, dict):
            continue
        raw = term.get("source_fact_ids") or []
        if isinstance(raw, str):
            raw = [raw]
        primary = term.get("source_fact_id")
        if primary:
            raw = [primary, *list(raw)]
        for fid in raw:
            fid_s = str(fid).strip()
            if fid_s and fid_s not in seen:
                seen.add(fid_s)
                out.append(fid_s)
    return out


def _bundle_records_by_id(
    proof_pool_metadata: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if not isinstance(proof_pool_metadata, dict):
        return {}
    records = proof_pool_metadata.get("competency_capability_bundles") or []
    if not records:
        packet = proof_pool_metadata.get("competency_capability_section_packet") or {}
        if isinstance(packet, dict):
            records = packet.get("competency_bundles") or []
    out: dict[str, dict[str, Any]] = {}
    for rec in records:
        if not isinstance(rec, dict):
            continue
        bid = str(rec.get("competency_bundle_id") or "").strip()
        if bid:
            out[bid] = rec
    return out


def check_competency_bundle_id_per_category(competencies: list[Any]) -> CompQualityResult:
    missing = [
        _category_label(c) or f"idx{i}"
        for i, c in enumerate(competencies or [])
        if not _cat_bundle_id(c)
    ]
    passed = not missing
    return CompQualityResult(
        gate_id="x2_competency_bundle_id_required_per_category",
        passed=passed,
        observed_value=missing if missing else "all_bound",
        threshold="every category carries competency_bundle_id",
        failure_reason=None if passed else f"Categories missing competency_bundle_id: {missing[:6]}",
        signals=missing[:6],
    )


def check_graph_skill_node_ids_per_category(competencies: list[Any]) -> CompQualityResult:
    missing = [
        _category_label(c) or f"idx{i}"
        for i, c in enumerate(competencies or [])
        if not _cat_graph_nodes(c)
    ]
    passed = not missing
    return CompQualityResult(
        gate_id="x2_graph_skill_node_ids_required_per_category",
        passed=passed,
        observed_value=missing if missing else "all_have_graph_nodes",
        threshold="every category carries >=1 graph_skill_node_id",
        failure_reason=None if passed else f"Categories missing graph_skill_node_ids: {missing[:6]}",
        signals=missing[:6],
    )


def check_source_fact_ids_or_graph_lineage_per_category(competencies: list[Any]) -> CompQualityResult:
    missing: list[str] = []
    for i, c in enumerate(competencies or []):
        has_facts = bool(_cat_source_fact_ids(c))
        has_lineage = bool(_cat_graph_nodes(c)) and bool(_cat_bundle_id(c))
        if not (has_facts or has_lineage):
            missing.append(_category_label(c) or f"idx{i}")
    passed = not missing
    return CompQualityResult(
        gate_id="x2_source_fact_ids_or_graph_lineage_required_per_category",
        passed=passed,
        observed_value=missing if missing else "all_have_lineage",
        threshold="every category has source_fact_ids OR (bundle_id + graph_skill_node_ids)",
        failure_reason=None if passed else f"Categories without source facts or graph lineage: {missing[:6]}",
        signals=missing[:6],
    )


def check_competency_bundle_source_fact_alignment(
    competencies: list[Any],
    proof_pool_metadata: dict[str, Any] | None,
) -> CompQualityResult:
    """Each emitted category must preserve at least one linked fact from its bound bundle."""
    bundle_by_id = _bundle_records_by_id(proof_pool_metadata)
    if not bundle_by_id:
        return CompQualityResult(
            gate_id="x2_competency_bundle_source_fact_alignment",
            passed=True,
            observed_value="no_bundle_records",
            threshold="category source facts intersect bound bundle linked_source_fact_ids",
            failure_reason=None,
            signals=[],
        )

    violations: list[dict[str, Any]] = []
    for index, cat in enumerate(competencies or []):
        if not isinstance(cat, dict):
            continue
        bundle_id = _cat_bundle_id(cat)
        if not bundle_id:
            continue
        bundle = bundle_by_id.get(bundle_id)
        if not bundle:
            violations.append({
                "category": _category_label(cat) or f"idx{index}",
                "competency_bundle_id": bundle_id,
                "reason": "unknown_competency_bundle_id",
                "observed_source_fact_ids": _category_and_term_source_fact_ids(cat),
                "expected_linked_source_fact_ids": [],
            })
            continue
        expected = {
            str(fid).strip()
            for fid in (bundle.get("linked_source_fact_ids") or [])
            if str(fid).strip()
        }
        if not expected:
            continue
        observed = set(_category_and_term_source_fact_ids(cat))
        if observed.intersection(expected):
            continue
        violations.append({
            "category": _category_label(cat) or f"idx{index}",
            "competency_bundle_id": bundle_id,
            "reason": "no_bundle_fact_intersection",
            "observed_source_fact_ids": sorted(observed),
            "expected_linked_source_fact_ids": sorted(expected),
        })

    passed = not violations
    return CompQualityResult(
        gate_id="x2_competency_bundle_source_fact_alignment",
        passed=passed,
        observed_value=violations if violations else "all_categories_intersect_bound_bundle_facts",
        threshold="every known competency_bundle_id has category/term source_fact_ids intersecting linked_source_fact_ids",
        failure_reason=None if passed else f"Competency categories use facts outside their bound bundles: {violations[:6]}",
        signals=[str(v.get("category")) for v in violations[:6]],
    )


def check_competency_source_fact_dominance(
    competencies: list[Any],
    *,
    max_category_share: float = 0.5,
    max_category_count: int = 4,
) -> CompQualityResult:
    """No single source fact may dominate the emitted competency categories."""
    category_count = len([c for c in (competencies or []) if isinstance(c, dict)])
    if category_count == 0:
        return CompQualityResult(
            gate_id="x2_competency_source_fact_dominance",
            passed=True,
            observed_value={"category_count": 0, "source_fact_category_counts": {}},
            threshold=f"no fact in >{max_category_share:.0%} categories or >{max_category_count} categories",
            failure_reason=None,
            signals=[],
        )

    fact_category_counts: dict[str, int] = {}
    for cat in competencies or []:
        if not isinstance(cat, dict):
            continue
        for fid in set(_category_and_term_source_fact_ids(cat)):
            fact_category_counts[fid] = fact_category_counts.get(fid, 0) + 1

    dominant: list[dict[str, Any]] = []
    for fid, count in sorted(fact_category_counts.items(), key=lambda item: (-item[1], item[0])):
        share = count / category_count
        if count > max_category_count or share > max_category_share:
            dominant.append({
                "source_fact_id": fid,
                "category_count": count,
                "category_share": round(share, 4),
            })

    passed = not dominant
    return CompQualityResult(
        gate_id="x2_competency_source_fact_dominance",
        passed=passed,
        observed_value={
            "category_count": category_count,
            "source_fact_category_counts": fact_category_counts,
            "dominant_source_facts": dominant,
        },
        threshold=f"no source fact may support >{max_category_share:.0%} categories or >{max_category_count} categories",
        failure_reason=None if passed else f"Source fact reuse dominates competency categories: {dominant[:6]}",
        signals=[str(v.get("source_fact_id")) for v in dominant[:6]],
    )


def check_default_fid_only_support_forbidden(competencies: list[Any]) -> CompQualityResult:
    """HARD variant: any term whose only support is default_fid backfill fails."""
    laundered: list[str] = []
    for cat in (competencies or []):
        for term in _category_terms(cat):
            if not isinstance(term, dict):
                continue
            if term.get("proof_source") == "default_fid_backfill":
                skill_ids = term.get("graph_skill_node_ids") or term.get("source_skill_ids") or []
                if not skill_ids:
                    laundered.append(str(term.get("term") or term.get("text") or "unknown"))
    passed = not laundered
    return CompQualityResult(
        gate_id="x2_default_fid_only_support_forbidden",
        passed=passed,
        observed_value=laundered if laundered else "none",
        threshold="zero default_fid-only terms",
        failure_reason=None if passed else f"default_fid-only support terms: {laundered[:6]}",
        signals=laundered[:6],
    )


def check_generic_taxonomy_only_category_forbidden(competencies: list[Any]) -> CompQualityResult:
    """Generic labels require bundle, category graph skills, and enough supported graph terms."""
    violations: list[dict[str, Any]] = []
    for cat in (competencies or []):
        label = _category_label(cat)
        if label not in GENERIC_CATEGORIES_REQUIRING_GRAPH:
            continue
        terms = _category_terms(cat)
        graph_terms = [t for t in terms if _is_graph_backed(t)]
        unsupported_graph_terms = [
            str(t.get("term") or t.get("text") or "unknown")
            for t in graph_terms
            if not _term_support_ids(t)
        ]
        reasons: list[str] = []
        if not _cat_bundle_id(cat):
            reasons.append("missing_competency_bundle_id")
        if not _cat_graph_skill_ids(cat):
            reasons.append("missing_category_graph_skill_node_ids")
        if len(graph_terms) < GENERIC_CATEGORY_MIN_GRAPH_TERMS:
            reasons.append("too_few_graph_backed_terms")
        if unsupported_graph_terms:
            reasons.append("graph_terms_missing_skill_or_fact_support")
        if reasons:
            violations.append({
                "category": label,
                "reasons": reasons,
                "graph_terms": len(graph_terms),
                "required_graph_terms": GENERIC_CATEGORY_MIN_GRAPH_TERMS,
                "unsupported_graph_terms": unsupported_graph_terms[:5],
            })
    passed = not violations
    return CompQualityResult(
        gate_id="x2_generic_taxonomy_only_category_forbidden",
        passed=passed,
        observed_value=violations if violations else "none",
        threshold=(
            "generic categories require bundle id, category graph_skill_node_ids, "
            f">={GENERIC_CATEGORY_MIN_GRAPH_TERMS} graph-backed terms, and term skill/fact support"
        ),
        failure_reason=None if passed else f"Generic taxonomy categories failed graph depth contract: {violations}",
        signals=[str(v.get("category")) for v in violations],
    )


def check_jd_only_skill_forbidden(
    competencies: list[Any], jd_text: str
) -> CompQualityResult:
    jd_low = str(jd_text or "").lower()
    hits: list[str] = []
    if jd_low:
        for cat in (competencies or []):
            for term in _category_terms(cat):
                if not isinstance(term, dict):
                    continue
                phrase = str(term.get("term") or term.get("text") or "").strip().lower()
                skill_ids = term.get("graph_skill_node_ids") or term.get("source_skill_ids") or []
                fact_ids = term.get("source_fact_ids") or []
                if (
                    phrase
                    and len(phrase.split()) >= 2
                    and phrase in jd_low
                    and not skill_ids
                    and not fact_ids
                ):
                    hits.append(phrase)
    passed = not hits
    return CompQualityResult(
        gate_id="x2_jd_only_skill_forbidden",
        passed=passed,
        observed_value=hits[:6] if hits else "none",
        threshold="no JD-lifted term without graph/source support",
        failure_reason=None if passed else f"JD-only skills without support: {hits[:6]}",
        signals=hits[:6],
    )


def check_competencies_archive_ngram_overlap(
    competencies_text: str,
    archive_competencies_texts: list[str],
    *,
    threshold: float = BASE_NGRAM_THRESHOLD,
    warn_only: bool = True,
) -> CompQualityResult:
    if not archive_competencies_texts:
        return CompQualityResult(
            gate_id="x2_base_archive_ngram_overlap_forbidden_or_warn",
            passed=True,
            observed_value=0.0,
            threshold=f"<={threshold:.0%} 4-gram overlap with archive competencies",
            failure_reason=None,
            signals=[],
        )
    overlap = compute_max_ngram_overlap_multi_reference(
        competencies_text, archive_competencies_texts, n=NGRAM_SIZE
    )
    passed_gate = overlap <= threshold
    passed = passed_gate or warn_only
    return CompQualityResult(
        gate_id="x2_base_archive_ngram_overlap_forbidden_or_warn",
        passed=passed,
        observed_value=round(overlap, 4),
        threshold=f"<={threshold:.0%} 4-gram overlap with archive competencies (WARN={'Y' if warn_only else 'N'})",
        failure_reason=(
            None
            if passed_gate
            else f"Archive n-gram overlap {overlap:.1%} exceeds threshold {threshold:.0%}."
        ),
        signals=["warn_mode"] if (warn_only and not passed_gate) else [],
    )


def check_competency_rigor_floor(
    competencies: list[Any], *, min_distinct_terms: int = 12
) -> CompQualityResult:
    distinct: set[str] = set()
    for cat in (competencies or []):
        for term in _category_terms(cat):
            phrase = (
                str(term.get("term") or term.get("text") or "")
                if isinstance(term, dict)
                else str(term or "")
            ).strip().lower()
            if phrase and len(phrase.split()) >= 2:
                distinct.add(phrase)
    n = len(distinct)
    passed = n >= min_distinct_terms
    return CompQualityResult(
        gate_id="x2_competency_rigor_floor_met",
        passed=passed,
        observed_value=n,
        threshold=f">={min_distinct_terms} distinct multi-word executive terms",
        failure_reason=None if passed else f"Only {n} distinct multi-word terms (rigor floor {min_distinct_terms}).",
        signals=[],
    )


def check_technical_density_floor(
    competencies: list[Any], *, min_density: float = 0.4
) -> CompQualityResult:
    total = 0
    technical = 0
    for cat in (competencies or []):
        for term in _category_terms(cat):
            total += 1
            toks = _term_tokens(term)
            if toks & _TECHNICAL_DENSITY_TOKENS:
                technical += 1
    density = (technical / total) if total else 0.0
    passed = density >= min_density
    return CompQualityResult(
        gate_id="x2_technical_density_floor_met",
        passed=passed,
        observed_value=round(density, 3),
        threshold=f">={min_density:.0%} terms carry technical-density tokens",
        failure_reason=None if passed else f"Technical density {density:.0%} below floor {min_density:.0%}.",
        signals=[],
    )


def check_required_capability_families_covered(
    competencies: list[Any], *, min_families: int = 7
) -> CompQualityResult:
    """Required-coverage gate: at least min_families of the 7 capability families present."""
    return CompQualityResult(
        gate_id="x2_required_capability_families_covered",
        passed=check_competencies_capability_family_coverage(competencies, min_families=min_families).passed,
        observed_value=check_competencies_capability_family_coverage(competencies, min_families=min_families).observed_value,
        threshold=f">={min_families} of 7 required capability families",
        failure_reason=check_competencies_capability_family_coverage(competencies, min_families=min_families).failure_reason,
        signals=[],
    )


def competencies_to_text_blob(competencies: list[Any]) -> str:
    """Flatten all category labels and term phrases to a single text blob for n-gram checking."""
    parts: list[str] = []
    for cat in (competencies or []):
        label = _category_label(cat)
        if label:
            parts.append(label)
        for term in _category_terms(cat):
            if isinstance(term, dict):
                phrase = str(term.get("term") or term.get("text") or "")
            else:
                phrase = str(term or "")
            if phrase:
                parts.append(phrase)
    return " ".join(parts)


__all__ = [
    "BASE_NGRAM_THRESHOLD",
    "CompQualityResult",
    "E0_NGRAM_THRESHOLD",
    "GENERIC_CATEGORIES_REQUIRING_GRAPH",
    "NGRAM_SIZE",
    "REQUIRED_CAPABILITY_FAMILIES",
    "check_capability_bundles_in_proof_pool",
    "check_competencies_archive_ngram_overlap",
    "check_competencies_base_ngram_overlap",
    "check_competencies_capability_family_coverage",
    "check_competencies_e0_ngram_overlap",
    "check_competencies_generic_category_has_graph_terms",
    "check_competencies_no_default_fid_proof",
    "check_competency_bundle_source_fact_alignment",
    "check_competency_bundle_id_per_category",
    "check_competency_rigor_floor",
    "check_competency_source_fact_dominance",
    "check_default_fid_only_support_forbidden",
    "check_generic_taxonomy_only_category_forbidden",
    "check_graph_skill_node_ids_per_category",
    "check_jd_only_skill_forbidden",
    "check_required_capability_families_covered",
    "check_source_fact_ids_or_graph_lineage_per_category",
    "check_technical_density_floor",
    "competencies_to_text_blob",
    "competency_bundle_consumption_active",
    "selected_graph_evidence_depth_result",
]
