"""Competencies authority X2 gate helpers (Headline/Competencies/Narrative Rigor plan).

Implements deterministic proxy gates enforcing graph-backed competencies proof:
- x2_competencies_capability_family_coverage: >=5 of required capability families present
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
    "partner_architecture": frozenset({
        "partner", "partnership", "co-sell", "cosell", "alliance",
        "reference", "accelerator", "enablement", "partner-ready",
    }),
    "engineering_leadership": frozenset({
        "engineering", "leadership", "organization", "operating", "model",
        "talent", "hiring", "recruiting", "team", "staff",
    }),
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
SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE = 0.75
MIN_UNIQUE_LEAF_SKILLS_PER_CATEGORY = 1
MIN_UNIQUE_SOURCE_FACTS_PER_CATEGORY = 1
MIN_SELECTED_UNIQUE_LEAF_SKILLS = 16
MIN_SELECTED_UNIQUE_SOURCE_FACTS = 4
MIN_SELECTED_UNIQUE_METRICS = 8

ROLE_PROFILE_REQUIRED_SKILL_AXES: dict[str, dict[str, tuple[str, ...]]] = {
    "ai_partnerships_gtm": {
        "partner_motions": ("partner", "partnership", "alliance"),
        "co_sell": ("co_sell", "cosell", "co-selling", "co_selling"),
        "hyperscaler_alliance": ("hyperscaler", "aws", "cloud_vendor", "cloud-vendor"),
        "joint_solution": ("joint_solution", "joint solution", "partner_led_ai_solutions"),
        "gtm_enablement": ("enablement", "gtm", "technical_close", "go-to-market"),
        "partner_architecture": (
            "partner_applied_ai_architecture",
            "applied_ai_partner_architecture",
            "reference_architecture",
            "reference architecture",
            "solution_architecture",
            "solution architecture",
        ),
    }
}

GENERIC_CONFIDENCE_PHRASES: frozenset[str] = frozenset({
    "technology strategy",
    "innovation",
    "leadership",
    "stakeholder management",
    "communication",
    "problem solving",
    "strategic planning",
    "cross-functional",
})

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
    """Term is graph-backed if it has graph_skill_node_ids, source_skill_ids, or is NOT default_fid_backfill."""
    if not isinstance(term, dict):
        return False
    if term.get("proof_source") == "default_fid_backfill":
        return False
    skill_ids = term.get("graph_skill_node_ids") or term.get("source_skill_ids") or []
    if skill_ids:
        return True
    fact_ids = term.get("source_fact_ids") or []
    return bool(fact_ids)


# ---------------------------------------------------------------------------
# Gate: capability family coverage
# ---------------------------------------------------------------------------


def check_competencies_capability_family_coverage(
    competencies: list[Any],
    min_families: int = 5,
) -> CompQualityResult:
    """Require at least min_families required capability families across all terms."""
    all_tokens: set[str] = set()
    for cat in (competencies or []):
        for term in _category_terms(cat):
            all_tokens |= _term_tokens(term)
        all_tokens.update(_tokenize(_category_label(cat)))

    matched_families: list[str] = []
    for family_name, signals in REQUIRED_CAPABILITY_FAMILIES.items():
        if signals & all_tokens:
            matched_families.append(family_name)

    passed = len(matched_families) >= min_families
    return CompQualityResult(
        gate_id="x2_competencies_capability_family_coverage",
        passed=passed,
        observed_value=matched_families,
        threshold=f">={min_families} of {len(REQUIRED_CAPABILITY_FAMILIES)} capability families",
        failure_reason=(
            None
            if passed
            else (
                f"Only {len(matched_families)}/{len(REQUIRED_CAPABILITY_FAMILIES)} capability families "
                f"detected (need {min_families}): {matched_families}. "
                "SVP Engineering competencies must cover Agentic Platform, Runtime Governance, "
                "Retrieval Context, LLMOps, Distributed Infra, Productization, Partner Architecture, "
                "and Engineering Leadership."
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
    "deterministic", "calibration", "judge", "accelerator", "reference",
    "solution", "enablement", "partner-ready",
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
    out: list[str] = []
    if isinstance(cat, dict):
        out.extend(_cat_graph_nodes_direct(cat))
        for term in cat.get("terms") or []:
            if not isinstance(term, dict):
                continue
            for key in ("graph_skill_node_ids", "source_skill_ids"):
                for x in (term.get(key) or []):
                    if str(x).strip():
                        out.append(str(x))
    return out


def _cat_graph_nodes_direct(cat: Any) -> list[str]:
    if isinstance(cat, dict):
        return [str(x) for x in (cat.get("graph_skill_node_ids") or []) if str(x).strip()]
    return []


def _cat_source_fact_ids(cat: Any) -> list[str]:
    out: list[str] = []
    if isinstance(cat, dict):
        out.extend(_cat_source_fact_ids_direct(cat))
        for term in cat.get("terms") or []:
            if not isinstance(term, dict):
                continue
            for fid in term.get("source_fact_ids") or []:
                if str(fid).strip():
                    out.append(str(fid).split("_metric_")[0])
            if str(term.get("source_fact_id") or "").strip():
                out.append(str(term.get("source_fact_id")).split("_metric_")[0])
    return out


def _cat_source_fact_ids_direct(cat: Any) -> list[str]:
    out: list[str] = []
    if isinstance(cat, dict):
        for fid in cat.get("source_fact_ids") or []:
            if str(fid).strip():
                out.append(str(fid).split("_metric_")[0])
    return out


def _cat_score(cat: Any) -> float | None:
    if not isinstance(cat, dict):
        return None
    for key in ("confidence", "selection_score", "score"):
        if key not in cat:
            continue
        try:
            return round(float(cat[key]), 4)
        except (TypeError, ValueError):
            return None
    return None


def _unique_strs(values: Any) -> list[str]:
    return sorted({str(x).strip() for x in (values or []) if str(x).strip()})


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _norm_score(value: Any) -> float | None:
    raw = _safe_float(value)
    if raw is None:
        return None
    if raw > 1.0:
        raw = raw / 100.0
    return round(_clamp01(raw), 4)


def _selected_graph_plan(proof_pool_metadata: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(proof_pool_metadata, dict):
        return {}
    plan = proof_pool_metadata.get("selected_graph_evidence_plan")
    return plan if isinstance(plan, dict) else {}


PARTNER_ARCHITECTURE_BUNDLE_ID = "ccb_partner_applied_ai_architecture"
PARTNER_ARCHITECTURE_FAMILY = "partner_applied_ai_architecture"
PARTNER_TARGET_PROFILES = frozenset({
    "ai_partnerships_gtm",
    "PARTNER_APPLIED_AI_ARCHITECTURE",
    "ANTHROPIC_PARTNERSHIPS_APPLIED_AI",
})
FORBIDDEN_PARTNER_EMPLOYER_LANES = frozenset({"insurtech", "ey"})
PARTNER_TEXT_RE = re.compile(
    r"\b(partner|partnership|alliance|co-?sell|cosell|ecosystem|hyperscaler)\b",
    re.IGNORECASE,
)
PARTNER_ARCHITECTURE_TEXT_RE = re.compile(
    r"\b(partner|partnership|alliance|co-?sell|cosell|ecosystem|hyperscaler)\b"
    r".*\b(architecture|architectures|solution|solutions|reference|accelerator|enablement|deployment)\b"
    r"|"
    r"\b(architecture|architectures|solution|solutions|reference|accelerator|enablement|deployment)\b"
    r".*\b(partner|partnership|alliance|co-?sell|cosell|ecosystem|hyperscaler)\b",
    re.IGNORECASE,
)


def _proof_bundles_by_id(proof_pool_metadata: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    bundles = []
    if isinstance(proof_pool_metadata, dict):
        bundles = proof_pool_metadata.get("competency_capability_bundles") or []
    out: dict[str, dict[str, Any]] = {}
    for bundle in bundles:
        if not isinstance(bundle, dict):
            continue
        bid = str(bundle.get("competency_bundle_id") or "").strip()
        if bid:
            out[bid] = bundle
    return out


def _cat_capability_family(cat: Any, bundles_by_id: dict[str, dict[str, Any]]) -> str:
    if isinstance(cat, dict):
        fam = str(cat.get("capability_family") or "").strip()
        if fam:
            return fam
        bundle = bundles_by_id.get(_cat_bundle_id(cat))
        if bundle:
            return str(bundle.get("capability_family") or "").strip()
    return ""


def _cat_text_for_partner_checks(cat: Any) -> str:
    parts = [_category_label(cat)]
    if isinstance(cat, dict):
        parts.extend(
            str(x)
            for x in (
                cat.get("competency_bundle_id"),
                cat.get("capability_family"),
            )
            if x
        )
        for term in _category_terms(cat):
            if isinstance(term, dict):
                parts.append(str(term.get("term") or term.get("text") or ""))
            else:
                parts.append(str(term or ""))
    return " ".join(p for p in parts if p)


def _selected_fact_employer_map(proof_pool_metadata: dict[str, Any] | None) -> dict[str, str]:
    plan = _selected_graph_plan(proof_pool_metadata)
    out: dict[str, str] = {}
    for row in plan.get("facts") or []:
        if not isinstance(row, dict):
            continue
        lane = str(row.get("employer_lane") or row.get("employer") or "").strip().lower()
        if not lane:
            continue
        for key in (
            row.get("fact_id"),
            row.get("role_episode_bundle_id"),
            row.get("employer_node_id"),
        ):
            ident = str(key or "").strip()
            if ident:
                out[ident] = lane
        for fid in row.get("source_fact_ids") or []:
            ident = str(fid or "").strip()
            if ident:
                out[ident] = lane
        for mid in row.get("metric_outcome_ids") or []:
            ident = str(mid or "").split("_metric_", 1)[0].strip()
            if ident:
                out[ident] = lane
    return out


def _partner_profile_active(proof_pool_metadata: dict[str, Any] | None) -> bool:
    plan = _selected_graph_plan(proof_pool_metadata)
    profile = str(plan.get("target_role_profile") or "").strip()
    if profile in PARTNER_TARGET_PROFILES:
        return True
    for key in (
        proof_pool_metadata.get("role_family_key") if isinstance(proof_pool_metadata, dict) else "",
        plan.get("role_family_key"),
        plan.get("projection_role_family_key"),
    ):
        if str(key or "").strip() in PARTNER_TARGET_PROFILES:
            return True
    selected_families = {
        str(x).strip()
        for x in (plan.get("selected_competency_families") or [])
        if str(x).strip()
    }
    return PARTNER_ARCHITECTURE_FAMILY in selected_families


def check_partner_architecture_bundle_present(
    competencies: list[Any],
    proof_pool_metadata: dict[str, Any] | None,
) -> CompQualityResult:
    """Anthropic/partnership profiles must select and render the partner architecture bundle."""
    if not _partner_profile_active(proof_pool_metadata):
        return CompQualityResult(
            gate_id="x2_partner_architecture_bundle_present",
            passed=True,
            observed_value="not_applicable",
            threshold="required only for partner/applied-ai architecture profiles",
            failure_reason=None,
            signals=[],
        )
    bundles_by_id = _proof_bundles_by_id(proof_pool_metadata)
    proof_pool_has_bundle = PARTNER_ARCHITECTURE_BUNDLE_ID in bundles_by_id
    rendered = [
        _category_label(cat) or f"idx{i}"
        for i, cat in enumerate(competencies or [])
        if _cat_bundle_id(cat) == PARTNER_ARCHITECTURE_BUNDLE_ID
        or _cat_capability_family(cat, bundles_by_id) == PARTNER_ARCHITECTURE_FAMILY
    ]
    passed = proof_pool_has_bundle and bool(rendered)
    return CompQualityResult(
        gate_id="x2_partner_architecture_bundle_present",
        passed=passed,
        observed_value={
            "proof_pool_has_bundle": proof_pool_has_bundle,
            "rendered_categories": rendered,
        },
        threshold=f"{PARTNER_ARCHITECTURE_BUNDLE_ID} present in proof pool and rendered",
        failure_reason=(
            None
            if passed
            else "Partner/applied-AI profile requires a rendered category bound to ccb_partner_applied_ai_architecture."
        ),
        signals=rendered,
    )


def check_partner_architecture_terms_require_bundle(
    competencies: list[Any],
    proof_pool_metadata: dict[str, Any] | None,
) -> CompQualityResult:
    """Partner architecture terms must be bound to the partner architecture bundle."""
    bundles_by_id = _proof_bundles_by_id(proof_pool_metadata)
    violations: list[str] = []
    for i, cat in enumerate(competencies or []):
        text = _cat_text_for_partner_checks(cat)
        if not PARTNER_ARCHITECTURE_TEXT_RE.search(text):
            continue
        bundle_id = _cat_bundle_id(cat)
        family = _cat_capability_family(cat, bundles_by_id)
        if bundle_id != PARTNER_ARCHITECTURE_BUNDLE_ID and family != PARTNER_ARCHITECTURE_FAMILY:
            violations.append(_category_label(cat) or f"idx{i}:{bundle_id or 'missing_bundle'}")
    passed = not violations
    return CompQualityResult(
        gate_id="x2_partner_architecture_terms_require_partner_bundle",
        passed=passed,
        observed_value=violations if violations else "none",
        threshold=f"partner architecture terms require {PARTNER_ARCHITECTURE_BUNDLE_ID}",
        failure_reason=(
            None
            if passed
            else f"Partner architecture wording appeared outside the partner architecture bundle: {violations[:6]}"
        ),
        signals=violations[:6],
    )


def check_partner_terms_source_roots(
    competencies: list[Any],
    proof_pool_metadata: dict[str, Any] | None,
) -> CompQualityResult:
    """Partner terms cannot be backed by InsurTech/EY roots."""
    bundles_by_id = _proof_bundles_by_id(proof_pool_metadata)
    fact_to_lane = _selected_fact_employer_map(proof_pool_metadata)
    violations: list[str] = []
    for i, cat in enumerate(competencies or []):
        text = _cat_text_for_partner_checks(cat)
        if not PARTNER_TEXT_RE.search(text):
            continue
        label = _category_label(cat) or f"idx{i}"
        bundle = bundles_by_id.get(_cat_bundle_id(cat)) or {}
        root_ids = set(_cat_source_fact_ids(cat))
        root_ids.update(str(x) for x in (bundle.get("employer_bindings") or []) if str(x).strip())
        root_ids.update(str(x) for x in (bundle.get("role_episode_bindings") or []) if str(x).strip())
        forbidden_roots = {
            str(x).strip()
            for x in (bundle.get("forbidden_partner_roots") or [])
            if str(x).strip()
        }

        for root_id in sorted(root_ids):
            low = root_id.lower()
            lane = fact_to_lane.get(root_id, "")
            if (
                root_id in forbidden_roots
                or lane in FORBIDDEN_PARTNER_EMPLOYER_LANES
                or "insurtech" in low
                or low in {"employment_exp_ey_001", "reb_ey_data_governance"}
            ):
                violations.append(f"{label}:{root_id}:{lane or 'root_hint'}")
                break
    passed = not violations
    return CompQualityResult(
        gate_id="x2_partner_terms_source_roots_forbid_insurtech_ey",
        passed=passed,
        observed_value=violations if violations else "none",
        threshold="partner terms may not bind to InsurTech/EY roots",
        failure_reason=(
            None
            if passed
            else f"Partner wording bound to forbidden InsurTech/EY roots: {violations[:6]}"
        ),
        signals=violations[:6],
    )


def _average_judge_score(x1d_judges: list[dict[str, Any]] | None) -> tuple[float | None, str]:
    scores: list[float] = []
    for judge in x1d_judges or []:
        if not isinstance(judge, dict):
            continue
        score = _norm_score(judge.get("score"))
        if score is not None:
            scores.append(score)
    if not scores:
        return None, "unavailable"
    return round(sum(scores) / len(scores), 4), "section_x1d_average"


def _category_text(cat: Any) -> str:
    parts = [_category_label(cat)]
    for term in _category_terms(cat):
        if isinstance(term, dict):
            parts.append(str(term.get("term") or term.get("text") or ""))
        else:
            parts.append(str(term or ""))
    return " ".join(p for p in parts if p).lower()


def _specific_alignment_score(category_text: str, jd_text: str, briefing_text: str) -> float:
    target_tokens = {
        tok
        for tok in _tokenize(f"{jd_text} {briefing_text}")
        if len(tok) >= 5 and tok not in _STOPWORDS_FOR_ALIGNMENT
    }
    if not target_tokens:
        return 0.0
    cat_tokens = {tok for tok in _tokenize(category_text) if len(tok) >= 5}
    if not cat_tokens:
        return 0.0
    hits = cat_tokens & target_tokens
    return round(_clamp01(len(hits) / 4.0), 4)


def _generic_phrase_penalty(category_text: str) -> float:
    hits = [phrase for phrase in GENERIC_CONFIDENCE_PHRASES if phrase in category_text]
    return round(min(0.2, 0.05 * len(hits)), 4)


def _fact_reuse_penalty(
    source_fact_ids: list[str],
    *,
    dominant_source_fact_id: str,
    dominant_share: float,
) -> float:
    if not dominant_source_fact_id or dominant_source_fact_id not in source_fact_ids:
        return 0.0
    overage = max(0.0, dominant_share - SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE)
    return round(min(0.2, overage), 4)


_STOPWORDS_FOR_ALIGNMENT = frozenset({
    "about",
    "above",
    "across",
    "after",
    "again",
    "against",
    "being",
    "build",
    "could",
    "every",
    "first",
    "their",
    "there",
    "these",
    "those",
    "through",
    "using",
    "where",
    "which",
    "while",
    "would",
})


def _rendered_competency_skill_ids(parsed_output: dict[str, Any] | None) -> list[str]:
    if not isinstance(parsed_output, dict):
        return []
    out: list[str] = []
    for key in ("competencies", "categories"):
        rows = parsed_output.get(key)
        if not isinstance(rows, list):
            continue
        for cat in rows:
            if not isinstance(cat, dict):
                continue
            for raw in cat.get("graph_skill_node_ids") or []:
                sid = str(raw).strip()
                if sid and sid not in out:
                    out.append(sid)
            for term in cat.get("terms") or []:
                if not isinstance(term, dict):
                    continue
                for field in ("graph_skill_node_ids", "source_skill_ids"):
                    for raw in term.get(field) or []:
                        sid = str(raw).strip()
                        if sid and sid not in out:
                            out.append(sid)
    return out


def _role_axis_coverage(
    plan: dict[str, Any],
    *,
    rendered_skill_ids: list[str] | None = None,
) -> dict[str, Any]:
    profile = str(plan.get("target_role_profile") or "").strip()
    required = ROLE_PROFILE_REQUIRED_SKILL_AXES.get(profile, {})
    selected_skill_text = " ".join(
        [
            " ".join(_unique_strs(plan.get("selected_skill_ids") or [])),
            " ".join(str(row.get("skill_id") or "") for row in plan.get("selected_skills") or [] if isinstance(row, dict)),
            " ".join(_unique_strs(rendered_skill_ids or [])),
        ]
    ).lower()
    covered: list[str] = []
    missing: list[str] = []
    for axis, signals in required.items():
        if any(signal.lower() in selected_skill_text for signal in signals):
            covered.append(axis)
        else:
            missing.append(axis)
    return {
        "target_role_profile": profile,
        "required_axes": sorted(required),
        "covered_axes": covered,
        "missing_axes": missing,
        "status": "not_applicable" if not required else ("covered" if not missing else "missing_axes"),
    }


def _build_traversal_sufficiency_receipt(
    *,
    proof_pool_metadata: dict[str, Any] | None,
    parsed_output: dict[str, Any] | None,
    category_count: int,
) -> dict[str, Any]:
    plan = _selected_graph_plan(proof_pool_metadata)
    selected_skills = [row for row in (plan.get("selected_skills") or []) if isinstance(row, dict)]
    selected_metrics_detail = [row for row in (plan.get("selected_metrics_detail") or []) if isinstance(row, dict)]
    rejected_skills = [row for row in (plan.get("excluded_due_to_root_cap") or []) if isinstance(row, dict)]
    rejected_metrics = [row for row in (plan.get("excluded_due_to_metric_cap") or []) if isinstance(row, dict)]
    facts = [row for row in (plan.get("facts") or []) if isinstance(row, dict)]

    selected_skill_ids = _unique_strs(
        [row.get("skill_id") for row in selected_skills] or plan.get("selected_skill_ids") or []
    )
    selected_metric_ids = _unique_strs(
        [row.get("metric_outcome_id") for row in selected_metrics_detail] or plan.get("selected_metrics") or []
    )
    rejected_skill_ids = _unique_strs(row.get("graph_evidence_id") for row in rejected_skills)
    rejected_metric_ids = _unique_strs(row.get("graph_evidence_id") for row in rejected_metrics)
    selected_root_ids = _unique_strs(
        [row.get("role_episode_bundle_id") for row in facts] or plan.get("selected_nodes") or []
    )
    selected_source_fact_ids = _unique_strs(row.get("fact_id") for row in facts)

    skill_depth_rows: list[dict[str, Any]] = []
    metrics_by_root: dict[str, int] = {}
    for row in selected_metrics_detail:
        rid = str(row.get("role_episode_bundle_id") or "").strip()
        if rid:
            metrics_by_root[rid] = metrics_by_root.get(rid, 0) + 1
    for row in selected_skills:
        rid = str(row.get("role_episode_bundle_id") or "").strip()
        sid = str(row.get("skill_id") or "").strip()
        if not sid:
            continue
        skill_depth_rows.append(
            {
                "skill_id": sid,
                "role_episode_bundle_id": rid,
                "employer_lane": str(row.get("employer_lane") or ""),
                "graph_depth": 1,
                "root_reaches_metric_depth": metrics_by_root.get(rid, 0) > 0,
                "max_path_depth_from_root": 2 if metrics_by_root.get(rid, 0) > 0 else 1,
            }
        )

    root_depth_rows = []
    for fact in facts:
        root_id = str(fact.get("role_episode_bundle_id") or fact.get("fact_id") or "").strip()
        graph_skill_count = len(_unique_strs(fact.get("graph_skill_node_ids") or []))
        metric_count = len(_unique_strs(fact.get("metric_outcome_ids") or []))
        root_depth_rows.append(
            {
                "role_episode_bundle_id": root_id,
                "fact_id": str(fact.get("fact_id") or ""),
                "employer_lane": str(fact.get("employer_lane") or ""),
                "skill_count": graph_skill_count,
                "metric_count": metric_count,
                "max_path_depth": 2 if metric_count else (1 if graph_skill_count else 0),
            }
        )

    audit: dict[str, Any] = {}
    if isinstance(parsed_output, dict):
        maybe_audit = parsed_output.get("competencies_rejected_neighbor_audit")
        if isinstance(maybe_audit, dict):
            audit = maybe_audit
    selector_candidate_labels = int(_safe_float(audit.get("candidate_label_count")) or 0)
    selector_selected = int(_safe_float(audit.get("selected_count")) or 0)
    selector_rejected = int(_safe_float(audit.get("rejected_neighbor_count")) or 0)

    candidate_nodes_visited_count = len(
        set(selected_root_ids)
        | set(selected_source_fact_ids)
        | set(selected_skill_ids)
        | set(selected_metric_ids)
        | set(rejected_skill_ids)
        | set(rejected_metric_ids)
    )
    depth_report = plan.get("graph_evidence_depth_report") if isinstance(plan.get("graph_evidence_depth_report"), dict) else {}
    pre_depth_report = (
        plan.get("graph_evidence_depth_pre_report")
        if isinstance(plan.get("graph_evidence_depth_pre_report"), dict)
        else {}
    )
    comparison_report = (
        plan.get("graph_evidence_depth_comparison_report")
        if isinstance(plan.get("graph_evidence_depth_comparison_report"), dict)
        else {}
    )
    selector_traversal = (
        plan.get("graph_traversal_receipt")
        if isinstance(plan.get("graph_traversal_receipt"), dict)
        else {}
    )
    candidate_conservation = (
        selector_traversal.get("candidate_conservation")
        if isinstance(selector_traversal.get("candidate_conservation"), dict)
        else {}
    )
    return {
        "schema_version": "competencies_graph_traversal_sufficiency_receipt_v1",
        "selector_traversal_schema_version": selector_traversal.get("schema_version") or "",
        "selector_plan_id": selector_traversal.get("plan_id") or plan.get("plan_id") or "",
        "selector_plan_digest": selector_traversal.get("plan_digest") or plan.get("plan_digest") or "",
        "candidate_conservation": candidate_conservation,
        "candidate_conservation_pass": bool(candidate_conservation.get("pass")),
        "target_role_profile": plan.get("target_role_profile") or "",
        "selection_method": plan.get("selection_method") or "",
        "candidate_nodes_visited_count": max(
            candidate_nodes_visited_count,
            int(candidate_conservation.get("role_episode_roots_total") or 0),
        ),
        "category_count": category_count,
        "selected_source_fact_count": len(selected_source_fact_ids),
        "selected_source_fact_ids": selected_source_fact_ids,
        "selected_role_episode_root_count": len(selected_root_ids),
        "selected_role_episode_root_ids": selected_root_ids,
        "selected_unique_leaf_skill_count": len(selected_skill_ids),
        "selected_leaf_skill_ids": selected_skill_ids,
        "selected_unique_metric_count": len(selected_metric_ids),
        "selected_metric_outcome_ids": selected_metric_ids,
        "rejected_sibling_skill_count": len(rejected_skill_ids),
        "rejected_sibling_skill_ids": rejected_skill_ids,
        "rejected_sibling_metric_count": len(rejected_metric_ids),
        "rejected_sibling_metric_ids": rejected_metric_ids,
        "frontier_size_by_hop_depth": selector_traversal.get("frontier_size_by_hop_depth")
        or {
            "0_role_episode_roots": len(selected_root_ids),
            "1_leaf_skill_candidates": len(set(selected_skill_ids) | set(rejected_skill_ids)),
            "2_metric_outcome_candidates": len(set(selected_metric_ids) | set(rejected_metric_ids)),
        },
        "frontier_size_by_hop_depth_detail": {
            "1_selected_leaf_skills": len(selected_skill_ids),
            "1_rejected_sibling_skills": len(rejected_skill_ids),
            "2_selected_metric_outcomes": len(selected_metric_ids),
            "2_rejected_sibling_metrics": len(rejected_metric_ids),
        },
        "graph_depth_by_selected_skill": skill_depth_rows,
        "graph_depth_by_selected_root": root_depth_rows,
        "rejected_sibling_skills": rejected_skills[:100],
        "rejected_sibling_metrics": rejected_metrics[:100],
        "selected_vs_rejected_candidate_comparison": {
            "graph_selected_leaf_skill_count": len(selected_skill_ids),
            "graph_rejected_sibling_skill_count": len(rejected_skill_ids),
            "graph_selected_metric_count": len(selected_metric_ids),
            "graph_rejected_sibling_metric_count": len(rejected_metric_ids),
            "selector_candidate_label_count": selector_candidate_labels,
            "selector_selected_count": selector_selected,
            "selector_rejected_neighbor_count": selector_rejected,
            "selector_audit_status": audit.get("audit_status") or ("present" if audit else "missing"),
        },
        "graph_evidence_depth_status": depth_report.get("status") or "",
        "graph_evidence_depth_summary": depth_report.get("summary") or "",
        "graph_evidence_depth_pre_status": pre_depth_report.get("status") or "",
        "graph_evidence_depth_comparison": comparison_report,
        "role_specific_axis_coverage": _role_axis_coverage(
            plan,
            rendered_skill_ids=_rendered_competency_skill_ids(parsed_output),
        ),
    }


def build_competencies_graph_sufficiency_receipt(
    competencies: list[Any],
    proof_pool_metadata: dict[str, Any] | None = None,
    parsed_output: dict[str, Any] | None = None,
    *,
    jd_text: str = "",
    briefing_text: str = "",
    x1d_judges: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Summarize rendered category evidence plus graph traversal breadth/depth."""
    categories: list[dict[str, Any]] = []
    fact_to_categories: dict[str, list[str]] = {}
    confidence_values: list[float] = []
    missing_confidence: list[str] = []
    category_confidence_values: list[float] = []

    for idx, cat in enumerate(competencies or []):
        label = _category_label(cat) or f"idx{idx}"
        source_fact_ids = sorted(set(_cat_source_fact_ids(cat)))
        graph_skill_node_ids = sorted(set(_cat_graph_nodes(cat)))
        score = _cat_score(cat)
        if score is None:
            missing_confidence.append(label)
        else:
            confidence_values.append(score)
        for fid in source_fact_ids:
            fact_to_categories.setdefault(fid, []).append(label)
        categories.append(
            {
                "category_label": label,
                "source_fact_ids": source_fact_ids,
                "graph_skill_node_ids": graph_skill_node_ids,
                "confidence": score,
            }
        )

    category_count = len(categories)
    dominant_source_fact_id = ""
    dominant_category_count = 0
    if fact_to_categories:
        dominant_source_fact_id, labels = max(
            fact_to_categories.items(),
            key=lambda kv: (len(kv[1]), kv[0]),
        )
        dominant_category_count = len(labels)
    dominant_share = (
        round(dominant_category_count / category_count, 4)
        if category_count
        else 0.0
    )
    unique_confidence_values = sorted(set(confidence_values))
    judge_score, judge_scope = _average_judge_score(x1d_judges)
    for idx, cat in enumerate(competencies or []):
        cat_receipt = categories[idx]
        label = str(cat_receipt.get("category_label") or f"idx{idx}")
        source_fact_ids = list(cat_receipt.get("source_fact_ids") or [])
        graph_skill_node_ids = list(cat_receipt.get("graph_skill_node_ids") or [])
        selector_score = _norm_score(cat_receipt.get("confidence"))
        category_text = _category_text(cat)
        graph_path_specificity = round(_clamp01(len(set(graph_skill_node_ids)) / 3.0), 4)
        source_fact_diversity = round(_clamp01(len(set(source_fact_ids)) / 2.0), 4)
        jd_brief_alignment = _specific_alignment_score(category_text, jd_text, briefing_text)
        generic_penalty = _generic_phrase_penalty(category_text)
        reuse_penalty = _fact_reuse_penalty(
            source_fact_ids,
            dominant_source_fact_id=dominant_source_fact_id,
            dominant_share=dominant_share,
        )
        weighted_components = [
            (graph_path_specificity, 0.25),
            (source_fact_diversity, 0.20),
            (selector_score, 0.25),
            (jd_brief_alignment, 0.15),
        ]
        if judge_score is not None:
            weighted_components.append((judge_score, 0.15))
        numerator = sum((value or 0.0) * weight for value, weight in weighted_components if value is not None)
        denominator = sum(weight for value, weight in weighted_components if value is not None)
        composite = _clamp01((numerator / denominator if denominator else 0.0) - generic_penalty - reuse_penalty)
        composite = round(composite, 4)
        category_confidence_values.append(composite)
        cat_receipt["confidence_breakdown"] = {
            "composite_confidence": composite,
            "graph_path_specificity": graph_path_specificity,
            "source_fact_diversity": source_fact_diversity,
            "selector_score": selector_score,
            "judge_score": judge_score,
            "judge_score_scope": judge_scope,
            "judge_score_available": judge_score is not None,
            "jd_brief_alignment": jd_brief_alignment,
            "penalties": {
                "generic_phrase_penalty": generic_penalty,
                "fact_reuse_penalty": reuse_penalty,
            },
        }
    return {
        "schema_version": "competencies_graph_sufficiency_receipt_v1",
        "category_count": category_count,
        "categories": categories,
        "source_fact_usage": {
            fid: {
                "category_count": len(labels),
                "category_labels": labels,
            }
            for fid, labels in sorted(fact_to_categories.items())
        },
        "dominant_source_fact_id": dominant_source_fact_id,
        "dominant_source_fact_category_count": dominant_category_count,
        "dominant_source_fact_category_share": dominant_share,
        "source_fact_concentration_threshold": SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE,
        "confidence_values": confidence_values,
        "unique_confidence_values": unique_confidence_values,
        "category_confidence_values": category_confidence_values,
        "unique_category_confidence_values": sorted(set(category_confidence_values)),
        "missing_confidence_category_labels": missing_confidence,
        "confidence_nonconstant": (
            not missing_confidence
            and (category_count <= 1 or len(set(category_confidence_values)) > 1)
        ),
        "traversal_sufficiency_receipt": _build_traversal_sufficiency_receipt(
            proof_pool_metadata=proof_pool_metadata,
            parsed_output=parsed_output,
            category_count=category_count,
        ),
    }


