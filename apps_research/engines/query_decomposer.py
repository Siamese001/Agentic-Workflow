"""Query decomposition primitive for apps_research retrieval pipeline.

Fan-out 3/4/5 for depth=shallow/standard/deep per plan
.windsurf/plans/apps-research-blend-baseline-c74787.md §P1.1.

The decomposer produces distinct sub-queries covering canonical research
facets (overview, capabilities, leadership, market, risks) rotated by
depth. No external calls; pure in-process transform.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Depth = Literal["shallow", "standard", "deep"]

_FAN_OUT: dict[Depth, int] = {"shallow": 3, "standard": 4, "deep": 5}

_FACET_TEMPLATES: tuple[tuple[str, str], ...] = (
    ("overview", "{topic} company overview services and positioning"),
    ("capabilities", "{topic} technical capabilities and delivery methodology"),
    ("leadership", "{topic} executive leadership team and strategic direction"),
    ("market", "{topic} target market segments and client case studies"),
    ("risks", "{topic} key risks competitive threats and operational constraints"),
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
