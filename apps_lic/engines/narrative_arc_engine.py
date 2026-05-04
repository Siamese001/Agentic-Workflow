"""apps_lic.engines.narrative_arc_engine — D6-P1.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W4 D6-P1

Selects the narrative arc for an outreach draft based on recipient_class and
relationship_distance. Returns an immutable NarrativeArcDecision.

Decision-only invariants
------------------------
- No durable writes.
- No provider API calls.
- No subprocess calls.
- Config-gated: feature disabled when ARC_ENGINE_ENABLED env var is absent/falsy.

Narrative arcs (canonical set)
--------------------------------
  problem_solution   — sender identifies a specific problem the recipient faces
                       and frames the outreach as offering a solution.
  mutual_gain        — sender highlights shared context or mutual benefit.
  social_proof       — sender leads with credibility signals relevant to recipient.
  asymmetric_insight — sender shares a non-obvious observation about recipient's context.
  warm_reconnect     — sender references prior relationship to re-engage.
  direct_ask         — brief, low-friction direct request (often best for execs).

Arc selection is driven by a 2-axis matrix: recipient_class bucket ×
relationship_distance bucket. The matrix is defined in config/arc_policy.yaml
(optional); defaults are hard-coded below.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "arc_policy.yaml"

_EXEC_CLASSES = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})
_RECRUITER_CLASSES = frozenset({"RECRUITER", "SENIOR_TA"})

_DEFAULT_ARC_MATRIX: dict[tuple[str, str], str] = {
    ("exec",     "cold"):     "asymmetric_insight",
    ("exec",     "warm"):     "mutual_gain",
    ("exec",     "referral"): "social_proof",
    ("exec",     "known"):    "warm_reconnect",
    ("hiring",   "cold"):     "problem_solution",
    ("hiring",   "warm"):     "mutual_gain",
    ("hiring",   "referral"): "social_proof",
    ("hiring",   "known"):    "warm_reconnect",
    ("recruiter","cold"):     "direct_ask",
    ("recruiter","warm"):     "social_proof",
    ("recruiter","referral"): "social_proof",
    ("recruiter","known"):    "warm_reconnect",
    ("default",  "cold"):     "problem_solution",
    ("default",  "warm"):     "mutual_gain",
    ("default",  "referral"): "social_proof",
    ("default",  "known"):    "warm_reconnect",
}


@lru_cache(maxsize=1)
def _load_config() -> dict:
    try:
        import yaml  # type: ignore[import]
        with open(_CONFIG_PATH, "r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    except Exception:  # noqa: BLE001
        # guardian: allow-broad-except -- optional config; fall through to defaults.
        return {}


@dataclass(frozen=True)
class NarrativeArcDecision:
    """Result of arc selection.

    Fields
    ------
    arc_name    : canonical arc identifier (see module docstring).
    recipient_bucket : derived bucket used in matrix lookup.
    distance_bucket  : derived distance bucket used in matrix lookup.
    enabled     : False when ARC_ENGINE_ENABLED is absent — arc_name is empty.
    source      : "config" | "default" | "disabled".
    """

    arc_name: str
    recipient_bucket: str
    distance_bucket: str
    enabled: bool
    source: str


def _recipient_bucket(recipient_class: str) -> str:
    rc = recipient_class.upper()
    if rc in _EXEC_CLASSES:
        return "exec"
    if rc in _RECRUITER_CLASSES:
        return "recruiter"
    if rc == "HIRING_MANAGER":
        return "hiring"
    return "default"


def _distance_bucket(relationship_distance: str) -> str:
    rd = relationship_distance.lower()
    if rd in {"referral", "warm_referral"}:
        return "referral"
    if rd in {"warm", "follow_up"}:
        return "warm"
    if rd in {"known", "prior_contact"}:
        return "known"
    return "cold"


class NarrativeArcEngine:
    """Selects the narrative arc for an outreach draft."""

    def __init__(self, config: dict | None = None) -> None:
        self._config = config if config is not None else _load_config()

    def select(
        self,
        *,
        recipient_class: str,
        relationship_distance: str,
    ) -> NarrativeArcDecision:
        """Select narrative arc.

        Parameters
        ----------
        recipient_class     : e.g. "EXECUTIVE", "RECRUITER"
        relationship_distance : e.g. "cold", "warm", "referral"
        """
        if not os.environ.get("ARC_ENGINE_ENABLED"):
            return NarrativeArcDecision(
                arc_name="",
                recipient_bucket=_recipient_bucket(recipient_class),
                distance_bucket=_distance_bucket(relationship_distance),
                enabled=False,
                source="disabled",
            )

        rb = _recipient_bucket(recipient_class)
        db = _distance_bucket(relationship_distance)
        key = (rb, db)

        arc_matrix = self._config.get("arc_matrix", {})
        if arc_matrix and rb in arc_matrix and db in arc_matrix[rb]:
            arc_name = str(arc_matrix[rb][db])
            source = "config"
        else:
            arc_name = _DEFAULT_ARC_MATRIX.get(key, _DEFAULT_ARC_MATRIX[("default", "cold")])
            source = "default"

        return NarrativeArcDecision(
            arc_name=arc_name,
            recipient_bucket=rb,
            distance_bucket=db,
            enabled=True,
            source=source,
        )


__all__ = ["NarrativeArcEngine", "NarrativeArcDecision"]
