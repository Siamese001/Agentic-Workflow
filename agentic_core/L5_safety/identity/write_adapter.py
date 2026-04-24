"""Principal-Aware Write Adapter (Wire-In) — L5 v4 Wave-E.

Provides a **one-call wire-in helper** that existing v3 write call sites
use to emit BOTH the legacy v3 `replay_key` AND a v4
`PrincipalAttachedWrite` in a single step. This is the incremental
adoption path for G-04: call sites migrate at their own pace; the
contract guarantees the v3 key is byte-identical to what the v3
interface would have produced.

Usage pattern (for migrating a v3 call site):

    # BEFORE (v3):
    from agentic_core.interfaces.write_gateway import compute_replay_key
    rk = compute_replay_key(plan_hash, tool_calls, stdout_digest, state_diff_hash)

    # AFTER (v4 — one import swap, same signature shape):
    from agentic_core.L5_safety.identity.write_adapter import emit_v4_write
    v3_key, attached = emit_v4_write(
        plan_hash=plan_hash,
        tool_calls=tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
    )
    # rk (v3 key) stays byte-identical; `attached` carries principal binding.

Invariants:
- The v3 key returned MUST equal `compute_replay_key(same args)` byte-identically.
- `attached.principal_replay_key` is distinct from the v3 key (W2 guarantee).
- The adapter resolves the front-door principal if none provided, so
  call sites do not need to thread a principal through every layer.

Reference:
  - docs/contracts/identity_propagation.md §3.4 (Write gateway threading)
  - agentic_core/interfaces/principal_aware_write.py (W2)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

from typing import Sequence

from agentic_core.interfaces.principal_aware_write import (
    PrincipalAttachedWrite,
    attach_principal_to_write,
)
from agentic_core.interfaces.principal_chain_types import PrincipalChain
from agentic_core.interfaces.write_gateway import compute_replay_key
from agentic_core.L5_safety.identity.front_door_resolver import (
    resolve_front_door_principal,
)


def emit_v4_write(
    *,
    plan_hash: str,
    tool_calls: Sequence[str],
    stdout_digest: str,
    state_diff_hash: str,
    principal_chain: PrincipalChain | None = None,
) -> tuple[str, PrincipalAttachedWrite]:
    """Emit a v4-compliant write attachment while preserving v3 replay_key.

    Returns (v3_replay_key, principal_attached_write).

    The v3 key is byte-identical to the legacy path — callers can continue
    to persist it into any legacy audit surface that expects the v3 shape.
    The `PrincipalAttachedWrite` carries the principal_chain binding and is
    intended for the v4-aware audit / exit-control / replay-envelope surfaces.

    `principal_chain` defaults to the resolved front-door principal when the
    caller does not thread one explicitly. This is the intended path for
    internal write flows that run on behalf of the invoking user without
    a handoff chain.
    """
    if principal_chain is None:
        principal_chain = resolve_front_door_principal()

    v3_key = compute_replay_key(
        plan_hash=plan_hash,
        tool_calls=tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
    )
    attached = attach_principal_to_write(
        plan_hash=plan_hash,
        tool_calls=tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
        principal_chain=principal_chain,
    )
    return v3_key, attached


__all__ = ["emit_v4_write"]
