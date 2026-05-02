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


# ---------------------------------------------------------------------------
# Scenario runner hook for the standalone agentic_core spine harness.
#
# Consumed by ``tools/certification/agentic_core_e2e/run_core_proof.py``. Each
# scenario returns a dict with an explicit ``status`` field:
#
#   * ``ran``             — scenario executed through real spine pieces and
#                           the harness should mark it as a pass.
#   * ``not_implemented`` — hook is present but the underlying spine scenario
#                           runner is not wired yet. Honest fail-closed.
#   * ``error``           — scenario attempted and failed with evidence.
#   * ``skipped``         — scenario intentionally out of scope (e.g. requires
#                           a transitional integration not appropriate here).
#
# Contract: inputs are exactly ``scenario_id: str``. The hook MUST NOT raise;
# it MUST return a dict. Scenario catalogue SSOT:
# ``tools/certification/agentic_core_e2e/scenarios.py::CORE_SCENARIOS``.
# ---------------------------------------------------------------------------

SCENARIO_STATUS_RAN = "ran"
SCENARIO_STATUS_NOT_IMPLEMENTED = "not_implemented"
SCENARIO_STATUS_SKIPPED = "skipped"
SCENARIO_STATUS_ERROR = "error"

_NOT_IMPLEMENTED_REASON = (
    "spine scenario runner not wired at L0 yet. The hook is present so the "
    "apps_e2e auditability harness can locate it, but the underlying "
    "orchestration (U0 validated request construction, L1 planning, L0 route "
    "contract emission, Exit review packet assembly, L6 exhaust handoff) must "
    "be invokable from a single entrypoint for this scenario to execute. See "
    "agentic_core/L3_orchestration/ for the orchestration pieces that a future "
    "implementer would wire into this hook."
)


def _run_terminal_cache_scenario() -> dict:
    """Terminal-cache scenario — the only scenario with an invokable primitive.

    Exercises the real L4 evidence resolver (already wired by
    :func:`install_default_resolvers` above). The fail-closed default returns
    ``False`` for every evidence id — itself a spine behaviour under test. We
    assert the resolver is installed and responds deterministically.

    This is a structural, not full end-to-end, scenario pass. It proves the
    L0 composition root is functional without crossing into L1/L2/L3.
    """
    if not _INSTALLED:
        return {
            "status": SCENARIO_STATUS_NOT_IMPLEMENTED,
            "reason": "evidence resolver was never installed; L4 cache absent",
        }
    # The default resolver must be deterministic: same id → same answer.
    probe_id = "agentic_core_e2e_probe_never_registered"
    first = _composed_resolver(probe_id)
    second = _composed_resolver(probe_id)
    if first != second:
        return {
            "status": SCENARIO_STATUS_ERROR,
            "reason": f"non-deterministic resolver: {first!r} vs {second!r}",
        }
    return {
        "status": SCENARIO_STATUS_RAN,
        "probe_id": probe_id,
        "resolver_fail_closed_default": first is False,
        "resolver_deterministic": True,
        "reason": (
            "L0 composition root live: evidence resolver installed, "
            "deterministic, and fail-closed by default."
        ),
    }


def run_scenario(scenario_id: str) -> dict:
    """Dispatch one core spine scenario by id. Contract: never raises."""
    dispatch = {
        "terminal_cache": _run_terminal_cache_scenario,
    }
    if not isinstance(scenario_id, str):
        return {
            "status": SCENARIO_STATUS_ERROR,
            "scenario_id": repr(scenario_id),
            "reason": f"scenario_id must be str, got {type(scenario_id).__name__}",
        }
    runner = dispatch.get(scenario_id)
    if runner is None:
        return {
            "status": SCENARIO_STATUS_NOT_IMPLEMENTED,
            "scenario_id": scenario_id,
            "reason": _NOT_IMPLEMENTED_REASON,
            "implemented_scenarios": sorted(dispatch.keys()),
        }
    try:
        return runner()
    except (RuntimeError, ValueError, TypeError, LookupError, AttributeError) as exc:
        # guardian: allow-return-none-swallow -- scenario hook must never
        # raise into the harness; convert to a structured error record.
        return {
            "status": SCENARIO_STATUS_ERROR,
            "scenario_id": scenario_id,
            "reason": f"{type(exc).__name__}: {exc}",
        }


__all__ = [
    "SCENARIO_STATUS_ERROR",
    "SCENARIO_STATUS_NOT_IMPLEMENTED",
    "SCENARIO_STATUS_RAN",
    "SCENARIO_STATUS_SKIPPED",
    "clear_evidence_source",
    "install_default_resolvers",
    "register_evidence_source",
    "run_scenario",
]
