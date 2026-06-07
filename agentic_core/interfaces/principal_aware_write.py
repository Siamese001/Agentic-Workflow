"""Principal-Aware Write Adapter — L5 v4 G-04 W2.

Attaches a `PrincipalChain` to every write operation without modifying the
existing HMAC-signed `InstructionPacket` contract or the `UniversalWriteGateway`
authority surface.

Rationale:
- `InstructionPacket` carries a cryptographic signature over a canonical
  JSON surface. Adding fields to it breaks signature determinism for every
  existing signer.
- `UniversalWriteGateway` has high fan-in; invasive changes there have
  outsize blast radius.
- Additive wrapper pattern: write sites import from here, pass both the
  existing packet AND a principal_chain, and the wrapper computes an
  extended replay_key that binds the two.

Contract:
  - Every v4-compliant write site MUST emit a `PrincipalAttachedWrite`
    before calling the write gateway.
  - The existing gateway continues to execute the InstructionPacket as
    before; the principal attachment is consumed by audit + L5 exit-control.
  - `compute_principal_replay_key()` extends `compute_replay_key()` with a
    principal_chain digest so replay reconstruction can verify identity
    alongside the write payload.

Reference:
  - docs/contracts/identity_propagation.md §3.4 (Tool invocation)
  - docs/reference/00_L5_Policy_Plane/capability_token.schema.md §7
Parent plan: docs/archive/windsurf/legacy-tree/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from agentic_core.interfaces._principal_envelope_base import (
    compose_replay_key,
    compute_principal_chain_digest,
    require_nonempty,
)
from agentic_core.interfaces.principal_chain_types import PrincipalChain
from agentic_core.interfaces.write_gateway import compute_replay_key


def compute_principal_replay_key(
    plan_hash: str,
    tool_calls: Sequence[str],
    stdout_digest: str,
    state_diff_hash: str,
    principal_chain: PrincipalChain,
) -> str:
    """replay_key for v4 writes, extended with principal_chain digest.

    Backward compatibility: the two-step composition (base replay_key +
    principal digest, hashed together) means v3 call sites that never see
    this helper continue to emit identical replay_keys; v4 call sites that
    DO see it emit a distinct, principal-bound replay_key. Collision with
    any v3 key is impossible because the v4 key includes an additional
    hash layer.
    """
    base = compute_replay_key(
        plan_hash=plan_hash,
        tool_calls=tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
    )
    principal_digest = compute_principal_chain_digest(principal_chain)
    return compose_replay_key({"base": base, "principal_digest": principal_digest})


@dataclass(frozen=True)
class PrincipalAttachedWrite:
    """Immutable record binding a write operation to an invoking principal.

    Carried alongside (not inside) an InstructionPacket so the packet's
    HMAC signature surface is untouched. Consumed by:
      - safety_audit_emitter (W5) — attribution
      - L5 exit-control (W4)     — delegation_depth + permission_ladder gate
      - replay envelope          — forensic reconstruction

    `principal_replay_key` is the v4 replay key that binds the write
    payload to the principal_chain (via
    `compute_principal_replay_key`).
    """

    plan_hash: str
    tool_calls: tuple[str, ...]
    stdout_digest: str
    state_diff_hash: str
    principal_chain: PrincipalChain
    principal_chain_digest: str
    principal_replay_key: str

    def __post_init__(self) -> None:
        require_nonempty(
            [
                ("PrincipalAttachedWrite: plan_hash", self.plan_hash),
                ("PrincipalAttachedWrite: stdout_digest", self.stdout_digest),
                ("PrincipalAttachedWrite: state_diff_hash", self.state_diff_hash),
                ("PrincipalAttachedWrite: principal_chain_digest", self.principal_chain_digest),
                ("PrincipalAttachedWrite: principal_replay_key", self.principal_replay_key),
            ]
        )
        # Enforce sorted invariant on tool_calls for determinism
        if list(self.tool_calls) != sorted(self.tool_calls):
            object.__setattr__(
                self,
                "tool_calls",
                tuple(sorted(self.tool_calls)),
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "plan_hash": self.plan_hash,
            "principal_chain": self.principal_chain.to_dict(),
            "principal_chain_digest": self.principal_chain_digest,
            "principal_replay_key": self.principal_replay_key,
            "state_diff_hash": self.state_diff_hash,
            "stdout_digest": self.stdout_digest,
            "tool_calls": list(self.tool_calls),
        }


def attach_principal_to_write(
    *,
    plan_hash: str,
    tool_calls: Sequence[str],
    stdout_digest: str,
    state_diff_hash: str,
    principal_chain: PrincipalChain,
) -> PrincipalAttachedWrite:
    """Factory: compute digests + replay key and return the attachment record."""
    sorted_tool_calls = tuple(sorted(tool_calls))
    principal_digest = compute_principal_chain_digest(principal_chain)
    replay_key = compute_principal_replay_key(
        plan_hash=plan_hash,
        tool_calls=sorted_tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
        principal_chain=principal_chain,
    )
    return PrincipalAttachedWrite(
        plan_hash=plan_hash,
        tool_calls=sorted_tool_calls,
        stdout_digest=stdout_digest,
        state_diff_hash=state_diff_hash,
        principal_chain=principal_chain,
        principal_chain_digest=principal_digest,
        principal_replay_key=replay_key,
    )


__all__ = [
    "PrincipalAttachedWrite",
    "attach_principal_to_write",
    "compute_principal_chain_digest",
    "compute_principal_replay_key",
]
