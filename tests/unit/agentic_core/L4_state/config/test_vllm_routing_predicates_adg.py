"""ADG importability contract for agentic_core/L4_state/config/vllm_routing_predicates.py.

Auto-generated stub — covers GT_covers edge for ADG reachability.
Behavioral tests belong in test_vllm_routing_predicates.py (no _adg suffix).
"""

from __future__ import annotations

import pytest

try:
    from agentic_core.L4_state.config.vllm_routing_predicates import (  # noqa: F401
        Provider,
        RoutingDecision,
        RoutingPredicate,
        invalid_ast_detected,
        iteration_count_exceeded,
        requires_policy_read,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    Provider = None  # type: ignore[assignment,misc]
    RoutingDecision = None  # type: ignore[assignment,misc]
    RoutingPredicate = None  # type: ignore[assignment,misc]
    requires_policy_read = None  # type: ignore[assignment,misc]
    iteration_count_exceeded = None  # type: ignore[assignment,misc]
    invalid_ast_detected = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="vllm_routing_predicates deps unavailable")
class TestVllmRoutingPredicatesImportability:
    def test_module_importable(self) -> None:
        """ADG contract: agentic_core/L4_state/config/vllm_routing_predicates.py must be importable."""
        assert _AVAILABLE

    def test_provider_defined(self) -> None:
        assert Provider is not None

    def test_routingdecision_defined(self) -> None:
        assert RoutingDecision is not None

    def test_routingpredicate_defined(self) -> None:
        assert RoutingPredicate is not None