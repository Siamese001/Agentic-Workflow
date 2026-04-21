"""Runtime HITL integration glue for governed app runners (W5).

Per plan `runtime-hitl-exit-control-c4e7b3.md` W5 and ADR-023 §3.2, every
governed runner calls :func:`classify_exit` immediately after sealing (E5) and
before any UWG invocation. This module centralizes the three pieces of glue
that would otherwise duplicate across apps_lic / apps_exec / apps_underwriting_ai:

1. :func:`build_exit_envelope` — construct the sealed-folder envelope that
   :func:`classify_exit` consumes. The envelope maps L5 gate outcome +
   retrieval-quality signals to the classification fields defined in
   ``config/runtime_hitl_policy.yaml`` (``is_financial``, ``is_regulated``,
   ``confidence_score``, ``novelty_score`` …).

2. :class:`RunStateCheckpoint` + :class:`RunStateStore` — G7 blocker closure.
   The ledger (W2) persists escalation state. Apps with long-running business
   state must ADDITIONALLY checkpoint their own runner context so a worker can
   resume the run after HITL resolution without replaying the whole pipeline.

3. :func:`maybe_escalate_hitl` — the single integration helper governed
   runners call. Returns an :class:`HitlResult` that records the
   :class:`ExitAction`, hitl_class, and ledger_id; runners translate this into
   their app-specific result records.

Feature flags (plan §"Feature Flags & Rollback", lines 260–262):
- ``RUNTIME_HITL_ENABLED`` env var (default ``false``) — master switch
- Per-runner ``HITL_ENABLED`` class attribute — per-app opt-in

Both must be truthy for escalation to occur; otherwise the helper returns
:class:`HitlResult` with ``action=ExitAction.COMMIT`` and no ledger write.

This module is pure glue; all policy and dispatch primitives live in L3/L5.
Layer direction: ``apps_shared`` may import from ``agentic_core`` (downward).
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Mapping

from agentic_core.L3_orchestration.exit_control.exit_controller import (
    ExitAction,
    ExitController,
    ExitDecision,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    DEFAULT_LEDGER_PATH,
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.exit_control.hitl_policy import HitlPolicy, load_policy

_log = logging.getLogger(__name__)

ENV_FLAG = "RUNTIME_HITL_ENABLED"
DEFAULT_RUN_STATE_PATH = Path("artifacts/runtime/run_state_checkpoints.db")


# ---------------------------------------------------------------------------
# Envelope construction
# ---------------------------------------------------------------------------


def build_exit_envelope(
    *,
    app_name: str,
    query: str,
    gate_disposition: str,
    grounded: bool,
    citation_count: int,
    support_coverage: float,
    disposition: str,
    policy_overrides: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Assemble the sealed-folder envelope for :func:`classify_exit`.

    The envelope MUST be deterministic — the ledger stores it verbatim and
    the hash chain (W7) binds it into the audit trail.

    Mapping rules (plan P2.1 envelope contract):

    - ``confidence_score`` = ``support_coverage`` clamped to [0, 1]. This is
      the retrieval-grounded confidence the L5 gate already computed.
    - ``novelty_score`` = 1.0 when the bundle has no citations (every chunk is
      "new" / unsupported). Otherwise 0.0 — apps may override via
      ``policy_overrides`` when they have a domain-specific novelty signal.
    - ``is_regulated`` / ``is_financial`` / ``is_safety_impacting`` default to
      False. Apps that know their domain (e.g. apps_lic under compliance mode,
      apps_underwriting_ai for covenant exceptions) MUST override.
    - ``requires_policy_override`` = ``gate_disposition`` in
      {"block", "denied"} — the L5 gate already said no; a human must vouch
      for the override.
    - ``deny`` = False here. The governed runner decides DENY separately; this
      envelope only flows when the runner wants classification or COMMIT.

    Arguments
    ---------
    app_name:
        Governed app identifier (e.g. "apps_lic"), stamped into the envelope
        for forensic tracing.
    query:
        Primary query string fed through the pipeline.
    gate_disposition:
        ``ExitDisposition.value`` from the L5 gate (lowercased).
    grounded:
        True when the L5 gate reports ``grounded_replayable=True``.
    citation_count:
        Number of citation anchors in the shaped bundle.
    support_coverage:
        Mean combined_score across ranked chunks (0.0 when bundle empty).
    disposition:
        ``WeakSupportDisposition.value`` (lowercased).
    policy_overrides:
        App-specific overrides merged on top of the defaults. Fields here
        WIN over the computed defaults — apps use this to stamp known
        regulatory or financial signals without re-deriving them.
    """
    confidence = max(0.0, min(1.0, float(support_coverage)))
    novelty = 1.0 if citation_count == 0 else 0.0
    requires_override = gate_disposition in {"block", "denied", "deny"}

    envelope: dict[str, Any] = {
        "app_name": app_name,
        "query": query,
        "gate_disposition": gate_disposition,
        "grounded": bool(grounded),
        "disposition": disposition,
        "citation_count": int(citation_count),
        "confidence_score": confidence,
        "novelty_score": novelty,
        "is_financial": False,
        "is_regulated": False,
        "is_safety_impacting": False,
        "requires_policy_override": requires_override,
        "deny": False,
    }

    if policy_overrides:
        for key, value in policy_overrides.items():
            envelope[key] = value

    return envelope