def check_source_fact_concentration_limit(
    competencies: list[Any],
    *,
    max_category_share: float = SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE,
) -> CompQualityResult:
    receipt = build_competencies_graph_sufficiency_receipt(competencies)
    share = float(receipt.get("dominant_source_fact_category_share") or 0.0)
    passed = share <= max_category_share
    return CompQualityResult(
        gate_id="x2_competencies_source_fact_concentration_limit",
        passed=passed,
        observed_value={
            "dominant_source_fact_id": receipt.get("dominant_source_fact_id"),
            "dominant_source_fact_category_share": share,
            "dominant_source_fact_category_count": receipt.get("dominant_source_fact_category_count"),
            "category_count": receipt.get("category_count"),
        },
        threshold=f"dominant source_fact_id category share <= {max_category_share:.2f}",
        failure_reason=(
            None
            if passed
            else (
                "dominant source fact supports too many competency categories: "
                f"{receipt.get('dominant_source_fact_id')} share={share:.2f}"
            )
        ),
        signals=[str(receipt.get("dominant_source_fact_id") or "")],
    )


def check_per_category_confidence_nonconstant(competencies: list[Any]) -> CompQualityResult:
    receipt = build_competencies_graph_sufficiency_receipt(competencies)
    missing = list(receipt.get("missing_confidence_category_labels") or [])
    unique_values = list(receipt.get("unique_category_confidence_values") or [])
    unique_selector_values = list(receipt.get("unique_confidence_values") or [])
    category_count = int(receipt.get("category_count") or 0)
    passed = bool(receipt.get("confidence_nonconstant")) and (
        category_count <= 1 or len(unique_selector_values) > 1
    )
    return CompQualityResult(
        gate_id="x2_competencies_per_category_confidence_nonconstant",
        passed=passed,
        observed_value={
            "missing_confidence_category_labels": missing,
            "unique_selector_confidence_values": unique_selector_values,
            "unique_confidence_values": unique_values,
            "category_count": category_count,
        },
        threshold=(
            "every category has numeric selector confidence/selection_score and decomposed "
            "per-category confidence values are nonconstant"
        ),
        failure_reason=(
            None
            if passed
            else (
                "per-category confidence is missing or constant; "
                f"missing={missing[:6]} unique_values={unique_values}"
            )
        ),
        signals=missing[:6] or [str(x) for x in unique_values[:6]],
    )


