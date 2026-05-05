"""apps_research capability registry — agentic_core delegation contract.

This module is the apps_research side of the core-owned route/capability
resolution contract. It registers the 'apps_research.company_brief_v1'
capability with the agentic_core runner and provides the resolution
delegate used by the R3_SIMPLE_GROUNDED_READ route.

Registration flow:
  1. bootstrap_capability() is called once during app startup (or lazily
     on first resolve_company_brief_capability() call).
  2. The registered handler wraps GovernedResearchRun, building a
     ResearchRequest from the argv list and delegating to the governed
     E2E runner.
  3. Capability unavailability raises CapabilityUnavailableError — the
     caller (__main__._run_canonical) routes this through Exit v6 with
     no generic brief fallback.

Plan: apps-research-spine-alignment-d4e8f2 W1.2.
"""
from __future__ import annotations

import logging
from typing import Any

_log = logging.getLogger("apps_research.capability_registry")

# ---------------------------------------------------------------------------
# Capability ID — must match route_registry.yaml selected_capability
# ---------------------------------------------------------------------------
CAPABILITY_ID = "apps_research.company_brief_v1"

# Route ID this capability serves
ROUTE_ID = "apps_research.company_brief_v1"

# Execution form declared in route_registry.yaml
EXECUTION_FORM = "SINGLE_STEP"

# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------


class CapabilityUnavailableError(RuntimeError):
    """Raised when the capability cannot be resolved.

    Must be caught by the agentic_core runner and routed through
    Exit v6 with reason_code=CAPABILITY_UNAVAILABLE — no generic brief fallback.
    """

    def __init__(self, capability_id: str, reason: str = "") -> None:
        self.capability_id = capability_id
        self.reason = reason
        super().__init__(
            f"Capability '{capability_id}' unavailable: {reason or 'not registered'}"
        )


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

_REGISTRY: dict[str, Any] = {}
_BOOTSTRAPPED: bool = False


def register_company_brief_capability(capability_id: str, handler: Any) -> None:
    """Register the company_brief capability handler.

    Called during app bootstrap. The handler must accept a list[str] argv
    and return an int exit code (0 = success).

    Args:
        capability_id: Must be CAPABILITY_ID ('apps_research.company_brief_v1').
        handler: Callable receiving (argv: list[str]) → int.
    """
    if capability_id != CAPABILITY_ID:
        raise ValueError(
            f"Unexpected capability_id '{capability_id}'. "
            f"apps_research only registers '{CAPABILITY_ID}'."
        )
    _REGISTRY[capability_id] = handler
    _log.debug(
        "[capability_registry] Registered capability '%s' route=%s form=%s",
        capability_id, ROUTE_ID, EXECUTION_FORM,
    )


def resolve_company_brief_capability(capability_id: str) -> Any:
    """Resolve the registered company_brief capability.

    Auto-bootstraps the default GovernedResearchRun-backed handler on
    first call if bootstrap_capability() has not been called explicitly.

    Args:
        capability_id: Must be CAPABILITY_ID.

    Returns:
        The registered handler callable.

    Raises:
        CapabilityUnavailableError: If bootstrap fails or the capability
            is not registered. The caller must route this through Exit v6 —
            no generic brief fallback.
    """
    global _BOOTSTRAPPED  # noqa: PLW0603
    if not _BOOTSTRAPPED:
        try:
            bootstrap_capability()
        except Exception as exc:  # guardian: allow-broad-exception -- bootstrap failure must surface as CapabilityUnavailableError so caller routes through Exit v6
            raise CapabilityUnavailableError(
                capability_id,
                reason=f"bootstrap failed: {type(exc).__name__}: {exc}",
            ) from exc
    if capability_id not in _REGISTRY:
        raise CapabilityUnavailableError(capability_id, reason="not registered after bootstrap")
    return _REGISTRY[capability_id]


def bootstrap_capability() -> None:
    """Bootstrap the default GovernedResearchRun-backed capability handler.

    Builds and registers a handler that:
    - Parses argv using an inline argparse parser (--topic, --mode, --depth)
    - Constructs a ResearchRequest from parsed args
    - Delegates to GovernedResearchRun.run_governed_e2e()
    - Returns 0 on success, 1 on any error

    The import of GovernedResearchRun is deferred to this function so that
    __main__.py imports only from this registry module (purity test 5).
    """
    global _BOOTSTRAPPED  # noqa: PLW0603

    def _company_brief_handler(argv: list[str]) -> int:
        """Governed company brief handler — wraps GovernedResearchRun."""
        import argparse  # noqa: PLC0415

        from apps_research.integrations.governed_research_run import (  # noqa: PLC0415
            GovernedResearchRun,
        )
        from apps_research.types.research_types import ResearchRequest  # noqa: PLC0415

        parser = argparse.ArgumentParser(prog="apps_research")
        parser.add_argument("--topic", required=True, help="Research topic")
        parser.add_argument("--mode", default="brief", help="Run mode (brief/deep)")
        parser.add_argument("--depth", default="standard", help="Depth profile")
        try:
            args = parser.parse_args(argv)
        except SystemExit:
            return 1

        request = ResearchRequest(
            topic=args.topic,
            mode=getattr(args, "mode", "brief"),
            depth_profile=getattr(args, "depth", "standard"),
            trace_id="",
        )

        runner = GovernedResearchRun()
        try:
            record = runner.run_governed_e2e(request)
            _log.info(
                "[apps_research] Governed run complete: run_id=%s disposition=%s error=%s",
                record.run_id,
                record.gate_disposition,
                record.error or "none",
            )
            return 0
        except Exception as exc:  # guardian: allow-broad-exception -- GovernedResearchRun raises heterogeneous errors; all logged, exit code = 1
            _log.error(
                "[apps_research] GovernedResearchRun raised %s: %s",
                type(exc).__name__, exc,
            )
            return 1

    register_company_brief_capability(CAPABILITY_ID, _company_brief_handler)
    _BOOTSTRAPPED = True
    _log.info(
        "[capability_registry] Bootstrapped '%s' with GovernedResearchRun handler",
        CAPABILITY_ID,
    )
