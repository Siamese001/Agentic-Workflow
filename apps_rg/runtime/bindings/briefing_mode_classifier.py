"""apps_rg briefing mode classifier.

W5: Strict precedence-based classification of the company-brief sourcing path.
No agentic_core imports — this is apps_rg-owned logic.

Canonical briefing modes (must match profile YAML):
  UPLOADED_BRIEFING        — caller supplied a manual_brief_path
  DELEGATED_APPS_RESEARCH  — research_via == "apps_research"
  NATIVE_C0                — chroma_path is resolved (local vector retrieval)
  NONE                     — no brief; no retrieval

Plan: apps-rg-retrieval-metrics-ownership-and-c0-evidence-plan W5
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Mode constants
# ---------------------------------------------------------------------------

BRIEFING_MODE_UPLOADED: str = "UPLOADED_BRIEFING"
BRIEFING_MODE_DELEGATED: str = "DELEGATED_APPS_RESEARCH"
BRIEFING_MODE_NATIVE_C0: str = "NATIVE_C0"
BRIEFING_MODE_NONE: str = "NONE"

_VALID_BRIEFING_MODES: frozenset[str] = frozenset({
    BRIEFING_MODE_UPLOADED,
    BRIEFING_MODE_DELEGATED,
    BRIEFING_MODE_NATIVE_C0,
    BRIEFING_MODE_NONE,
})


# ---------------------------------------------------------------------------
# Decision shape
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class BriefingModeDecision:
    """Result of classify_briefing_mode.

    retrieval_mode and briefing_source_type are always identical — the
    duplication is intentional so c0_metrics fields can use either name.

    company_brief_provenance is a dict for UPLOADED/DELEGATED modes, None
    for NATIVE_C0/NONE modes.

    classified_from is a human-readable string naming the signal that drove
    the classification (e.g. the key or value that was checked).
    """

    retrieval_mode: str
    briefing_source_type: str
    company_brief_provenance: Optional[dict]
    classified_from: str = ""


# ---------------------------------------------------------------------------
# Classifier
# ---------------------------------------------------------------------------

def classify_briefing_mode(
    app_payload: dict[str, Any],
    chroma_path_resolved: Optional[str],
    research_via: Optional[str] = None,
) -> BriefingModeDecision:
    """Classify the briefing mode from the payload using strict precedence.

    Precedence order (highest → lowest):
    1. UPLOADED_BRIEFING  — policy_refs.manual_brief_path is non-empty
    2. DELEGATED_APPS_RESEARCH — research_via == "apps_research" (caller arg
       or payload["research_via"] or payload["briefing"]["research_via"])
    3. NATIVE_C0          — chroma_path_resolved is non-empty
    4. NONE               — nothing else matched

    No loose string inference is performed.  Values are resolved from
    explicit payload keys only.

    Parameters
    ----------
    app_payload:
        The validated request payload dict for this run.
    chroma_path_resolved:
        Resolved Chroma collection path, or None if not resolved.
    research_via:
        Explicit caller override for research delegation channel.

    Returns
    -------
    BriefingModeDecision
    """
    policy_refs: dict[str, Any] = app_payload.get("policy_refs", {}) or {}
    briefing: dict[str, Any] = app_payload.get("briefing", {}) or {}

    # 1. Uploaded briefing
    manual_path = policy_refs.get("manual_brief_path") or ""
    if manual_path:
        provenance: Optional[dict] = {
            "source": "uploaded_brief",
            "path": manual_path,
            "fetched_at": policy_refs.get("brief_fetched_at", ""),
            "freshness_ttl_days": policy_refs.get("brief_freshness_ttl_days", None),
        }
        return BriefingModeDecision(
            retrieval_mode=BRIEFING_MODE_UPLOADED,
            briefing_source_type=BRIEFING_MODE_UPLOADED,
            company_brief_provenance=provenance,
            classified_from="policy_refs.manual_brief_path",
        )

    # 2. Delegated apps_research
    resolved_via = (
        research_via
        or app_payload.get("research_via")
        or briefing.get("research_via")
        or ""
    )
    if resolved_via == "apps_research":
        provenance = {
            "source": "delegated_apps_research",
            "delegate": "apps_research",
            "fetched_at": briefing.get("fetched_at", ""),
            "freshness_ttl_days": briefing.get("freshness_ttl_days", None),
        }
        return BriefingModeDecision(
            retrieval_mode=BRIEFING_MODE_DELEGATED,
            briefing_source_type=BRIEFING_MODE_DELEGATED,
            company_brief_provenance=provenance,
            classified_from=f"research_via=apps_research",
        )

    # 3. Native C0 (local Chroma retrieval)
    if chroma_path_resolved:
        return BriefingModeDecision(
            retrieval_mode=BRIEFING_MODE_NATIVE_C0,
            briefing_source_type=BRIEFING_MODE_NATIVE_C0,
            company_brief_provenance=None,
            classified_from="chroma_path_resolved",
        )

    # 4. NONE — explicit, not silent
    return BriefingModeDecision(
        retrieval_mode=BRIEFING_MODE_NONE,
        briefing_source_type=BRIEFING_MODE_NONE,
        company_brief_provenance=None,
        classified_from="no_signal",
    )


def assert_mode_is_canonical(mode: str) -> None:
    """Raise ValueError if mode is not in the canonical set.

    Used in tests and at runtime to guard against loose inference producing
    non-canonical values.
    """
    if mode not in _VALID_BRIEFING_MODES:
        raise ValueError(
            f"Non-canonical briefing mode {mode!r}; "
            f"valid values: {sorted(_VALID_BRIEFING_MODES)}"
        )


__all__ = [
    "BRIEFING_MODE_UPLOADED",
    "BRIEFING_MODE_DELEGATED",
    "BRIEFING_MODE_NATIVE_C0",
    "BRIEFING_MODE_NONE",
    "BriefingModeDecision",
    "_VALID_BRIEFING_MODES",
    "assert_mode_is_canonical",
    "classify_briefing_mode",
]
