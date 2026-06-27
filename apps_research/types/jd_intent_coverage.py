"""JD-derived evidence intent contract for apps_research gates.

This module keeps role relevance generic: the JD selects evidence intents,
and each intent contributes required source families plus sourced signal terms.
It deliberately avoids treating a single ambiguous word such as "partner" as
proof that a role is partnership-led.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class EvidenceIntent:
    """A role-relevant research intent inferred from JD text."""

    intent_id: str
    required_families: tuple[str, ...]
    signal_terms: tuple[str, ...]


_INTENT_CATALOG: dict[str, EvidenceIntent] = {
    "partnerships": EvidenceIntent(
        intent_id="partnerships",
        required_families=("partner_ecosystem", "commercial_motion", "adoption_motion"),
        signal_terms=(
            "co-sell",
            "cosell",
            "gsi",
            "isv",
            "channel",
            "enablement",
            "joint solution",
            "technical close",
            "ecosystem revenue",
            "partner-led",
        ),
    ),
    "platform_engineering": EvidenceIntent(
        intent_id="platform_engineering",
        required_families=("tech_stack_and_tools", "adoption_motion"),
        signal_terms=("architecture", "platform", "infrastructure", "integration", "deployment"),
    ),
    "security_trust": EvidenceIntent(
        intent_id="security_trust",
        required_families=("regulatory_and_legal", "tech_stack_and_tools"),
        signal_terms=("security", "trust", "compliance", "risk", "privacy", "governance"),
    ),
    "product_strategy": EvidenceIntent(
        intent_id="product_strategy",
        required_families=("recent_news_and_signals", "competitive_landscape", "adoption_motion"),
        signal_terms=("product", "roadmap", "launch", "adoption", "customer"),
    ),
    "sales_gtm": EvidenceIntent(
        intent_id="sales_gtm",
        required_families=("commercial_motion", "competitive_landscape", "financials_and_growth"),
        signal_terms=("sales", "gtm", "go-to-market", "revenue", "commercial", "buyer"),
    ),
    "regulated_enterprise": EvidenceIntent(
        intent_id="regulated_enterprise",
        required_families=("regulatory_and_legal", "tech_stack_and_tools"),
        signal_terms=("regulated", "bank", "insurance", "audit", "compliance", "risk"),
    ),
    "applied_ai": EvidenceIntent(
        intent_id="applied_ai",
        required_families=("tech_stack_and_tools", "adoption_motion", "recent_news_and_signals"),
        signal_terms=("ai", "machine learning", "ml", "llm", "model", "agentic"),
    ),
}

_INTENT_PATTERNS: dict[str, tuple[str, ...]] = {
    "partnerships": (
        r"\bstrategic partnerships?\b",
        r"\bpartnerships?\b",
        r"\balliances?\b",
        r"\bco-?sell\b",
        r"\bgsi\b",
        r"\bisv\b",
        r"\bchannel partners?\b",
        r"\bpartner ecosystem\b",
        r"\becosystem revenue\b",
    ),
    "platform_engineering": (
        r"\bplatform\b",
        r"\barchitecture\b",
        r"\barchitect\b",
        r"\binfrastructure\b",
        r"\bengineering\b",
        r"\bdata platform\b",
    ),
    "security_trust": (
        r"\bsecurity\b",
        r"\btrust\b",
        r"\bprivacy\b",
        r"\bgovernance\b",
        r"\bcompliance\b",
        r"\brisk\b",
    ),
    "product_strategy": (
        r"\bproduct\b",
        r"\broadmap\b",
        r"\blaunch\b",
        r"\badoption\b",
        r"\bcustomer experience\b",
    ),
    "sales_gtm": (
        r"\bsales\b",
        r"\bgtm\b",
        r"\bgo-to-market\b",
        r"\brevenue\b",
        r"\bcommercial\b",
        r"\bbuyer\b",
    ),
    "regulated_enterprise": (
        r"\bregulated\b",
        r"\bbank(?:ing)?\b",
        r"\binsurance\b",
        r"\baudit\b",
        r"\bfinserv\b",
    ),
    "applied_ai": (
        r"\bapplied ai\b",
        r"\bai\b",
        r"\bmachine learning\b",
        r"\bml\b",
        r"\bllm\b",
        r"\bgenai\b",
        r"\bmodel\b",
        r"\bagentic\b",
    ),
}


def jd_context_text(jd_context: dict[str, Any] | None) -> str:
    """Flatten JD context into lower-case text."""

    if not jd_context:
        return ""
    parts: list[str] = []
    for value in jd_context.values():
        if isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
        elif isinstance(value, (list, tuple, set)):
            parts.extend(str(item) for item in value)
        else:
            parts.append(str(value))
    return " ".join(parts).lower()


def infer_evidence_intents_from_text(jd_text: str) -> tuple[EvidenceIntent, ...]:
    """Infer role-relevant evidence intents from JD text."""

    low = (jd_text or "").lower()
    if not low:
        return ()
    intents: list[EvidenceIntent] = []
    for intent_id, patterns in _INTENT_PATTERNS.items():
        if any(re.search(pattern, low) for pattern in patterns):
            intents.append(_INTENT_CATALOG[intent_id])
    return tuple(intents)


def infer_evidence_intents(jd_context: dict[str, Any] | None) -> tuple[EvidenceIntent, ...]:
    """Infer role-relevant evidence intents from structured JD context."""

    return infer_evidence_intents_from_text(jd_context_text(jd_context))


def required_families_for_intents(intents: Iterable[EvidenceIntent]) -> tuple[str, ...]:
    """Return ordered unique source families required by intents."""

    families: list[str] = []
    for intent in intents:
        for family in intent.required_families:
            if family not in families:
                families.append(family)
    return tuple(families)


def signal_terms_for_intents(intents: Iterable[EvidenceIntent]) -> tuple[str, ...]:
    """Return ordered unique sourced signal terms required by intents."""

    terms: list[str] = []
    for intent in intents:
        for term in intent.signal_terms:
            if term not in terms:
                terms.append(term)
    return tuple(terms)


def intent_ids(intents: Iterable[EvidenceIntent]) -> tuple[str, ...]:
    """Return ordered intent ids."""

    return tuple(intent.intent_id for intent in intents)


__all__ = [
    "EvidenceIntent",
    "infer_evidence_intents",
    "infer_evidence_intents_from_text",
    "intent_ids",
    "jd_context_text",
    "required_families_for_intents",
    "signal_terms_for_intents",
]
