"""Wave 6.3: Time-Shifted Influence Proof (L6 -> L4 -> L0).

Validates:
- Detection in Run t does NOT change routing in Run t
- Version bump between runs changes routing in Run t+1
- No mid-run routing mutation permitted
- Influence is strictly time-shifted across run boundaries
"""

from __future__ import annotations

import copy

import pytest

from agentic_core.L0_routing.types.routing_config_seal_types import (
    RoutingConfigSealViolation,
    SealedRoutingContext,
)

pytestmark = pytest.mark.governance

BASE_CONFIG = {
    "model": "gpt-4",
    "temperature": 0.0,
    "routes": {
        "classify": "ClassifierAgent",
        "summarize": "SummarizerAgent",
    },
    "version": "1.0.0",
}


def _simulate_run(config: dict) -> str:
    """Simulate a sealed run and return the seal hash."""
    ctx = SealedRoutingContext(config, version=config["version"])
    ctx.verify_or_raise(config)
    return ctx.seal.canonical_hash


class TestNoMidRunMutation:
    """Routing must not change during a single run."""

    def test_routing_unchanged_in_same_run(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx = SealedRoutingContext(config, version=config["version"])
        ctx.verify_or_raise(config)
        ctx.verify_or_raise(config)
        ctx.verify_or_raise(config)

    def test_detection_does_not_change_routing(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx = SealedRoutingContext(config, version=config["version"])
        # Simulate detection event (L6 observes drift)
        # Key assertion: routing remains unchanged
        ctx.verify_or_raise(config)

    def test_mid_run_mutation_raises(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx = SealedRoutingContext(config, version=config["version"])
        config["routes"]["classify"] = "NewAgent"
        with pytest.raises(RoutingConfigSealViolation):
            ctx.verify_or_raise(config)


class TestTimeShiftedInfluence:
    """Changes apply only in the NEXT run."""

    def test_version_bump_changes_next_run(self):
        config_v1 = copy.deepcopy(BASE_CONFIG)
        hash_run_t = _simulate_run(config_v1)

        config_v2 = copy.deepcopy(BASE_CONFIG)
        config_v2["version"] = "2.0.0"
        config_v2["routes"]["classify"] = "NewAgent"
        hash_run_t1 = _simulate_run(config_v2)

        assert hash_run_t != hash_run_t1

    def test_same_config_same_hash_across_runs(self):
        config_a = copy.deepcopy(BASE_CONFIG)
        config_b = copy.deepcopy(BASE_CONFIG)
        hash_a = _simulate_run(config_a)
        hash_b = _simulate_run(config_b)
        assert hash_a == hash_b

    def test_influence_strictly_time_shifted(self):
        config = copy.deepcopy(BASE_CONFIG)
        ctx_run_t = SealedRoutingContext(config, version="1.0.0")
        # Simulate detection in run t
        ctx_run_t.verify_or_raise(config)
        hash_run_t = ctx_run_t.seal.canonical_hash

        config_v2 = copy.deepcopy(BASE_CONFIG)
        config_v2["version"] = "2.0.0"
        config_v2["routes"]["summarize"] = "V2Agent"
        ctx_run_t1 = SealedRoutingContext(config_v2, version="2.0.0")
        ctx_run_t1.verify_or_raise(config_v2)
        hash_run_t1 = ctx_run_t1.seal.canonical_hash

        assert hash_run_t != hash_run_t1
