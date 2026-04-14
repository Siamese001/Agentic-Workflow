"""C0-to-PromptAssembly bridge adapter (L_TOOLS layer).

Translates a validated C0EvidenceContract into a pre-shaped EvidenceBundle
and replay_extras dict for direct injection into _assemble(pre_shaped_bundle=...).

Layer authority:
    This module lives in L_TOOLS, which is permitted to import from L3
    (ALLOWED_LAYER_EDGES: L_TOOLS->L3).  The reverse direction (L3->L_TOOLS)
    is FORBIDDEN and must never be added.

Public API:
    translate_contract(contract, packet_type) -> tuple[EvidenceBundle | None, dict]
"""

from __future__ import annotations

from typing import Any, cast

from agentic_core.L3_orchestration.types.c0_evidence_contract_types import (
    C0EvidenceContract,
    CitedSpan,
)
from tools.adg.prompt_assembly.contracts import (
    ContradictionFlag,
    EvidenceBundle,
    EvidenceItem,
    SourceType,
)
from tools.adg.prompt_assembly.shaping.evidence_shaper import shape_evidence


# ---------------------------------------------------------------------------
# Constants (mirroring C0 contract thresholds — do NOT import private _ names)
# ---------------------------------------------------------------------------

_ABSTAIN_COVERAGE_THRESHOLD: float = 0.30  # mirrors C0EvidenceContract._ABSTAIN_COVERAGE_THRESHOLD
_MIN_RELEVANCE_SCORE: float = 0.10
_MAX_TEXT_SNIPPET_CHARS: int = 512
_MAX_SPANS_PER_SOURCE_REF: int = 3
_SPAN_CAPS: dict[str, int] = {
    "executive_summary": 15,
    "graph_path_explanation": 20,
}
_DEFAULT_SPAN_CAP: int = 15
_MAX_CONTRADICTION_FLAGS: int = 4

_COVERAGE_HIGH: float = 0.80
_COVERAGE_MEDIUM: float = 0.50
_WEAK_SUPPORT_COVERAGE_THRESHOLD: float = 0.60
_WEAK_SUPPORT_MIN_SPANS: int = 2


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _classify_source_type(source_ref: str) -> SourceType:
    """Map a CitedSpan.source_ref to the nearest SourceType literal."""
    ref_lower = source_ref.lower()
    if ref_lower.endswith(".sqlite") or "sqlite" in ref_lower:
        return cast(SourceType, "sqlite")
    if "ratchet" in ref_lower:
        return cast(SourceType, "ratchet")
    if any(k in ref_lower for k in ("graph_db", "adg", "neo4j")):
        return cast(SourceType, "graph_db")
    if any(k in ref_lower for k in ("infra", "wiring", "infrastructure")):
        return cast(SourceType, "infra_view")
    if any(k in ref_lower for k in ("ast", "module", "struct", "code", "structural")):
        return cast(SourceType, "structural")
    return cast(SourceType, "json_report")  # safe proxy for all text-based sources


def _truncate_snippet(text: str, max_chars: int = _MAX_TEXT_SNIPPET_CHARS) -> str:
    """Truncate text at word boundary up to max_chars."""
    if len(text) <= max_chars:
        return text
    truncated = text[:max_chars]
    last_space = truncated.rfind(" ")
    if last_space > max_chars // 2:
        return truncated[:last_space]
    return truncated


def _prune_and_sort_spans(spans: tuple, packet_type: str) -> list[CitedSpan]:
    """Sort by relevance DESC, discard low-relevance, apply source diversity cap, apply span cap."""
    sorted_spans: list[CitedSpan] = sorted(spans, key=lambda s: s.relevance_score, reverse=True)

    filtered = [s for s in sorted_spans if s.relevance_score >= _MIN_RELEVANCE_SCORE]

    source_counts: dict[str, int] = {}
    diverse: list[CitedSpan] = []
    for span in filtered:
        count = source_counts.get(span.source_ref, 0)
        if count < _MAX_SPANS_PER_SOURCE_REF:
            diverse.append(span)
            source_counts[span.source_ref] = count + 1

    cap = _SPAN_CAPS.get(packet_type, _DEFAULT_SPAN_CAP)
    return diverse[:cap]


def _translate_span(span: CitedSpan, freshness: str) -> EvidenceItem:
    """Translate a single CitedSpan to an EvidenceItem."""
    return EvidenceItem(
        source_artifact=span.source_ref,
        source_type=_classify_source_type(span.source_ref),
        snapshot_id="c0",
        row_references=[span.chunk_hash] if span.chunk_hash else [],
        cited_spans=[span.span_id],
        support_score=span.relevance_score,
        coverage_score=1.0,  # per-item placeholder; bundle merger overrides at bundle level
        is_derived=False,
        freshness=freshness,
        data={"text_snippet": _truncate_snippet(span.text_snippet)},
    )