def check_competencies_rejected_neighbor_audit_present(
    parsed_output: dict[str, Any] | None,
    proof_pool_metadata: dict[str, Any] | None = None,
) -> CompQualityResult:
    audit: dict[str, Any] = {}
    if isinstance(parsed_output, dict):
        raw_audit = parsed_output.get("competencies_rejected_neighbor_audit")
        if isinstance(raw_audit, dict):
            audit = raw_audit
    schema_ok = audit.get("schema_version") == "competencies_rejected_neighbor_audit_v1"
    try:
        candidate_label_count = int(audit.get("candidate_label_count") or 0)
    except (TypeError, ValueError):
        candidate_label_count = 0
    try:
        candidate_variant_count = int(audit.get("candidate_variant_count") or 0)
    except (TypeError, ValueError):
        candidate_variant_count = 0
    try:
        selected_count = int(audit.get("selected_count") or 0)
    except (TypeError, ValueError):
        selected_count = 0
    try:
        rejected_count = int(audit.get("rejected_neighbor_count") or 0)
    except (TypeError, ValueError):
        rejected_count = 0
    passed = (
        schema_ok
        and candidate_label_count > selected_count
        and rejected_count > 0
        and candidate_variant_count >= candidate_label_count
    )
    graph_candidate_receipt = {}
    if isinstance(proof_pool_metadata, dict) and isinstance(
        proof_pool_metadata.get("graph_candidate_receipt"), dict
    ):
        graph_candidate_receipt = proof_pool_metadata.get("graph_candidate_receipt") or {}
    graph_candidate_schema_ok = graph_candidate_receipt.get("schema_version") == "graph_candidate_receipt_v1"
    graph_rejected_count = int(graph_candidate_receipt.get("rejected_candidate_count") or 0)
    graph_conservation_pass = bool(graph_candidate_receipt.get("candidate_conservation_pass"))
    graph_candidate_pass = graph_candidate_schema_ok and graph_conservation_pass and graph_rejected_count > 0
    passed = passed or graph_candidate_pass
    return CompQualityResult(
        gate_id="x2_competencies_rejected_neighbor_audit_present",
        passed=passed,
        observed_value={
            "schema_ok": schema_ok,
            "audit_status": audit.get("audit_status") or "missing",
            "candidate_label_count": candidate_label_count,
            "candidate_variant_count": candidate_variant_count,
            "selected_count": selected_count,
            "rejected_neighbor_count": rejected_count,
            "graph_candidate_receipt_schema_ok": graph_candidate_schema_ok,
            "graph_candidate_conservation_pass": graph_conservation_pass,
            "graph_rejected_candidate_count": graph_rejected_count,
        },
        threshold=(
            "competencies_rejected_neighbor_audit_v1 with rejected neighbors OR "
            "graph_candidate_receipt_v1 with conserved selected/rejected candidates"
        ),
        failure_reason=(
            None
            if passed
            else (
                "competencies graph selector did not prove rejected-neighbor breadth; "
                f"schema_ok={schema_ok} candidate_labels={candidate_label_count} "
                f"selected={selected_count} rejected={rejected_count} "
                f"graph_schema_ok={graph_candidate_schema_ok} graph_rejected={graph_rejected_count}"
            )
        ),
        signals=[str(x.get("category_label") or "") for x in audit.get("rejected_neighbors", [])[:6]]
        if isinstance(audit.get("rejected_neighbors"), list)
        else [],
    )


