"""PER-CAND Resume Gates — Evaluate individual candidates.

Gates that run per ensemble candidate (before winner selection).
W5 implements rigorous resume domain quality checks.

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W5)
"""

from __future__ import annotations

import logging
import re
from typing import Any

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

_log = logging.getLogger("apps_rg.gates.per_cand")


# W5: Forbidden filler words and buzzwords
FORBIDDEN_FILLERS = frozenset([
    "synergy", "synergies", "synergistic",
    "leverage", "leveraging", "leveraged",
    "paradigm", "paradigms",
    "thinking outside the box",
    "low-hanging fruit",
    "move the needle",
    "boil the ocean",
    "circle back",
    "double-click",
    "ecosystem", "ecosystems",
    "disruptive", "disruption",
    "innovative", "innovation"  # Context-dependent, flagged for review
])


def _extract_text(artifact: Any) -> str:
    """Extract text from artifact."""
    if isinstance(artifact, dict):
        return artifact.get("text", "")
    elif hasattr(artifact, "text"):
        return str(getattr(artifact, "text", ""))
    return ""


def _count_words(text: str) -> int:
    """Count words in text."""
    return len(text.split())


def _split_sentences(text: str) -> list[str]:
    """Split text into sentences."""
    # Simple sentence splitting on .!? followed by space or end
    sentences = re.split(r'[.!?]+\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def _count_quantified_outcomes(text: str) -> int:
    """Count numeric claims/outcomes in text."""
    # Pattern: number with %, $, or unit
    pattern = r'(?i)(?:\$?\d+(?:\.\d+)?[\s]?[MKBkm]?(?:illion)?(?:\%|\s*(?:users?|customers?|revenue?|savings?|percent|\%|x|times?))?)'
    matches = re.findall(pattern, text)
    return len(matches)


def length_parity_strict_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W5: Word count within ±15% of base section length.
    
    Ensures generated text maintains similar length to source material,
    preventing both over-expansion and excessive compression.
    """
    gate_id = "length_parity_strict"
    
    text = _extract_text(artifact)
    if not text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No text available for length check",
            reason_codes=("missing_text",),
        )
    
    # Get reference length from context (base section or seed)
    reference_word_count = context.get("reference_word_count")
    if reference_word_count is None:
        # Try to get from seed text in context
        seed_text = context.get("seed_text", "")
        if seed_text:
            reference_word_count = _count_words(seed_text)
    
    if reference_word_count is None or reference_word_count == 0:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No reference length available for parity check",
            reason_codes=("missing_reference",),
        )
    
    actual_word_count = _count_words(text)
    tolerance = 0.15  # ±15%
    
    # Use round() to avoid floating point truncation issues (e.g., int(100*1.15)=114)
    min_words = round(reference_word_count * (1 - tolerance))
    max_words = round(reference_word_count * (1 + tolerance))
    
    if min_words <= actual_word_count <= max_words:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.PASS,
            reason=f"Length parity: {actual_word_count} words (ref: {reference_word_count}, ±15%)",
            reason_codes=("length_within_tolerance", f"words:{actual_word_count}"),
            evidence_refs=(
                f"reference:{reference_word_count}",
                f"actual:{actual_word_count}",
                f"range:[{min_words},{max_words}]",
            ),
        )
    
    _log.warning(
        "[W5] Length parity fail: %d words (expected %d-%d)",
        actual_word_count, min_words, max_words
    )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.FAIL,
        reason=f"Length outside ±15% tolerance: {actual_word_count} words (ref: {reference_word_count})",
        reason_codes=(
            "length_outside_tolerance",
            f"words:{actual_word_count}",
            f"reference:{reference_word_count}",
        ),
        evidence_refs=(
            f"reference:{reference_word_count}",
            f"actual:{actual_word_count}",
            f"min:{min_words}",
            f"max:{max_words}",
        ),
    )


def quantified_outcome_count_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W5: Exec summary must contain ≥2 numeric claims.
    
    Ensures executive summaries have concrete, measurable outcomes.
    """
    gate_id = "quantified_outcome_count"
    
    text = _extract_text(artifact)
    if not text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No text available for outcome counting",
            reason_codes=("missing_text",),
        )
    
    outcome_count = _count_quantified_outcomes(text)
    min_required = 2
    
    if outcome_count >= min_required:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.PASS,
            reason=f"Quantified outcomes: {outcome_count} (min: {min_required})",
            reason_codes=("sufficient_outcomes", f"count:{outcome_count}"),
            evidence_refs=(f"outcomes:{outcome_count}",),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.FAIL,
        reason=f"Insufficient quantified outcomes: {outcome_count} (min: {min_required})",
        reason_codes=(
            "insufficient_outcomes",
            f"count:{outcome_count}",
            f"min_required:{min_required}",
        ),
        evidence_refs=(f"outcomes:{outcome_count}",),
    )


