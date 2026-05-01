"""Mutual-connection resolver for HOP3 sender grounding.

W2-P5 of the apps_lic LinkedIn response-rate maximization plan
(Notion page 35327693-f55c-81e2-9b58-debeeb48bb35).

Industry benchmark: outreach messages that open with a mutual-connection
priming line (e.g., "Saw Dana speak of your work on X") achieve ~2x the
reply rate of cold opens without priming.

This module resolves candidate mutual connections and renders a priming
line ready for HOP5 to inject. The mutual-connection graph itself is
OUT OF SCOPE — this module accepts candidates as input (from LinkedIn
API, CRM, or a future graph service) and focuses on:

    1. Ranking candidates by relevance (recency + shared-topic weight)
    2. Rendering a compliant priming line with fallback

Ranking is deterministic. Rendering is template-driven with safe
format-map (missing keys degrade to empty strings, not KeyError).

Call surface:

    resolver = MutualConnectionResolver()
    line = resolver.resolve_priming_line(
        candidates=[
            {"name": "Dana Lee", "topic": "AI infrastructure", "last_seen_days": 5},
            {"name": "Sam Patel", "topic": "product strategy", "last_seen_days": 90},
        ],
    )
    # "Dana Lee recently mentioned your work in AI infrastructure."
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final, Iterable, Mapping, Optional

# Priming-line templates, keyed by recency band. Each template supports
# the same format keys; unused keys degrade to empty strings via the
# internal ``_DefaultMissing`` renderer.
_TEMPLATE_RECENT: Final[str] = (
    "{mutual_name} recently mentioned your work on {topic}."
)
_TEMPLATE_RECENT_NO_TOPIC: Final[str] = (
    "{mutual_name} recently mentioned your work."
)
_TEMPLATE_OLDER: Final[str] = (
    "{mutual_name} spoke of your work on {topic} earlier this year."
)
_TEMPLATE_OLDER_NO_TOPIC: Final[str] = (
    "{mutual_name} spoke of your work earlier this year."
)
_TEMPLATE_NONE: Final[str] = ""

# Recency threshold in days. Connections seen within this window use the
# "recently" phrasing; older connections use the "earlier this year"
# phrasing which is less time-sensitive if the message is not sent
# immediately.
RECENT_THRESHOLD_DAYS: Final[int] = 30

# Priming-line visual cap. Longer than this truncates with ellipsis.
# LinkedIn outreach opens benefit from brevity — keep it under 90 chars.
PRIMING_LINE_MAX_CHARS: Final[int] = 90


@dataclass(frozen=True)
class MutualConnectionCandidate:
    """One candidate mutual connection between sender and recipient.

    Attributes:
        name: Full name as it should appear in the rendered line.
            Required — an empty name disqualifies the candidate.
        topic: Optional shared-work topic. When present, the priming
            line mentions the topic. When absent, a topic-less template
            is used.
        last_seen_days: How recently the mutual was in contact with the
            sender, in days. Used for recency-band template selection
            and ranking. Zero or negative values treated as "today".
        relevance_boost: Optional override (>= 0.0) that lifts this
            candidate above recency-based ranking. Used when CRM has
            explicit "warm introducer" tagging.
    """

    name: str
    topic: Optional[str] = None
    last_seen_days: int = 999
    relevance_boost: float = 0.0


class MutualConnectionResolver:
    """Resolve mutual connections to a priming-line string.

    Thread-safe (no mutable instance state aside from the telemetry bus).
    Pass a telemetry bus to record events; omit it for pure resolution.

    The resolver never raises — unresolvable inputs yield the empty
    string, which HOP5 MUST interpret as "no priming line, use default
    opener".
    """

    def __init__(self, telemetry_bus: Optional[Any] = None) -> None:
        self._telemetry_bus = telemetry_bus

    def resolve_priming_line(
        self,
        candidates: Iterable[Mapping[str, Any]] | Iterable[MutualConnectionCandidate],
    ) -> str:
        """Pick the best candidate and render its priming line.

        Args:
            candidates: Iterable of candidate mappings or
                ``MutualConnectionCandidate`` instances. Each mapping
                supports keys ``name``, ``topic``, ``last_seen_days``,
                ``relevance_boost``. Missing keys take dataclass defaults.

        Returns:
            Rendered priming line, or empty string when no candidate is
            eligible. Rendered string never exceeds
            ``PRIMING_LINE_MAX_CHARS``.
        """
        normalised = list(self._iter_candidates(candidates))
        if not normalised:
            self._emit("mutual_connection_no_candidates", {})
            return _TEMPLATE_NONE
        best = self._rank(normalised)
        if best is None or not best.name.strip():
            self._emit("mutual_connection_no_candidates", {})
            return _TEMPLATE_NONE
        line = self._render(best)
        self._emit(
            "mutual_connection_rendered",
            {
                "mutual_name": best.name,
                "has_topic": bool(best.topic),
                "recency_days": best.last_seen_days,
                "line_length": len(line),
            },
        )
        return line

    def best_candidate(
        self,
        candidates: Iterable[Mapping[str, Any]] | Iterable[MutualConnectionCandidate],
    ) -> Optional[MutualConnectionCandidate]:
        """Return the single best-ranked candidate, or None."""
        normalised = list(self._iter_candidates(candidates))
        return self._rank(normalised)

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _iter_candidates(
        candidates: Iterable[Mapping[str, Any]] | Iterable[MutualConnectionCandidate],
    ) -> Iterable[MutualConnectionCandidate]:
        """Normalise mixed input into a stream of MutualConnectionCandidate."""
        for item in candidates:
            if isinstance(item, MutualConnectionCandidate):
                yield item
                continue
            if not isinstance(item, Mapping):
                continue
            name = item.get("name") or ""
            if not isinstance(name, str) or not name.strip():
                continue
            topic = item.get("topic")
            if topic is not None and not isinstance(topic, str):
                topic = str(topic)
            last_seen_raw = item.get("last_seen_days", 999)
            try:
                last_seen = int(last_seen_raw)
            except (TypeError, ValueError):
                last_seen = 999
            boost_raw = item.get("relevance_boost", 0.0)
            try:
                boost = float(boost_raw)
            except (TypeError, ValueError):
                boost = 0.0
            if boost < 0.0:
                boost = 0.0
            yield MutualConnectionCandidate(
                name=name.strip(),
                topic=topic.strip() if isinstance(topic, str) and topic.strip() else None,
                last_seen_days=max(last_seen, 0),
                relevance_boost=boost,
            )

    @staticmethod
    def _rank(
        candidates: list[MutualConnectionCandidate],
    ) -> Optional[MutualConnectionCandidate]:
        """Highest relevance_boost first, then most recent, then by name."""
        if not candidates:
            return None
        return min(
            candidates,
            key=lambda c: (-c.relevance_boost, c.last_seen_days, c.name),
        )

    @staticmethod
    def _render(candidate: MutualConnectionCandidate) -> str:
        """Template-substitute the candidate into a priming line."""
        if candidate.last_seen_days <= RECENT_THRESHOLD_DAYS:
            template = _TEMPLATE_RECENT if candidate.topic else _TEMPLATE_RECENT_NO_TOPIC
        else:
            template = _TEMPLATE_OLDER if candidate.topic else _TEMPLATE_OLDER_NO_TOPIC
        rendered = template.format_map(
            _DefaultMissing(
                mutual_name=candidate.name,
                topic=candidate.topic or "",
            )
        )
        # Collapse accidental double-spaces produced by empty substitutions.
        rendered = " ".join(rendered.split())
        if len(rendered) > PRIMING_LINE_MAX_CHARS:
            rendered = rendered[: PRIMING_LINE_MAX_CHARS - 1].rstrip() + "\u2026"
        return rendered

    def _emit(self, event_name: str, payload: dict) -> None:
        if self._telemetry_bus is None:
            return
        try:
            self._telemetry_bus.record(event_name, payload)
        except (AttributeError, TypeError, RuntimeError, ValueError, OSError):  # guardian: allow-log-and-swallow -- telemetry must never break resolution
            pass


class _DefaultMissing(dict):
    """dict subclass returning '' for missing keys during format_map."""

    def __missing__(self, key: str) -> str:  # noqa: D401 -- dict hook
        return ""


__all__ = [
    "MutualConnectionCandidate",
    "MutualConnectionResolver",
    "PRIMING_LINE_MAX_CHARS",
    "RECENT_THRESHOLD_DAYS",
]
