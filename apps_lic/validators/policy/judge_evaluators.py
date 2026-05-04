"""Deterministic evaluators for the LIC Judge family.

W3-P1/P2/P3 of plan judge-base-and-four-judges-c5e1f3. Each function
implements the deterministic backend for one of the rubric YAMLs in
`apps_lic/policy/rubrics/`. They are pure functions matching the
``EvaluateFn`` contract from `judge_base`:

    (state, rubric) -> (score, reason_codes, evidence_refs, remediation_hint)

Each is a leaf swap-in target: replacing any one with an
``evaluate_with_llm`` variant does not change the HOP integration
surface (D2). HOP6's evaluator lives in HOP6ValidationAgent.py
historically (W2-P1); the three shipped here are the W3 batch.
"""
from __future__ import annotations

from typing import Any

from apps_lic.validators.policy.judge_base import Rubric


# ---------------------------------------------------------------------- #
# HOP1: LLM-fallback classifier Judge (W3-P1)
# ---------------------------------------------------------------------- #


def evaluate_hop1_llm_fallback(
    state: dict[str, Any], rubric: Rubric
) -> tuple[float, list[str], list[str], str]:
    """Judges classifications produced by HOP1's LLM-fallback branch.

    State fields:
      - title: the input recipient title
      - archetype: the LLM's chosen archetype
      - confidence: the LLM's reported confidence in [0, 1]
      - reasoning: the LLM's reasoning string

    Score is the average of two sub-scores in [0, 1]:
      a) confidence_floor_score: max(0, min(1, (confidence - floor_low) / (floor_high - floor_low)))
      b) title_evidence_score: fraction of title-tokens referenced in the
         reasoning string, capped by ``min_title_tokens_referenced``.

    Raises ValueError when the title is missing — caller (JudgeBase)
    converts to ABSTAIN per D6.
    """
    title = (state.get("title") or "").strip()
    if not title:
        raise ValueError("title missing; cannot judge LLM-fallback classification")

    confidence = float(state.get("confidence", 0.0))
    reasoning = (state.get("reasoning") or "").lower()

    params = rubric.params
    floor = float(params.get("confidence_floor", 0.55))
    min_tokens_referenced = int(params.get("min_title_tokens_referenced", 1))
    min_token_length = int(params.get("min_token_length", 4))
    stopwords = {str(w).lower() for w in params.get("stopwords", [])}

    # Confidence sub-score: scale [floor-0.20, floor+0.20] linearly into [0, 1].
    floor_low = max(0.0, floor - 0.20)
    floor_high = min(1.0, floor + 0.20)
    if floor_high == floor_low:
        confidence_score = 1.0 if confidence >= floor else 0.0
    else:
        confidence_score = (confidence - floor_low) / (floor_high - floor_low)
        confidence_score = max(0.0, min(1.0, confidence_score))

    # Evidence sub-score: count meaningful title tokens that appear in the
    # reasoning string. Reasoning that mentions no title tokens is
    # almost certainly hallucinated.
    title_tokens = [
        w.lower()
        for w in title.split()
        if len(w) >= min_token_length and w.lower() not in stopwords
    ]
    referenced = [t for t in title_tokens if t in reasoning]
    if not title_tokens:
        # Title has no scorable tokens — fall back to confidence-only.
        evidence_score = 1.0 if confidence >= floor else 0.5
    else:
        ratio = len(referenced) / max(len(title_tokens), 1)
        target = min(1.0, min_tokens_referenced / max(len(title_tokens), 1))
        evidence_score = min(1.0, ratio / target) if target > 0 else 1.0

    score = (confidence_score + evidence_score) / 2.0

    reason_codes: list[str] = []
    if confidence < floor:
        reason_codes.append("confidence_below_floor")
    if not referenced and title_tokens:
        reason_codes.append("reasoning_does_not_reference_title")

    remediation = ""
    if score < 0.50:
        remediation = rubric.raw.get("remediation_hints", {}).get("weak", "")
    elif score < 0.75:
        remediation = rubric.raw.get("remediation_hints", {}).get("moderate", "")

    evidence_refs = [f"title_token:{t}" for t in referenced[:6]]

    return (score, reason_codes, evidence_refs, remediation)


