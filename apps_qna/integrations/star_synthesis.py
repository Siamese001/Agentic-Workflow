"""STAR / RCA synthesis from ExperiencePoints — Wave 3 phase 3.1.

Projects ``ExperiencePoint`` rows from ``master_resume_svp.json`` onto the
``Story`` (STAR) and ``RCAStory`` shapes the card pack expects, ranks them
by relevance to the interviewer signal (JD + research hot buttons + role
areas), and returns the top-N most relevant stories.

Architecture
------------
**Deterministic projection + spine-routed ranking.** This module does NOT
invoke an LLM. The projection from ExperiencePoint to Story is a
field-mapping deterministic transform. The ranking primitive is BGE-M3
via ``spine_adapter.classify_section_topic`` — same primitive used by
W2 retrieval, so the embedding/keyword-fallback contract is symmetric.

Why not LLM synthesis (yet)
- Resume content is factual-claim territory; LLM hallucination risk is
  unacceptable for stories the candidate will tell live in an interview.
- Build determinism is a canonical card-builder invariant (same YAML in
  → byte-identical output, modulo the manifest timestamp).
- W2.1 set the precedent ``no LLM in parsing``; STAR projection is
  parsing-adjacent (structured input → structured output).
- Future L2 swap is trivial: replace ``_project_to_star`` with an L2
  call; the input/output contract stays identical.

RCA handling
------------
``synthesize_rca_skeletons`` emits SKELETON ``RCAStory`` entries (with
operator-fill placeholders) drawn from the riskiest-looking bullets
(transformation, modernization, large-scale moves). Real RCA stories
require the candidate to honestly recall a failure with root-cause
analysis; auto-generating fictional failures is harmful. The skeletons
exist as scaffolding for the operator to flesh out, not as paste-ready
content.

Spine routing summary
---------------------
- L1 cognition (BGE embeddings) → ranking
- Domain knowledge (resume schema, STAR shape, RCA shape) → apps_qna
- L2 execution (LLM synthesis) → reserved for a future phase
"""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING

from apps_qna.integrations.spine_adapter import classify_section_topic
from apps_qna.types.qna_types import (
    ExperienceLibrary,
    ExperiencePoint,
    RCAStory,
    Story,
    StoryBank,
)

if TYPE_CHECKING:
    pass

_log = logging.getLogger(__name__)


# Story selection cap for STAR. The card-builder pack template iterates
# every story; too many entries dilute the operator's choice. 8 is the
# operator's typical "story bank" capacity for a 60-90 min interview.
_DEFAULT_STAR_TOP_N: int = 8

# RCA skeleton cap. Operator typically prepares 2-3 RCAs; emit 4
# skeletons so the operator has a small selection to choose from.
_DEFAULT_RCA_TOP_N: int = 4

# Score thresholds (mirror the W2 spine_adapter contract).
_EMBEDDING_THRESHOLD: float = 0.35
_KEYWORD_THRESHOLD: float = 0.08

# Tag families that signal RCA territory. Bullets with these tags map
# onto plausible failure modes and are surfaced as RCA skeletons.
_RCA_TAG_HINTS: frozenset[str] = frozenset(
    {
        "legacy-modernization",
        "lab-to-production",
        "refactor-risk",
        "rollback",
        "metric-50pct-latency-reduction",
        "metric-30pct-overhead-reduction",
        "metric-40pct-tco-reduction",
        "metric-6mo-to-3wk",
        "lifecycle",
        "cloud-migration",
        "reliability",
        "evaluation-gates",
    }
)

