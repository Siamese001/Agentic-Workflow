"""apps_qna learning adapter — Wave 5 phase 5.1.

Closes the feedback loop that activates the W4.1 NamespaceBandit.

Captures post-rehearsal outcomes ("interviewer asked route X", "card Y
landed for question Z") as durable EpisodicEvent rows in the
``apps_qna_pack_lifecycle`` ledger (event_kind=``interview_outcome``)
AND propagates them into the W4.1 bandit's posterior via
``AppsQnaRouteBandit.update_outcome``. Across process restarts, a
replay function rebuilds the bandit's posterior from the ledger so
accumulated learning survives.

Architecture
------------
The apps_qna_pack_lifecycle ledger is the canonical episodic surface.
A separate ChromaDB-backed semantic index of outcomes (for "find similar
past interviews" cross-interview transfer) is intentionally deferred to
W5.2 — that's a system_learning concern; this phase keeps the surface
narrow and ergonomic.

CLI integration
---------------
``python -m apps_qna feedback --slug <slug> --outcomes outcomes.json``
takes a JSON file shaped like::

    {
      "namespace": "qna_signal_<12hex>",
      "interviewer": "Vrinda Khurjekar",
      "outcomes": [
        {"asked_route": "executive_fit", "card_id": "13_EXECUTIVE_FIT.md",
         "asked": true, "landed": true, "notes": "..."},
        ...
      ]
    }

The operator fills it after the rehearsal; the CLI persists rows AND
updates the bandit. Subsequent ``apps_qna init`` runs that instantiate
the bandit will see the accumulated posterior.

Spine routing
-------------
- L0 routing: imports ``agentic_core.L0_routing.config.path_constants``
  for the canonical artifacts/ledgers/ path resolution
- L6 observability: writes flow through
  ``apps_qna.integrations.spine_adapter.emit_pack_lifecycle_event``
  (W1.4-validated)

Constitutional alignment
------------------------
- §29: every outcome bind pairs a ``ROUTER_DECISION:`` outcome marker
  with the ledger row (the bandit also propagates to its own L0/bandit
  ledger via the spine NamespaceBandit's closed-loop helper)
"""

from __future__ import annotations

import json
import logging
import sqlite3
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

if TYPE_CHECKING:
    from apps_qna.router.route_bandit import AppsQnaRouteBandit

_log = logging.getLogger(__name__)

_LEDGER_NAME: str = "apps_qna_pack_lifecycle"
_INTERVIEW_OUTCOME_KIND: str = "interview_outcome"


@dataclass(frozen=True)
class RehearsalOutcome:
    """One per-question rehearsal observation.

    Bernoulli success for the W4.1 bandit is ``asked AND landed`` — the
    interviewer probed the route AND the bound card resolved the answer.
    Asked-but-card-missed is a routing miss; not-asked is a ranking miss.
    """

    asked_route: str
    """Route id the interviewer's question routed to."""

    card_id: str
    """Pack card filename that the operator pasted (e.g. ``13_EXECUTIVE_FIT.md``)."""

    asked: bool
    """True iff the interviewer probed this route during the live rehearsal."""

    landed: bool
    """True iff the bound card actually resolved the question on first try."""

    notes: str = ""
    """Operator-authored qualitative note (free-form)."""

    @property
    def success(self) -> bool:
        """Bernoulli success label for the bandit."""
        return self.asked and self.landed


@dataclass
class RehearsalSession:
    """The full set of outcomes captured after one rehearsal."""

    slug: str
    """Interview slug (e.g. ``searce-applied-ai``)."""

    namespace: str
    """W4.1 bandit namespace key (the qna_signal_<hex> from route_bandit)."""

    interviewer: str
    """Primary interviewer name."""

    outcomes: list[RehearsalOutcome] = field(default_factory=list)


def record_rehearsal_outcomes(
    session: RehearsalSession,
    *,
    bandit: "AppsQnaRouteBandit | None" = None,
) -> int:
    """Persist outcomes to the ledger AND update the bandit.

    Args:
        session: ``RehearsalSession`` with the operator's outcome bindings.
        bandit: optional ``AppsQnaRouteBandit`` instance whose posterior
            should be updated. When None, only the ledger row is emitted
            and the bandit update is deferred to a later replay.

    Returns:
        Number of outcomes successfully persisted (counts ledger writes).
        Bandit update failures are logged at debug and do not affect the
        return count.
    """
    persisted = 0
    for outcome in session.outcomes:
        event_id = emit_pack_lifecycle_event(
            event_kind=_INTERVIEW_OUTCOME_KIND,
            prediction={
                "namespace": session.namespace,
                "interviewer": session.interviewer,
                "asked_route": outcome.asked_route,
                "card_id": outcome.card_id,
            },
            outcome={
                "asked": outcome.asked,
                "landed": outcome.landed,
                "success": outcome.success,
                "notes": outcome.notes,
            },
            score_band="hit" if outcome.success else "miss",
            repo_area=f"reports/qna/{session.slug}",
            metadata={
                "rehearsal_session_id": uuid.uuid4().hex,
                "outcome_kind": "post_rehearsal",
            },
        )
        if event_id:
            persisted += 1
        if bandit is not None:
            try:
                bandit.update_outcome(
                    namespace=session.namespace,
                    route=outcome.asked_route,
                    asked=outcome.asked,
                    landed=outcome.landed,
                )
            except (AttributeError, TypeError, ValueError, RuntimeError) as exc:
                _log.debug(
                    "bandit.update_outcome failed for route=%s: %r",
                    outcome.asked_route,
                    exc,
                )
    _log.info(
        "recorded %d/%d outcomes for slug=%s namespace=%s",
        persisted,
        len(session.outcomes),
        session.slug,
        session.namespace,
    )
    return persisted


