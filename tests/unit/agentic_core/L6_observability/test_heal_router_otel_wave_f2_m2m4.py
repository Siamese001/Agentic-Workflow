"""Wave F2 M2-M4 tests — unified heal_router.v1 wire-up, alias feeders, DDL.

Covers:
  - M2 root-span hook: HealingRouter.route() emits a RoutingSpanRecord via
    the default emitter and the record carries all required attributes.
  - M2 alias feeder: QwenInferenceTelemetry.record_metric() dual-emits a
    synthetic dispatch.qwen record via append_alias_record.
  - M3 DDL: ensure_schema creates the routing_decision_events table with
    indexes; insert_record round-trips a RoutingSpanRecord.
  - M4 deprecation: importing the qwen telemetry module and heal_classifier
    model emits DeprecationWarning.
"""

from __future__ import annotations

import importlib
import sqlite3
import sys
import time
import warnings


def _fresh_emitter():
    """Import and reset the module-level default emitter for test isolation."""
    from agentic_core.L6_observability import heal_router_otel as hro  # noqa: PLC0415

    hro._default_emitter = None  # noqa: SLF001  — test-only singleton reset
    emitter = hro.get_default_emitter()
    emitter.clear()
    return emitter


# ---------------------------------------------------------------------------
# M2: HealingRouter.route() wire-up
# ---------------------------------------------------------------------------


def test_m2_healing_router_emits_root_span() -> None:
    from agentic_core.L2_execution.healers.confidence_scorer import (  # noqa: PLC0415
        ConfidenceScore,
        HealTier,
    )
    from agentic_core.L2_execution.healers.failure_signal import FailureSignal  # noqa: PLC0415
    from agentic_core.L2_execution.healers.healing_router import HealingRouter  # noqa: PLC0415

    emitter = _fresh_emitter()

    router = HealingRouter()
    score = ConfidenceScore(score=0.42, tier=HealTier.LOW, confidence_in_score=0.8, reasoning="test")
    signal = FailureSignal(
        check_id="t1",
        retry_count=0,
        error_code="E_TEST",
        error_message="",
        lineage_hash="h",
        context_snapshot={},
        source_layer="L2_execution",
        operation="heal",
        timestamp=time.time(),
    )

    decision = router.route(score, signal, context=None)

    records = emitter.recent(limit=10)
    assert records, "route() did not emit a span"
    rec = records[-1]
    assert rec.target_model == decision.target_model
    assert rec.tier == decision.tier.name
    assert rec.gate_applied == decision.gate_applied
    assert rec.gemini_subtier == decision.gemini_subtier
    assert rec.cost_demoted == decision.cost_demoted
    assert rec.app_name == "healing_router"
    assert rec.confidence_score == 0.42


def test_m2_emission_never_raises_when_emitter_broken(monkeypatch) -> None:
    """Best-effort contract: route() must return decision even if emit fails."""
    from agentic_core.L2_execution.healers.confidence_scorer import (  # noqa: PLC0415
        ConfidenceScore,
        HealTier,
    )
    from agentic_core.L2_execution.healers.failure_signal import FailureSignal  # noqa: PLC0415
    from agentic_core.L2_execution.healers import healing_router as hr_mod  # noqa: PLC0415

    def boom() -> None:
        raise RuntimeError("simulated OTEL failure")

    monkeypatch.setattr(hr_mod, "_get_default_heal_router_emitter", boom)

    router = hr_mod.HealingRouter()
    score = ConfidenceScore(score=0.9, tier=HealTier.HIGH, confidence_in_score=0.9, reasoning="hi")
    signal = FailureSignal(
        check_id="t1",
        retry_count=0,
        error_code="E",
        error_message="",
        lineage_hash="h",
        context_snapshot={},
        source_layer="L2_execution",
        operation="heal",
        timestamp=time.time(),
    )

    decision = router.route(score, signal)
    assert decision.tier == HealTier.HIGH  # route still returned


# ---------------------------------------------------------------------------
# M2 alias feeder: QwenInferenceTelemetry.record_metric
# ---------------------------------------------------------------------------


