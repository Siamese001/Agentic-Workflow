"""Archetype-conditioned subject-line bandit configuration.

W1-P1 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35, Bundle A).

Configuration source for the subject-line variant bandit. The bandit itself
is the existing ``agentic_core.L0_routing.reasoning.namespace_bandit``
``NamespaceBandit`` — this module only supplies:

1. The admissible variant IDs per archetype.
2. The namespace-string builder that binds
   ``namespace=apps_lic.subject_line.<archetype>`` for the closed-loop
   ROUTER_DECISION ledger.
3. The subject-line template strings keyed by variant ID.

Each archetype gets three arms — the three empirically highest-reply-rate
subject-line shapes in LinkedIn outreach literature:

- ``question``            — ends in "?", personalised to recipient context
- ``observation``         — opens with a specific, verifiable observation
- ``mutual_ref``          — references a shared connection or company trigger

Variant ``pipeline`` and ``quality_filter`` replace ``mutual_ref`` for
SENIOR_TA and RECRUITER respectively because mutual-connection framing
under-performs for those archetypes per industry data.

This module is pure config — no I/O, no state, no side effects. The only
runtime dependency is on ``str.format`` for template substitution.
"""

from __future__ import annotations

from typing import Final, Mapping

# SSOT for the five canonical archetype labels emitted by ProfilePlanner
# and consumed throughout the HOP pipeline. Sorted for deterministic iter.
ARCHETYPES: Final[tuple[str, ...]] = (
    "C_LEVEL",
    "EXECUTIVE",
    "OTHER",
    "RECRUITER",
    "SENIOR_TA",
)

# Admissible variant IDs per archetype. Three arms per archetype keeps
# bandit convergence tractable — Wilson CI reaches 95% after ~200 samples.
ADMISSIBLE_VARIANTS: Final[Mapping[str, tuple[str, ...]]] = {
    "C_LEVEL":   ("question", "observation", "mutual_ref"),
    "EXECUTIVE": ("question", "observation", "mutual_ref"),
    "SENIOR_TA": ("question", "observation", "pipeline"),
    "RECRUITER": ("question", "observation", "quality_filter"),
    "OTHER":     ("question", "observation", "mutual_ref"),
}

# Template strings keyed by (archetype, variant_id). Each template expects
# the following format keys:
#   {recipient_first_name}, {recipient_company}, {observation}, {mutual_name}
# When a template lacks a given key the renderer supplies the empty string.
#
# Subject lines are capped at 50 characters visually; formats here aim for
# 40-48 to leave headroom once substituted. The renderer in
# ``subject_line_variant_selector.SubjectLineVariantSelector.render`` is
# responsible for truncation + fallback.
SUBJECT_TEMPLATES: Final[Mapping[tuple[str, str], str]] = {
    # C_LEVEL — very formal, deference-signalling
    ("C_LEVEL", "question"):     "{recipient_first_name}, one strategic question",
    ("C_LEVEL", "observation"):  "{recipient_company}'s {observation}",
    ("C_LEVEL", "mutual_ref"):   "{mutual_name} suggested I reach out",
    # EXECUTIVE — formal, specific
    ("EXECUTIVE", "question"):    "{recipient_first_name}, quick strategic question",
    ("EXECUTIVE", "observation"): "Noticed {recipient_company}'s {observation}",
    ("EXECUTIVE", "mutual_ref"):  "{mutual_name} recommended a conversation",
    # SENIOR_TA — pipeline-focused
    ("SENIOR_TA", "question"):    "{recipient_first_name}, pipeline question",
    ("SENIOR_TA", "observation"): "{recipient_company} {observation}",
    ("SENIOR_TA", "pipeline"):    "Candidate pipeline for {recipient_company}",
    # RECRUITER — quality-filter framing
    ("RECRUITER", "question"):       "{recipient_first_name}, one filter question",
    ("RECRUITER", "observation"):    "{recipient_company}'s {observation}",
    ("RECRUITER", "quality_filter"): "Pre-filtered candidate, {recipient_company}",
    # OTHER — general best-practice defaults
    ("OTHER", "question"):    "{recipient_first_name}, quick question",
    ("OTHER", "observation"): "Noticed {recipient_company}",
    ("OTHER", "mutual_ref"):  "{mutual_name} mentioned you",
}

# Visual cap for LinkedIn subject lines. Longer subjects truncate with
# ellipsis in the LinkedIn UI — industry data shows reply-rate drops ~30%
# at 50+ characters.
SUBJECT_LINE_MAX_CHARS: Final[int] = 50

# Namespace prefix for the bandit. The fully-qualified namespace is
# ``{BANDIT_NAMESPACE_PREFIX}.{archetype}`` (lowercase archetype for
# consistency with existing namespace_bandit cells such as
# "apps_rg.retrieval"). The prefix is stable — downstream calibration
# reports pattern-match on it.
BANDIT_NAMESPACE_PREFIX: Final[str] = "apps_lic.subject_line"


def build_namespace(archetype: str) -> str:
    """Build the fully-qualified bandit namespace for an archetype.

    Deterministic. Lowercase-normalised. The output string is the
    ``namespace`` argument to ``NamespaceBandit.choose`` /
    ``NamespaceBandit.update``.

    Args:
        archetype: One of the five ``ARCHETYPES`` values. Unknown values
            are accepted — they get the prefix with the raw (lower-cased)
            label, so the bandit still learns but under a distinct cell.

    Returns:
        ``f"{BANDIT_NAMESPACE_PREFIX}.{archetype.lower()}"``.
    """
    return f"{BANDIT_NAMESPACE_PREFIX}.{archetype.lower()}"


def admissible_variants_for(archetype: str) -> tuple[str, ...]:
    """Return the admissible variant IDs for an archetype.

    Falls back to the OTHER archetype's admissible set when the archetype
    is not in ``ADMISSIBLE_VARIANTS``. This preserves the bandit contract
    that ``choose`` is called with a non-empty admissible list.
    """
    return ADMISSIBLE_VARIANTS.get(archetype, ADMISSIBLE_VARIANTS["OTHER"])


def template_for(archetype: str, variant_id: str) -> str:
    """Return the subject-line template for ``(archetype, variant_id)``.

    Falls back to ``OTHER``'s ``question`` template when the key is
    missing — preserves the generation contract that every (archetype,
    variant_id) the bandit can emit has a renderable template.
    """
    key = (archetype, variant_id)
    if key in SUBJECT_TEMPLATES:
        return SUBJECT_TEMPLATES[key]
    return SUBJECT_TEMPLATES[("OTHER", "question")]


__all__ = [
    "ADMISSIBLE_VARIANTS",
    "ARCHETYPES",
    "BANDIT_NAMESPACE_PREFIX",
    "SUBJECT_LINE_MAX_CHARS",
    "SUBJECT_TEMPLATES",
    "admissible_variants_for",
    "build_namespace",
    "template_for",
]
