"""Curated spam-trigger phrase list for outreach validation.

W3-P8 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Each phrase in this list has been empirically associated with
reply-rate-bottom-decile messages in LinkedIn outreach research. The
categories make the blocklist explainable — a violation tells the
operator both WHAT matched and WHY it hurts reply rates.

The validator performs a word-boundary, case-insensitive match — so
"circle back" matches in "I'll circle back" but NOT in "circled backwards".

Categories:
    corporate_cliche  — worn-out corporate buzzwords (17 phrases)
    pushy_cta         — aggressive sales CTAs that trigger spam filters (9)
    generic_opener    — formulaic greetings that scream template (10)
    false_urgency     — manufactured scarcity / time pressure (5)

Total: 41 phrases. Revisiting this list is a data-driven exercise —
add a new phrase only when A/B data shows it correlates with a reply-
rate drop of >5%.
"""

from __future__ import annotations

from typing import Final, Mapping, Tuple

# Canonical spam-trigger phrases grouped by category. Each phrase is
# lowercase and uses single-space separators; the validator handles
# case-folding on incoming text.
SPAM_TRIGGER_PHRASES: Final[Mapping[str, Tuple[str, ...]]] = {
    "corporate_cliche": (
        "circle back",
        "touch base",
        "synergy",
        "synergies",
        "synergistic",
        "thought leader",
        "thought leadership",
        "move the needle",
        "deep dive",
        "low hanging fruit",
        "boil the ocean",
        "paradigm shift",
        "game changer",
        "game-changer",
        "disruptive",
        "bleeding edge",
        "best in class",
    ),
    "pushy_cta": (
        "act now",
        "don't miss out",
        "limited time",
        "book a call",
        "grab time on my calendar",
        "schedule a demo",
        "15 minute demo",
        "quick 15 minute call",
        "calendly",
    ),
    "generic_opener": (
        "hope this finds you well",
        "hope this email finds you well",
        "hope all is well",
        "reaching out because",
        "i came across your profile",
        "i wanted to reach out",
        "just wanted to reach out",
        "quick question",
        "i hope you're doing well",
        "trust this message finds you well",
    ),
    "false_urgency": (
        "last chance",
        "ending soon",
        "only a few spots",
        "final call",
        "deadline approaching",
    ),
}

# Flattened, sorted view used for iteration. Stable order so telemetry
# reports have deterministic ordering.
ALL_PHRASES: Final[Tuple[Tuple[str, str], ...]] = tuple(
    sorted(
        (phrase, category)
        for category, phrases in SPAM_TRIGGER_PHRASES.items()
        for phrase in phrases
    )
)

# Severity tier per category. The validator emits per-category counts
# and can hard-reject at "critical" tier while warning at "medium".
CATEGORY_SEVERITY: Final[Mapping[str, str]] = {
    "corporate_cliche": "medium",
    "pushy_cta": "high",
    "generic_opener": "medium",
    "false_urgency": "critical",
}


def phrases_in_category(category: str) -> Tuple[str, ...]:
    """Return the tuple of phrases in ``category``, or empty tuple."""
    return SPAM_TRIGGER_PHRASES.get(category, ())


def category_for_phrase(phrase: str) -> str | None:
    """Return the category label for ``phrase`` or None if not tracked."""
    needle = phrase.lower().strip()
    for category, phrases in SPAM_TRIGGER_PHRASES.items():
        if needle in phrases:
            return category
    return None


__all__ = [
    "ALL_PHRASES",
    "CATEGORY_SEVERITY",
    "SPAM_TRIGGER_PHRASES",
    "category_for_phrase",
    "phrases_in_category",
]