def _compute_confidence_band(coverage_score: float) -> str:
    """Map coverage_score to a confidence band label."""
    if coverage_score >= _COVERAGE_HIGH:
        return "HIGH"
    if coverage_score >= _COVERAGE_MEDIUM:
        return "MEDIUM"
    return "LOW"


def _merge_bundle(
    shaped: EvidenceBundle,
    contract: C0EvidenceContract,
    pruned_spans: list[CitedSpan],
) -> EvidenceBundle:
    """Merge shaper output with C0 authoritative values.

    Overrides coverage_score with contract.coverage_score (authoritative).
    Caps ContradictionFlags at _MAX_CONTRADICTION_FLAGS.
    Computes weak_support from coverage + span count.
    Injects C0 coverage gap string if critically low.
    """
    merged_contradictions: list[ContradictionFlag] = list(shaped.contradictions)
    if len(merged_contradictions) > _MAX_CONTRADICTION_FLAGS:
        merged_contradictions = merged_contradictions[:_MAX_CONTRADICTION_FLAGS]

    if any(c.severity == "major" for c in merged_contradictions):
        contradiction_status: str = "major"
    elif merged_contradictions:
        contradiction_status = "minor"
    else:
        contradiction_status = "none"

    weak_support = (
        contract.coverage_score < _WEAK_SUPPORT_COVERAGE_THRESHOLD
        or len(pruned_spans) < _WEAK_SUPPORT_MIN_SPANS
    )

    merged_gaps: list[str] = list(shaped.gaps)
    if contract.coverage_score < _ABSTAIN_COVERAGE_THRESHOLD:
        merged_gaps.append(f"c0_coverage_critically_low:{contract.coverage_score:.2f}")

    return EvidenceBundle(
        items=shaped.items,
        coverage_score=contract.coverage_score,  # authoritative override
        contradiction_status=contradiction_status,  # type: ignore[arg-type]
        contradictions=merged_contradictions,
        gaps=merged_gaps,
        freshness=shaped.freshness,
        weak_support=weak_support,
    )


def _build_abstain_extras(contract: C0EvidenceContract, packet_type: str) -> dict[str, Any]:
    """Build replay_extras for an abstain path return."""
    return {
        "retrieval_id": contract.retrieval_id,
        "request_id": contract.request_id,
        "evidence_hmac": contract.evidence_hmac,
        "coverage_score": contract.coverage_score,
        "abstain_hint": True,
        "packet_type": packet_type,
        "confidence_band": "LOW",
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def translate_contract(
    contract: C0EvidenceContract,
    packet_type: str,
) -> tuple[EvidenceBundle | None, dict[str, Any]]:
    """Translate a C0EvidenceContract into a pre-shaped EvidenceBundle and replay_extras.

    Returns (None, replay_extras) if the adapter-side abstain gate fires.
    Returns (EvidenceBundle, replay_extras) on success.

    Caller pattern::

        bundle, extras = translate_contract(contract, "executive_summary")
        if bundle is None:
            return None  # abstain — do not call _assemble
        template = get_template("executive_summary")
        must_items = [EvidenceItem(**i) for i in bundle.items]  # or pass directly
        envelope = _assemble(template, must_items, [], task_block, extras, bundle)
    """
    # Step 1: validate required fields (raises C0ContractViolation on failure)
    contract.validate()

    # Step 2: adapter-side abstain gate
    has_usable_spans = any(s.relevance_score >= _MIN_RELEVANCE_SCORE for s in contract.cited_spans)
    if (
        contract.abstain_hint
        or contract.coverage_score < _ABSTAIN_COVERAGE_THRESHOLD
        or not contract.cited_spans
        or not has_usable_spans
    ):
        return None, _build_abstain_extras(contract, packet_type)

    # Step 3: prune, sort, diversify
    pruned_spans = _prune_and_sort_spans(contract.cited_spans, packet_type)
    if not pruned_spans:
        return None, _build_abstain_extras(contract, packet_type)

    # Step 4: translate CitedSpan → EvidenceItem
    freshness = getattr(contract, "retrieval_timestamp", "") or ""
    items = [_translate_span(span, freshness) for span in pruned_spans]

    # Step 5: shape evidence (must_use_sources=[] — C0 provides no must-use catalog)
    shaped = shape_evidence(items, must_use_sources=[])

    # Step 6: bridge merger — override coverage, merge gaps, compute weak_support
    confidence_band = _compute_confidence_band(contract.coverage_score)
    merged_bundle = _merge_bundle(shaped, contract, pruned_spans)

    # Step 7: build replay_extras — runtime-only metadata, NOT stored in EvidenceBundle
    replay_extras: dict[str, Any] = {
        "retrieval_id": contract.retrieval_id,
        "request_id": contract.request_id,
        "evidence_hmac": contract.evidence_hmac,
        "coverage_score": contract.coverage_score,
        "abstain_hint": contract.abstain_hint,
        "packet_type": packet_type,
        "confidence_band": confidence_band,
    }

    return merged_bundle, replay_extras