# Metric-tag -> human-readable result fragment. Drives the deterministic
# `result` field of the projected STAR story.
_METRIC_TAG_TO_RESULT: dict[str, str] = {
    "metric-15M-revenue": "$15M in incremental revenue",
    "metric-22M-revenue": "$22M in productized AI revenue",
    "metric-20pct-margin": "20% gross margin expansion",
    "metric-25pct-renewal": "25% improvement in renewal rates",
    "metric-30pct-overhead-reduction": "30% reduction in infrastructure overhead",
    "metric-40pct-tco-reduction": "40% reduction in total cost of ownership",
    "metric-50pct-latency-reduction": "50% reduction in regulatory response latency",
    "metric-6mo-to-3wk": "lab-to-production cycle compressed from six months to three weeks",
    "metric-99.9-uptime": "99.9% uptime maintained across regulated environments",
    "metric-8-to-28-team": "scaled the engineering team from 8 to 28 specialists",
    "metric-14M-capacity": "$14M in operating capacity reclaimed",
}


# ----------------------------------------------------------------------------
# Projection helpers
# ----------------------------------------------------------------------------


def _extract_metric_phrase(point: ExperiencePoint) -> str | None:
    """Find the most descriptive metric phrase in the point's tags + text."""
    for tag in point.technical_depth_tags:
        if tag in _METRIC_TAG_TO_RESULT:
            return _METRIC_TAG_TO_RESULT[tag]
    # Fallback: scan the text for a numeric pattern (e.g. "20%", "$22M",
    # "from six months to three weeks"). Pick the FIRST plausible numeric
    # phrase since the bullet is usually anchored on its lead metric.
    numeric_match = re.search(
        r"(\$?\d+(?:\.\d+)?\s*(?:%|M|B|K|x)?(?:\s+(?:reduction|improvement|expansion|growth|increase|in|to|from)?\s+[a-z][\w\s,]{3,80}?)?)",
        point.one_liner,
    )
    if numeric_match:
        return numeric_match.group(1).strip().rstrip(",;.")
    return None


def _split_text_for_action(text: str) -> tuple[str, str]:
    """Return (action_segment, residual_segment) from the bullet text.

    The action is the first 1-2 sentences (cap at ~280 chars) — the live
    description of what the candidate did. The residual is the remainder,
    used as context grounding the result claim.
    """
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    if not sentences:
        return (text.strip(), "")
    action_parts: list[str] = []
    char_budget = 280
    consumed = 0
    for s in sentences:
        if consumed + len(s) > char_budget and action_parts:
            break
        action_parts.append(s)
        consumed += len(s) + 1
        if len(action_parts) >= 2:
            break
    action = " ".join(action_parts).strip()
    residual = " ".join(sentences[len(action_parts) :]).strip()
    return (action, residual)


def _derive_lesson(tags: list[str]) -> str:
    """Project tag-clusters onto a deterministic lesson statement.

    Order matters — the first matching cluster wins. This is intentionally
    conservative; lessons that don't match a known cluster fall back to a
    generic "platform discipline scales when..." stance.
    """
    tag_set = set(tags)
    if "governance" in tag_set or "policy-gating" in tag_set:
        return (
            "Governance has to be designed in from day one — bolted-on policy "
            "controls fail under enterprise scale and regulatory scrutiny."
        )
    if "productization" in tag_set or "shared-services" in tag_set:
        return (
            "Bespoke wins compound only when their primitives become reusable "
            "platform services — IP economics live in the conversion."
        )
    if "lifecycle" in tag_set or "lab-to-production" in tag_set:
        return (
            "Cycle compression comes from standardized lifecycles, not heroic "
            "individual sprints — the discipline scales the team faster."
        )
    if "telemetry" in tag_set or "observability" in tag_set or "lineage" in tag_set:
        return (
            "If you cannot replay the trace, you cannot debug the production "
            "incident — observability is a Day-1 architecture concern."
        )
    if "leadership" in tag_set or "team" in tag_set or any(t.startswith("metric-8-to") for t in tags):
        return (
            "Scaling the engineering org is a function of leveling and "
            "ownership clarity, not headcount — high-trust autonomy wins."
        )
    if "cloud-migration" in tag_set or "legacy-modernization" in tag_set:
        return (
            "Legacy modernization succeeds when the architecture ladder lets "
            "old systems retire one component at a time, not all at once."
        )
    if "co-sell" in tag_set or "hyperscaler-alliance" in tag_set:
        return (
            "Real co-sell economics come from joint roadmaps with the "
            "partner's account team — marketing-line alliances do not move pipeline."
        )
    return (
        "Platform discipline scales when the operating model, not the "
        "individual hero, owns the outcome."
    )


