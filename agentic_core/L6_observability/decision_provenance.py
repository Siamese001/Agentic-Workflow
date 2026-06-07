"""Decision provenance stamp — five-field identifier for every decision row.

Plan: ``docs/archive/windsurf/legacy-tree/plans/routing-decision-process-enhancement-9c7e4d.md`` Wave W3.

Every row in the unified ``decision_events`` table carries a five-field
provenance stamp so any downstream regression can be traced back to:

* ``decision_layer`` — which routing layer issued the decision (closed
  vocabulary in :data:`agentic_core.L6_observability.decision_events_schema.DECISION_LAYERS`)
* ``policy_hash`` — hash of the active policy snapshot at decision time
* ``snapshot_id`` — ADG / data-snapshot identifier
* ``calibration_version`` — version of the threshold YAML / bandit weights
* ``judge_version`` — version of the active LLM judge / rubric

The :class:`DecisionProvenance` dataclass is the canonical surface. Two
deterministic helpers are provided:

* :func:`provenance_digest` — sha256 over canonical JSON, stable across
  processes / hosts. Used as the ``provenance_digest`` column in the
  ``decision_events`` table.
* :func:`current_provenance` — factory that pulls live values from
  process-state with sentinel fallbacks. Never raises.

This module deliberately does NOT import from any other ``agentic_core``
layer at module top level — it must be safe to import from L0 routing
without pulling in L4/L5/L6 cycles.
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass
from typing import Final

from agentic_core.L6_observability.decision_events_schema import (
    DECISION_LAYERS,
    UnknownDecisionLayerError,
)

# ---------------------------------------------------------------------------
# Sentinel values for missing fields. Never raise; always emit a row.
# ---------------------------------------------------------------------------

UNKNOWN_POLICY_HASH: Final[str] = "policy:unknown"
UNKNOWN_SNAPSHOT_ID: Final[str] = "snapshot:unknown"
UNKNOWN_CALIBRATION_VERSION: Final[str] = "calibration:unknown"
UNKNOWN_JUDGE_VERSION: Final[str] = "judge:unknown"

# Environment overrides — used by tests and by deployment surfaces that
# inject the active versions before process start.
_ENV_POLICY_HASH = "AGENTIC_POLICY_HASH"
_ENV_SNAPSHOT_ID = "AGENTIC_SNAPSHOT_ID"
_ENV_CALIBRATION_VERSION = "AGENTIC_CALIBRATION_VERSION"
_ENV_JUDGE_VERSION = "AGENTIC_JUDGE_VERSION"


# ---------------------------------------------------------------------------
# Dataclass.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class DecisionProvenance:
    """Five-field provenance stamp attached to every decision row.

    Every field is a string. ``decision_layer`` MUST be in ``DECISION_LAYERS``.
    The other four use the ``UNKNOWN_*`` sentinel when the underlying source
    is unavailable — never raise.
    """

    decision_layer: str
    policy_hash: str = UNKNOWN_POLICY_HASH
    snapshot_id: str = UNKNOWN_SNAPSHOT_ID
    calibration_version: str = UNKNOWN_CALIBRATION_VERSION
    judge_version: str = UNKNOWN_JUDGE_VERSION

    def __post_init__(self) -> None:
        if self.decision_layer not in DECISION_LAYERS:
            raise UnknownDecisionLayerError(
                f"unknown decision_layer={self.decision_layer!r}; allowed={sorted(DECISION_LAYERS)}",
            )

    def to_dict(self) -> dict[str, str]:
        """Return a plain dict (safe for ``decision_events.extras_json``)."""
        return asdict(self)


# ---------------------------------------------------------------------------
# Deterministic digest.
# ---------------------------------------------------------------------------


def provenance_digest(prov: DecisionProvenance) -> str:
    """Return the sha256 digest over canonical JSON of the provenance.

    Same inputs MUST yield the same digest across processes / hosts.
    Used as the ``decision_events.provenance_digest`` column value.
    """
    payload = json.dumps(
        prov.to_dict(),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


# ---------------------------------------------------------------------------
# Factory — pulls live values from process-state with sentinels.
# ---------------------------------------------------------------------------


def current_provenance(decision_layer: str) -> DecisionProvenance:
    """Return the active provenance stamp for ``decision_layer``.

    Resolution order for each non-layer field:

    1. Environment variable (``AGENTIC_POLICY_HASH`` / ``AGENTIC_SNAPSHOT_ID``
       / ``AGENTIC_CALIBRATION_VERSION`` / ``AGENTIC_JUDGE_VERSION``)
    2. Module-level cache (set by ``set_active_provenance`` for in-process
       overrides — used by orchestration surfaces that bind the values at
       startup but cannot mutate the env)
    3. ``UNKNOWN_*`` sentinel

    Never raises (except for an unknown ``decision_layer``, which is a
    programmer error and surfaces immediately).
    """
    return DecisionProvenance(
        decision_layer=decision_layer,
        policy_hash=_resolve(_ENV_POLICY_HASH, _ACTIVE.get("policy_hash"), UNKNOWN_POLICY_HASH),
        snapshot_id=_resolve(_ENV_SNAPSHOT_ID, _ACTIVE.get("snapshot_id"), UNKNOWN_SNAPSHOT_ID),
        calibration_version=_resolve(
            _ENV_CALIBRATION_VERSION,
            _ACTIVE.get("calibration_version"),
            UNKNOWN_CALIBRATION_VERSION,
        ),
        judge_version=_resolve(
            _ENV_JUDGE_VERSION,
            _ACTIVE.get("judge_version"),
            UNKNOWN_JUDGE_VERSION,
        ),
    )


# ---------------------------------------------------------------------------
# In-process active-provenance binding (used by composition root).
# ---------------------------------------------------------------------------

_ACTIVE: dict[str, str] = {}


def set_active_provenance(
    *,
    policy_hash: str | None = None,
    snapshot_id: str | None = None,
    calibration_version: str | None = None,
    judge_version: str | None = None,
) -> None:
    """Bind active provenance values for the current process.

    Called by the composition root when policy / snapshot / calibration /
    judge are loaded. Values can be cleared by passing ``None``.
    """
    if policy_hash is not None:
        _ACTIVE["policy_hash"] = policy_hash
    if snapshot_id is not None:
        _ACTIVE["snapshot_id"] = snapshot_id
    if calibration_version is not None:
        _ACTIVE["calibration_version"] = calibration_version
    if judge_version is not None:
        _ACTIVE["judge_version"] = judge_version


def reset_active_provenance() -> None:
    """Clear the in-process active-provenance cache. Test-only helper."""
    _ACTIVE.clear()


def _resolve(env_var: str, in_process: str | None, sentinel: str) -> str:
    """Resolve a single field via env → in-process cache → sentinel."""
    env_val = os.environ.get(env_var)
    if env_val:
        return env_val
    if in_process:
        return in_process
    return sentinel


__all__ = [
    "DecisionProvenance",
    "UNKNOWN_CALIBRATION_VERSION",
    "UNKNOWN_JUDGE_VERSION",
    "UNKNOWN_POLICY_HASH",
    "UNKNOWN_SNAPSHOT_ID",
    "current_provenance",
    "provenance_digest",
    "reset_active_provenance",
    "set_active_provenance",
]
