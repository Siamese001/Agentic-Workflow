"""Active §5 enforcement bridge (plan `-d5e8b3` §Q4).

Env var ``EVAL_SPINE_ENFORCE=1`` opts a request into having the
eval_spine ExitDecision *upgrade* the legacy ExitControlGate disposition
when — and only when — eval_spine wants something strictly stricter.

Upgrade-only semantics (never loosens; fail-closed):

    eval_spine disposition    -> applied only if legacy is weaker
    ---------------------------------------------------
    escalate_hitl             -> ESCALATE_TO_HITL (always replaces)
    deny_reroute              -> DENY_RETURN (replaces ALLOW/COMMIT)
    allow_finish              -> never replaces legacy
    commit_request            -> never replaces legacy

``policy_halt=true`` on eval_spine safety flags forces ESCALATE_TO_HITL
even if eval_spine's own disposition string is softer (defense in depth
against kill-switch misrouting).

This module is a thin adapter. It owns NO disposition logic; that lives
in ``agentic_core.L5_safety.eval_spine.exit_eval.evaluate_exit``. Here
we only translate and merge.
"""

from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from agentic_core.L5_safety.types.exit_disposition_types import ExitDisposition

if TYPE_CHECKING:
    from agentic_core.L5_safety.eval_spine.exit_decision import ExitDecision

_ENFORCE_FLAG = "EVAL_SPINE_ENFORCE"
_logger = logging.getLogger(__name__)

# Strictness order — higher index is stricter.
_LEGACY_STRICTNESS: dict[ExitDisposition, int] = {
    ExitDisposition.ALLOW_RESPONSE: 0,
    ExitDisposition.COMMIT_TO_UWG: 0,
    ExitDisposition.DENY_RETURN: 2,
    ExitDisposition.ESCALATE_TO_HITL: 3,
}

# Map eval_spine disposition strings → canonical ExitDisposition.
_EVAL_SPINE_TO_LEGACY: dict[str, ExitDisposition] = {
    "allow_finish": ExitDisposition.ALLOW_RESPONSE,
    "commit_request": ExitDisposition.COMMIT_TO_UWG,
    "deny_reroute": ExitDisposition.DENY_RETURN,
    "escalate_hitl": ExitDisposition.ESCALATE_TO_HITL,
}


def is_enforce_enabled() -> bool:
    """Return True iff ``EVAL_SPINE_ENFORCE`` is set to a truthy value."""
    raw = os.environ.get(_ENFORCE_FLAG, "")
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def eval_spine_to_legacy(eval_spine_disposition: str) -> ExitDisposition | None:
    """Translate eval_spine disposition string → canonical ExitDisposition.

    Returns None on unrecognized input (caller should fall back to legacy).
    """
    return _EVAL_SPINE_TO_LEGACY.get(eval_spine_disposition)


def merge_disposition(
    legacy: ExitDisposition,
    decision: "ExitDecision",
) -> tuple[ExitDisposition, str | None]:
    """Merge eval_spine decision into legacy disposition.

    Returns ``(final_disposition, upgrade_reason)`` where ``upgrade_reason``
    is non-None iff eval_spine caused an upgrade (strictly stricter).

    Rules:
      1. ``decision.safety.policy_halt`` → force ESCALATE_TO_HITL.
      2. Translate ``decision.disposition`` via the map.
      3. If translated is strictly stricter than legacy, replace. Else keep legacy.
    """
    # Rule 1: policy halt always wins.
    if decision.safety.policy_halt:
        if legacy != ExitDisposition.ESCALATE_TO_HITL:
            return (
                ExitDisposition.ESCALATE_TO_HITL,
                f"eval_spine.policy_halt; reason_code={decision.reason_code}",
            )
        return legacy, None

    translated = eval_spine_to_legacy(decision.disposition)
    if translated is None:
        return legacy, None

    legacy_rank = _LEGACY_STRICTNESS.get(legacy, 0)
    new_rank = _LEGACY_STRICTNESS.get(translated, 0)
    if new_rank > legacy_rank:
        return (
            translated,
            f"eval_spine.{decision.disposition}; reason_code={decision.reason_code}",
        )
    return legacy, None


__all__ = [
    "eval_spine_to_legacy",
    "is_enforce_enabled",
    "merge_disposition",
]
