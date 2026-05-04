"""apps_lic.engines.archetype_tone_selector — D6-P2.

Plan: .windsurf/plans/apps-lic-deferred-scope-followup-d3f9b2.md W4 D6-P2

Selects a tone archetype for an outreach draft. Additive-only: this selector
supplements (does not replace) the existing personalization_mode selection.

Decision-only invariants
------------------------
- No durable writes.
- No provider API calls.
- No subprocess calls.
- Config-gated: feature disabled when ARCHETYPE_TONE_ENABLED env var is absent.

Tone archetypes (canonical set)
---------------------------------
  peer_expert         — knowledgeable peer talking to an equal; avoids condescension.
  strategic_advisor   — brings forward-looking perspective; used for exec audiences.
  concise_practitioner — lean, no-frills; respects recipient's time (exec/hiring).
  warm_connector      — relationship-first, human tone; warm/referral contexts.
  credibility_anchor  — proof-forward tone; grounds claims in evidence.

Additive non-replacement contract
----------------------------------
The archetype tone AUGMENTS personalization_mode. It does not replace it.
A run with personalization_mode="recipient" + archetype_tone="peer_expert"
means: personalise to the recipient AND use a peer-expert voice.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_CONFIG_PATH = Path(__file__).parent.parent / "config" / "archetype_tone_policy.yaml"

_EXEC_CLASSES = frozenset({"EXECUTIVE", "C_LEVEL", "CTO", "VP_ENG"})
_RECRUITER_CLASSES = frozenset({"RECRUITER", "SENIOR_TA"})

_DEFAULT_TONE_MATRIX: dict[tuple[str, str], str] = {
    ("exec",      "cold"):     "strategic_advisor",
    ("exec",      "warm"):     "peer_expert",
    ("exec",      "referral"): "warm_connector",
    ("exec",      "known"):    "warm_connector",
    ("hiring",    "cold"):     "concise_practitioner",
    ("hiring",    "warm"):     "credibility_anchor",
    ("hiring",    "referral"): "warm_connector",
    ("hiring",    "known"):    "warm_connector",
    ("recruiter", "cold"):     "credibility_anchor",
    ("recruiter", "warm"):     "warm_connector",
    ("recruiter", "referral"): "warm_connector",
    ("recruiter", "known"):    "warm_connector",
    ("default",   "cold"):     "concise_practitioner",
    ("default",   "warm"):     "peer_expert",
    ("default",   "referral"): "warm_connector",
    ("default",   "known"):    "warm_connector",
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
class ArchetypeToneDecision:
    """Result of tone archetype selection.

    Fields
    ------
    archetype   : canonical archetype name (see module docstring).
    enabled     : False when ARCHETYPE_TONE_ENABLED is absent.
    source      : "config" | "default" | "disabled".
    """

    archetype: str
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


class ArchetypeToneSelector:
    """Selects a tone archetype additive to the existing personalization_mode."""

    def __init__(self, config: dict | None = None) -> None:
        self._config = config if config is not None else _load_config()

    def select(
        self,
        *,
        recipient_class: str,
        relationship_distance: str,
    ) -> ArchetypeToneDecision:
        """Select tone archetype.

        Parameters
        ----------
        recipient_class       : e.g. "EXECUTIVE", "RECRUITER"
        relationship_distance : e.g. "cold", "warm"
        """
        if not os.environ.get("ARCHETYPE_TONE_ENABLED"):
            rb = _recipient_bucket(recipient_class)
            db = _distance_bucket(relationship_distance)
            return ArchetypeToneDecision(
                archetype="",
                recipient_bucket=rb,
                distance_bucket=db,
                enabled=False,
                source="disabled",
            )

        rb = _recipient_bucket(recipient_class)
        db = _distance_bucket(relationship_distance)
        key = (rb, db)

        tone_matrix = self._config.get("tone_matrix", {})
        if tone_matrix and rb in tone_matrix and db in tone_matrix[rb]:
            archetype = str(tone_matrix[rb][db])
            source = "config"
        else:
            archetype = _DEFAULT_TONE_MATRIX.get(key, _DEFAULT_TONE_MATRIX[("default", "cold")])
            source = "default"

        return ArchetypeToneDecision(
            archetype=archetype,
            recipient_bucket=rb,
            distance_bucket=db,
            enabled=True,
            source=source,
        )


__all__ = ["ArchetypeToneSelector", "ArchetypeToneDecision"]
