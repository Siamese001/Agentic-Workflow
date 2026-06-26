"""Narrative alignment X2 gate helpers (Headline/Competencies/Narrative Rigor plan).

Implements deterministic quality gates for Unify and IBM narrative sections:
- x2_narrative_seniority_floor: strong action verb + authority scope signal required
- x2_narrative_no_consulting_language: consulting phrase blocklist (HARD FAIL)
- x2_narrative_technical_specificity_floor: ≥1 named mechanism/technology token (HARD FAIL)
- x2_narrative_not_bullet_recap: ≤3 shared 5-grams with companion bullet texts (WARN)
- x2_narrative_upstream_graph_proof_required: upstream graph_skill_node_ids gate must pass (WARN)
- x2_narrative_base_prose_ngram_overlap: ≤25% 4-gram overlap with base role_narrative (WARN)
- x2_narrative_e0_ngram_overlap: ≤20% overlap with E0 examples (WARN)
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from apps_rg.runtime.validators.bullet_ngram_overlap_x2 import (
    compute_max_ngram_overlap,
    compute_max_ngram_overlap_multi_reference,
)

# ---------------------------------------------------------------------------
# Weak verbs and consulting phrases
# ---------------------------------------------------------------------------

NARRATIVE_WEAK_VERBS: frozenset[str] = frozenset({
    "supported", "helped", "assisted", "contributed", "participated",
    "worked", "involved", "utilized", "leveraged",
})

NARRATIVE_CONSULTING_PHRASES: frozenset[str] = frozenset({
    "drive strategic value",
    "ensure alignment",
    "leveraged best practices",
    "worked closely with",
    "partnered with stakeholders",
    "aligned with the business",
    "facilitating collaboration",
    "drove alignment",
    "drove strategic alignment",
    "enabling the business",
    "providing thought leadership",
    "thought leadership",
    "best practices",
})

# Strong verbs that signal senior executive ownership
NARRATIVE_STRONG_VERBS: frozenset[str] = frozenset({
    "owned", "drove", "scaled", "championed", "productized", "operationalized",
    "established", "anchored", "stewarded", "originated", "architected",
    "engineered", "directed", "structured", "converted", "deployed", "designed",
    "launched", "modernized", "forged", "built", "standardized", "unified",
    "accelerated", "transformed", "generated", "delivered", "implemented",
    "oversaw", "managed", "steered", "pioneered", "defined", "spearheaded",
    "led", "created",
})

# Authority scope signals
NARRATIVE_AUTHORITY_SIGNALS: frozenset[str] = frozenset({
    "platform", "enterprise", "mandate", "roadmap", "infrastructure", "organization",
    "architecture", "governance", "production", "regulated", "commercialization",
    "productization", "strategy", "operating", "model",
})

# Mechanism vocabulary for technical specificity
MECHANISM_VOCAB: frozenset[str] = frozenset({
    # AI / ML specific
    "agentic", "llm", "rag", "graphrag", "embedding", "vector", "retrieval",
    "orchestration", "evaluation", "eval", "fine-tuning", "inference",
    # Platform / infra
    "lakehouse", "databricks", "microservices", "kubernetes", "spark",
    "streaming", "pipeline", "runtime", "gateway", "api", "aws",
    "bi", "dashboard", "dashboards",
    # Engineering practices
    "telemetry", "tracing", "observability", "monitoring", "cicd", "devops",
    "lineage",
    # Domain-specific
    "ccar", "basel", "insuretech", "underwriting", "actuarial", "hpc",
    "hyperscaler", "hyperscalers",
})

BASE_NGRAM_THRESHOLD = 0.25
E0_NGRAM_THRESHOLD = 0.20
BULLET_RECAP_MAX_SHARED_NGRAMS = 3
NGRAM_SIZE_OVERLAP = 4
NGRAM_SIZE_RECAP = 5

# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------


@dataclass
class NarrativeQualityResult:
    gate_id: str
    passed: bool
    observed_value: Any
    threshold: Any
    failure_reason: str | None
    signals: list[str]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _first_word(text: str) -> str:
    tokens = _tokenize(text)
    return tokens[0] if tokens else ""


# ---------------------------------------------------------------------------
# Gate: seniority floor (strong verb + authority scope)
# ---------------------------------------------------------------------------


def check_narrative_seniority_floor(text: str) -> NarrativeQualityResult:
    """Require ≥1 strong action verb AND ≥1 authority scope signal in the narrative."""
    tokens = set(_tokenize(text))
    strong_hits = list(NARRATIVE_STRONG_VERBS & tokens)
    authority_hits = list(NARRATIVE_AUTHORITY_SIGNALS & tokens)

    first_w = _first_word(text)
    weak_opener = first_w in NARRATIVE_WEAK_VERBS

    passed = bool(strong_hits) and bool(authority_hits) and not weak_opener
    issues: list[str] = []
    if not strong_hits:
        issues.append("no_strong_verb")
    if not authority_hits:
        issues.append("no_authority_scope_signal")
    if weak_opener:
        issues.append(f"weak_opener:{first_w!r}")

    return NarrativeQualityResult(
        gate_id="x2_narrative_seniority_floor",
        passed=passed,
        observed_value={"strong_verbs": strong_hits, "authority": authority_hits, "issues": issues},
        threshold="≥1 strong verb + ≥1 authority scope signal, no weak opener",
        failure_reason=(
            None
            if passed
            else (
                f"Seniority floor failed: {', '.join(issues)}. "
                "Narrative must open with a senior executive ownership verb "
                "(Owned, Drove, Scaled, Championed, etc.) and reference a platform/mandate/architecture scope."
            )
        ),
        signals=issues,
    )


# ---------------------------------------------------------------------------
# Gate: no consulting language
# ---------------------------------------------------------------------------


def check_narrative_no_consulting_language(text: str) -> NarrativeQualityResult:
    """Fail if narrative contains consulting phrase blocklist patterns."""
    text_low = text.lower()
    found: list[str] = [phrase for phrase in NARRATIVE_CONSULTING_PHRASES if phrase in text_low]
    passed = len(found) == 0
    return NarrativeQualityResult(
        gate_id="x2_narrative_no_consulting_language",
        passed=passed,
        observed_value=found if found else "none",
        threshold="zero consulting phrases",
        failure_reason=(
            None
            if passed
            else (
                f"Consulting language detected: {found}. "
                "Remove these vague consulting phrases and replace with specific mechanism vocabulary."
            )
        ),
        signals=[f"consulting:{f}" for f in found],
    )


# ---------------------------------------------------------------------------
# Gate: technical specificity floor (named mechanism token)
# ---------------------------------------------------------------------------


def check_narrative_technical_specificity(
    text: str,
    mechanism_vocab: frozenset[str] | None = None,
) -> NarrativeQualityResult:
    """Require ≥1 named mechanism or technology token from the mechanism vocab."""
    vocab = mechanism_vocab if mechanism_vocab is not None else MECHANISM_VOCAB
    tokens = set(_tokenize(text))
    hits = list(vocab & tokens)
    passed = len(hits) >= 1
    return NarrativeQualityResult(
        gate_id="x2_narrative_technical_specificity_floor",
        passed=passed,
        observed_value=hits if hits else "none",
        threshold="≥1 named mechanism/technology token",
        failure_reason=(
            None
            if passed
            else (
                "No named mechanism or technology token found. "
                "Narrative must name at least one specific mechanism, technology, or platform "
                "(e.g. agentic, LLM, RAG, Databricks, Kubernetes, pipeline, telemetry, CCAR)."
            )
        ),
        signals=hits,
    )


# ---------------------------------------------------------------------------
# Gate: not bullet recap (n-gram overlap with companion bullets)
# ---------------------------------------------------------------------------


def check_narrative_not_bullet_recap(
    narrative_text: str,
    bullet_texts: list[str],
    *,
    max_shared_ngrams: int = BULLET_RECAP_MAX_SHARED_NGRAMS,
    warn_only: bool = True,
) -> NarrativeQualityResult:
    """Fail if narrative shares > max_shared_ngrams 5-grams with any companion bullet."""
    if not bullet_texts:
        return NarrativeQualityResult(
            gate_id="x2_narrative_not_bullet_recap",
            passed=True,
            observed_value=0.0,
            threshold=f"<={max_shared_ngrams} shared 5-grams with bullets",
            failure_reason=None,
            signals=[],
        )
    overlap = compute_max_ngram_overlap_multi_reference(narrative_text, bullet_texts, n=5)
    n_narrative_ngrams = max(1, len(_tokenize(narrative_text)) - 4)
    shared_count = int(round(overlap * n_narrative_ngrams))
    passed_gate = shared_count <= max_shared_ngrams
    passed = passed_gate or warn_only
    return NarrativeQualityResult(
        gate_id="x2_narrative_not_bullet_recap",
        passed=passed,
        observed_value={"max_5gram_overlap": round(overlap, 4), "est_shared_ngrams": shared_count},
        threshold=f"<={max_shared_ngrams} shared 5-grams (WARN={'Y' if warn_only else 'N'})",
        failure_reason=(
            None
            if passed_gate
            else (
                f"Narrative shares ~{shared_count} 5-grams with bullets "
                f"(threshold: {max_shared_ngrams}). "
                "Narrative must provide strategic mandate framing, not echo bullet content."
            )
        ),
        signals=["warn_mode"] if (warn_only and not passed_gate) else [],
    )


# ---------------------------------------------------------------------------
# Gate: upstream graph proof required
# ---------------------------------------------------------------------------


def check_narrative_upstream_graph_proof_bundle(
    upstream_x2_results: list[dict[str, Any]],
    *,
    gate_id_to_check: str = "x2_bullet_graph_skill_node_ids_required",
    warn_only: bool = True,
) -> NarrativeQualityResult:
    """Narrative should only pass when upstream graph_skill_node_ids bullet gate passed."""
    relevant = [r for r in (upstream_x2_results or []) if r.get("gate_id") == gate_id_to_check]
    if not relevant:
        passed_gate = False
        observed = "upstream_gate_not_found"
    else:
        passed_gate = all(bool(r.get("pass_")) for r in relevant)
        observed = [{"gate_id": r.get("gate_id"), "pass": r.get("pass_")} for r in relevant]

    passed = passed_gate or warn_only
    return NarrativeQualityResult(
        gate_id="x2_narrative_upstream_graph_proof_required",
        passed=passed,
        observed_value=observed,
        threshold=f"upstream {gate_id_to_check} == PASS (WARN={'Y' if warn_only else 'N'})",
        failure_reason=(
            None
            if passed_gate
            else (
                f"Upstream gate {gate_id_to_check!r} did not pass. "
                "Narrative proof authority depends on bullet graph_skill_node_ids being validated. "
                "Resolve bullet X2 gates before promoting narrative to HARD FAIL."
            )
        ),
        signals=["warn_mode"] if (warn_only and not passed_gate) else [],
    )


# ---------------------------------------------------------------------------
# Gate: base prose n-gram overlap (anti-hydration)
# ---------------------------------------------------------------------------


def check_narrative_base_prose_ngram_overlap(
    narrative_text: str,
    base_narrative_texts: list[str],
    *,
    threshold: float = BASE_NGRAM_THRESHOLD,
    warn_only: bool = True,
) -> NarrativeQualityResult:
    """Fail if narrative has > threshold 4-gram overlap with base resume role_narrative."""
    if not base_narrative_texts:
        return NarrativeQualityResult(
            gate_id="x2_narrative_base_prose_ngram_overlap",
            passed=True,
            observed_value=0.0,
            threshold=f"<={threshold:.0%} 4-gram overlap with base role_narrative",
            failure_reason=None,
            signals=[],
        )
    overlap = compute_max_ngram_overlap_multi_reference(
        narrative_text, base_narrative_texts, n=NGRAM_SIZE_OVERLAP
    )
    passed_gate = overlap <= threshold
    passed = passed_gate or warn_only
    return NarrativeQualityResult(
        gate_id="x2_narrative_base_prose_ngram_overlap",
        passed=passed,
        observed_value=round(overlap, 4),
        threshold=f"<={threshold:.0%} 4-gram overlap with base role_narrative (WARN={'Y' if warn_only else 'N'})",
        failure_reason=(
            None
            if passed_gate
            else (
                f"Base narrative n-gram overlap {overlap:.1%} exceeds threshold {threshold:.0%}. "
                "Narrative must be generated organically from C0 facts, not from base resume prose."
            )
        ),
        signals=["warn_mode"] if (warn_only and not passed_gate) else [],
    )


# ---------------------------------------------------------------------------
# Gate: E0 n-gram overlap (anti-leakage)
# ---------------------------------------------------------------------------


def check_narrative_e0_ngram_overlap(
    narrative_text: str,
    e0_texts: list[str],
    *,
    threshold: float = E0_NGRAM_THRESHOLD,
    warn_only: bool = True,
) -> NarrativeQualityResult:
    """Fail if narrative has > threshold 4-gram overlap with E0 example texts."""
    if not e0_texts:
        return NarrativeQualityResult(
            gate_id="x2_narrative_e0_ngram_overlap",
            passed=True,
            observed_value=0.0,
            threshold=f"<={threshold:.0%} 4-gram overlap with E0 examples",
            failure_reason=None,
            signals=[],
        )
    overlap = compute_max_ngram_overlap_multi_reference(
        narrative_text, e0_texts, n=NGRAM_SIZE_OVERLAP
    )
    passed_gate = overlap <= threshold
    passed = passed_gate or warn_only
    return NarrativeQualityResult(
        gate_id="x2_narrative_e0_ngram_overlap",
        passed=passed,
        observed_value=round(overlap, 4),
        threshold=f"<={threshold:.0%} 4-gram overlap with E0 examples (WARN={'Y' if warn_only else 'N'})",
        failure_reason=(
            None
            if passed_gate
            else (
                f"E0 n-gram overlap {overlap:.1%} exceeds threshold {threshold:.0%}. "
                "Narrative appears to reuse E0 example phrasing."
            )
        ),
        signals=["warn_mode"] if (warn_only and not passed_gate) else [],
    )


__all__ = [
    "BASE_NGRAM_THRESHOLD",
    "BULLET_RECAP_MAX_SHARED_NGRAMS",
    "E0_NGRAM_THRESHOLD",
    "MECHANISM_VOCAB",
    "NARRATIVE_CONSULTING_PHRASES",
    "NARRATIVE_STRONG_VERBS",
    "NARRATIVE_WEAK_VERBS",
    "NarrativeQualityResult",
    "NGRAM_SIZE_OVERLAP",
    "check_narrative_base_prose_ngram_overlap",
    "check_narrative_e0_ngram_overlap",
    "check_narrative_no_consulting_language",
    "check_narrative_not_bullet_recap",
    "check_narrative_seniority_floor",
    "check_narrative_technical_specificity",
    "check_narrative_upstream_graph_proof_bundle",
]
