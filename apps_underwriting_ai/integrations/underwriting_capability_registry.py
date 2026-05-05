"""Capability registry for apps_underwriting_ai.

Declares and resolves the apps_underwriting_ai.decision_packet_v1 capability
so that agentic_core owns route and capability resolution. This module is
the app-side delegation contract: agentic_core resolves the capability;
apps_underwriting_ai registers what it can serve.

Plan: apps-underwriting-ai-spine-hardening-d7f3b2 P0.2.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L0_routing.types.routing_artifact_types import L0Route

_CAPABILITY_ID = "apps_underwriting_ai.decision_packet_v1"
_L0_ROUTE = L0Route.R3R4_MANAGED
_ROUTE_FAMILY = "R3R4_MANAGED_WORKFLOW"
_EXECUTION_FORM = "MANAGED_WORKFLOW"

_registry: dict[str, dict[str, Any]] = {}


def register_decision_packet_capability() -> None:
    """Register the underwriting decision_packet_v1 capability.

    Declares the route family, execution form, and required spine contracts
    so agentic_core can resolve the capability at runtime without embedding
    underwriting-specific knowledge in the core runner.

    Must be called once at startup (import side-effect of apps_underwriting_ai.cert).
    """
    _registry[_CAPABILITY_ID] = {
        "capability_id": _CAPABILITY_ID,
        "l0_route": _L0_ROUTE.value,
        "route_family": _ROUTE_FAMILY,
        "execution_form": _EXECUTION_FORM,
        "l3_required": True,
        "c0_required": True,
        "c0_mode": "SUBMITTED_DOCUMENT_EVIDENCE_ONLY",
        "pa_required": "rationale_enrichment_enabled",
        "exit_mode": "FAIL_CLOSED",
        "durable_write_path": "UWG_ONLY",
        "data_mode": "SYNTHETIC_DEMO_ONLY",
        "selected_capability": _CAPABILITY_ID,
    }


def resolve_decision_packet_capability(
    capability_id: str = _CAPABILITY_ID,
) -> dict[str, Any] | None:
    """Resolve a registered underwriting capability by ID.

    Delegates capability lookup to the agentic_core registry contract.
    Returns None when the capability is not registered — callers must
    treat None as a fail-closed terminal (R5 fallback).

    Args:
        capability_id: The capability ID to resolve. Defaults to the
            canonical apps_underwriting_ai decision_packet_v1.

    Returns:
        Capability metadata dict or None if not registered.
    """
    return _registry.get(capability_id)


def list_registered_capabilities() -> list[str]:
    """Return all registered capability IDs."""
    return list(_registry.keys())
