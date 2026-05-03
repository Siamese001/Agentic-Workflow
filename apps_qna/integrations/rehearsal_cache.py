"""Rehearsal semantic cache (W4.2).

Wave 4 phase 4.2 of ``apps-qna-dag-enhancements-e4c7b2``. The operator
rehearses the same shape of question repeatedly across sessions (e.g.
eight variants of "tell me about a time you led architecture"). Without a
cache, each rehearsal re-runs the full bandit / embedding / LLM-fallback
cascade from scratch, and the warm-start signal is lost.

This module adds a lightweight question-level cache that piggybacks on
the existing ``apps_qna_pack_lifecycle`` ledger (constitutional §29
canonical store for apps_qna) — **no new database**, per plan constraint.
It:

* Canonicalizes question text → a stable signature hash.
* On lookup, scans the last ``N`` ``cache_hit`` / ``cache_miss`` events
  for a matching signature; returns the persisted pick when found.
* On every lookup, emits a paired §29 ``ROUTER_DECISION: layer=L6
  router=apps_qna_rehearsal_cache`` marker + ledger row (``cache_hit``
  or ``cache_miss``), so downstream learning and audits see cache
  dynamics without scraping logs.

Both bandits (W4.1 route / W4.2 paste) consume this module as a warm-start
signal: a cache hit is equivalent to a binary "asked=True ∧ landed=True"
observation on the cached route/card, independent of the rehearsal's own
outcome. The cache therefore accelerates cold-start convergence without
double-counting real rehearsal outcomes.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

_log = logging.getLogger(__name__)

_LEDGER_NAME: str = "apps_qna_pack_lifecycle"
_ROUTER_LAYER: str = "L6"
_ROUTER_NAME: str = "apps_qna_rehearsal_cache"

# How many recent cache_hit/cache_miss rows to scan on each lookup.
# Bounded to keep the sqlite scan cheap even on long-lived ledgers.
_RECENT_EVENT_LIMIT: int = 200

_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")


def _normalize_question(text: str) -> str:
    """Strip case / punctuation / filler whitespace for signature stability.

    The signature does NOT do semantic equivalence — it is a literal
    normalization. Paraphrases yield different signatures by design; the
    cache is for *exact-shape* rehearsals of the same prompt (operator
    repeating a prep question verbatim across sessions).
    """
    lowered = (text or "").strip().lower()
    collapsed = _NORMALIZE_RE.sub(" ", lowered).strip()
    return collapsed


def question_signature(text: str) -> str:
    """Hash a normalized question to a stable 16-char signature."""
    norm = _normalize_question(text)
    if not norm:
        return "qna_q_empty"
    h = hashlib.sha256(norm.encode("utf-8")).hexdigest()
    return f"qna_q_{h[:16]}"


@dataclass(frozen=True)
class CacheLookupResult:
    """Outcome of a rehearsal cache lookup.

    ``hit`` is True iff a prior entry matched the question signature and
    was within the ``cache_hit``/``cache_miss`` scan window. ``route_id``
    is the previously-cached route when available.
    """

    hit: bool
    signature: str
    route_id: str | None
    decision_id: str


def _ledger_db_path() -> Path | None:
    try:
        from tools.ledgers.schema_registry import get  # noqa: PLC0415

        return get(_LEDGER_NAME).db_path
    except (ImportError, KeyError):
        return None


def _scan_recent_cache_rows(signature: str) -> str | None:
    """Return the cached route_id for ``signature``, or None.

    Scans the most recent ``_RECENT_EVENT_LIMIT`` ``cache_hit`` rows for
    a matching signature. A row shape is:

        prediction_json = {"signature": "qna_q_<hex>", "route_id": "..."}
    """
    path = _ledger_db_path()
    if path is None or not path.is_file():
        return None
    sql = (
        "SELECT prediction_json FROM events "
        "WHERE event_kind IN ('cache_hit', 'cache_miss') "
        "ORDER BY ts_utc DESC LIMIT ?"
    )
    try:
        con = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
        try:
            rows = list(con.execute(sql, (_RECENT_EVENT_LIMIT,)))
        finally:
            con.close()
    except sqlite3.Error as exc:
        _log.debug("rehearsal_cache scan sqlite error: %r", exc)
        return None

    for (prediction_json,) in rows:
        if not prediction_json:
            continue
        try:
            pred = json.loads(prediction_json)
        except json.JSONDecodeError:
            continue
        if pred.get("signature") != signature:
            continue
        route_id = pred.get("route_id")
        # We only treat prior cache_hit entries as hits; a cache_miss row
        # means the question was asked before but nothing was cached.
        if pred.get("event_kind") == "cache_hit" or pred.get("cached"):
            if isinstance(route_id, str) and route_id:
                return route_id
    return None


def _emit_marker(
    *,
    decision_id: str,
    signature: str,
    hit: bool,
    route_id: str | None,
) -> None:
    """Constitutional §29 paired marker."""
    kind = "cache_hit" if hit else "cache_miss"
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={decision_id} selected={route_id or ''} "
        f"signature={signature} event={kind}"
    )


def lookup(question: str) -> CacheLookupResult:
    """Look up a question in the rehearsal cache.

    Always emits a §29 paired marker + ledger row (``cache_hit`` or
    ``cache_miss``), so the audit surface sees every attempted lookup.
    """
    decision_id = uuid.uuid4().hex
    signature = question_signature(question)
    if signature == "qna_q_empty":
        _emit_marker(
            decision_id=decision_id,
            signature=signature,
            hit=False,
            route_id=None,
        )
        emit_pack_lifecycle_event(
            event_kind="cache_miss",
            prediction={
                "signature": signature,
                "route_id": None,
                "reason": "empty_question",
            },
            metadata={"decision_id": decision_id},
        )
        return CacheLookupResult(
            hit=False, signature=signature, route_id=None, decision_id=decision_id
        )

    cached = _scan_recent_cache_rows(signature)
    if cached:
        _emit_marker(
            decision_id=decision_id,
            signature=signature,
            hit=True,
            route_id=cached,
        )
        emit_pack_lifecycle_event(
            event_kind="cache_hit",
            prediction={
                "signature": signature,
                "route_id": cached,
            },
            metadata={"decision_id": decision_id},
        )
        return CacheLookupResult(
            hit=True,
            signature=signature,
            route_id=cached,
            decision_id=decision_id,
        )

    _emit_marker(
        decision_id=decision_id, signature=signature, hit=False, route_id=None
    )
    emit_pack_lifecycle_event(
        event_kind="cache_miss",
        prediction={
            "signature": signature,
            "route_id": None,
        },
        metadata={"decision_id": decision_id},
    )
    return CacheLookupResult(
        hit=False, signature=signature, route_id=None, decision_id=decision_id
    )


def write(*, question: str, route_id: str) -> str:
    """Persist a (question, route_id) observation to the cache.

    Emits a ``cache_hit`` ledger row so subsequent ``lookup`` calls for
    the same signature return ``route_id``. Also writes a §29 paired
    marker. ``route_id`` should be a registry-admissible id — the cache
    does NOT validate admissibility (caller's responsibility).

    Returns the decision_id.
    """
    decision_id = uuid.uuid4().hex
    signature = question_signature(question)
    _emit_marker(
        decision_id=decision_id,
        signature=signature,
        hit=True,
        route_id=route_id,
    )
    emit_pack_lifecycle_event(
        event_kind="cache_hit",
        prediction={
            "signature": signature,
            "route_id": route_id,
            "cached": True,
            "event_kind": "cache_hit",
        },
        metadata={"decision_id": decision_id, "source": "rehearsal_cache.write"},
    )
    return decision_id


def warm_start_signal(question: str) -> dict[str, Any] | None:
    """Convenience surface for the bandits (W4.1/W4.2).

    Returns a dict ``{route_id, signature, decision_id}`` on cache hit;
    ``None`` on miss. Bandits treat the hit as an equivalent-to-positive
    Bernoulli observation on the cached route (``asked=True,
    landed=True``) when they are still in cold-start.
    """
    result = lookup(question)
    if not result.hit or not result.route_id:
        return None
    return {
        "route_id": result.route_id,
        "signature": result.signature,
        "decision_id": result.decision_id,
    }


__all__ = [
    "CacheLookupResult",
    "lookup",
    "question_signature",
    "warm_start_signal",
    "write",
]
