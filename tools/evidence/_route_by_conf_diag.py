"""Diagnose route_by_confidence and compute_routing_decision behavior."""


def test_route_by_confidence_routing_logic():
    from agentic_core.L2_execution.healers.healing_tier_router import route_by_confidence
    from agentic_core.L2_execution.healers.healing_tier_types import HealingTier

    # The bridge re-computes confidence via compute_heal_confidence
    # Test what tiers various confidence inputs produce
    for conf in [0.99, 0.95, 0.85, 0.81, 0.80, 0.79, 0.75, 0.65, 0.55, 0.51, 0.50, 0.45, 0.30, 0.10]:
        result = route_by_confidence(confidence=conf)
        print(f"  input_conf={conf:.2f}  heal_conf={result.heal_confidence:.4f}  tier={result.tier.value}")


def test_compute_routing_decision_return():
    from agentic_core.L0_routing.scripts._ssot_routing import compute_routing_decision
    from agentic_core.L0_routing.scripts._ssot_types import RoutingInputs
    import inspect

    # Check return type
    sig = inspect.signature(compute_routing_decision)
    print(f"\ncompute_routing_decision sig: {sig}")

    det_inputs = RoutingInputs(failure_type=None, retry_count=0, C=1, B=1, A=0, N=0, F=1, L=0)
    result = compute_routing_decision(det_inputs)
    print(f"Result type: {type(result)}")
    print(f"Result: {result}")
    if result is not None:
        print(f"Result attrs: {dir(result)}")