# ---------------------------------------------------------------------------
# G7 — RunState checkpoint (app-owned business state)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class RunStateCheckpoint:
    """App-owned business-state snapshot for HITL suspend-resume.

    The runtime HITL ledger handles ESCALATION state (pending / approved /
    denied / timeout). The governed runner's OWN state — query, sub-queries,
    shaped bundle references, app-specific context — lives here.

    ``payload`` is an opaque mapping the app serializes and rehydrates. It
    MUST be JSON-serializable (enforced on write).

    ``ledger_id`` binds the checkpoint to its escalation so resume can find
    the right row.
    """

    run_id: str
    ledger_id: str
    app_name: str
    checkpoint_kind: str  # e.g. "pre_uwg", "covenant_exception"
    payload: Mapping[str, Any] = field(default_factory=dict)
    created_at: float = 0.0


_RUN_STATE_SCHEMA = """
CREATE TABLE IF NOT EXISTS run_state_checkpoints (
    run_id          TEXT NOT NULL,
    ledger_id       TEXT NOT NULL,
    app_name        TEXT NOT NULL,
    checkpoint_kind TEXT NOT NULL,
    payload_json    TEXT NOT NULL,
    created_at      REAL NOT NULL,
    PRIMARY KEY (run_id, ledger_id)
);
CREATE INDEX IF NOT EXISTS idx_runstate_ledger ON run_state_checkpoints(ledger_id);
CREATE INDEX IF NOT EXISTS idx_runstate_app ON run_state_checkpoints(app_name);
"""