def target_company_name_absence_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W5: Prose must NOT contain target_company string.
    
    Prevents resume from appearing overly customized or contrived.
    Authenticity guard — candidates should be positioned by capability,
    not flattery.
    """
    gate_id = "target_company_name_absence"
    
    text = _extract_text(artifact)
    if not text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No text available for company name check",
            reason_codes=("missing_text",),
        )
    
    target_company = context.get("target_company")
    if not target_company:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="target_company not provided in context",
            reason_codes=("missing_target_company",),
        )
    
    # Case-insensitive check
    text_lower = text.lower()
    company_lower = target_company.lower()
    
    if company_lower in text_lower:
        _log.warning(
            "[W5] Target company name '%s' found in text",
            target_company
        )
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"Target company name '{target_company}' present in prose",
            reason_codes=(
                "target_company_present",
                f"company:{target_company}",
            ),
            evidence_refs=(
                f"found:{target_company}",
                "violation:authenticity",
            ),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason=f"Target company name '{target_company}' not found in prose",
        reason_codes=("target_company_absent", f"company:{target_company}"),
    )


def forbidden_filler_strict_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W5: Reject candidates with banned buzzwords.
    
    Enforces professional, authentic language without clichés.
    """
    gate_id = "forbidden_filler_strict"
    
    text = _extract_text(artifact)
    if not text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No text available for filler check",
            reason_codes=("missing_text",),
        )
    
    text_lower = text.lower()
    violations = []
    
    for filler in FORBIDDEN_FILLERS:
        if filler.lower() in text_lower:
            violations.append(filler)
    
    if violations:
        _log.warning(
            "[W5] Forbidden fillers found: %s",
            violations[:5]  # Log first 5
        )
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"{len(violations)} forbidden buzzwords/fillers found",
            reason_codes=(
                "forbidden_filler_found",
                f"count:{len(violations)}",
                f"examples:{violations[:3]}",
            ),
            evidence_refs=tuple(f"found:{v}" for v in violations[:5]),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason="No forbidden buzzwords or fillers found",
        reason_codes=("no_forbidden_fillers",),
    )


