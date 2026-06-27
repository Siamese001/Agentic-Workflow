"""Query decomposition primitive for apps_research retrieval pipeline.

Fan-out 3/4/5 for depth=shallow/standard/deep per plan
docs/archive/windsurf/legacy-tree/plans/apps-research-blend-baseline-c74787.md §P1.1.

W2 (plan apps-research-spine-deferred-followup-9c3e1a P2.1): adds
coverage-family dispatch. _COVERAGE_FAMILY_CATALOG and related depth-
profile tables move here from company_brief_engine (L2 → L1 cognition
layer). CompanyBriefEngine delegates fan-out decisions to
``decompose_coverage_families()`` so the engine stays purely
assembly-oriented.

The decomposer produces distinct sub-queries covering canonical research
facets. Partnership JDs get explicit partner, commercial, adoption, and
funding/valuation query families instead of relying on generic role-context
retrieval. That keeps retrieval-mode/provider migrations from silently
changing the quality contract.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal

Depth = Literal["shallow", "standard", "deep"]

_FAN_OUT: dict[Depth, int] = {"shallow": 3, "standard": 4, "deep": 5}

_FACET_TEMPLATES: tuple[tuple[str, str], ...] = (
    (
        "overview",
        "{topic} company overview services positioning latest funding valuation announcements",
    ),
    (
        "capabilities",
        "{topic} technical capabilities platform enterprise product partnerships alliances",
    ),
    (
        "leadership",
        "{topic} executive leadership team strategic direction partnerships revenue",
    ),
    (
        "market",
        "{topic} enterprise customers partner ecosystem co-sell GSI ISV channel adoption",
    ),
    (
        "risks",
        "{topic} key risks competitive threats operational constraints latest valuation funding",
    ),
)

_PARTNERSHIP_JD_HINTS: tuple[str, ...] = (
    "partnership",
    "partner",
    "alliance",
    "alliances",
    "co-sell",
    "cosell",
    "ecosystem",
    "gsi",
    "isv",
    "channel",
)


@dataclass(frozen=True)
class SubQuery:
    """A decomposed sub-query facet."""

    facet: str
    text: str


def decompose(topic: str, depth: Depth = "standard") -> list[SubQuery]:
    """Return ``_FAN_OUT[depth]`` distinct facet-targeted sub-queries for ``topic``.

    Args:
        topic: the research topic (company, role, or subject).
        depth: one of ``shallow`` (3), ``standard`` (4), ``deep`` (5).

    Returns:
        List of :class:`SubQuery` instances. Each ``text`` is a complete
        English question-form string; facet labels never repeat.

    Raises:
        ValueError: if ``topic`` is empty or whitespace-only.
        KeyError: if ``depth`` is not a valid :data:`Depth` value.
    """
    stripped = (topic or "").strip()
    if not stripped:
        raise ValueError("topic must be non-empty")
    n = _FAN_OUT[depth]
    return [
        SubQuery(facet=facet, text=template.format(topic=stripped))
        for facet, template in _FACET_TEMPLATES[:n]
    ]


# ---------------------------------------------------------------------------
# W2 — Coverage-family catalog and depth profiles
# Moved here from company_brief_engine.py (W4/W5 C0 pipeline) so that
# fan-out decisions live at the L1-cognition layer rather than in the
# assembly engine. CompanyBriefEngine imports from this module.
# ---------------------------------------------------------------------------

_COVERAGE_FAMILY_CATALOG: Dict[str, Dict[str, Any]] = {
    "company_basics": {
        "query_template": "{topic} company overview founding history core business",
        "min_sources": 2,
    },
    "role_context": {
        "query_template": "{topic} job openings roles hiring engineering",
        "min_sources": 1,
    },
    "leadership_and_org": {
        "query_template": "{topic} executive team CEO CTO leadership board",
        "min_sources": 1,
    },
    "recent_news_and_signals": {
        "query_template": "{topic} news 2025 2026 announcements funding valuation partnership launch",
        "min_sources": 2,
    },
    "competitive_landscape": {
        "query_template": "{topic} competitors alternatives market positioning",
        "min_sources": 1,
    },
    "financials_and_growth": {
        "query_template": "{topic} latest funding valuation revenue growth Series H Series G",
        "min_sources": 1,
    },
    "tech_stack_and_tools": {
        "query_template": "{topic} technology stack tools infrastructure engineering",
        "min_sources": 1,
    },
    "culture_and_values": {
        "query_template": "{topic} culture values diversity employee experience",
        "min_sources": 1,
    },
    "partner_ecosystem": {
        "query_template": "{topic} partners alliances cloud partnerships co-sell GSI ISV ecosystem",
        "min_sources": 1,
    },
    "commercial_motion": {
        "query_template": "{topic} enterprise sales commercial motion revenue partner-led co-sell channel",
        "min_sources": 1,
    },
    "adoption_motion": {
        "query_template": "{topic} enterprise adoption deployment implementation enablement production rollout",
        "min_sources": 1,
    },
    # DS-5 W5 (apps-research-deferred-scope-b7e3d2) — post-DOSSIER families.
    "competitive_intel": {
        "query_template": "{topic} competitive intelligence market share win-loss analysis",
        "min_sources": 2,
    },
    "regulatory_and_legal": {
        "query_template": "{topic} regulatory compliance legal filings litigation regulatory risk",
        "min_sources": 2,
    },
}

# ---------------------------------------------------------------------------
# Depth profiles — min_sources / min_citation_anchors / gate thresholds
# ---------------------------------------------------------------------------

_DEPTH_PROFILES: Dict[str, Dict[str, Any]] = {
    "COMPANY_BRIEF_LIGHT": {
        "min_sources": 5,
        "min_citation_anchors": 8,
        "max_queries": 3,
        "coverage_floor": 0.50,
        "gate_weak_floor": 0.40,
        "query_fan_out_strategy": "breadth_first",
    },
    "COMPANY_BRIEF_STANDARD": {
        "min_sources": 10,
        "min_citation_anchors": 18,
        "max_queries": 6,
        "coverage_floor": 0.65,
        "gate_weak_floor": 0.58,
        "query_fan_out_strategy": "depth_first",
    },
    "COMPANY_BRIEF_DEEP": {
        "min_sources": 18,
        "min_citation_anchors": 30,
        "max_queries": 10,
        "coverage_floor": 0.75,
        "gate_weak_floor": 0.60,
        "query_fan_out_strategy": "depth_first",
    },
    "COMPANY_BRIEF_DOSSIER": {
        "min_sources": 25,
        "min_citation_anchors": 45,
        "max_queries": 15,
        "coverage_floor": 0.85,
        "gate_weak_floor": 0.75,
        "query_fan_out_strategy": "depth_first",
    },
    # DS-5 W5 (apps-research-deferred-scope-b7e3d2) — post-DOSSIER profiles.
    # COMPETITIVE_SCAN: lighter than DOSSIER, focused on competitive landscape.
    # max_queries=12 keeps latency under 240s p99 while covering market + intel.
    # SLO entry: SLO.md §Depth-Profile SLO Thresholds.
    "COMPANY_BRIEF_COMPETITIVE_SCAN": {
        "min_sources": 20,
        "min_citation_anchors": 35,
        "max_queries": 12,
        "coverage_floor": 0.80,
        "gate_weak_floor": 0.65,
        "query_fan_out_strategy": "breadth_first",
    },
    # FORENSIC: deepest tier — regulatory, legal, and due-diligence coverage.
    # max_queries=20 allows full fanout across all 10 coverage families.
    # SLO p99 ceiling: 480s (forensic runs are background tasks).
    "COMPANY_BRIEF_FORENSIC": {
        "min_sources": 35,
        "min_citation_anchors": 60,
        "max_queries": 20,
        "coverage_floor": 0.90,
        "gate_weak_floor": 0.80,
        "query_fan_out_strategy": "depth_first",
    },
}

# depth_param_map — alias strings → canonical profile ID
_DEPTH_PARAM_MAP: Dict[str, str] = {
    "shallow": "COMPANY_BRIEF_LIGHT",
    "light": "COMPANY_BRIEF_LIGHT",
    "standard": "COMPANY_BRIEF_STANDARD",
    "deep": "COMPANY_BRIEF_DEEP",
    "dossier": "COMPANY_BRIEF_DOSSIER",
    # DS-5 W5 aliases
    "competitive_scan": "COMPANY_BRIEF_COMPETITIVE_SCAN",
    "competitive": "COMPANY_BRIEF_COMPETITIVE_SCAN",
    "forensic": "COMPANY_BRIEF_FORENSIC",
    "due_diligence": "COMPANY_BRIEF_FORENSIC",
}

# Families required per depth profile
_PROFILE_REQUIRED_FAMILIES: Dict[str, List[str]] = {
    "COMPANY_BRIEF_LIGHT": ["company_basics", "leadership_and_org"],
    "COMPANY_BRIEF_STANDARD": [
        "company_basics", "role_context", "leadership_and_org",
        "recent_news_and_signals", "competitive_landscape",
    ],
    "COMPANY_BRIEF_DEEP": [
        "company_basics", "role_context", "leadership_and_org",
        "recent_news_and_signals", "competitive_landscape",
        "financials_and_growth", "tech_stack_and_tools", "culture_and_values",
    ],
    # DOSSIER = all original catalog families plus explicit partner-motion families.
    "COMPANY_BRIEF_DOSSIER": [
        "company_basics", "role_context", "leadership_and_org",
        "recent_news_and_signals", "competitive_landscape",
        "financials_and_growth", "tech_stack_and_tools", "culture_and_values",
        "partner_ecosystem", "commercial_motion", "adoption_motion",
    ],
    # DS-5 W5 — post-DOSSIER profiles.
    # COMPETITIVE_SCAN: market + competitive intel focus; drops culture/role.
    "COMPANY_BRIEF_COMPETITIVE_SCAN": [
        "company_basics", "leadership_and_org",
        "recent_news_and_signals", "competitive_landscape",
        "financials_and_growth", "tech_stack_and_tools",
        "competitive_intel",
    ],
    # FORENSIC: all families including regulatory and due-diligence.
    "COMPANY_BRIEF_FORENSIC": list(_COVERAGE_FAMILY_CATALOG.keys()),
}


def _resolve_depth_profile(raw: str) -> str:
    """Resolve a depth param alias or profile ID to a canonical profile key."""
    if raw in _DEPTH_PROFILES:
        return raw
    return _DEPTH_PARAM_MAP.get(raw.lower(), "COMPANY_BRIEF_STANDARD")


@dataclass(frozen=True)
class QueryPlan:
    """A resolved query plan for one coverage family."""

    family: str
    query: str
    min_sources: int
    jd_boosted: bool = False


def _jd_blob(jd_context: Dict[str, Any] | None) -> str:
    if not jd_context:
        return ""
    parts: list[str] = []
    for value in jd_context.values():
        if isinstance(value, (list, tuple, set)):
            parts.extend(str(item) for item in value)
        elif isinstance(value, dict):
            parts.extend(str(item) for item in value.values())
        else:
            parts.append(str(value))
    return " ".join(parts).lower()


def _is_partnership_jd(jd_context: Dict[str, Any] | None) -> bool:
    blob = _jd_blob(jd_context)
    return any(token in blob for token in _PARTNERSHIP_JD_HINTS)


def _ordered_unique(values: list[str]) -> list[str]:
    ordered: list[str] = []
    for value in values:
        if value and value not in ordered:
            ordered.append(value)
    return ordered


def decompose_coverage_families(
    topic: str,
    depth_profile: str,
    jd_context: Dict[str, Any] | None = None,
) -> List[QueryPlan]:
    """Return a list of QueryPlan objects for the given topic and depth profile.

    Fan-out is determined by ``_PROFILE_REQUIRED_FAMILIES[depth_profile]``.
    When ``jd_context`` is provided, ``role_context`` and
    ``tech_stack_and_tools`` are included with the ``jd_boosted=True`` flag
    even if they would not be selected by the base profile. Partnership JDs
    promote explicit partner, commercial, adoption, recent-news, and
    financial/growth families into the executable prefix; ``role_context``
    alone is never treated as partner evidence.

    Args:
        topic: Company or subject name.
        depth_profile: Canonical profile key (e.g. "COMPANY_BRIEF_STANDARD").
            Aliases (``"standard"``, ``"deep"``, etc.) are resolved.
        jd_context: Optional JD dict; activates role_context + tech_stack_and_tools
            or explicit partnership retrieval families.

    Returns:
        Ordered list of :class:`QueryPlan` instances, one per family.
        Never empty for valid topics.

    Raises:
        ValueError: if ``topic`` is empty or whitespace-only.
    """
    stripped = (topic or "").strip()
    if not stripped:
        raise ValueError("topic must be non-empty")

    resolved = _resolve_depth_profile(depth_profile)
    base_families = list(
        _PROFILE_REQUIRED_FAMILIES.get(
            resolved,
            _PROFILE_REQUIRED_FAMILIES["COMPANY_BRIEF_STANDARD"],
        )
    )

    partnership_mode = _is_partnership_jd(jd_context)
    if partnership_mode:
        partner_prefix = [
            "company_basics",
            "financials_and_growth",
            "partner_ecosystem",
            "commercial_motion",
            "adoption_motion",
            "recent_news_and_signals",
            "leadership_and_org",
            "tech_stack_and_tools",
            "competitive_landscape",
        ]
        base_families = _ordered_unique(
            partner_prefix + [fam for fam in base_families if fam != "role_context"]
        )
    else:
        # JD presence activates role_context + tech_stack_and_tools if not already present.
        jd_boosted_families: list[str] = []
        if jd_context:
            for fam in ("role_context", "tech_stack_and_tools"):
                if fam not in base_families:
                    jd_boosted_families.append(fam)
        base_families = _ordered_unique(base_families + jd_boosted_families)

    plans: List[QueryPlan] = []
    for fam in base_families:
        cfg = _COVERAGE_FAMILY_CATALOG.get(fam, {})
        query = cfg.get("query_template", "{topic} " + fam.replace("_", " ")).format(topic=stripped)
        plans.append(QueryPlan(
            family=fam,
            query=query,
            min_sources=cfg.get("min_sources", 1),
            jd_boosted=bool(jd_context) and (
                fam in {"role_context", "tech_stack_and_tools"}
                or (partnership_mode and fam in {
                    "financials_and_growth",
                    "partner_ecosystem",
                    "commercial_motion",
                    "adoption_motion",
                    "recent_news_and_signals",
                })
            ),
        ))
    return plans