def _project_to_star(point: ExperiencePoint, role_context: str) -> Story:
    """Map an ExperiencePoint + role context onto a STAR Story.

    Field projection:
      - name      = ExperiencePoint.title (the bullet's label)
      - tags      = ExperiencePoint.technical_depth_tags
      - situation = role-level context (the role's framing prose)
      - task      = "Lead / build / design <label>" — derived from label
      - action    = first 1-2 sentences of bullet text
      - result    = metric phrase from tags or extracted from text
      - lesson    = deterministic mapping from tag clusters
    """
    action, _residual = _split_text_for_action(point.one_liner)
    metric = _extract_metric_phrase(point)
    label = point.title.strip()

    # Task: turn the label into an active-voice task statement. Most
    # labels are noun-phrases ("Enterprise Agentic AI Platform
    # Architecture"); prefix with "Own/Lead/Build" verb if absent.
    if any(label.lower().startswith(v) for v in ("design ", "build ", "lead ", "own ", "scale ", "convert ", "stand")):
        task = label
    else:
        task = f"Own and lead: {label}"

    # Result: prefer the deterministic metric-tag mapping; fall back to a
    # full-action-sentence echo when no metric is detectable.
    if metric:
        result = f"Delivered {metric}."
    else:
        result = action.split(".")[0] + "." if action else "(see Action)"

    return Story(
        name=label,
        situation=role_context.strip(),
        task=task,
        action=action,
        result=result,
        lesson=_derive_lesson(point.technical_depth_tags),
        tags=list(point.technical_depth_tags),
    )


def _project_to_rca_skeleton(point: ExperiencePoint, role_context: str) -> RCAStory:
    """Map an RCA-suitable ExperiencePoint onto an RCAStory skeleton.

    Critical: the ``root_cause``, ``action``, and ``operating_model_change``
    fields are SKELETON placeholders. The candidate MUST replace them
    with a real, honest recollection before paste-ready. Auto-generating
    fictional root causes is harmful; this scaffold exists only to give
    the operator a starting point keyed off real territory from the
    resume.
    """
    label = point.title.strip()
    return RCAStory(
        name=f"RCA: {label}",
        situation=role_context.strip(),
        task=f"Own and lead: {label}",
        root_cause="(SKELETON — replace with the real root cause from your recollection)",
        action="(SKELETON — describe the corrective action you actually took)",
        result=point.one_liner.split(".")[0] + ".",
        operating_model_change=(
            "(SKELETON — name the durable operating-model change that "
            "stayed in place after the fix; this is the most credible "
            "part of an RCA story)"
        ),
    )


# ----------------------------------------------------------------------------
# Ranking helpers
# ----------------------------------------------------------------------------


def _build_signal_document(
    jd_text: str | None,
    interviewer_lenses: dict[str, str],
    role_areas: list[str],
    industry_trends: list[str],
) -> str:
    """Concatenate the demand-side signal for ranking stories."""
    parts: list[str] = []
    if jd_text:
        parts.append("Job description: " + jd_text)
    if interviewer_lenses:
        parts.append("Interviewer lens: " + " ".join(interviewer_lenses.values()))
    if role_areas:
        parts.append("Role areas of focus: " + "; ".join(role_areas))
    if industry_trends:
        parts.append("Industry trends: " + "; ".join(industry_trends))
    return "\n\n".join(parts)


