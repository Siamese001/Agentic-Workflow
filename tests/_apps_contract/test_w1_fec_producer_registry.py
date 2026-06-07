"""Tests for apps_shared.cert.fec_producer registry.

Plan: `docs/archive/windsurf/legacy-tree/plans/apps-eval-harness-residual-a2d9c7.md` W1.P2.
"""

from __future__ import annotations

import pytest

from apps_shared.cert.fec_producer import (
    clear_registry,
    get_producer,
    register_producer,
    registered_app_ids,
    resolve_fec,
    unregister_producer,
)


@pytest.fixture(autouse=True)
def _isolate_registry():
    clear_registry()
    yield
    clear_registry()


def test_resolve_fec_returns_empty_dict_when_no_producer_registered():
    assert resolve_fec("apps_qna", {"evidence_bundle": {}}) == {}


def test_register_and_resolve_producer_returns_producer_output():
    def producer(ctx):
        return {"c0_status": "PASS", "support_score": 0.91, "cited_spans": ["s1"]}

    register_producer("apps_qna", producer)
    result = resolve_fec("apps_qna", {"evidence_bundle": {"items": []}})
    assert result["c0_status"] == "PASS"
    assert result["support_score"] == 0.91


def test_register_producer_validates_inputs():
    with pytest.raises(ValueError):
        register_producer("", lambda ctx: {})
    with pytest.raises(TypeError):
        register_producer("apps_qna", "not_callable")  # type: ignore[arg-type]


def test_unregister_producer_returns_true_when_removed_else_false():
    register_producer("apps_qna", lambda ctx: {})
    assert unregister_producer("apps_qna") is True
    assert unregister_producer("apps_qna") is False


def test_get_producer_returns_noop_default_when_unregistered():
    producer = get_producer("apps_missing")
    assert producer({}) == {}


def test_resolve_fec_coerces_non_dict_return_to_empty():
    register_producer("apps_bad", lambda ctx: ["not", "a", "dict"])  # type: ignore[return-value,arg-type]
    assert resolve_fec("apps_bad", {}) == {}


def test_resolve_fec_catches_producer_exception_and_returns_empty():
    def failing(ctx):
        raise ValueError("boom")

    register_producer("apps_bad", failing)
    assert resolve_fec("apps_bad", {}) == {}


def test_resolve_fec_handles_none_run_context():
    register_producer("apps_qna", lambda ctx: {"c0_status": "UNKNOWN"})
    assert resolve_fec("apps_qna", None) == {"c0_status": "UNKNOWN"}


def test_registered_app_ids_returns_sorted_snapshot():
    register_producer("apps_rfp", lambda ctx: {})
    register_producer("apps_qna", lambda ctx: {})
    register_producer("apps_exec", lambda ctx: {})
    assert registered_app_ids() == ("apps_exec", "apps_qna", "apps_rfp")
