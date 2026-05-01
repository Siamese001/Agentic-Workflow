"""Outreach trigger types for HOP2 research signal injection.

W2-P4 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

A CompanyTrigger is a structured, archetype-relevant piece of recent
news that elevates reply probability when referenced in the opening
line of an outreach message. Industry data: messages that lead with a
concrete trigger (funding round, leadership change, product launch,
earnings beat) convert at ~1.8x the baseline reply rate.

Trigger taxonomy (fixed — extending requires an ADR):
    - funding_round   : Series X raise, IPO pricing, private round close
    - leadership      : New exec hire, CXO transition, board appointment
    - product_launch  : GA announcement, new feature, public beta release
    - earnings        : Quarterly results beat/miss, guidance change
    - acquisition     : M&A event (target or acquirer)
    - expansion       : Geographic / market expansion, new office
    - award           : Industry award, recognition, top-N list inclusion

Strength bands:
    - strong    : explicit corroboration (quoted figure, named source)
    - moderate  : keyword match with quantifier nearby
    - weak      : keyword match only
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Final, Tuple

# Canonical trigger-type labels. Immutable tuple so accidental mutation
# is impossible; extension requires touching this constant + the
# extractor rules table in ``company_trigger_extractor._TRIGGER_RULES``.
TRIGGER_TYPES: Final[Tuple[str, ...]] = (
    "funding_round",
    "leadership",
    "product_launch",
    "earnings",
    "acquisition",
    "expansion",
    "award",
)

# Canonical strength labels. Lower case. ``strong`` sorts ahead of
# ``moderate`` ahead of ``weak`` when the extractor must choose a
# single trigger for the opening line.
STRENGTH_BANDS: Final[Tuple[str, ...]] = ("strong", "moderate", "weak")


@dataclass(frozen=True)
class CompanyTrigger:
    """Structured outreach trigger extracted from HOP2 research.

    Attributes:
        trigger_type: One of ``TRIGGER_TYPES``. Callers MUST NOT rely on
            unknown values — HOP5 only knows how to compose opening
            lines for the canonical set.
        raw_excerpt: Up to 240 chars from the source research artifact
            that motivated the trigger. Kept for audit / compliance.
        strength: One of ``STRENGTH_BANDS``. Drives ordering when HOP5
            has multiple triggers to choose from.
        source_id: Artifact ID from HOP2 evidence_pack.
        matched_keyword: The exact substring that matched in the source.
            Useful for explaining the trigger to the operator and for
            test harness assertions.
        metadata: Free-form extension dict. Extractors MAY populate but
            HOP5 MUST tolerate absence of all keys.
    """

    trigger_type: str
    raw_excerpt: str
    strength: str
    source_id: str
    matched_keyword: str
    metadata: dict = field(default_factory=dict)


__all__ = [
    "STRENGTH_BANDS",
    "TRIGGER_TYPES",
    "CompanyTrigger",
]