def test_m2_qwen_record_metric_aliases_into_heal_router() -> None:
    emitter = _fresh_emitter()

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        from agentic_core.L3_orchestration.inference.qwen_vllm.telemetry import (  # noqa: PLC0415
            QwenInferenceMetric,
            QwenInferenceTelemetry,
        )

    tele = QwenInferenceTelemetry()
    sid = tele.start_session("app-under-test")
    metric = QwenInferenceMetric(
        timestamp=123.0,
        app_name="app-under-test",
        model_id="qwen-stub",
        metric_name="latency_ms",
        value=42.0,
    )
    tele.record_metric(sid, metric)

    records = emitter.recent(limit=10)
    aliased = [
        r for r in records if r.extra_attributes.get("routing.alias_source") == "qwen_inference_telemetry"
    ]
    assert aliased, "QwenInferenceTelemetry did not dual-emit into heal_router"
    assert aliased[-1].target_model == "qwen-stub"
    assert aliased[-1].gate_applied == "DISPATCH_ALIAS"
    assert aliased[-1].tier == "MEDIUM"


# ---------------------------------------------------------------------------
# M3: routing_decision_events DDL
# ---------------------------------------------------------------------------


def test_m3_ensure_schema_is_idempotent() -> None:
    from agentic_core.L6_observability.routing_decision_events_schema import (  # noqa: PLC0415
        ensure_schema,
    )

    conn = sqlite3.connect(":memory:")
    ensure_schema(conn)
    ensure_schema(conn)  # idempotent second call

    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='routing_decision_events'")
    assert cur.fetchone() is not None
    cur.execute("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_routing_gate'")
    assert cur.fetchone() is not None
    conn.close()


def test_m3_insert_record_round_trip() -> None:
    from agentic_core.L6_observability.heal_router_otel import RoutingSpanRecord  # noqa: PLC0415
    from agentic_core.L6_observability.routing_decision_events_schema import (  # noqa: PLC0415
        ensure_schema,
        insert_record,
    )

    conn = sqlite3.connect(":memory:")
    ensure_schema(conn)

    rec = RoutingSpanRecord(
        routing_trace_id="t-1",
        timestamp=100.0,
        app_name="demo",
        tier="LOW",
        gate_applied="NO_OVERRIDE",
        gemini_subtier="FLASH",
        cost_demoted=True,
        target_model="gemini-flash",
        confidence_score=0.33,
        cost_usd=0.02,
        cost_budget_remaining_usd=0.5,
        latency_ms=12,
        outcome_success=True,
        dry_plan=False,
        error_code=None,
        extra_attributes={"routing.alias_source": "qwen_inference_telemetry"},
    )
    insert_record(conn, rec)

    cur = conn.cursor()
    cur.execute(
        "SELECT tier, gemini_subtier, cost_demoted, target_model, alias_source "
        "FROM routing_decision_events WHERE routing_trace_id='t-1'"
    )
    row = cur.fetchone()
    assert row == ("LOW", "FLASH", 1, "gemini-flash", "qwen_inference_telemetry")
    conn.close()


# ---------------------------------------------------------------------------
# M4: DeprecationWarning on legacy feeders
# ---------------------------------------------------------------------------


def test_m4_qwen_telemetry_emits_deprecation_warning() -> None:
    mod = "agentic_core.L3_orchestration.inference.qwen_vllm.telemetry"
    sys.modules.pop(mod, None)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        importlib.import_module(mod)
    assert any(
        issubclass(w.category, DeprecationWarning) and "ADR-025" in str(w.message) for w in captured
    ), "qwen_vllm.telemetry did not emit ADR-025 DeprecationWarning"


def test_m4_heal_classifier_model_emits_deprecation_warning() -> None:
    mod = "agentic_core.L2_execution.healers.heal_classifier_model"
    sys.modules.pop(mod, None)
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        importlib.import_module(mod)
    assert any(
        issubclass(w.category, DeprecationWarning) and "ADR-025" in str(w.message) for w in captured
    ), "heal_classifier_model did not emit ADR-025 DeprecationWarning"
