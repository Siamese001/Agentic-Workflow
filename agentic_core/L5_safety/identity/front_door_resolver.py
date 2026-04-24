"""Front-Door Principal Resolver — L5 v4 G2 entry (G-04, W1 P1.2).

Resolves the invoking principal at the front door of the governance plane.
In single-operator mode, this reads OS-level environment variables
(USER / USERNAME) and classifies the invocation as HUMAN, AUTOMATION,
or SYSTEM based on well-known CI / automation markers.

Ratified decision (ADR-049 §7.3): full principal_chain from day one,
env-seeded invoking_user. Multi-user rollout later = swap the resolver
source (e.g., to authenticated session lookup) without touching any
downstream consumer of PrincipalChain.

Reference: docs/contracts/identity_propagation.md §3.1
Parent plan: .windsurf/plans/l5-v4-g04-identity-propagation-0b9d22.md
"""
from __future__ import annotations

import os
import threading

from agentic_core.interfaces.principal_chain_types import (
    InvokingUserKind,
    PrincipalChain,
)

FRONT_DOOR_AUTOMATION_ENV_VARS: tuple[str, ...] = (
    "CI",
    "AUTOMATION",
    "GITHUB_ACTIONS",
    "GITLAB_CI",
    "BUILDKITE",
    "JENKINS_URL",
    "CIRCLECI",
)
"""Environment variables whose truthy presence indicates automation context."""

FRONT_DOOR_AGENT_ID_ENV_VAR = "AGENTIC_FRONT_DOOR_AGENT_ID"
FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR = "AGENTIC_INVOKING_USER"
FRONT_DOOR_SCOPE_TAG_ENV_VAR = "AGENTIC_FRONT_DOOR_SCOPE_TAG"

DEFAULT_FRONT_DOOR_AGENT_ID = "front_door"
UNKNOWN_OPERATOR_SENTINEL = "unknown_local_operator"
AUTOMATION_PRINCIPAL_SENTINEL = "automation_principal"

_cache_lock = threading.Lock()
_cached_chain: PrincipalChain | None = None


def _is_automation_context() -> bool:
    """Return True when any well-known automation env var is truthy."""
    for var in FRONT_DOOR_AUTOMATION_ENV_VARS:
        raw = os.environ.get(var, "")
        if raw and raw.lower() not in {"", "0", "false", "no"}:
            return True
    return False


def _resolve_invoking_user(is_automation: bool) -> str:
    """Pick the principal identifier from the environment.

    Precedence:
      1. `AGENTIC_INVOKING_USER` override (explicit single-operator seed)
      2. `USER` (POSIX) / `USERNAME` (Windows)
      3. automation sentinel (CI) or unknown-operator sentinel (human)
    """
    override = os.environ.get(FRONT_DOOR_INVOKING_USER_OVERRIDE_ENV_VAR, "").strip()
    if override:
        return override
    # POSIX first, then Windows — both can be set; prefer the primary.
    for var in ("USER", "USERNAME", "LOGNAME"):
        val = os.environ.get(var, "").strip()
        if val:
            return val
    return AUTOMATION_PRINCIPAL_SENTINEL if is_automation else UNKNOWN_OPERATOR_SENTINEL


def _resolve_scope_tag() -> str:
    """Pick the scope compartment tag.

    Precedence:
      1. `AGENTIC_FRONT_DOOR_SCOPE_TAG` explicit override
      2. Deterministic per-process tag `session:<hex(pid)>`
    """
    explicit = os.environ.get(FRONT_DOOR_SCOPE_TAG_ENV_VAR, "").strip()
    if explicit:
        return explicit
    return f"session:{format(os.getpid(), 'x')}"


def _resolve_agent_id() -> str:
    """Pick the front-door agent id.

    Precedence:
      1. `AGENTIC_FRONT_DOOR_AGENT_ID` explicit override
      2. DEFAULT_FRONT_DOOR_AGENT_ID sentinel
    """
    explicit = os.environ.get(FRONT_DOOR_AGENT_ID_ENV_VAR, "").strip()
    return explicit or DEFAULT_FRONT_DOOR_AGENT_ID


def resolve_front_door_principal(*, refresh: bool = False) -> PrincipalChain:
    """Resolve and memoize the front-door principal chain for this process.

    Thread-safe: the first caller wins the race to populate the cache;
    subsequent callers receive the same chain object.

    Args:
        refresh: When True, bypass the cache and re-resolve from environment.
            Primarily useful in tests that mutate os.environ.

    Returns:
        An immutable PrincipalChain at delegation_depth=0 representing the
        front-door invocation. Safe to use directly as the seed for every
        L5 v4 capability_token issued in this process.
    """
    global _cached_chain
    if not refresh:
        cached = _cached_chain
        if cached is not None:
            return cached

    with _cache_lock:
        if not refresh and _cached_chain is not None:
            return _cached_chain

        is_automation = _is_automation_context()
        invoking_user = _resolve_invoking_user(is_automation)
        user_kind = (
            InvokingUserKind.AUTOMATION
            if is_automation
            else InvokingUserKind.HUMAN
        )
        # Explicit sentinel: no USER/USERNAME AND no CI markers ⇒ SYSTEM
        if (
            not is_automation
            and invoking_user == UNKNOWN_OPERATOR_SENTINEL
        ):
            user_kind = InvokingUserKind.SYSTEM

        auth_method = (
            "env:automation"
            if is_automation
            else "env:local_operator"
        )

        chain = PrincipalChain(
            invoking_user=invoking_user,
            invoking_user_kind=user_kind,
            auth_method=auth_method,
            agent_id=_resolve_agent_id(),
            scope_tag=_resolve_scope_tag(),
            parent_agent_id=None,
            handoff_history=(),
            scopes=(),
        )
        _cached_chain = chain
        return chain


def clear_resolver_cache() -> None:
    """Reset the resolver cache. Test-only; not part of production flow."""
    global _cached_chain
    with _cache_lock:
        _cached_chain = None
