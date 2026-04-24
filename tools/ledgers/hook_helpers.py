"""tools.ledgers.hook_helpers — Convenience surface for post-hook writer calls.

Each Windsurf post-hook adds ONE import + ONE call at its main-analysis tail:

    from tools.ledgers.hook_helpers import emit_ledger_event
    emit_ledger_event(
        ledger="tool_routing",
        event_kind="retrieval_tool_choice",
        prediction=prediction_dict,
        outcome=outcome_dict,     # optional; None if not yet bound
        score_band="correct",     # optional
        repo_area=file_path,
        latency_ms=None,
        metadata={"session_id": session_id},
    )

The helper:
    - Swallows every exception internally (hook paths must never crash)
    - Returns the event_id on success, empty string on any failure/bypass
    - Imports tools.ledgers lazily so the overall hook pays zero import cost
      on the happy path where a ledger call isn't reached
"""

from __future__ import annotations

import sys
from typing import Any


def emit_ledger_event(
    *,
    ledger: str,
    event_kind: str,
    prediction: Any = None,
    outcome: Any = None,
    score_band: str | None = None,
    score_numeric: float | None = None,
    repo_area: str = "",
    session_id: str = "",
    branch: str = "",
    commit_sha: str = "",
    adg_snapshot_id: str = "",
    latency_ms: int | None = None,
    metadata: Any = None,
) -> str:
    """Best-effort ledger row emit. Returns event_id or empty string on any error."""
    try:
        from tools.ledgers import writer_for  # lazy import
        return writer_for(ledger).append(
            event_kind=event_kind,
            prediction=prediction,
            outcome=outcome,
            score_band=score_band,
            score_numeric=score_numeric,
            repo_area=repo_area,
            session_id=session_id,
            branch=branch,
            commit_sha=commit_sha,
            adg_snapshot_id=adg_snapshot_id,
            latency_ms=latency_ms,
            metadata=metadata,
        )
    except Exception as exc:  # broad catch is intentional: hooks must never raise
        # guardian: allow-broad-except -- hook fail-soft contract; writer path already
        # fail-soft, this catches ImportError / circular-import edge cases in CI envs
        print(f"[hook_helpers] emit_ledger_event({ledger}) suppressed: {exc!r}",
              file=sys.stderr)
        return ""


def bind_ledger_outcome(
    *,
    ledger: str,
    event_id: str,
    outcome: Any,
    score_band: str | None = None,
    score_numeric: float | None = None,
    latency_ms: int | None = None,
) -> bool:
    """Best-effort late-outcome binding. Returns True on success."""
    if not event_id:
        return False
    try:
        from tools.ledgers import writer_for
        return writer_for(ledger).bind_outcome(
            event_id,
            outcome=outcome,
            score_band=score_band,
            score_numeric=score_numeric,
            latency_ms=latency_ms,
        )
    except Exception as exc:  # noqa: BLE001
        # guardian: allow-broad-except -- hook fail-soft contract
        print(f"[hook_helpers] bind_ledger_outcome({ledger}) suppressed: {exc!r}",
              file=sys.stderr)
        return False
