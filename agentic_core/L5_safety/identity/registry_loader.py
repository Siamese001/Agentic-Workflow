"""Registry Loader + Cache — L5 v4 Wave-I.

Process-local singleton for the active 4-registry `RegistrySnapshot`.
Token issuance and exit-control verification both need to bind against
the SAME snapshot for a given run; this loader provides a deterministic
access point that:

- Loads a snapshot from an in-memory spec (today) or JSON on disk (future)
- Caches the snapshot per-process so the digest is stable within a run
- Exposes `get_active_registry_snapshot()` for token issuance + verifier
- Lets tests/tooling swap in a fresh snapshot via `set_active_registry_snapshot`

Adoption path:

    # v3: registries loaded ad-hoc via various modules in L5_safety/config/
    # v4: one import; one call
    from agentic_core.L5_safety.identity.registry_loader import (
        get_active_registry_snapshot,
    )
    snap = get_active_registry_snapshot()  # deterministic per-process
    # token issuance: token.registry_digest = snap.registry_digest
    # verifier:       verify_token_against_registry(token.registry_digest, snap)

Rationale: Wave-C `build_registry_snapshot` is a pure factory; production
call sites need a cache-backed accessor that composes with the front-door
resolver pattern (Wave-W1). This loader provides the compose point.

Reference:
  - agentic_core/L5_safety/identity/registries.py (Wave-C)
  - agentic_core/L5_safety/identity/front_door_resolver.py (Wave-W1 — same pattern)
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

import threading

from agentic_core.L5_safety.identity.registries import (
    AgentRegistryEntry,
    MCPConnectorRegistryEntry,
    PromptRegistryEntry,
    PromptRole,
    RegistrySnapshot,
    ToolKind,
    ToolRegistryEntry,
    build_registry_snapshot,
)

# Default policy version pinned alongside the empty bootstrap snapshot
_BOOTSTRAP_POLICY_VERSION = "v4.0.0-bootstrap"

_lock = threading.Lock()
_active_snapshot: RegistrySnapshot | None = None


def _build_bootstrap_snapshot() -> RegistrySnapshot:
    """Build the minimum-viable bootstrap snapshot.

    Starts with an empty ledger. Production systems replace this with
    a loaded snapshot before any v4 token is issued.
    """
    return build_registry_snapshot(policy_version=_BOOTSTRAP_POLICY_VERSION)


def get_active_registry_snapshot() -> RegistrySnapshot:
    """Return the process-local active RegistrySnapshot.

    Thread-safe, memoized. Lazily builds the bootstrap snapshot on first call.
    """
    global _active_snapshot  # noqa: PLW0603
    if _active_snapshot is not None:
        return _active_snapshot
    with _lock:
        if _active_snapshot is None:
            _active_snapshot = _build_bootstrap_snapshot()
    return _active_snapshot


def set_active_registry_snapshot(snapshot: RegistrySnapshot) -> None:
    """Replace the active snapshot (for tests, tooling, policy bumps).

    In production, only the policy-promotion path should call this, and
    ONLY after `decide_policy_promotion` green-lights the new version.
    """
    global _active_snapshot  # noqa: PLW0603
    with _lock:
        _active_snapshot = snapshot


def clear_active_snapshot() -> None:
    """Reset the cache (tests only)."""
    global _active_snapshot  # noqa: PLW0603
    with _lock:
        _active_snapshot = None


__all__ = [
    "AgentRegistryEntry",
    "MCPConnectorRegistryEntry",
    "PromptRegistryEntry",
    "PromptRole",
    "ToolKind",
    "ToolRegistryEntry",
    "build_registry_snapshot",
    "clear_active_snapshot",
    "get_active_registry_snapshot",
    "set_active_registry_snapshot",
]
