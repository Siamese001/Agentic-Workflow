"""Cross-exam depth anchor synthesis from ExperiencePoints — Wave 3 phase 3.2.

Groups multiple related ExperiencePoints into defensive anchors for
cross-exam interview probes. An anchor is a thesis statement (e.g. "$22M
productized AI revenue economics") backed by 2-4 ExperiencePoints from
different roles + a hand-derivable defensive narrative.

Architecture
------------
Same primitive as W3.1 (deterministic field projection + spine BGE
ranking) extended to multi-point composition. Tags drive clustering;
the cluster's title becomes the anchor heading; the cluster's metric
phrases become the defensive evidence list.

No-LLM contract: tag clusters are computed deterministically from
``_ANCHOR_TAG_CLUSTERS``; ranking against the JD/research signal flows
through the spine adapter's BGE/keyword path (same as W3.1).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from apps_qna.integrations.spine_adapter import classify_section_topic

if TYPE_CHECKING:
    from apps_qna.types.qna_types import ExperienceLibrary, ExperiencePoint

_log = logging.getLogger(__name__)

# Predefined anchor archetypes. Each cluster maps a thesis to the tag set
# that qualifies an ExperiencePoint as supporting evidence. Multi-tag
# clusters require BOTH: e.g. "Productization economics" needs both
# "productization" AND a metric tag.
_ANCHOR_TAG_CLUSTERS: list[tuple[str, str, frozenset[str]]] = [
    (
        "Productization economics",
        "Defensive thesis: bespoke -> platform shift drives durable margin "
        "expansion, not headcount cuts.",
        frozenset({"productization", "shared-services", "metric-22M-revenue",
                   "metric-15M-revenue", "metric-20pct-margin",
                   "metric-25pct-renewal"}),
    ),
    (
        "Engineering org scaling",
        "Defensive thesis: leveling clarity + ownership over headcount.",
        frozenset({"leadership", "metric-8-to-28-team", "team"}),
    ),
    (
        "Cycle compression discipline",
        "Defensive thesis: standardized lifecycle, not heroic sprints.",
        frozenset({"lifecycle", "lab-to-production", "metric-6mo-to-3wk",
                   "ai-cicd"}),
    ),
    (
        "Hyperscaler co-sell motion",
        "Defensive thesis: real co-sell needs joint roadmaps with the "
        "partner's account team, not marketing-line padding.",
        frozenset({"co-sell", "hyperscaler-alliance", "metric-15M-revenue"}),
    ),
    (
        "Regulated-industries delivery",
        "Defensive thesis: governance + audit + uptime are first-class "
        "design concerns, not bolted-on after the fact.",
        frozenset({"regulated", "metric-99.9-uptime", "lineage",
                   "observability", "metric-50pct-latency-reduction"}),
    ),
    (
        "Legacy-to-cloud transformation",
        "Defensive thesis: architecture ladder lets old systems retire one "
        "component at a time, not all at once.",
        frozenset({"cloud-migration", "legacy-modernization",
                   "metric-30pct-overhead-reduction",
                   "metric-40pct-tco-reduction", "aws"}),
    ),
    (
        "Governed agentic platform",
        "Defensive thesis: deterministic routing + multi-agent orchestration "
        "+ replayable execution traces are the constitutional surface.",
        frozenset({"agentic-platform", "governance", "graphrag",
                   "sandboxing", "replayable-traces", "policy-gating"}),
    ),
]

_MIN_POINTS_PER_ANCHOR: int = 2
_MAX_POINTS_PER_ANCHOR: int = 4
_DEFAULT_TOP_N: int = 5
_EMBEDDING_THRESHOLD: float = 0.30
_KEYWORD_THRESHOLD: float = 0.08


@dataclass(frozen=True)
class DepthAnchor:
    """A multi-experience defensive anchor for cross-exam probes."""

    title: str
    thesis: str
    supporting_points: tuple[str, ...]
    """List of ExperiencePoint title strings — the operator pastes the actual
    one-liners from the matching points for the live answer."""

    tag_overlap: tuple[str, ...]


def _qualifying_points(
    library: "ExperienceLibrary",
    cluster_tags: frozenset[str],
) -> list["ExperiencePoint"]:
    """Return points whose tags overlap the cluster (any-match)."""
    qualifying: list[ExperiencePoint] = []
    for point in library.points:
        overlap = set(point.technical_depth_tags) & cluster_tags
        if overlap:
            qualifying.append(point)
    return qualifying


def synthesize_cross_exam_anchors(
    library: "ExperienceLibrary",
    *,
    jd_text: str | None = None,
    interviewer_lenses: dict[str, str] | None = None,
    role_areas: list[str] | None = None,
    industry_trends: list[str] | None = None,
    top_n: int = _DEFAULT_TOP_N,
) -> list[DepthAnchor]:
    """Synthesize the cross-exam depth-anchor list.

    For each predefined cluster, collect ExperiencePoints whose tags
    overlap the cluster. Skip clusters with fewer than
    ``_MIN_POINTS_PER_ANCHOR`` qualifying points. Cap supporting points
    at ``_MAX_POINTS_PER_ANCHOR``. Rank the resulting anchors against
    the demand signal (JD + interviewer lens + role areas + trends) via
    the spine BGE/keyword classifier.
    """
    if not library.points:
        return []

    # First pass: build raw anchors from clusters.
    raw_anchors: list[DepthAnchor] = []
    for title, thesis, cluster_tags in _ANCHOR_TAG_CLUSTERS:
        qualifying = _qualifying_points(library, cluster_tags)
        if len(qualifying) < _MIN_POINTS_PER_ANCHOR:
            continue
        # Order by "tag overlap richness" (more overlap = more central).
        qualifying.sort(
            key=lambda p: len(set(p.technical_depth_tags) & cluster_tags),
            reverse=True,
        )
        capped = qualifying[:_MAX_POINTS_PER_ANCHOR]
        overlap = sorted(
            {tag for p in capped for tag in (set(p.technical_depth_tags) & cluster_tags)}
        )
        raw_anchors.append(
            DepthAnchor(
                title=title,
                thesis=thesis,
                supporting_points=tuple(p.title for p in capped),
                tag_overlap=tuple(overlap),
            )
        )

    if not raw_anchors:
        return []

    # Second pass: rank against the demand signal if any signal is present.
    signal_parts: list[str] = []
    if jd_text:
        signal_parts.append(jd_text)
    if interviewer_lenses:
        signal_parts.append(" ".join(interviewer_lenses.values()))
    if role_areas:
        signal_parts.append("; ".join(role_areas))
    if industry_trends:
        signal_parts.append("; ".join(industry_trends))
    signal = "\n\n".join(signal_parts)

    if not signal.strip():
        # No signal -> registry order, capped at top_n.
        return raw_anchors[:top_n]

    # Build candidate descriptors (title + thesis + tags) for ranking.
    candidates = {
        anchor.title: f"{anchor.title}. {anchor.thesis} Tags: {', '.join(anchor.tag_overlap)}"
        for anchor in raw_anchors
    }
    ranked: list[tuple[DepthAnchor, float, str]] = []
    for anchor in raw_anchors:
        topic, score, mode = classify_section_topic(
            signal,
            {anchor.title: candidates[anchor.title]},
        )
        ranked.append((anchor, score, mode))
    ranked.sort(key=lambda r: r[1], reverse=True)

    accepted: list[DepthAnchor] = []
    for anchor, score, mode in ranked:
        threshold = (
            _EMBEDDING_THRESHOLD if mode == "embedding" else _KEYWORD_THRESHOLD
        )
        if mode == "empty" or score >= threshold:
            accepted.append(anchor)
        if len(accepted) >= top_n:
            break

    # If thresholds drop everything, return registry order so we always
    # produce something.
    if not accepted:
        accepted = raw_anchors[:top_n]

    _log.info(
        "cross-exam anchor synthesis: %d clusters -> %d anchors emitted",
        len(_ANCHOR_TAG_CLUSTERS),
        len(accepted),
    )
    return accepted


def synthesize_into_extra_context(
    library: "ExperienceLibrary",
    *,
    jd_text: str | None = None,
    interviewer_lenses: dict[str, str] | None = None,
    role_areas: list[str] | None = None,
    industry_trends: list[str] | None = None,
    existing: list | None = None,
    top_n: int = _DEFAULT_TOP_N,
) -> list[dict[str, str]]:
    """Synthesize anchors as Jinja-friendly dict shape.

    Templates iterate over ``cross_exam_depth_anchors`` and read
    ``topic`` + ``specifics`` keys (matches the existing Searce YAML
    extra_context convention). When ``existing`` is non-empty, returns
    it unchanged (operator-curated wins).
    """
    if existing:
        return existing
    anchors = synthesize_cross_exam_anchors(
        library,
        jd_text=jd_text,
        interviewer_lenses=interviewer_lenses,
        role_areas=role_areas,
        industry_trends=industry_trends,
        top_n=top_n,
    )
    return [
        {
            "topic": anchor.title,
            "specifics": (
                f"{anchor.thesis} Supporting points: "
                + "; ".join(anchor.supporting_points)
            ),
        }
        for anchor in anchors
    ]


__all__ = [
    "DepthAnchor",
    "synthesize_cross_exam_anchors",
    "synthesize_into_extra_context",
]
