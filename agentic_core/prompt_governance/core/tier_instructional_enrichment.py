"""Tier-Aware I0 Instructional Enrichment Provider.

Generates contextual I0 instructional content scaled by reasoning tier.
LOW-tier agents receive richer, more explicit instructions to compensate
for limited reasoning depth (max_branches=1, max_depth=1, no reflection).

Authority: L0 (routing layer). This provider is consulted during
GovernedPayload assembly when an agent's ReasoningTier is known.

Slot authority: I0 (instructional) — GOVERNED authority level.
Must not override S0 or D0. Must be deterministic and hashable.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EnrichmentTier(str, Enum):
    """Maps to ReasoningTier for instructional enrichment decisions."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class InstructionalEnrichment:
    """Immutable I0 instructional enrichment payload for a reasoning tier."""

    tier: EnrichmentTier
    preamble: str
    constraints: tuple[str, ...]
    guidance: tuple[str, ...]
    examples_hint: str
    enrichment_hash: str = ""

    def to_i0_content(self) -> str:
        """Render as I0 instructional slot content string."""
        lines = []
        if self.preamble:
            lines.append(self.preamble)
        if self.constraints:
            lines.append("CONSTRAINTS:")
            for c in self.constraints:
                lines.append(f"  - {c}")
        if self.guidance:
            lines.append("GUIDANCE:")
            for g in self.guidance:
                lines.append(f"  - {g}")
        if self.examples_hint:
            lines.append(f"EXAMPLES: {self.examples_hint}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Tier-specific enrichment templates (deterministic, no runtime dependencies)
# ---------------------------------------------------------------------------

_LOW_TIER_ENRICHMENT = InstructionalEnrichment(
    tier=EnrichmentTier.LOW,
    preamble=(
        "You are operating in LOW reasoning mode. Follow instructions exactly. "
        "Do not speculate or explore alternative approaches. "
        "Produce a single, direct answer."
    ),
    constraints=(
        "Single-pass execution only — no branching or backtracking.",
        "Do not generate intermediate reasoning steps visible to the user.",
        "Stay within the token budget; prefer concise outputs.",
        "If uncertain, return a structured error rather than guessing.",
        "Do not invoke reflection or self-correction loops.",
    ),
    guidance=(
        "Use the provided context (C0) as your primary information source.",
        "Apply the directives (D0) without reinterpretation.",
        "Format output exactly as specified in the output schema.",
        "If the task requires multi-step reasoning, decompose into explicit sequential steps.",
        "Prefer deterministic patterns over probabilistic generation.",
    ),
    examples_hint="Follow the exact format shown in prior successful outputs for this agent type.",
)

_MEDIUM_TIER_ENRICHMENT = InstructionalEnrichment(
    tier=EnrichmentTier.MEDIUM,
    preamble=(
        "You are operating in MEDIUM reasoning mode. "
        "Limited branching is permitted (max 2 alternatives). "
        "Evaluate options briefly before committing."
    ),
    constraints=(
        "Maximum 2 reasoning branches — select the strongest.",
        "Depth limit: 2 levels of recursive reasoning.",
        "No reflection loops — commit to your best answer.",
        "Stay within the allocated token budget.",
    ),
    guidance=(
        "Consider up to 2 alternative approaches before selecting one.",
        "Use chain-of-thought reasoning where beneficial.",
        "Validate your output against the expected schema before returning.",
    ),
    examples_hint="Review context carefully; moderate exploration is allowed.",
)

_HIGH_TIER_ENRICHMENT = InstructionalEnrichment(
    tier=EnrichmentTier.HIGH,
    preamble="Standard reasoning mode. Full chain-of-thought and tree-of-thought available.",
    constraints=(
        "Maximum 3 reasoning branches.",
        "Reflection enabled — verify your reasoning before finalizing.",
    ),
    guidance=(
        "Use the full reasoning toolkit available to you.",
        "Apply reflection to validate critical outputs.",
    ),
    examples_hint="",
)

_CRITICAL_TIER_ENRICHMENT = InstructionalEnrichment(
    tier=EnrichmentTier.CRITICAL,
    preamble=(
        "CRITICAL reasoning mode. Maximum depth and breadth. "
        "All reasoning strategies available including reflexion."
    ),
    constraints=(
        "Up to 5 reasoning branches permitted.",
        "Full reflexion loops available for self-correction.",
        "Extended token budget — use it for thorough analysis.",
    ),
    guidance=(
        "Explore all viable approaches before committing.",
        "Use reflexion to detect and correct reasoning errors.",
        "Produce comprehensive, well-justified outputs.",
    ),
    examples_hint="",
)

TIER_ENRICHMENT_TABLE: dict[EnrichmentTier, InstructionalEnrichment] = {
    EnrichmentTier.LOW: _LOW_TIER_ENRICHMENT,
    EnrichmentTier.MEDIUM: _MEDIUM_TIER_ENRICHMENT,
    EnrichmentTier.HIGH: _HIGH_TIER_ENRICHMENT,
    EnrichmentTier.CRITICAL: _CRITICAL_TIER_ENRICHMENT,
}


def get_tier_enrichment(tier: str | EnrichmentTier) -> InstructionalEnrichment:
    """Get the I0 instructional enrichment for a given reasoning tier.

    Args:
        tier: Reasoning tier as string ("low", "medium", "high", "critical")
              or EnrichmentTier enum value.

    Returns:
        InstructionalEnrichment for the specified tier.

    Raises:
        ValueError: If tier is not recognized.
    """
    if isinstance(tier, str):
        try:
            tier = EnrichmentTier(tier.lower())
        except ValueError:
            raise ValueError(
                f"Unknown reasoning tier: {tier!r}. Valid tiers: {[t.value for t in EnrichmentTier]}",
            ) from None
    enrichment = TIER_ENRICHMENT_TABLE.get(tier)
    if enrichment is None:
        raise ValueError(f"No enrichment defined for tier: {tier}")
    return enrichment


def enrich_i0_for_tier(
    existing_i0: str,
    tier: str | EnrichmentTier,
    agent_id: str = "",
) -> str:
    """Enrich an existing I0 instructional slot with tier-appropriate content.

    Prepends tier-specific instructional guidance to whatever I0 content
    already exists. This preserves any agent-specific instructions while
    adding tier-appropriate constraints and guidance.

    Args:
        existing_i0: Current I0 slot content (may be empty).
        tier: Reasoning tier for the target agent.
        agent_id: Optional agent identifier for logging/tracing.

    Returns:
        Enriched I0 content string.
    """
    enrichment = get_tier_enrichment(tier)
    tier_content = enrichment.to_i0_content()

    if existing_i0 and existing_i0.strip() and existing_i0.strip() != "instructional":
        return f"{tier_content}\n\nAGENT-SPECIFIC INSTRUCTIONS:\n{existing_i0}"
    return tier_content


__all__ = [
    "EnrichmentTier",
    "InstructionalEnrichment",
    "TIER_ENRICHMENT_TABLE",
    "enrich_i0_for_tier",
    "get_tier_enrichment",
]
