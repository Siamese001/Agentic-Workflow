"""Outreach-learning subscriber — aggregates JSONL events into rollups.

Reads events emitted by ``JsonlEventBus`` (validator telemetry from
W1-W4) and produces structured rollup metrics intended for:
    1. weekly calibration reports (per-archetype reply-rate proxies)
    2. promotion gates that consult violation rates
    3. operator dashboards that need a per-session view

The subscriber is **stateless** — it reads the JSONL file fresh on
every ``aggregate()`` call. Callers concerned with replay should pass
``session_id`` to scope to one run.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Final, Iterable, Optional

# Canonical event names that this subscriber knows how to aggregate.
KNOWN_EVENTS: Final[frozenset[str]] = frozenset(
    {
        "message_length_cap_violation",
        "mutual_connection_rendered",
        "mutual_connection_no_candidates",
        "question_ending_violation",
        "spam_trigger_hits",
    }
)


@dataclass
class OutreachLearningRollup:
    """One rollup snapshot — produced by ``aggregate()``."""

    total_events: int = 0
    events_by_name: dict[str, int] = field(default_factory=dict)
    length_violations_by_archetype: dict[str, int] = field(default_factory=dict)
    question_ending_violations_by_archetype: dict[str, int] = field(
        default_factory=dict
    )
    spam_trigger_hits_by_category: dict[str, int] = field(default_factory=dict)
    spam_trigger_total_messages_with_hits: int = 0
    mutual_connection_priming_rate: float = 0.0  # rendered / (rendered + no_candidates)
    unknown_events: list[str] = field(default_factory=list)
    session_ids_observed: list[str] = field(default_factory=list)


class OutreachLearningSubscriber:
    """Stateless subscriber that aggregates JSONL events into rollups."""

    def __init__(self, log_path: str | Path) -> None:
        self._log_path = Path(log_path)

    def aggregate(
        self, *, session_id: Optional[str] = None
    ) -> OutreachLearningRollup:
        """Walk the JSONL log and produce one rollup.

        Args:
            session_id: When supplied, only events with matching
                ``session_id`` are counted. When None, all sessions
                contribute.
        """
        rollup = OutreachLearningRollup()
        if not self._log_path.exists():
            return rollup
        sessions_seen: set[str] = set()
        length_by_archetype: Counter[str] = Counter()
        qe_by_archetype: Counter[str] = Counter()
        spam_by_category: Counter[str] = Counter()
        events_by_name: Counter[str] = Counter()
        unknown_seen: set[str] = set()
        mutual_rendered = 0
        mutual_no_candidates = 0
        spam_hit_messages = 0

        for row in self._iter_rows():
            row_session = row.get("session_id")
            if session_id is not None and row_session != session_id:
                continue
            if isinstance(row_session, str):
                sessions_seen.add(row_session)
            event = row.get("event")
            payload = row.get("payload") or {}
            if not isinstance(event, str):
                continue
            rollup.total_events += 1
            events_by_name[event] += 1
            if event not in KNOWN_EVENTS:
                unknown_seen.add(event)
                continue
            if event == "message_length_cap_violation":
                arch = str(payload.get("archetype") or "OTHER")
                length_by_archetype[arch] += 1
            elif event == "question_ending_violation":
                arch = str(payload.get("archetype") or "OTHER")
                qe_by_archetype[arch] += 1
            elif event == "spam_trigger_hits":
                spam_hit_messages += 1
                cats = payload.get("categories") or {}
                if isinstance(cats, dict):
                    for cat, n in cats.items():
                        try:
                            spam_by_category[str(cat)] += int(n)
                        except (TypeError, ValueError):
                            continue
            elif event == "mutual_connection_rendered":
                mutual_rendered += 1
            elif event == "mutual_connection_no_candidates":
                mutual_no_candidates += 1

        rollup.events_by_name = dict(events_by_name)
        rollup.length_violations_by_archetype = dict(length_by_archetype)
        rollup.question_ending_violations_by_archetype = dict(qe_by_archetype)
        rollup.spam_trigger_hits_by_category = dict(spam_by_category)
        rollup.spam_trigger_total_messages_with_hits = spam_hit_messages
        denom = mutual_rendered + mutual_no_candidates
        rollup.mutual_connection_priming_rate = (
            mutual_rendered / denom if denom > 0 else 0.0
        )
        rollup.unknown_events = sorted(unknown_seen)
        rollup.session_ids_observed = sorted(sessions_seen)
        return rollup

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _iter_rows(self) -> Iterable[dict]:
        """Yield parsed JSONL rows, tolerating malformed lines."""
        with self._log_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(row, dict):
                    yield row


__all__ = [
    "KNOWN_EVENTS",
    "OutreachLearningRollup",
    "OutreachLearningSubscriber",
]