def sentence_max_length_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W5: No sentence >40 words.
    
    Ensures readability and executive-appropriate brevity.
    """
    gate_id = "sentence_max_length"
    
    text = _extract_text(artifact)
    if not text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No text available for sentence length check",
            reason_codes=("missing_text",),
        )
    
    max_words = 40
    sentences = _split_sentences(text)
    violations = []
    
    for i, sentence in enumerate(sentences):
        word_count = len(sentence.split())
        if word_count > max_words:
            violations.append({
                "index": i,
                "words": word_count,
                "preview": sentence[:50] + "..." if len(sentence) > 50 else sentence,
            })
    
    if violations:
        _log.warning(
            "[W5] %d sentences exceed %d words",
            len(violations), max_words
        )
        return GateVerdict(
            gate_id=gate_id,
            result=Result.FAIL,
            reason=f"{len(violations)} sentences exceed {max_words} words",
            reason_codes=(
                "sentence_too_long",
                f"violations:{len(violations)}",
            ),
            evidence_refs=tuple(
                f"sentence:{v['index']},words:{v['words']}" for v in violations[:3]
            ),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.PASS,
        reason=f"All {len(sentences)} sentences within {max_words} words",
        reason_codes=("sentences_within_limit", f"count:{len(sentences)}"),
    )


def archetype_lead_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W5: Sentence 1 must contain archetype string.
    
    Ensures executive summary immediately establishes candidate archetype.
    """
    gate_id = "archetype_lead"
    
    text = _extract_text(artifact)
    if not text:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No text available for archetype check",
            reason_codes=("missing_text",),
        )
    
    archetype = context.get("archetype")
    if not archetype:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="archetype not provided in context",
            reason_codes=("missing_archetype",),
        )
    
    sentences = _split_sentences(text)
    if not sentences:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.UNKNOWN,
            reason="No sentences found in text",
            reason_codes=("no_sentences",),
        )
    
    first_sentence = sentences[0].lower()
    archetype_lower = archetype.lower()
    
    # Check for archetype or synonyms
    archetype_parts = archetype_lower.split()
    found = any(part in first_sentence for part in archetype_parts if len(part) > 3)
    
    if found:
        return GateVerdict(
            gate_id=gate_id,
            result=Result.PASS,
            reason=f"Archetype '{archetype}' found in opening sentence",
            reason_codes=("archetype_present", f"archetype:{archetype}"),
        )
    
    return GateVerdict(
        gate_id=gate_id,
        result=Result.FAIL,
        reason=f"Opening sentence lacks archetype '{archetype}'",
        reason_codes=(
            "archetype_missing",
            f"archetype:{archetype}",
            f"first_sentence:{first_sentence[:50]}...",
        ),
        evidence_refs=(
            f"expected:{archetype}",
            f"actual:{first_sentence[:50]}",
        ),
    )


def per_cand_quality_composite_gate(artifact: Any, context: dict[str, Any]) -> GateVerdict:
    """W5: Composite PER-CAND gate running all W5 checks.
    
    Aggregated quality check for ensemble candidate evaluation.
    """
    gates = [
        ("length_parity", length_parity_strict_gate),
        ("quantified_outcomes", quantified_outcome_count_gate),
        ("target_company_absent", target_company_name_absence_gate),
        ("forbidden_filler", forbidden_filler_strict_gate),
        ("sentence_length", sentence_max_length_gate),
        ("archetype_lead", archetype_lead_gate),
    ]
    
    failures = []
    passes = []
    unknowns = []
    
    for name, gate_fn in gates:
        verdict = gate_fn(artifact, context)
        if verdict.result == Result.FAIL:
            failures.append((name, verdict))
        elif verdict.result == Result.PASS:
            passes.append((name, verdict))
        else:
            unknowns.append((name, verdict))
    
    # Composite result
    if failures:
        return GateVerdict(
            gate_id="per_cand_quality_composite",
            result=Result.FAIL,
            reason=f"PER-CAND quality failures: {', '.join(f[0] for f in failures)}",
            reason_codes=tuple(f"fail:{f[0]}" for f in failures),
        )
    
    if unknowns and not passes:
        return GateVerdict(
            gate_id="per_cand_quality_composite",
            result=Result.UNKNOWN,
            reason=f"PER-CAND quality indeterminate: {', '.join(u[0] for u in unknowns)}",
            reason_codes=tuple(f"unknown:{u[0]}" for u in unknowns),
        )
    
    return GateVerdict(
        gate_id="per_cand_quality_composite",
        result=Result.PASS,
        reason=f"PER-CAND quality passed: {len(passes)} checks",
        reason_codes=tuple(f"pass:{p[0]}" for p in passes),
    )


__all__ = [
    "length_parity_strict_gate",
    "quantified_outcome_count_gate",
    "target_company_name_absence_gate",
    "forbidden_filler_strict_gate",
    "sentence_max_length_gate",
    "archetype_lead_gate",
    "per_cand_quality_composite_gate",
]
