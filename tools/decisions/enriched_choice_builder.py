"""Enriched choice builder for standard ask_user_question decisions.

Lightweight wrapper that adds UI invariants to ask_user_question options:
- [confidence=X.XX] prefix on all options
- ⭐ star indicator on recommended option (exactly one when recommendation exists)
- · trade-off: segment in every option
- ASK_USER_QUESTION_PACKET telemetry (returned, caller must emit)

Per hardened plan ui-choice-consistency-zero-loss-hardened-d9f3a1:
- DEFAULT_HEURISTIC_CONFIDENCE = 0.72 (labeled fallback, not measured)
- confidence_source explicitly tracked (explicit vs heuristic_default)
- Builder returns telemetry packet; caller MUST emit
- AUTHOR_GATE_PACKET never emitted from this path

Authority boundary:
- AUTHOR_GATE = canonical pipeline for architecture/refactoring/deletion/governance
- ENRICHED_CHOICE = this wrapper for standard multi-option decisions
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Literal

# Hardened per review #5: labeled fallback, not magic number
DEFAULT_HEURISTIC_CONFIDENCE: float = 0.72

ConfidenceSource = Literal["explicit", "heuristic_default"]


@dataclass
class EnrichedOption:
    """Internal representation of an enriched option."""

    id: str
    label: str
    description: str
    tradeoff: str
    confidence: float
    confidence_source: ConfidenceSource
    is_recommended: bool = False

    def format_label(self) -> str:
        """Format label with optional star and confidence."""
        if self.is_recommended:
            return f"⭐ {self.id} [confidence={self.confidence:.2f}] {self.label}"
        return f"{self.id} [confidence={self.confidence:.2f}] {self.label}"

    def format_description(self) -> str:
        """Format description with confidence prefix and trade-off segment."""
        prefix = f"[confidence={self.confidence:.2f}]"
        return f"{prefix} · trade-off: {self.tradeoff} · {self.description}"

    def to_ask_user_question_dict(self) -> dict[str, str]:
        """Convert to ask_user_question-compatible dict."""
        return {
            "label": self.format_label()[:120],  # Cap length
            "description": self.format_description()[:240],  # Cap length
        }


@dataclass
class TelemetryPacket:
    """Telemetry packet for ASK_USER_QUESTION_PACKET emission."""

    packet_type: str = "ASK_USER_QUESTION_PACKET"
    context: str = "enriched_choice"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    option_count: int = 0
    recommended_index: int | None = None
    confidence_source: ConfidenceSource = "heuristic_default"
    invariants: list[str] = field(default_factory=lambda: [
        "confidence_prefix",
        "tradeoff_segment",
        "star_marker",
    ])

    def to_dict(self) -> dict[str, Any]:
        return {
            "packet_type": self.packet_type,
            "context": self.context,
            "timestamp": self.timestamp,
            "option_count": self.option_count,
            "recommended_index": self.recommended_index,
            "confidence_source": self.confidence_source,
            "invariants": self.invariants,
        }


def _validate_options(
    options: list[dict[str, Any]],
    recommended_id: str | None,
) -> None:
    """Validate input options before enrichment.

    Raises:
        ValueError: If validation fails.
    """
    if not options:
        raise ValueError("At least one option required")

    if len(options) > 4:
        raise ValueError(f"Maximum 4 options allowed, got {len(options)}")

    # Check for duplicate IDs
    ids = [opt.get("id") for opt in options]
    if len(set(ids)) != len(ids):
        raise ValueError("Option IDs must be unique")

    # Validate recommended_id exists if provided
    if recommended_id is not None and recommended_id not in ids:
        raise ValueError(f"recommended_id '{recommended_id}' not found in options")

    # Validate each option has required fields
    for opt in options:
        if not opt.get("id"):
            raise ValueError("Option must have 'id' field")
        if not opt.get("label"):
            raise ValueError(f"Option {opt.get('id')!r} must have 'label' field")
        if not opt.get("description"):
            raise ValueError(f"Option {opt.get('id')!r} must have 'description' field")
        if not opt.get("tradeoff"):
            raise ValueError(f"Option {opt.get('id')!r} must have 'tradeoff' field")


def _enrich_options(
    options: list[dict[str, Any]],
    recommended_id: str | None,
) -> list[EnrichedOption]:
    """Enrich raw options with confidence, star, and formatting."""
    enriched: list[EnrichedOption] = []

    for opt in options:
        opt_id = opt["id"]
        label = opt["label"]
        description = opt["description"]
        tradeoff = opt["tradeoff"]

        # Confidence handling per hardened review #5
        explicit_confidence = opt.get("confidence")
        if explicit_confidence is not None:
            confidence = float(explicit_confidence)
            confidence_source: ConfidenceSource = "explicit"
        else:
            confidence = DEFAULT_HEURISTIC_CONFIDENCE
            confidence_source = "heuristic_default"

        # Clamp confidence to valid range
        confidence = max(0.0, min(1.0, confidence))

        # Determine if recommended
        is_recommended = recommended_id is not None and opt_id == recommended_id

        enriched.append(EnrichedOption(
            id=opt_id,
            label=label,
            description=description,
            tradeoff=tradeoff,
            confidence=confidence,
            confidence_source=confidence_source,
            is_recommended=is_recommended,
        ))

    return enriched


def _validate_star_invariant(enriched: list[EnrichedOption]) -> None:
    """Validate star count invariant: exactly one if recommendation exists, zero if none."""
    recommended_count = sum(1 for opt in enriched if opt.is_recommended)

    if recommended_count > 1:
        raise ValueError(f"Multiple recommended options found ({recommended_count}), expected exactly one")

    # Note: recommended_count == 0 is valid (no recommendation)
    # recommended_count == 1 is valid (exactly one recommendation)


def build_enriched_choice_question(
    question: str,
    options: list[dict[str, Any]],
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
) -> dict[str, Any]:
    """Build enriched ask_user_question payload with UI invariants.

    Args:
        question: Base question text.
        options: List of option dicts. Each must have:
            - id: str (unique identifier)
            - label: str (short title)
            - description: str (what it does)
            - tradeoff: str (required - trade-off/consequence)
            - confidence: float (optional, uses DEFAULT_HEURISTIC_CONFIDENCE if missing)
        recommended_id: ID of recommended option, or None for no recommendation.
        telemetry_context: Optional context string for telemetry.

    Returns:
        Dict with keys:
        - question: str (unchanged from input)
        - options: list[dict] (formatted for ask_user_question with confidence/star/trade-off)
        - telemetry_packet: dict (ASK_USER_QUESTION_PACKET shape)

    Raises:
        ValueError: If options invalid or invariants violated.

    Example:
        >>> payload = build_enriched_choice_question(
        ...     question="Which approach?",
        ...     options=[
        ...         {
        ...             "id": "A",
        ...             "label": "Fast approach",
        ...             "description": "Quick implementation",
        ...             "tradeoff": "Higher risk of edge-case misses",
        ...             "confidence": 0.74,
        ...         },
        ...         {
        ...             "id": "B",
        ...             "label": "Safe approach",
        ...             "description": "Conservative implementation",
        ...             "tradeoff": "Slower but validates all assumptions",
        ...             "confidence": 0.88,
        ...         },
        ...     ],
        ...     recommended_id="B",
        ...     telemetry_context="branch-resolution",
        ... )
        >>> ask_user_question(
        ...     question=payload["question"],
        ...     options=payload["options"],
        ...     allowMultiple=False,
        ... )
        >>> print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))
    """
    # Validate inputs
    _validate_options(options, recommended_id)

    # Enrich with confidence, star, formatting
    enriched = _enrich_options(options, recommended_id)

    # Validate star invariant
    _validate_star_invariant(enriched)

    # Find recommended index for telemetry
    recommended_index = None
    for i, opt in enumerate(enriched):
        if opt.is_recommended:
            recommended_index = i
            break

    # Determine confidence source for telemetry
    # If any option has explicit confidence, mark as explicit
    # Otherwise heuristic_default
    has_explicit = any(
        opt.confidence_source == "explicit" for opt in enriched
    )
    telemetry_confidence_source: ConfidenceSource = (
        "explicit" if has_explicit else "heuristic_default"
    )

    # Build telemetry packet (per hardened review #7: concrete, returned, caller emits)
    telemetry = TelemetryPacket(
        context=telemetry_context or "enriched_choice",
        option_count=len(enriched),
        recommended_index=recommended_index,
        confidence_source=telemetry_confidence_source,
    )

    # Convert to ask_user_question format
    ask_user_question_options = [opt.to_ask_user_question_dict() for opt in enriched]

    return {
        "question": question,
        "options": ask_user_question_options,
        "telemetry_packet": telemetry.to_dict(),
    }


def format_ask_user_question_call(
    question: str,
    options: list[dict[str, Any]],
    recommended_id: str | None = None,
    telemetry_context: str | None = None,
) -> str:
    """Format a complete ask_user_question call with telemetry emission.

    Returns a string that can be printed/executed to perform the ask_user_question
    call and emit the telemetry packet.

    This is a convenience wrapper for documentation and examples.
    """
    payload = build_enriched_choice_question(
        question=question,
        options=options,
        recommended_id=recommended_id,
        telemetry_context=telemetry_context,
    )

    lines = [
        "# Build enriched payload",
        f'payload = build_enriched_choice_question(',
        f'    question={question!r},',
        f'    options={options!r},',
    ]
    if recommended_id:
        lines.append(f'    recommended_id={recommended_id!r},')
    if telemetry_context:
        lines.append(f'    telemetry_context={telemetry_context!r},')
    lines.extend([
        ')',
        '',
        '# Invoke ask_user_question',
        'ask_user_question(',
        '    question=payload["question"],',
        '    options=payload["options"],',
        '    allowMultiple=False,',
        ')',
        '',
        '# Emit telemetry (REQUIRED - caller must emit)',
        'print("ASK_USER_QUESTION_PACKET: " + json.dumps(payload["telemetry_packet"]))',
    ])

    return '\n'.join(lines)