def _ledger_db_path() -> Path | None:
    """Resolve the apps_qna_pack_lifecycle ledger DB path.

    Returns None when the registry is unavailable (test environments
    without tools.ledgers) so callers can fall back gracefully.
    """
    try:
        from tools.ledgers.schema_registry import get

        return get(_LEDGER_NAME).db_path
    except (ImportError, KeyError):
        return None


def replay_outcomes_into_bandit(
    bandit: "AppsQnaRouteBandit",
    *,
    namespace: str | None = None,
    db_path: Path | None = None,
) -> int:
    """Rebuild bandit posterior by replaying ledger outcome rows.

    Mirrors the spine ``NamespaceBandit.rebuild_from_decision_events``
    pattern but reads from the apps_qna_pack_lifecycle ledger.

    Args:
        bandit: target bandit to update.
        namespace: optional namespace filter. When None, replays every
            ``interview_outcome`` row regardless of namespace (useful at
            cold-start; expensive but bounded).
        db_path: explicit ledger path (test override). Falls back to the
            registered path when None.

    Returns:
        Number of outcome rows replayed. 0 on any failure or when no DB
        is materialized.
    """
    path = db_path or _ledger_db_path()
    if path is None or not path.is_file():
        _log.debug("replay_outcomes_into_bandit: ledger DB not found")
        return 0

    sql = (
        "SELECT prediction_json, outcome_json FROM events "
        "WHERE event_kind = ? AND outcome_json IS NOT NULL"
    )
    params: tuple[Any, ...] = (_INTERVIEW_OUTCOME_KIND,)
    if namespace is not None:
        sql += " AND prediction_json LIKE ?"
        # Writer serializes via json.dumps(..., separators=(",", ":")) so the
        # stored shape is compact: {"namespace":"qna_signal_..."}. Match that
        # literal form (no space after the colon).
        params = (_INTERVIEW_OUTCOME_KIND, f'%"namespace":"{namespace}"%')

    applied = 0
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            for prediction_json, outcome_json in con.execute(sql, params):
                if not prediction_json or not outcome_json:
                    continue
                try:
                    pred = json.loads(prediction_json)
                    out = json.loads(outcome_json)
                except json.JSONDecodeError:
                    continue
                ns = pred.get("namespace")
                route = pred.get("asked_route")
                asked = bool(out.get("asked", False))
                landed = bool(out.get("landed", False))
                if not ns or not route:
                    continue
                try:
                    bandit.update_outcome(
                        namespace=ns,
                        route=route,
                        asked=asked,
                        landed=landed,
                    )
                    applied += 1
                except (AttributeError, TypeError, ValueError, RuntimeError):
                    continue
        finally:
            con.close()
    except sqlite3.Error as exc:
        _log.debug("replay_outcomes_into_bandit: sqlite error %r", exc)
        return applied
    _log.info(
        "replayed %d outcome rows into bandit (namespace=%s)",
        applied,
        namespace or "*",
    )
    return applied


def load_session_from_json(slug: str, path: Path) -> RehearsalSession:
    """Load a RehearsalSession from a JSON file.

    Schema (operator-authored)::

        {
          "namespace": "qna_signal_<12hex>",
          "interviewer": "<name>",
          "outcomes": [
            {"asked_route": "<id>", "card_id": "<filename>",
             "asked": <bool>, "landed": <bool>, "notes": "<text>"},
            ...
          ]
        }
    """
    if not path.is_file():
        raise FileNotFoundError(f"Outcomes file not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    namespace = (raw.get("namespace") or "").strip()
    if not namespace:
        raise ValueError("outcomes JSON must include 'namespace'")
    interviewer = (raw.get("interviewer") or "").strip()
    outcomes_raw = raw.get("outcomes") or []
    if not isinstance(outcomes_raw, list):
        raise ValueError("'outcomes' must be a JSON array")
    outcomes: list[RehearsalOutcome] = []
    for item in outcomes_raw:
        if not isinstance(item, dict):
            continue
        outcomes.append(
            RehearsalOutcome(
                asked_route=str(item.get("asked_route", "")),
                card_id=str(item.get("card_id", "")),
                asked=bool(item.get("asked", False)),
                landed=bool(item.get("landed", False)),
                notes=str(item.get("notes", "")),
            )
        )
    return RehearsalSession(
        slug=slug,
        namespace=namespace,
        interviewer=interviewer,
        outcomes=outcomes,
    )


__all__ = [
    "RehearsalOutcome",
    "RehearsalSession",
    "load_session_from_json",
    "record_rehearsal_outcomes",
    "replay_outcomes_into_bandit",
]
