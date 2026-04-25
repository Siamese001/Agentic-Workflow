"""
Step-scoped narrow identity — W2-P2.3 (gap plan b7c4e2 G16).

Per codebridge.tech 2026 agent-guardrails doctrine:

    "An agent should never inherit broad access by default. It should
    operate with a narrow identity, limited tool access, and only the
    permissions required for a specific workflow or task."

The existing cap-token / ``SovereignLLMGateway.authorize_and_execute``
path authenticates at the **agent** level. This module narrows identity
to the **step** level: every `run_l2_phases` invocation derives a
``StepIdentity`` that is a strict subset of the agent identity, bound to
the step's trace_id, allowed capabilities, and allowed egress audiences.

Backward compatibility: the existing agent identity field on execution
traces is untouched. ``StepIdentity.parent_agent_id`` carries the agent
identity so legacy consumers can continue reading it.

Guardian note: no broad exceptions, no subprocess, no filesystem writes.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Any, Iterable

__all__ = [
    "StepIdentity",
    "IdentityDerivation",
    "derive_step_identity",
]


@dataclass(frozen=True, slots=True)
class StepIdentity:
    """Narrow identity for a single L2 step.

    * ``step_id`` — stable id for the step (prefer trace_id).
    * ``parent_agent_id`` — preserves the original agent identity for
      backward-compat consumers; MUST NOT be used for authorization decisions.
    * ``allowed_capabilities`` — strict subset of the parent agent's caps.
    * ``allowed_audiences`` — egress / credential audiences the step may use.
    * ``narrow_hash`` — deterministic fingerprint for audit logs.
    """

    step_id: str
    parent_agent_id: str
    allowed_capabilities: frozenset[str]
    allowed_audiences: frozenset[str]
    issued_at: float
    narrow_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def has_capability(self, cap: str) -> bool:
        return cap in self.allowed_capabilities

    def can_reach(self, audience: str) -> bool:
        return audience in self.allowed_audiences

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "parent_agent_id": self.parent_agent_id,
            "allowed_capabilities": sorted(self.allowed_capabilities),
            "allowed_audiences": sorted(self.allowed_audiences),
            "issued_at": self.issued_at,
            "narrow_hash": self.narrow_hash,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class IdentityDerivation:
    """Inputs to ``derive_step_identity``.

    The caller supplies the *parent* agent's full capability / audience sets
    plus the *requested* narrow subset for this step. The factory enforces
    the subset invariant — you cannot derive more authority than the parent.
    """

    step_id: str
    parent_agent_id: str
    parent_capabilities: frozenset[str]
    parent_audiences: frozenset[str]
    requested_capabilities: frozenset[str]
    requested_audiences: frozenset[str]
    metadata: dict[str, Any] = field(default_factory=dict)


class CapabilityEscalation(Exception):
    """Raised when a step requests a capability the parent does not hold."""


class AudienceEscalation(Exception):
    """Raised when a step requests an egress audience the parent does not hold."""


def derive_step_identity(derivation: IdentityDerivation) -> StepIdentity:
    """Derive a ``StepIdentity`` that is a strict subset of the parent agent.

    Raises ``CapabilityEscalation`` or ``AudienceEscalation`` when the
    requested narrow set is not contained in the parent's authority.
    """
    if not derivation.step_id:
        raise ValueError("step_id is required")
    if not derivation.parent_agent_id:
        raise ValueError("parent_agent_id is required")

    extra_caps = derivation.requested_capabilities - derivation.parent_capabilities
    if extra_caps:
        raise CapabilityEscalation(
            f"step {derivation.step_id!r} requested capabilities outside parent: {sorted(extra_caps)}"
        )

    extra_auds = derivation.requested_audiences - derivation.parent_audiences
    if extra_auds:
        raise AudienceEscalation(
            f"step {derivation.step_id!r} requested audiences outside parent: {sorted(extra_auds)}"
        )

    issued_at = time.time()
    narrow_hash = _fingerprint(derivation, issued_at)
    return StepIdentity(
        step_id=derivation.step_id,
        parent_agent_id=derivation.parent_agent_id,
        allowed_capabilities=frozenset(derivation.requested_capabilities),
        allowed_audiences=frozenset(derivation.requested_audiences),
        issued_at=issued_at,
        narrow_hash=narrow_hash,
        metadata=dict(derivation.metadata),
    )


def _fingerprint(derivation: IdentityDerivation, issued_at: float) -> str:
    payload = (
        f"{derivation.step_id}|{derivation.parent_agent_id}|"
        f"{sorted(derivation.requested_capabilities)}|"
        f"{sorted(derivation.requested_audiences)}|{int(issued_at)}"
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:24]


def subset_from(parent_caps: Iterable[str], picks: Iterable[str]) -> frozenset[str]:
    """Convenience helper for callers assembling narrow sets."""
    parent = frozenset(parent_caps)
    picked = frozenset(picks)
    extra = picked - parent
    if extra:
        raise CapabilityEscalation(f"picks outside parent: {sorted(extra)}")
    return picked
