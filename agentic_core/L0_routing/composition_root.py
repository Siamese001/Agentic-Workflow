"""L0 composition root for cache-side dependency injection.

This module wires process-wide pluggable resolvers that the L4 semantic
cache depends on. It exists in L0 (routing) because L0 is the highest
layer in gravity order that owns app-level composition decisions and
imports the cache module via :mod:`agentic_core.L0_routing.reasoning.route_gates`.

Currently wires:

* G2 evidence resolver — backs
  :func:`agentic_core.L4_state.utils.memory.semantic_cache_manager.set_evidence_resolver`
  used by the support-manifest reuse validator. Default behavior is
  **fail-closed**: when no real resolver is registered, every evidence id is
  treated as **unresolved** so the validator rejects cache reuse rather than
  serving potentially stale grounding evidence.

Downstream apps register their real evidence store via
:func:`register_evidence_source`. The wiring runs at module import time
through :func:`install_default_resolvers` so it is sufficient to import this
module once during L0 boot — typically from
``agentic_core/L0_routing/reasoning/route_gates.py``.

Feature flag ``SEMANTIC_CACHE_FAIL_OPEN_RESOLVER=1`` reverts to the legacy
fail-open default (every id resolvable). Operators only flip this during a
controlled rollback if a regression is observed.
"""

from __future__ import annotations

import logging
import os
from typing import Callable

Logger = logging.getLogger(__name__)

_EvidenceResolver = Callable[[str], bool]

# Module-private registry. ``None`` means "no app has registered a real
# resolver yet"; the active resolver dispatches accordingly.
_REGISTERED_RESOLVER: _EvidenceResolver | None = None
_INSTALLED: bool = False


def _fail_closed_resolver(evidence_id: str) -> bool:
    """Default: refuse to validate any evidence id.

    Returning ``False`` causes the L4 support-manifest validator to mark the
    cached row as unresolved and reject reuse. This is the safe default when
    no real evidence store is wired.
    """
    del evidence_id
    return False


def _fail_open_resolver(evidence_id: str) -> bool:
    """Legacy: treat every evidence id as resolvable. Rollback only."""
    del evidence_id
    return True


def _composed_resolver(evidence_id: str) -> bool:
    """Active resolver: delegate to registered impl, else fail-closed/open."""
    if _REGISTERED_RESOLVER is not None:
        try:
            return bool(_REGISTERED_RESOLVER(evidence_id))
        except (LookupError, ValueError, RuntimeError, TypeError) as exc:
            # guardian: allow-log-and-swallow -- resolver failure must not
            # crash the cache; treat as unresolved (fail-closed).
            Logger.debug(
                "composition_root: registered resolver raised for %r: %s",
                evidence_id,
                exc,
            )
            return False
    if os.getenv("SEMANTIC_CACHE_FAIL_OPEN_RESOLVER", "0") == "1":
        return _fail_open_resolver(evidence_id)
    return _fail_closed_resolver(evidence_id)


def register_evidence_source(resolver: _EvidenceResolver) -> None:
    """Install the app-supplied resolver. Last writer wins; idempotent.

    Apps wire their real evidence store (UWG row check, ledger lookup, etc.)
    by passing a callable ``(evidence_id: str) -> bool``. The callable should
    return ``True`` iff the evidence is still valid grounding for cache reuse.
    """
    global _REGISTERED_RESOLVER  # noqa: PLW0603
    _REGISTERED_RESOLVER = resolver
    Logger.info(
        "composition_root: evidence resolver registered (callable=%r)",
        getattr(resolver, "__qualname__", repr(resolver)),
    )


def clear_evidence_source() -> None:
    """Drop the registered resolver. Subsequent calls revert to default.

    Test-only helper. Production code should not call this.
    """
    global _REGISTERED_RESOLVER  # noqa: PLW0603
    _REGISTERED_RESOLVER = None


def install_default_resolvers() -> None:
    """Wire :func:`_composed_resolver` into the L4 cache. Idempotent."""
    global _INSTALLED  # noqa: PLW0603
    if _INSTALLED:
        return
    try:
        from agentic_core.L4_state.utils.memory.semantic_cache_manager import (  # noqa: PLC0415
            set_evidence_resolver,
        )
    except ImportError as exc:  # guardian: allow-return-none-swallow -- L4 cache is optional at L0 boot; if it cannot be imported, route_gates already handles cache absence and None signals the missing resolver to the caller
        Logger.debug("composition_root: L4 cache import failed: %s", exc)
        return
    set_evidence_resolver(_composed_resolver)
    _INSTALLED = True
    Logger.info("composition_root: evidence resolver wired (fail-closed default)")


# Auto-install on import so a single ``import agentic_core.L0_routing.composition_root``
# anywhere in the L0 boot path is sufficient.
install_default_resolvers()


__all__ = [
    "clear_evidence_source",
    "install_default_resolvers",
    "register_evidence_source",
]