def _build_story_descriptor(point: ExperiencePoint) -> str:
    """Concatenate per-story signals into a single descriptor for embedding."""
    parts = [point.title, point.one_liner]
    if point.technical_depth_tags:
        parts.append("Tags: " + ", ".join(point.technical_depth_tags))
    return ". ".join(parts)


def _rank_points_by_signal(
    points: list[ExperiencePoint],
    signal: str,
    *,
    top_n: int,
) -> list[tuple[ExperiencePoint, float, str]]:
    """Rank ExperiencePoints against the demand signal.

    Returns ``[(point, score, mode), ...]`` sorted by score descending.
    When signal is empty, returns the points in registry order (no
    ranking) up to ``top_n``.
    """
    if not signal.strip() or not points:
        return [(p, 0.0, "empty") for p in points[:top_n]]
    scored: list[tuple[ExperiencePoint, float, str]] = []
    for point in points:
        descriptor = _build_story_descriptor(point)
        topic, score, mode = classify_section_topic(
            signal,
            {point.title: descriptor},
        )
        scored.append((point, score, mode))
    scored.sort(key=lambda r: r[1], reverse=True)
    return scored[:top_n]


# ----------------------------------------------------------------------------
# Resume role-context lookup
# ----------------------------------------------------------------------------


def _load_role_context_map(
    resume_path: Path,
) -> dict[str, str]:
    """Build a lookup from ExperiencePoint.title (bullet label) -> role.context.

    The role context is the prose that frames a bullet's situation. Without
    it the projected STAR ``situation`` field is just the bullet text again,
    which removes the role-level framing every interviewer expects.
    """
    if not resume_path.is_file():
        return {}
    try:
        data = json.loads(resume_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    label_to_context: dict[str, str] = {}
    for role in data.get("professional_experience", []):
        context = (role.get("context") or "").strip()
        if not context:
            continue
        for bullet in role.get("bullet_pool", []):
            if isinstance(bullet, dict):
                label = (bullet.get("label") or "").strip()
                if label:
                    label_to_context[label] = context
    return label_to_context


# ----------------------------------------------------------------------------
# Public surface
# ----------------------------------------------------------------------------


def synthesize_star_bank(
    library: ExperienceLibrary,
    *,
    jd_text: str | None = None,
    interviewer_lenses: dict[str, str] | None = None,
    role_areas: list[str] | None = None,
    industry_trends: list[str] | None = None,
    role_context_map: dict[str, str] | None = None,
    top_n: int = _DEFAULT_STAR_TOP_N,
) -> StoryBank:
    """Synthesize a ranked STAR bank from the experience library.

    Args:
        library: ``ExperienceLibrary`` from
            ``apps_qna.integrations.from_apps_shared.load_master_resume``.
        jd_text: optional job-description full text (drives ranking).
        interviewer_lenses: ``{name: lens_text}`` from
            ``ResearchInputs.interviewer_lenses``.
        role_areas: from ``ResearchInputs.role_areas_of_focus``.
        industry_trends: from ``ResearchInputs.industry_trends``.
        role_context_map: ``{bullet_label: role.context}`` lookup. When
            absent, the projected STAR ``situation`` defaults to
            ``"(role context unavailable)"``.
        top_n: cap on ranked stories returned. Default 8.

    Returns:
        ``StoryBank`` with the top-N stories sorted by relevance descending.
        When no signal is provided, stories are emitted in
        ``library.points`` order.
    """
    if not library.points:
        return StoryBank(stories=[])
    signal = _build_signal_document(
        jd_text=jd_text,
        interviewer_lenses=interviewer_lenses or {},
        role_areas=role_areas or [],
        industry_trends=industry_trends or [],
    )
    ranked = _rank_points_by_signal(library.points, signal, top_n=top_n)
    accepted: list[Story] = []
    role_ctx = role_context_map or {}
    for point, score, mode in ranked:
        threshold = (
            _EMBEDDING_THRESHOLD if mode == "embedding" else _KEYWORD_THRESHOLD
        )
        # When signal-mode is empty (no JD/interviewer/role data), accept
        # all points up to top_n. Otherwise apply per-mode threshold.
        if mode != "empty" and score < threshold:
            continue
        context = role_ctx.get(point.title) or "(role context unavailable)"
        story = _project_to_star(point, role_context=context)
        accepted.append(story)
    _log.info(
        "STAR synthesis: %d points -> %d ranked stories (top_n=%d, signal_present=%s)",
        len(library.points),
        len(accepted),
        top_n,
        bool(signal.strip()),
    )
    return StoryBank(stories=accepted)


def synthesize_rca_skeletons(
    library: ExperienceLibrary,
    *,
    role_context_map: dict[str, str] | None = None,
    top_n: int = _DEFAULT_RCA_TOP_N,
) -> list[RCAStory]:
    """Synthesize SKELETON RCA stories from RCA-suitable bullets.

    Selects ExperiencePoints whose tags overlap with ``_RCA_TAG_HINTS``
    (transformation, modernization, lifecycle, lab-to-production, etc.)
    and emits skeleton ``RCAStory`` entries. The skeleton has placeholder
    text for ``root_cause``, ``action``, and ``operating_model_change``
    that the operator MUST replace before the pack is paste-ready.

    Returns up to ``top_n`` skeletons in registry order.
    """
    if not library.points:
        return []
    candidates = [
        p for p in library.points
        if set(p.technical_depth_tags) & _RCA_TAG_HINTS
    ]
    role_ctx = role_context_map or {}
    skeletons = [
        _project_to_rca_skeleton(
            point,
            role_context=role_ctx.get(point.title) or "(role context unavailable)",
        )
        for point in candidates[:top_n]
    ]
    _log.info(
        "RCA skeletons: %d candidates -> %d skeletons (operator must flesh out)",
        len(candidates),
        len(skeletons),
    )
    return skeletons


def synthesize_into_library(
    library: ExperienceLibrary,
    *,
    jd_text: str | None = None,
    interviewer_lenses: dict[str, str] | None = None,
    role_areas: list[str] | None = None,
    industry_trends: list[str] | None = None,
    resume_path: Path | None = None,
    star_top_n: int = _DEFAULT_STAR_TOP_N,
    rca_top_n: int = _DEFAULT_RCA_TOP_N,
) -> ExperienceLibrary:
    """Synthesize STAR bank + RCA skeletons into a new ExperienceLibrary.

    Returns a new library with populated ``star_bank`` and ``rca_bank``.
    Existing stories on the input library are PRESERVED — synthesis only
    fills empty banks. Operator-curated stories beat synthesized ones.

    The role-context lookup uses ``resume_path`` (defaults to
    ``apps_shared/data/master_resume_svp.json``); when the file is
    missing, projection still runs but ``situation`` falls back to a
    placeholder.
    """
    role_context_map = _load_role_context_map(
        resume_path or Path("apps_shared/data/master_resume_svp.json")
    )

    # Preserve operator-curated stories. Synthesize only when empty.
    if library.star_bank.stories:
        new_star_bank = library.star_bank
    else:
        new_star_bank = synthesize_star_bank(
            library,
            jd_text=jd_text,
            interviewer_lenses=interviewer_lenses,
            role_areas=role_areas,
            industry_trends=industry_trends,
            role_context_map=role_context_map,
            top_n=star_top_n,
        )

    if library.rca_bank:
        new_rca_bank = library.rca_bank
    else:
        new_rca_bank = synthesize_rca_skeletons(
            library,
            role_context_map=role_context_map,
            top_n=rca_top_n,
        )

    return ExperienceLibrary(
        points=library.points,
        star_bank=new_star_bank,
        rca_bank=new_rca_bank,
    )


__all__ = [
    "synthesize_into_library",
    "synthesize_rca_skeletons",
    "synthesize_star_bank",
]