def check_competencies_graph_traversal_sufficiency(
    competencies: list[Any],
    proof_pool_metadata: dict[str, Any] | None,
    parsed_output: dict[str, Any] | None,
    *,
    jd_text: str = "",
    briefing_text: str = "",
    x1d_judges: list[dict[str, Any]] | None = None,
) -> CompQualityResult:
    receipt = build_competencies_graph_sufficiency_receipt(
        competencies,
        proof_pool_metadata,
        parsed_output,
        jd_text=jd_text,
        briefing_text=briefing_text,
        x1d_judges=x1d_judges,
    )
    traversal = receipt.get("traversal_sufficiency_receipt")
    if not isinstance(traversal, dict):
        traversal = {}
    role_axes = traversal.get("role_specific_axis_coverage")
    role_axes = role_axes if isinstance(role_axes, dict) else {}

    selected_count = int(traversal.get("selected_unique_leaf_skill_count") or 0)
    metric_count = int(traversal.get("selected_unique_metric_count") or 0)
    source_fact_count = int(traversal.get("selected_source_fact_count") or 0)
    candidate_count = int(traversal.get("candidate_nodes_visited_count") or 0)
    rejected_skill_count = int(traversal.get("rejected_sibling_skill_count") or 0)
    conservation = traversal.get("candidate_conservation")
    conservation = conservation if isinstance(conservation, dict) else {}
    conservation_pass = bool(traversal.get("candidate_conservation_pass"))
    unexplained_roots = int(conservation.get("role_episode_roots_unexplained") or 0)
    rejected_roots = int(conservation.get("role_episode_roots_rejected") or 0)
    depth_status = str(traversal.get("graph_evidence_depth_status") or "").strip().lower()
    missing_axes = [str(x) for x in (role_axes.get("missing_axes") or []) if str(x).strip()]
    required_axes = [str(x) for x in (role_axes.get("required_axes") or []) if str(x).strip()]

    failures: list[str] = []
    if traversal.get("schema_version") != "competencies_graph_traversal_sufficiency_receipt_v1":
        failures.append("missing_traversal_receipt_schema")
    if traversal.get("selector_traversal_schema_version") != "graph_traversal_receipt_v1":
        failures.append("missing_selector_emitted_traversal_receipt")
    if not conservation_pass:
        failures.append(f"candidate_conservation_failed:unexplained_roots={unexplained_roots}")
    if rejected_roots <= 0:
        failures.append("no_rejected_eligible_roots")
    if depth_status != "judge_grade":
        failures.append(f"depth_status:{depth_status or 'missing'}")
    if selected_count < MIN_SELECTED_UNIQUE_LEAF_SKILLS:
        failures.append(f"selected_leaf_skills:{selected_count}<{MIN_SELECTED_UNIQUE_LEAF_SKILLS}")
    if source_fact_count < MIN_SELECTED_UNIQUE_SOURCE_FACTS:
        failures.append(f"source_facts:{source_fact_count}<{MIN_SELECTED_UNIQUE_SOURCE_FACTS}")
    if metric_count < MIN_SELECTED_UNIQUE_METRICS:
        failures.append(f"metric_outcomes:{metric_count}<{MIN_SELECTED_UNIQUE_METRICS}")
    if rejected_skill_count <= 0:
        failures.append("no_rejected_sibling_skills")
    if candidate_count <= selected_count:
        failures.append(f"candidate_nodes_not_broader_than_selected:{candidate_count}<={selected_count}")
    if required_axes and missing_axes:
        failures.append(f"missing_role_axes:{','.join(missing_axes)}")

    passed = not failures
    return CompQualityResult(
        gate_id="x2_competencies_graph_traversal_sufficiency",
        passed=passed,
        observed_value={
            "target_role_profile": traversal.get("target_role_profile") or "",
            "candidate_nodes_visited_count": candidate_count,
            "selected_unique_leaf_skill_count": selected_count,
            "selected_unique_metric_count": metric_count,
            "selected_source_fact_count": source_fact_count,
            "rejected_sibling_skill_count": rejected_skill_count,
            "candidate_conservation": conservation,
            "rejected_eligible_root_count": rejected_roots,
            "frontier_size_by_hop_depth": traversal.get("frontier_size_by_hop_depth") or {},
            "graph_evidence_depth_status": traversal.get("graph_evidence_depth_status") or "",
            "missing_role_axes": missing_axes,
        },
        threshold=(
            f">={MIN_SELECTED_UNIQUE_LEAF_SKILLS} unique leaf skills, "
            f">={MIN_SELECTED_UNIQUE_SOURCE_FACTS} source facts, "
            f">={MIN_SELECTED_UNIQUE_METRICS} metrics, rejected siblings present, "
            "judge_grade depth, and required role axes covered"
        ),
        failure_reason=None if passed else "; ".join(failures),
        signals=failures[:8],
    )


