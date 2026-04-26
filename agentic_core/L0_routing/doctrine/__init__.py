"""L0 Routing Doctrine — formal contract types per docs/reference/03_L0_Routing/03.x.

This sub-package realizes the named-contract surface from the doctrine without
disturbing the existing v15 wiring (``agentic_core/L0_routing/types/route_contract_v15.py``,
``agentic_core/L0_routing/reasoning/v15_route_selector.py``).

It is **additive**:

- ``contracts_l0_1`` — 03.1 Route Input + Preflight inputs/outputs
- ``preflight`` — 03.1 ``run_l0_preflight()`` pipeline
- ``contracts_l0_2`` — 03.2 RouteScoreVector / FixedDecisionOrderReceipt / RouteSelectionReceipt
- ``selector`` — 03.2 ``select_route()`` deterministic dispatcher
- ``terminal_routes`` — 03.3 R1A/R1B/R5 + HITL posture
- ``handoffs`` — 03.4 R3/R4/R3R4 single-step handoffs
- ``telemetry`` — 03.5 RouteTelemetryEvent
- ``replay`` — 03.5 RouteReplayManifest

Constitutional compliance:

- Frozen dataclasses, no mutation.
- Specific exception types (``DoctrineContractError``).
- Closed-vocabulary Enums for every taxonomic field.
- No PowerShell, no ``except Exception``, no I/O.
- Pure data + pure functions.
"""

from __future__ import annotations


class DoctrineContractError(ValueError):
    """Raised when an L0 doctrine contract violates an invariant.

    Specific subclass of ``ValueError`` so callers can either catch this exact
    type or fall through to ``ValueError``. Per constitutional §15, callers
    MUST NOT catch bare ``Exception``.
    """


__all__ = ["DoctrineContractError"]