# ---------------------------------------------------------------------- #
# HOP2: strategic_brief faithfulness Judge (W3-P2)
# ---------------------------------------------------------------------- #


def evaluate_hop2_grounding(
    state: dict[str, Any], rubric: Rubric
) -> tuple[float, list[str], list[str], str]:
    """Judges the strategic_brief for citation faithfulness against evidence_pack.

    State fields:
      - strategic_brief: the synthesized brief text
      - evidence_pack: list of {artifact_id, summary, source, confidence, ...}

    Score is the fraction of brief claim-sentences that lexically
    overlap with at least one evidence_pack summary, weighted by the
    fraction of evidence artifacts that meet the source_weight floor.

    Raises ValueError when evidence_pack is empty (no signal possible)
    or strategic_brief has no claim-sentences. JudgeBase converts to
    ABSTAIN per D6.
    """
    brief = (state.get("strategic_brief") or "").strip()
    evidence_pack = state.get("evidence_pack") or []

    params = rubric.params
    min_artifacts = int(params.get("min_artifacts", 1))
    min_source_weight = float(params.get("min_source_weight", 0.4))
    min_claim_sentences = int(params.get("min_claim_sentences", 1))
    min_token_length = int(params.get("min_token_length", 4))

    if not isinstance(evidence_pack, list) or len(evidence_pack) < min_artifacts:
        raise ValueError(
            f"evidence_pack has {len(evidence_pack) if isinstance(evidence_pack, list) else 0} "
            f"artifacts, below floor {min_artifacts}; abstain"
        )

    # Sentences in the brief: simple period split.
    sentences = [s.strip() for s in brief.split(".") if s.strip()]
    if len(sentences) < min_claim_sentences:
        raise ValueError(
            f"strategic_brief has {len(sentences)} claim-sentences, "
            f"below floor {min_claim_sentences}; abstain"
        )

    # Build a token-set per evidence summary.
    def _tokens(text: str) -> set[str]:
        return {w.lower() for w in str(text).split() if len(w) >= min_token_length}

    evidence_token_sets: list[tuple[str, set[str], float]] = []
    for art in evidence_pack:
        if not isinstance(art, dict):
            continue
        artifact_id = str(art.get("artifact_id", ""))
        summary = art.get("summary", "")
        confidence = float(art.get("confidence", 0.7))
        evidence_token_sets.append((artifact_id, _tokens(summary), confidence))

    if not evidence_token_sets:
        raise ValueError("evidence_pack contains no usable artifacts; abstain")

    # Source-weight gate: fraction of artifacts at-or-above floor.
    weighted = [t for t in evidence_token_sets if t[2] >= min_source_weight]
    weight_fraction = len(weighted) / len(evidence_token_sets)

    # Per-sentence: does ANY artifact summary share at least 2 meaningful tokens?
    cited_sentences = 0
    cited_artifact_ids: set[str] = set()
    uncited_sentences: list[str] = []
    for sent in sentences:
        sent_tokens = _tokens(sent)
        if not sent_tokens:
            continue
        best_overlap = 0
        best_artifact = ""
        for artifact_id, tokens, _ in evidence_token_sets:
            overlap = len(sent_tokens & tokens)
            if overlap > best_overlap:
                best_overlap = overlap
                best_artifact = artifact_id
        if best_overlap >= 2:
            cited_sentences += 1
            if best_artifact:
                cited_artifact_ids.add(best_artifact)
        else:
            uncited_sentences.append(sent[:80])

    citation_fraction = cited_sentences / max(len(sentences), 1)
    score = citation_fraction * (0.7 + 0.3 * weight_fraction)
    score = max(0.0, min(1.0, score))

    reason_codes: list[str] = []
    if citation_fraction < 0.5:
        reason_codes.append("majority_claims_uncited")
    if weight_fraction < 0.5:
        reason_codes.append("low_source_weight_pack")

    remediation = ""
    if score < 0.40:
        remediation = rubric.raw.get("remediation_hints", {}).get("weak", "")
    elif score < 0.70:
        remediation = rubric.raw.get("remediation_hints", {}).get("moderate", "")

    evidence_refs = [f"artifact:{aid}" for aid in sorted(cited_artifact_ids)[:6]]

    return (score, reason_codes, evidence_refs, remediation)


