import pytest

from auto_tuner_stub import PolicyAutoTunerStub
from l3_graph_orchestrator import GraphOrchestrator
from predictive_cache import PredictiveCache


def test_predictive_cache_set_get_deterministic():
    cache = PredictiveCache()
    cache.set("alpha", {"value": 1})

    assert cache.get("alpha") == {"value": 1}
    assert cache.get("missing") is None


def test_predictive_cache_snapshot_is_copy():
    cache = PredictiveCache()
    cache.set("beta", {"count": 2})

    snapshot = cache.snapshot()
    snapshot["beta"] = {"count": 3}
    snapshot["gamma"] = {"count": 4}

    assert cache.get("beta") == {"count": 2}
    assert "gamma" not in cache.cache


def test_policy_auto_tuner_stub_suggests_deterministically():
    tuner = PolicyAutoTunerStub()
    suggestion = tuner.suggest_config(state={}, metrics={})

    assert suggestion == {
        "temperature": 0.3,
        "max_tokens": 500,
        "routing_adjustment": "none",
    }


def test_graph_orchestrator_exposes_predictive_cache_and_tuning_metadata():
    orchestrator = GraphOrchestrator()
    result = orchestrator.orchestrate()
    final_state = result.state

    assert final_state.get("predictive_cache") == {"snapshot": {}}
    assert final_state.get("tuning", {}).get("suggestion") == {
        "temperature": 0.3,
        "max_tokens": 500,
    }