def check_competencies_graph_granularity_gates(
    competencies: list[Any],
    proof_pool_metadata: dict[str, Any] | None,
    parsed_output: dict[str, Any] | None,
    *,
    jd_text: str = "",
    briefing_text: str = "",
    x1d_judges: list[dict[str, Any]] | None = None,
) -> CompQualityResult:
    receipt = build_competencies_graph_sufficiency_receipt(
        competencies,
        proof_pool_metadata,
        parsed_output,
        jd_text=jd_text,
        briefing_text=briefing_text,
        x1d_judges=x1d_judges,
    )
    categories = [row for row in (receipt.get("categories") or []) if isinstance(row, dict)]
    missing_leaf_skill_categories: list[str] = []
    missing_source_fact_categories: list[str] = []
    for row in categories:
        label = str(row.get("category_label") or "")
        if len(_unique_strs(row.get("graph_skill_node_ids") or [])) < MIN_UNIQUE_LEAF_SKILLS_PER_CATEGORY:
            missing_leaf_skill_categories.append(label)
        if len(_unique_strs(row.get("source_fact_ids") or [])) < MIN_UNIQUE_SOURCE_FACTS_PER_CATEGORY:
            missing_source_fact_categories.append(label)

    dominant_share = float(receipt.get("dominant_source_fact_category_share") or 0.0)
    traversal = receipt.get("traversal_sufficiency_receipt")
    role_axes = traversal.get("role_specific_axis_coverage") if isinstance(traversal, dict) else {}
    role_axes = role_axes if isinstance(role_axes, dict) else {}
    missing_axes = [str(x) for x in (role_axes.get("missing_axes") or []) if str(x).strip()]
    required_axes = [str(x) for x in (role_axes.get("required_axes") or []) if str(x).strip()]

    failures: list[str] = []
    if missing_leaf_skill_categories:
        failures.append(f"categories_missing_leaf_skills:{missing_leaf_skill_categories[:6]}")
    if missing_source_fact_categories:
        failures.append(f"categories_missing_source_facts:{missing_source_fact_categories[:6]}")
    if dominant_share > SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE:
        failures.append(
            "dominant_source_fact_share:"
            f"{dominant_share:.2f}>{SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE:.2f}"
        )
    if required_axes and missing_axes:
        failures.append(f"missing_role_axes:{','.join(missing_axes)}")

    passed = not failures
    return CompQualityResult(
        gate_id="x2_competencies_graph_granularity_gates",
        passed=passed,
        observed_value={
            "category_count": receipt.get("category_count"),
            "min_unique_leaf_skills_per_category": MIN_UNIQUE_LEAF_SKILLS_PER_CATEGORY,
            "categories_missing_leaf_skills": missing_leaf_skill_categories,
            "min_unique_source_facts_per_category": MIN_UNIQUE_SOURCE_FACTS_PER_CATEGORY,
            "categories_missing_source_facts": missing_source_fact_categories,
            "dominant_source_fact_id": receipt.get("dominant_source_fact_id"),
            "dominant_source_fact_category_share": dominant_share,
            "source_fact_concentration_threshold": SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE,
            "target_role_profile": role_axes.get("target_role_profile") or "",
            "required_role_axes": required_axes,
            "missing_role_axes": missing_axes,
        },
        threshold=(
            "each category has >=1 leaf skill and >=1 source fact, dominant fact reuse "
            f"<= {SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE:.2f}, and JD-critical axes covered"
        ),
        failure_reason=None if passed else "; ".join(failures),
        signals=failures[:8],
    )


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
        if not _cat_graph_nodes_direct(c)
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
        has_facts = bool(_cat_source_fact_ids_direct(c))
        has_lineage = bool(_cat_graph_nodes_direct(c)) and bool(_cat_bundle_id(c))
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
    """A generic category label with no graph-backed terms and no bundle binding fails."""
    violations: list[str] = []
    for cat in (competencies or []):
        label = _category_label(cat)
        if label not in GENERIC_CATEGORIES_REQUIRING_GRAPH:
            continue
        graph_terms = sum(1 for t in _category_terms(cat) if _is_graph_backed(t))
        if graph_terms < GENERIC_CATEGORY_MIN_GRAPH_TERMS and not _cat_bundle_id(cat):
            violations.append(label)
    passed = not violations
    return CompQualityResult(
        gate_id="x2_generic_taxonomy_only_category_forbidden",
        passed=passed,
        observed_value=violations if violations else "none",
        threshold="generic categories require graph-backed terms or bundle binding",
        failure_reason=None if passed else f"Generic taxonomy-only categories: {violations}",
        signals=violations,
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
    competencies: list[Any], *, min_families: int = 8
) -> CompQualityResult:
    """Required-coverage gate: at least min_families required capability families present."""
    return CompQualityResult(
        gate_id="x2_required_capability_families_covered",
        passed=check_competencies_capability_family_coverage(competencies, min_families=min_families).passed,
        observed_value=check_competencies_capability_family_coverage(competencies, min_families=min_families).observed_value,
        threshold=f">={min_families} of {len(REQUIRED_CAPABILITY_FAMILIES)} required capability families",
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
    "SOURCE_FACT_CONCENTRATION_MAX_CATEGORY_SHARE",
    "build_competencies_graph_sufficiency_receipt",
    "check_capability_bundles_in_proof_pool",
    "check_competencies_archive_ngram_overlap",
    "check_competencies_base_ngram_overlap",
    "check_competencies_capability_family_coverage",
    "check_competencies_e0_ngram_overlap",
    "check_competencies_generic_category_has_graph_terms",
    "check_competencies_graph_granularity_gates",
    "check_competencies_graph_traversal_sufficiency",
    "check_competencies_no_default_fid_proof",
    "check_competencies_rejected_neighbor_audit_present",
    "check_competency_bundle_id_per_category",
    "check_competency_rigor_floor",
    "check_default_fid_only_support_forbidden",
    "check_generic_taxonomy_only_category_forbidden",
    "check_graph_skill_node_ids_per_category",
    "check_jd_only_skill_forbidden",
    "check_partner_architecture_bundle_present",
    "check_partner_architecture_terms_require_bundle",
    "check_partner_terms_source_roots",
    "check_per_category_confidence_nonconstant",
    "check_required_capability_families_covered",
    "check_source_fact_ids_or_graph_lineage_per_category",
    "check_source_fact_concentration_limit",
    "check_technical_density_floor",
    "competencies_to_text_blob",
    "competency_bundle_consumption_active",
    "selected_graph_evidence_depth_result",
]