class RunStateStore:
    """SQLite-backed checkpoint store for governed runner business state.

    Co-located with the HITL ledger (defaults to ``artifacts/runtime/``) but
    stored in a separate DB file to keep schemas independent — ledger integrity
    and business-state integrity have different retention policies.
    """

    def __init__(
        self,
        path: Path | str | None = None,
        *,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._path = Path(path) if path is not None else DEFAULT_RUN_STATE_PATH
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._now = now or time.time
        self._conn = sqlite3.connect(str(self._path), isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._conn.executescript(_RUN_STATE_SCHEMA)

    def close(self) -> None:
        self._conn.close()

    def __enter__(self) -> "RunStateStore":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    def checkpoint(
        self,
        *,
        run_id: str,
        ledger_id: str,
        app_name: str,
        checkpoint_kind: str,
        payload: Mapping[str, Any] | None = None,
    ) -> RunStateCheckpoint:
        """Persist a checkpoint row. Payload MUST be JSON-serializable."""
        data = dict(payload or {})
        try:
            payload_json = json.dumps(data, sort_keys=True)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"RunStateCheckpoint payload not JSON-serializable: {exc}") from exc
        created_at = self._now()
        self._conn.execute(
            """INSERT OR REPLACE INTO run_state_checkpoints
               (run_id, ledger_id, app_name, checkpoint_kind, payload_json, created_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (run_id, ledger_id, app_name, checkpoint_kind, payload_json, created_at),
        )
        return RunStateCheckpoint(
            run_id=run_id,
            ledger_id=ledger_id,
            app_name=app_name,
            checkpoint_kind=checkpoint_kind,
            payload=data,
            created_at=created_at,
        )

    def load(self, *, run_id: str, ledger_id: str) -> RunStateCheckpoint | None:
        """Return the checkpoint for ``(run_id, ledger_id)`` or None."""
        row = self._conn.execute(
            """SELECT run_id, ledger_id, app_name, checkpoint_kind, payload_json, created_at
               FROM run_state_checkpoints WHERE run_id = ? AND ledger_id = ?""",
            (run_id, ledger_id),
        ).fetchone()
        if row is None:
            return None
        return RunStateCheckpoint(
            run_id=row["run_id"],
            ledger_id=row["ledger_id"],
            app_name=row["app_name"],
            checkpoint_kind=row["checkpoint_kind"],
            payload=json.loads(row["payload_json"]),
            created_at=float(row["created_at"]),
        )

    def list_by_app(self, app_name: str) -> list[RunStateCheckpoint]:
        rows = self._conn.execute(
            """SELECT run_id, ledger_id, app_name, checkpoint_kind, payload_json, created_at
               FROM run_state_checkpoints WHERE app_name = ? ORDER BY created_at ASC""",
            (app_name,),
        ).fetchall()
        return [
            RunStateCheckpoint(
                run_id=r["run_id"],
                ledger_id=r["ledger_id"],
                app_name=r["app_name"],
                checkpoint_kind=r["checkpoint_kind"],
                payload=json.loads(r["payload_json"]),
                created_at=float(r["created_at"]),
            )
            for r in rows
        ]


# ---------------------------------------------------------------------------
# Runner-facing helper
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class HitlResult:
    """Outcome of :func:`maybe_escalate_hitl`.

    - ``action`` is always populated.
    - ``hitl_class`` / ``ledger_id`` / ``approver_pool`` / ``timeout_s`` are
      populated only when ``action == ExitAction.ESCALATE_HITL``.
    - ``checkpoint`` is populated only when escalation occurred AND a non-None
      ``checkpoint_payload`` was supplied.
    - ``enabled`` is False when either the env flag or the per-app flag was
      off; the action will be COMMIT and no ledger row was written.
    """

    action: ExitAction
    enabled: bool
    hitl_class: str = ""
    ledger_id: str = ""
    approver_pool: str = ""
    timeout_s: int = 0
    fallback: str = ""
    deny_reason: str = ""
    checkpoint: RunStateCheckpoint | None = None


def is_hitl_enabled(runner_flag: bool) -> bool:
    """Return True only when BOTH the env flag AND the per-runner flag are on."""
    env_value = os.environ.get(ENV_FLAG, "").strip().lower()
    env_on = env_value in {"1", "true", "yes", "on"}
    return env_on and bool(runner_flag)


def maybe_escalate_hitl(
    *,
    app_name: str,
    run_id: str,
    trace_id: str,
    envelope: Mapping[str, Any],
    runner_flag: bool,
    controller: ExitController | None = None,
    policy: HitlPolicy | None = None,
    ledger: RuntimeHitlLedger | None = None,
    run_state_store: RunStateStore | None = None,
    checkpoint_kind: str = "pre_uwg",
    checkpoint_payload: Mapping[str, Any] | None = None,
) -> HitlResult:
    """Classify ``envelope`` via :func:`classify_exit`; checkpoint on escalate.

    All dependencies are injectable — this keeps the governed runner hermetic
    in tests and allows production composition to bind a real ledger +
    checkpoint store once at startup.

    Short-circuit semantics:

    - If the flags are off → return ``HitlResult(action=COMMIT, enabled=False)``
      with NO ledger / checkpoint side effects. This is the rollback path
      (plan §"Feature Flags & Rollback").
    - If the L5 gate's envelope carries ``deny=True`` → surface as
      ``ExitAction.DENY`` without classification.
    - If classification returns ``COMMIT`` → no ledger row, no checkpoint.
    - If classification returns ``ESCALATE_HITL`` → ledger row written by
      ``classify_exit``; a checkpoint row is ADDITIONALLY written here when
      ``checkpoint_payload`` is not None.
    """
    if not is_hitl_enabled(runner_flag):
        return HitlResult(action=ExitAction.COMMIT, enabled=False)

    active_controller = controller
    if active_controller is None:
        if policy is None:
            policy = load_policy()
        if ledger is None:
            ledger = RuntimeHitlLedger(DEFAULT_LEDGER_PATH)
        active_controller = ExitController(policy=policy, ledger=ledger)

    try:
        decision: ExitDecision = active_controller.classify(envelope, run_id=run_id, trace_id=trace_id)
    except (TypeError, ValueError) as exc:
        _log.warning(
            "[runtime_hitl] classify_exit failed run_id=%s app=%s: %s",
            run_id,
            app_name,
            exc,
        )
        return HitlResult(action=ExitAction.COMMIT, enabled=True)

    if decision.action is ExitAction.DENY:
        return HitlResult(
            action=ExitAction.DENY,
            enabled=True,
            deny_reason=decision.deny_reason or "",
        )

    if decision.action is ExitAction.COMMIT:
        return HitlResult(action=ExitAction.COMMIT, enabled=True)

    # ESCALATE_HITL — optionally checkpoint business state (G7 closure)
    checkpoint: RunStateCheckpoint | None = None
    if checkpoint_payload is not None and decision.ledger_id:
        store = run_state_store or RunStateStore()
        try:
            checkpoint = store.checkpoint(
                run_id=run_id,
                ledger_id=decision.ledger_id,
                app_name=app_name,
                checkpoint_kind=checkpoint_kind,
                payload=checkpoint_payload,
            )
        except (ValueError, sqlite3.DatabaseError) as exc:
            _log.warning(
                "[runtime_hitl] checkpoint failed run_id=%s ledger_id=%s: %s",
                run_id,
                decision.ledger_id,
                exc,
            )
        finally:
            if run_state_store is None:
                store.close()

    return HitlResult(
        action=ExitAction.ESCALATE_HITL,
        enabled=True,
        hitl_class=decision.hitl_class.value if decision.hitl_class else "",
        ledger_id=decision.ledger_id or "",
        approver_pool=decision.approver_pool or "",
        timeout_s=decision.timeout_s or 0,
        fallback=decision.fallback or "",
        checkpoint=checkpoint,
    )


__all__ = [
    "DEFAULT_RUN_STATE_PATH",
    "ENV_FLAG",
    "HitlResult",
    "RunStateCheckpoint",
    "RunStateStore",
    "build_exit_envelope",
    "is_hitl_enabled",
    "maybe_escalate_hitl",
]
