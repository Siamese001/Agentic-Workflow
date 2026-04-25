"""Tests for G10 structured cache event emit (_emit_structured_cache_event).

Covers:
* Payload is built and forwarded as a JSON-shaped event to _emit_emits_metric_event
* SEMANTIC_CACHE_STRUCTURED_EMIT=0 disables the emit (pure no-op)
* Invalid reason_code raises in payload validation but is swallowed (debug-logged)
* All cache_lineage values produce a valid payload (L1 / L2 / L2_to_L1_writeback)
"""

from __future__ import annotations

import json

import pytest


@pytest.fixture
def captured_events(monkeypatch):
    """Capture every _emit_emits_metric_event call inside semantic_cache_manager."""
    from agentic_core.L4_state.utils.memory import semantic_cache_manager  # noqa: PLC0415

    events: list[tuple[str, str, str]] = []

    def _capture(module: str, code: str, event: str) -> None:
        events.append((module, code, event))

    monkeypatch.setattr(semantic_cache_manager, "_emit_emits_metric_event", _capture)
    return events, semantic_cache_manager


def test_structured_emit_default_on_produces_json_payload(captured_events, monkeypatch):
    monkeypatch.delenv("SEMANTIC_CACHE_STRUCTURED_EMIT", raising=False)
    events, scm = captured_events
    scm._emit_structured_cache_event(
        namespace="ns_test",
        tenant_id="tenant_a",
        cache_lineage="L1",
        reason_code="exact_hit",
        ttl_seconds=300,
        embedding_model_id="bge-m3-v1",
        cache_tier="static",
    )
    assert len(events) == 1
    _, _, event_str = events[0]
    assert event_str.startswith("structured:exact_hit:")
    payload = json.loads(event_str.split(":", 2)[2])
    assert payload["namespace"] == "ns_test"
    assert payload["tenant_id"] == "tenant_a"
    assert payload["cache_lineage"] == "L1"
    assert payload["cache_tier"] == "static"
    assert payload["reason_codes"] == ["exact_hit"]
    assert payload["ttl_seconds"] == 300
    assert payload["embedding_model_id"] == "bge-m3-v1"
    assert payload["freshness_class"] in {"hot", "warm", "cold"}


def test_structured_emit_disabled_is_noop(captured_events, monkeypatch):
    monkeypatch.setenv("SEMANTIC_CACHE_STRUCTURED_EMIT", "0")
    events, scm = captured_events
    scm._emit_structured_cache_event(
        namespace="x",
        tenant_id="y",
        cache_lineage="L2",
        reason_code="exact_hit",
    )
    assert events == []


def test_invalid_reason_code_swallowed_no_emit(captured_events, monkeypatch):
    monkeypatch.delenv("SEMANTIC_CACHE_STRUCTURED_EMIT", raising=False)
    events, scm = captured_events
    # not in whitelist
    scm._emit_structured_cache_event(
        namespace="x",
        tenant_id="y",
        cache_lineage="L1",
        reason_code="totally_made_up",
    )
    assert events == []  # ValueError swallowed, no emit


def test_l2_writeback_lineage(captured_events, monkeypatch):
    monkeypatch.delenv("SEMANTIC_CACHE_STRUCTURED_EMIT", raising=False)
    events, scm = captured_events
    scm._emit_structured_cache_event(
        namespace="ns",
        tenant_id="t",
        cache_lineage="L2_to_L1_writeback",
        reason_code="hybrid_hit",
        dense_score=0.97,
        evidence_ids=("e1", "e2"),
        embedding_model_id="bge-m3-v1",
        cache_tier="dynamic",
    )
    assert len(events) == 1
    payload = json.loads(events[0][2].split(":", 2)[2])
    assert payload["cache_lineage"] == "L2_to_L1_writeback"
    assert payload["reason_codes"] == ["hybrid_hit"]
    assert payload["dense_score"] == 0.97
    assert payload["evidence_ids"] == ["e1", "e2"]
    assert payload["cache_tier"] == "dynamic"


def test_freshness_class_age_buckets(captured_events, monkeypatch):
    """Old written_at → cold; recent → hot."""
    import time  # noqa: PLC0415

    monkeypatch.delenv("SEMANTIC_CACHE_STRUCTURED_EMIT", raising=False)
    events, scm = captured_events
    # written 2 days ago → cold
    scm._emit_structured_cache_event(
        namespace="ns",
        tenant_id="t",
        cache_lineage="L2",
        reason_code="exact_hit",
        written_at=time.time() - 2 * 86400,
    )
    payload = json.loads(events[-1][2].split(":", 2)[2])
    assert payload["freshness_class"] == "cold"
    # written 5 minutes ago → hot
    scm._emit_structured_cache_event(
        namespace="ns",
        tenant_id="t",
        cache_lineage="L2",
        reason_code="exact_hit",
        written_at=time.time() - 300,
    )
    payload = json.loads(events[-1][2].split(":", 2)[2])
    assert payload["freshness_class"] == "hot"
