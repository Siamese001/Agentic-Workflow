"""Tests for BaselineRegistry — G25 task-class baseline store."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L5_safety.runtime_gates.baseline_registry import (
    DEFAULT_ALPHA,
    Baseline,
    BaselineRegistry,
)


def test_first_sample_seeds_baseline() -> None:
    reg = BaselineRegistry()
    out = reg.update("summarize", {"tokens": 1000, "cost_usd": 0.05})
    assert out["tokens"] == 1000.0
    assert out["cost_usd"] == 0.05


def test_ema_update_blends_observation() -> None:
    reg = BaselineRegistry(alpha=0.5)
    reg.update("task", {"tokens": 1000})
    out = reg.update("task", {"tokens": 2000})
    # 0.5 * 2000 + 0.5 * 1000 = 1500
    assert out["tokens"] == pytest.approx(1500.0)


def test_ema_default_alpha_used() -> None:
    reg = BaselineRegistry()
    assert reg.alpha == DEFAULT_ALPHA


def test_invalid_alpha_rejected() -> None:
    with pytest.raises(ValueError):
        BaselineRegistry(alpha=0.0)
    with pytest.raises(ValueError):
        BaselineRegistry(alpha=1.5)


def test_get_returns_snapshot_copy() -> None:
    reg = BaselineRegistry()
    reg.update("task", {"tokens": 100})
    snap = reg.get("task")
    snap["tokens"] = 999
    assert reg.get("task")["tokens"] == 100.0


def test_has_and_all_classes() -> None:
    reg = BaselineRegistry()
    assert not reg.has("task")
    reg.update("task", {"tokens": 1})
    reg.update("other", {"tokens": 2})
    assert reg.has("task")
    assert reg.all_classes() == ["other", "task"]


def test_reset_removes_class() -> None:
    reg = BaselineRegistry()
    reg.update("task", {"tokens": 1})
    reg.reset("task")
    assert not reg.has("task")


def test_persistence_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "baselines.json"
    reg1 = BaselineRegistry(path=p)
    reg1.update("summarize", {"tokens": 1000, "cost_usd": 0.05})
    reg1.update("translate", {"tokens": 500, "latency_ms": 200})
    assert p.exists()
    payload = json.loads(p.read_text(encoding="utf-8"))
    assert "summarize" in payload
    assert "translate" in payload
    # Reload with a fresh instance.
    reg2 = BaselineRegistry(path=p)
    assert reg2.get("summarize")["tokens"] == 1000.0
    assert reg2.get("translate")["latency_ms"] == 200.0


def test_persistence_survives_reset(tmp_path: Path) -> None:
    p = tmp_path / "baselines.json"
    reg1 = BaselineRegistry(path=p)
    reg1.update("a", {"tokens": 1})
    reg1.update("b", {"tokens": 2})
    reg1.reset("a")
    reg2 = BaselineRegistry(path=p)
    assert not reg2.has("a")
    assert reg2.has("b")


def test_corrupt_json_tolerated(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not valid json", encoding="utf-8")
    reg = BaselineRegistry(path=p)
    # Should load empty, not raise.
    assert reg.all_classes() == []


def test_baseline_dict_roundtrip() -> None:
    b = Baseline(task_class="x", metrics={"tokens": 5.0}, sample_count=3)
    rebuilt = Baseline.from_dict(b.to_dict())
    assert rebuilt.task_class == "x"
    assert rebuilt.metrics == {"tokens": 5.0}
    assert rebuilt.sample_count == 3


def test_unknown_metric_ignored() -> None:
    reg = BaselineRegistry()
    out = reg.update("task", {"tokens": 100, "unknown_metric": 999})
    assert "unknown_metric" not in out
    assert out["tokens"] == 100.0


def test_integration_with_g25_anomaly_gate() -> None:
    """Wire BaselineRegistry → G25 RuntimeAnomalyGate."""
    from agentic_core.L5_safety.runtime_gates import GateContext, evaluate
    from agentic_core.L5_safety.runtime_gates.types import Disposition

    reg = BaselineRegistry()
    # Seed baseline with normal observations.
    for _ in range(3):
        reg.update("summarize", {"tokens": 1000, "cost_usd": 0.05})
    baseline = reg.get("summarize")
    # Severe anomaly: 5x tokens vs baseline.
    ctx = GateContext(
        baseline=baseline,
        observed={"tokens": 5000, "cost_usd": 0.05},
        impact_class="write",
    )
    decision = evaluate("G25", ctx)
    assert decision.disposition is Disposition.ESCALATE_HITL
    assert decision.stop_condition_violated
