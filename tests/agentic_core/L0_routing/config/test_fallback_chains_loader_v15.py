"""v15 fallback chain loader tests."""
from __future__ import annotations

from agentic_core.L0_routing.config.fallback_chains_loader_v15 import (
    get_fallback_chain_v15,
    reset_cache,
)
from agentic_core.L0_routing.types.route_contract_v15 import RouteIdV15


def test_managed_workflow_chain_ends_r5() -> None:
    reset_cache()
    chain = get_fallback_chain_v15(RouteIdV15.R3R4_MANAGED_WORKFLOW)
    assert len(chain) >= 2
    assert chain[-1].route_id == RouteIdV15.R5_FALLBACK
    assert chain[0].route_id == RouteIdV15.R3_SIMPLE_GROUNDED_READ


def test_single_action_hitl_tier() -> None:
    reset_cache()
    chain = get_fallback_chain_v15(RouteIdV15.R4_SINGLE_ACTION)
    assert chain[0].route_id == RouteIdV15.R3R4_MANAGED_WORKFLOW
    assert chain[0].cost_tier.value == "TIER_HITL"
