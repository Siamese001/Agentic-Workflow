"""Quality floor X2 gate helpers for bullet generation (W4: Bullet Proof Bundle Redesign).

Implements deterministic proxy gates (no LLM required):
- x2_bullet_seniority_floor: strong action verb + scale signal required
- x2_bullet_technical_specificity_floor: named mechanism, technology, or domain term required
- x2_no_generic_consulting_substitution: extended GENERIC_FILLER blocklist for consulting-speak

These gates catch low-quality bullets that passed structural gates but lack the depth
of an SVP Engineering-level candidate narrative.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Sequence

# ---------------------------------------------------------------------------
# Seniority floor: strong action verbs and organizational scale signals
# ---------------------------------------------------------------------------

STRONG_ACTION_VERBS: frozenset[str] = frozenset({
    "architected", "engineered", "operationalized", "directed", "structured",
    "converted", "deployed", "designed", "established", "led", "built",
    "launched", "modernized", "forged", "drove", "productized", "standardized",
    "unified", "accelerated", "scaled", "transformed", "generated", "delivered",
    "created", "implemented", "developed", "oversaw", "managed", "steered",
    "pioneered", "defined", "spearheaded", "owned", "headed", "championed",
})

WEAK_ACTION_VERBS: frozenset[str] = frozenset({
    "supported", "helped", "assisted", "worked on", "participated", "contributed",
    "involved in", "part of", "utilized",
})

SCALE_SIGNALS: frozenset[str] = frozenset({
    "fortune 500", "enterprise", "financial institutions", "regulated", "global",
    "large-scale", "enterprise-scale", "multi-year", "hyperscaler", "cross-functional",
    "regulated financial", "fortune", "billion", "multi-million",
})

_NUMERIC_SIGNAL_PATTERN = re.compile(
    r"\$\d+[mk]?\b|\b\d+[\.,]\d+%|\b\d+%|\b\d+x\b|\b\d+\s*(?:percent|million|billion)\b",
    re.IGNORECASE,
)
_FIRST_WORD_RE = re.compile(r"^\s*(\w+)")

SENIORITY_FLOOR_SCORE = 1  # Minimum score to pass the seniority gate


def _score_bullet_seniority(bullet_text: str) -> tuple[int, list[str]]:
    """Compute a deterministic seniority proxy score for a bullet.

    Returns (score, reasons) where:
    - +1 for strong action verb at start
    - +1 for organizational scale signal present
    - +1 for numeric metric present ($XM, XX%, etc.)
    - -1 for weak action verb at start
    """
    text_lower = bullet_text.lower().strip()
    score = 0
    signals: list[str] = []

    first_match = _FIRST_WORD_RE.match(text_lower)
    first_word = first_match.group(1) if first_match else ""

    if first_word in STRONG_ACTION_VERBS:
        score += 1
        signals.append(f"strong_verb:{first_word}")
    elif first_word in WEAK_ACTION_VERBS:
        score -= 1
        signals.append(f"weak_verb:{first_word}")
    elif any(text_lower.startswith(wv) for wv in WEAK_ACTION_VERBS):
        score -= 1
        signals.append("weak_verb_phrase")

    for sig in SCALE_SIGNALS:
        if sig in text_lower:
            score += 1
            signals.append(f"scale_signal:{sig}")
            break

    if _NUMERIC_SIGNAL_PATTERN.search(bullet_text):
        score += 1
        signals.append("numeric_metric")

    return score, signals


# ---------------------------------------------------------------------------
# Technical specificity floor: named mechanism, technology, or domain term
# ---------------------------------------------------------------------------

# Consulting-speak substitution patterns that replace specific technical mechanisms
GENERIC_CONSULTING_SUBSTITUTIONS: frozenset[str] = frozenset({
    # Plan-spec blocklist
    "drive strategic value",
    "ensure alignment",
    "stakeholder management",
    "delivered solutions",
    "managed the relationship",
    "worked closely with",
    "collaborated to deliver",
    "ensured the platform",
    "leveraged best practices",
    # Additional consulting filler
    "best-in-class solutions",
    "value-added solutions",
    "end-to-end solutions",
    "key stakeholders",
    "thought leadership",
    "strategic alignment",
    "holistic approach",
    "synergies",
    "robust framework",
    "go-to-market strategy",
    "driving growth",
    "enabling innovation",
    "key deliverables",
    "seamless integration",
    "best practices",
    "actionable insights",
})

_TECH_TOKEN_PATTERN = re.compile(
    r"\b(?:"
    r"aws|azure|gcp|databricks|kafka|kubernetes|docker|terraform|"
    r"python|scala|spark|sql|api|rest|graphql|hpc|microservices|"
    r"llm|gpt|claude|ai|ml|nlp|rag|graphrag|vector|embedding|"
    r"lineage|observability|telemetry|latency|throughput|sla|uptime|"
    r"runtime|control.plane|route.policy|deterministic|policy.gate|"
    r"policy.gating|execution.trace|traceability|sandbox|"
    r"cloud.native|platform|architecture|infrastructure|pipeline|"
    r"bi|dashboard|dashboards|data.model|data.models|semantic.view|semantic.views|"
    r"regulatory|compliance|basel|ccar|sox|iso|"
    r"saas|paas|iaas|serverless|lambda|"
    r"kubernetes|etl|data.lake|lakehouse|warehouse"
    r")\b",
    re.IGNORECASE,
)


def _has_technical_specificity(bullet_text: str, mechanism_vocab: list[str] | None = None) -> bool:
    """True if bullet contains at least one named mechanism, technology, or domain term.

    Accepts:
    - Known technology tokens (AWS, Databricks, Kafka, etc.)
    - Mechanism vocabulary tokens from the proof bundle for this bullet slot
    """
    if _TECH_TOKEN_PATTERN.search(bullet_text):
        return True
    if mechanism_vocab:
        text_lower = bullet_text.lower()
        return any(str(v).lower() in text_lower for v in mechanism_vocab if v)
    return False


def _has_consulting_substitution(bullet_text: str) -> list[str]:
    """Return list of consulting-speak substitution phrases found in bullet_text."""
    text_lower = bullet_text.lower()
    return [phrase for phrase in GENERIC_CONSULTING_SUBSTITUTIONS if phrase in text_lower]


# ---------------------------------------------------------------------------
# Gate runner
# ---------------------------------------------------------------------------

@dataclass
class QualityFloorResult:
    gate_id: str
    passed: bool
    bullet_id: str
    score: int
    signals: list[str]
    failure_reason: str | None


def check_bullet_seniority_floor(
    bullet_id: str,
    bullet_text: str,
    *,
    floor: int = SENIORITY_FLOOR_SCORE,
) -> QualityFloorResult:
    score, signals = _score_bullet_seniority(bullet_text)
    passed = score >= floor
    return QualityFloorResult(
        gate_id="x2_bullet_seniority_floor",
        passed=passed,
        bullet_id=bullet_id,
        score=score,
        signals=signals,
        failure_reason=(
            f"{bullet_id}: seniority score {score} < floor {floor} (signals={signals})"
            if not passed
            else None
        ),
    )


def check_bullet_technical_specificity_floor(
    bullet_id: str,
    bullet_text: str,
    *,
    mechanism_vocab: list[str] | None = None,
) -> QualityFloorResult:
    has_tech = _has_technical_specificity(bullet_text, mechanism_vocab=mechanism_vocab)
    return QualityFloorResult(
        gate_id="x2_bullet_technical_specificity_floor",
        passed=has_tech,
        bullet_id=bullet_id,
        score=1 if has_tech else 0,
        signals=["tech_token_found"] if has_tech else [],
        failure_reason=(
            f"{bullet_id}: no named mechanism/technology in bullet text"
            if not has_tech
            else None
        ),
    )


def check_bullet_no_generic_consulting_substitution(
    bullet_id: str,
    bullet_text: str,
) -> QualityFloorResult:
    hits = _has_consulting_substitution(bullet_text)
    return QualityFloorResult(
        gate_id="x2_no_generic_consulting_substitution",
        passed=not hits,
        bullet_id=bullet_id,
        score=0 if hits else 1,
        signals=hits,
        failure_reason=(
            f"{bullet_id}: consulting-speak substitution phrases: {hits}"
            if hits
            else None
        ),
    )


def run_bullet_quality_floor_gates(
    bullets: list[dict[str, Any]],
    *,
    section_id: str,
    mechanism_vocab_by_slot: dict[str, list[str]] | None = None,
    seniority_floor: int = SENIORITY_FLOOR_SCORE,
) -> tuple[
    bool,  # seniority gate overall pass
    list[QualityFloorResult],  # per bullet seniority results
    bool,  # technical specificity gate overall pass
    list[QualityFloorResult],  # per bullet tech results
    bool,  # no-generic-consulting gate overall pass
    list[QualityFloorResult],  # per bullet consulting results
]:
    """Run all three quality floor gates across all bullets in a section."""
    bullet_id_prefix = "bul_ibm_" if section_id == "ibm_bullets" else "bul_unify_"
    seniority_results: list[QualityFloorResult] = []
    tech_results: list[QualityFloorResult] = []
    consulting_results: list[QualityFloorResult] = []

    for b in bullets:
        if not isinstance(b, dict):
            continue
        bid = str(b.get("bullet_id") or "")
        if not bid.startswith(bullet_id_prefix):
            continue
        text = str(b.get("bullet_text") or "").strip()
        if not text:
            continue

        seniority_results.append(
            check_bullet_seniority_floor(bid, text, floor=seniority_floor)
        )
        vocab = (mechanism_vocab_by_slot or {}).get(bid)
        tech_results.append(
            check_bullet_technical_specificity_floor(bid, text, mechanism_vocab=vocab)
        )
        consulting_results.append(
            check_bullet_no_generic_consulting_substitution(bid, text)
        )

    seniority_pass = all(r.passed for r in seniority_results) if seniority_results else True
    tech_pass = all(r.passed for r in tech_results) if tech_results else True
    consulting_pass = all(r.passed for r in consulting_results) if consulting_results else True
    return seniority_pass, seniority_results, tech_pass, tech_results, consulting_pass, consulting_results


__all__ = [
    "GENERIC_CONSULTING_SUBSTITUTIONS",
    "SCALE_SIGNALS",
    "SENIORITY_FLOOR_SCORE",
    "STRONG_ACTION_VERBS",
    "WEAK_ACTION_VERBS",
    "QualityFloorResult",
    "check_bullet_no_generic_consulting_substitution",
    "check_bullet_seniority_floor",
    "check_bullet_technical_specificity_floor",
    "run_bullet_quality_floor_gates",
]
