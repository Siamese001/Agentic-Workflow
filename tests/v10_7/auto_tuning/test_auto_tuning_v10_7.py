import copy

import pytest

from core_v10_7 import ConfigV10_7, MetricsCollector, PolicyAutoTuner, TuningProfile


CONFIG_PATH = "master_config_v10_7.json"


def _enabled_config() -> ConfigV10_7:
    cfg = ConfigV10_7(CONFIG_PATH)
    cfg.auto_tuning_config.enabled = True
    return cfg


def _make_metrics(*entries):
    metrics = MetricsCollector()
    for entry in entries:
        metrics.metrics.append(entry)
    return metrics


def _drafting_metric(duration_ms: float, workflow_id: str = "wf-1"):
    return {
        "agent_name": "DraftingStrategistTool",
        "task_name": "tool_drafting_llm",
        "duration_ms": duration_ms,
        "success": True,
        "metadata": {"workflow_id": workflow_id},
    }


def _rag_metric(duration_ms: float, workflow_id: str = "wf-1"):
    return {
        "agent_name": "RAG_SearchAgent",
        "task_name": "run_agentic_rag",
        "duration_ms": duration_ms,
        "success": True,
        "metadata": {"workflow_id": workflow_id},
    }


def _drafting_signal_metric(stage: str):
    return {
        "agent_name": "ArbitrationEngine",
        "task_name": "run_check",
        "duration_ms": 5,
        "success": True,
        "metadata": {"stage": stage, "workflow_id": "wf-2"},
    }


def test_auto_tuning_disabled_no_change():
    cfg = ConfigV10_7(CONFIG_PATH)
    metrics = _make_metrics(_drafting_metric(2500))
    tuner = PolicyAutoTuner(cfg, metrics)
    profile = TuningProfile()
    before = copy.deepcopy(profile.model_dump())

    updated = tuner.tune_profile(profile)

    assert updated.temperature == before["temperature"]
    assert updated.history == []
    assert updated.drafting_expand_summary == before["drafting_expand_summary"]


def test_temperature_adjusts_with_latency():
    cfg = _enabled_config()
    metrics = _make_metrics(_drafting_metric(4000))
    tuner = PolicyAutoTuner(cfg, metrics)
    profile = TuningProfile(temperature=0.5)
    original_prune = profile.prune_factor

    updated = tuner.tune_profile(profile)

    assert pytest.approx(updated.temperature) == 0.45
    assert updated.prune_factor == original_prune


def test_rag_force_multi_tool_engages():
    cfg = _enabled_config()
    metrics = _make_metrics(
        _drafting_metric(2000),
        _rag_metric(cfg.auto_tuning_config.latency_target_ms * 1.2),
    )
    tuner = PolicyAutoTuner(cfg, metrics)
    profile = TuningProfile()

    updated = tuner.tune_profile(profile)

    assert updated.rag_force_multi_tool is True


def test_drafting_overrides_trigger():
    cfg = _enabled_config()
    metrics = _make_metrics(
        _drafting_metric(2000),
        _drafting_signal_metric("draft_post_assembly"),
    )
    tuner = PolicyAutoTuner(cfg, metrics)
    profile = TuningProfile()

    updated = tuner.tune_profile(profile)

    assert updated.drafting_expand_summary is True
    assert updated.drafting_boost_metrics is True


def test_profile_history_populates():
    cfg = _enabled_config()
    metrics = _make_metrics(_drafting_metric(2000))
    tuner = PolicyAutoTuner(cfg, metrics)
    profile = TuningProfile()

    updated = tuner.tune_profile(profile)

    assert len(updated.history) == 1
    record = updated.history[0]
    assert "timestamp" in record
    assert record["temperature"] == updated.temperature
    assert updated.last_update >= record["timestamp"]