# ---------------------------------------------------------------------- #
# HOP8: narrative executive_summary Judge (W3-P3)
# ---------------------------------------------------------------------- #


def evaluate_hop8_narrative(
    state: dict[str, Any], rubric: Rubric
) -> tuple[float, list[str], list[str], str]:
    """Score-band template selector for HOP8's executive_summary narrative.

    State fields:
      - total_score: the QA report's weighted total in [0, 1]
      - score_breakdown: dict of dimension -> score (used to find top_signal / top_gap)

    Score is total_score itself (the Judge ratifies the deterministic
    weighted-score; an LLM backend would replace this with a rubric-
    prompted faithfulness check on the rendered summary text).

    The deterministic backend ALSO synthesises a 3-sentence
    ``executive_summary`` that the HOP8 caller stores into the buffer.
    """
    total_score = float(state.get("total_score", 0.0))
    breakdown = state.get("score_breakdown") or {}

    params = rubric.params
    excellent = float(params.get("total_score_excellent", 0.90))
    solid = float(params.get("total_score_solid", 0.75))
    acceptable = float(params.get("total_score_acceptable", 0.60))
    templates = params.get("templates") or {}

    # Find top signal + top gap for narrative interpolation.
    if isinstance(breakdown, dict) and breakdown:
        top_signal = max(breakdown.items(), key=lambda kv: kv[1])[0]
        top_gap = min(breakdown.items(), key=lambda kv: kv[1])[0]
    else:
        top_signal = "unknown"
        top_gap = "unknown"

    # Template selection.
    if total_score >= excellent:
        template_key = "excellent"
        minor_fix = "none"
        recommendation = "ship as-is"
    elif total_score >= solid:
        template_key = "solid"
        minor_fix = top_gap
        recommendation = f"tighten {top_gap}"
    elif total_score >= acceptable:
        template_key = "acceptable"
        minor_fix = top_gap
        recommendation = f"strengthen {top_gap} before delivery"
    else:
        template_key = "needs_work"
        minor_fix = top_gap
        recommendation = f"block delivery; remediate {top_gap}"

    template = str(templates.get(template_key, "Run scored {total_score:.2f}."))
    try:
        narrative = template.format(
            total_score=total_score,
            top_signal=top_signal,
            top_gap=top_gap,
            minor_fix=minor_fix,
            recommendation=recommendation,
        )
    except (KeyError, IndexError, ValueError):
        narrative = f"Run scored {total_score:.2f}. Top signal: {top_signal}. Top gap: {top_gap}."

    score = max(0.0, min(1.0, total_score))

    reason_codes: list[str] = [f"narrative_template:{template_key}"]
    if total_score < acceptable:
        reason_codes.append("score_below_acceptable_floor")

    remediation = ""
    if score < 0.50:
        remediation = rubric.raw.get("remediation_hints", {}).get("weak", "")
    elif score < 0.80:
        remediation = rubric.raw.get("remediation_hints", {}).get("moderate", "")

    # The narrative itself is shipped as an evidence_ref so the HOP8
    # caller can read it back from the scorecard without a separate
    # plumbing path.
    evidence_refs = [f"narrative:{narrative}"]

    return (score, reason_codes, evidence_refs, remediation)
