"""Unit + integration tests for L3 runtime HITL exit controller.

Covers ADR-023 §3.2 dispatch semantics, ledger round-trip, and OTel span
emission (verified via monkeypatched emit_* functions).

Scope: runtime HITL (v30 step [5]) — NOT developer-loop Author-Gate.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from agentic_core.L3_orchestration.exit_control import hitl_spans
from agentic_core.L3_orchestration.exit_control.exit_controller import (
    ExitAction,
    ExitController,
    ExitDecision,
    classify_exit,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    DEFAULT_LEDGER_PATH,
    LedgerEntry,
    LedgerState,
    RuntimeHitlLedger,
    _hash_payload,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from agentic_core.L5_safety.exit_control.hitl_policy import load_policy


VALID_POLICY_YAML = """
version: 1
thresholds:
  novelty_min: 0.72
  confidence_max: 0.60
classes:
  financial:
    {timeout_s: 3600, fallback: DENY, approver_pool: finance_oncall}
  safety:
    {timeout_s: 1800, fallback: DENY, approver_pool: safety_oncall}
  regulated:
    {timeout_s: 7200, fallback: DENY, approver_pool: compliance_oncall}
  novel_context:
    {timeout_s: 900, fallback: DENY, approver_pool: ops_oncall}
  low_confidence:
    {timeout_s: 600, fallback: DENY, approver_pool: ops_oncall}
  policy_override:
    {timeout_s: 86400, fallback: DENY, approver_pool: policy_board}
precedence:
  - policy_override
  - regulated
  - safety
  - financial
  - novel_context
  - low_confidence
"""


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def loaded_policy(tmp_path: Path):
    p = tmp_path / "policy.yaml"
    p.write_text(VALID_POLICY_YAML, encoding="utf-8")
    return load_policy(p, policy_snapshot="test-snap-abc")


@pytest.fixture
def ledger(tmp_path: Path):
    counter = {"t": 1_700_000_000.0}

    def fake_now() -> float:
        counter["t"] += 0.5
        return counter["t"]

    db = tmp_path / "hitl_ledger.db"
    with RuntimeHitlLedger(db, now=fake_now) as lg:
        yield lg


@pytest.fixture
def controller(loaded_policy, ledger):
    counter = {"t": 1_700_001_000.0}

    def fake_now() -> float:
        counter["t"] += 1.0
        return counter["t"]

    return ExitController(loaded_policy, ledger, now=fake_now)


@pytest.fixture
def span_capture(monkeypatch):
    """Capture all emit_* calls as (name, kwargs) tuples."""
    captured: list[tuple[str, dict[str, Any]]] = []

    def make(name: str):
        def _emit(**kwargs: Any) -> None:
            captured.append((name, kwargs))

        return _emit

    monkeypatch.setattr(hitl_spans, "emit_escalate", make("escalate"))
    monkeypatch.setattr(hitl_spans, "emit_approved", make("approved"))
    monkeypatch.setattr(hitl_spans, "emit_denied", make("denied"))
    monkeypatch.setattr(hitl_spans, "emit_timeout", make("timeout"))
    # exit_controller imports the module, so patching the module-level names is sufficient.
    return captured


# ---------------------------------------------------------------------------
# classify_exit — three outcomes
# ---------------------------------------------------------------------------


def test_classify_exit_commit_path(loaded_policy, ledger, span_capture):
    env = {"confidence_score": 0.99, "novelty_score": 0.1}
    d = classify_exit(env, loaded_policy, run_id="r1", trace_id="t1", ledger=ledger)
    assert d.action is ExitAction.COMMIT
    assert d.hitl_class is None and d.ledger_id is None
    assert span_capture == []  # no span on COMMIT
    assert ledger.list_pending() == []


def test_classify_exit_deny_path(loaded_policy, ledger, span_capture):
    env = {"deny": True, "deny_reason": "guardrail_block"}
    d = classify_exit(env, loaded_policy, run_id="r1", trace_id="t1", ledger=ledger)
    assert d.action is ExitAction.DENY
    assert d.deny_reason == "guardrail_block"
    assert d.hitl_class is None
    assert span_capture == []
    assert ledger.list_pending() == []


def test_classify_exit_deny_reason_empty_is_none(loaded_policy, ledger):
    env = {"deny": True}
    d = classify_exit(env, loaded_policy, run_id="r1", trace_id="t1", ledger=ledger)
    assert d.action is ExitAction.DENY
    assert d.deny_reason is None


def test_classify_exit_escalate_records_ledger_and_span(
    loaded_policy, ledger, span_capture
):
    env = {"is_financial": True, "amount": 10_000}
    d = classify_exit(env, loaded_policy, run_id="run-1", trace_id="tr-1", ledger=ledger)

    assert d.action is ExitAction.ESCALATE_HITL
    assert d.hitl_class is HitlClass.FINANCIAL
    assert d.approver_pool == "finance_oncall"
    assert d.timeout_s == 3600
    assert d.fallback == "DENY"
    assert d.ledger_id is not None

    pending = ledger.list_pending()
    assert len(pending) == 1
    entry = pending[0]
    assert entry.run_id == "run-1"
    assert entry.trace_id == "tr-1"
    assert entry.hitl_class is HitlClass.FINANCIAL
    assert entry.state is LedgerState.PENDING
    assert entry.envelope["amount"] == 10_000
    assert entry.policy_snapshot == "test-snap-abc"
    assert entry.prev_hash == ""  # first entry for this run
    assert entry.entry_hash  # non-empty

    assert len(span_capture) == 1
    name, kwargs = span_capture[0]
    assert name == "escalate"
    assert kwargs["run_id"] == "run-1"
    assert kwargs["hitl_class"] == "financial"
    assert kwargs["timeout_s"] == 3600
    assert kwargs["policy_snapshot"] == "test-snap-abc"


def test_classify_exit_rejects_non_mapping(loaded_policy, ledger):
    with pytest.raises(TypeError, match="mapping"):
        classify_exit(
            ["not", "a", "mapping"],  # type: ignore[arg-type]
            loaded_policy,
            run_id="r",
            trace_id="t",
            ledger=ledger,
        )


# ---------------------------------------------------------------------------
# ExitController — resume paths + spans
# ---------------------------------------------------------------------------


def test_controller_approval_emits_span_and_updates_ledger(controller, span_capture):
    d = controller.classify(
        {"is_safety_impacting": True}, run_id="run-A", trace_id="tr-A"
    )
    assert d.action is ExitAction.ESCALATE_HITL
    entry = controller.record_approval(
        d.ledger_id, approver_id="alice", rationale="looks fine"
    )
    assert entry.state is LedgerState.APPROVED
    assert entry.approver_id == "alice"
    assert entry.rationale == "looks fine"

    names = [n for n, _ in span_capture]
    assert names == ["escalate", "approved"]
    approved_kwargs = span_capture[1][1]
    assert approved_kwargs["approver_id"] == "alice"
    assert approved_kwargs["rationale_len"] == len("looks fine")
    assert approved_kwargs["latency_ms"] >= 0


def test_controller_denial_emits_span(controller, span_capture):
    d = controller.classify({"is_regulated": True}, run_id="run-B", trace_id="tr-B")
    entry = controller.record_denial(
        d.ledger_id, approver_id="bob", reason_code="NON_COMPLIANT", rationale="violates 10-K"
    )
    assert entry.state is LedgerState.DENIED
    assert entry.reason_code == "NON_COMPLIANT"

    names = [n for n, _ in span_capture]
    assert names == ["escalate", "denied"]
    denied_kwargs = span_capture[1][1]
    assert denied_kwargs["reason_code"] == "NON_COMPLIANT"


def test_controller_timeout_emits_span_with_fallback(controller, span_capture):
    d = controller.classify({"is_financial": True}, run_id="run-C", trace_id="tr-C")
    entry = controller.record_timeout(d.ledger_id)
    assert entry.state is LedgerState.TIMEOUT
    assert entry.reason_code == "TIMEOUT"

    names = [n for n, _ in span_capture]
    assert names == ["escalate", "timeout"]
    timeout_kwargs = span_capture[1][1]
    assert timeout_kwargs["timeout_s"] == 3600
    assert timeout_kwargs["fallback_taken"] == "DENY"


def test_controller_idempotency_rejects_double_resolve(controller):
    d = controller.classify({"is_financial": True}, run_id="run-D", trace_id="tr-D")
    controller.record_approval(d.ledger_id, approver_id="alice")
    with pytest.raises(ValueError, match="already resolved"):
        controller.record_approval(d.ledger_id, approver_id="bob")
    with pytest.raises(ValueError, match="already resolved"):
        controller.record_denial(d.ledger_id, approver_id="bob", reason_code="X")
    with pytest.raises(ValueError, match="already resolved"):
        controller.record_timeout(d.ledger_id)


def test_controller_unknown_ledger_id_raises(controller):
    with pytest.raises(KeyError, match="not found"):
        controller.record_approval("does-not-exist", approver_id="alice")
    with pytest.raises(KeyError, match="not found"):
        controller.record_denial("does-not-exist", approver_id="a", reason_code="x")
    with pytest.raises(KeyError, match="not found"):
        controller.record_timeout("does-not-exist")


# ---------------------------------------------------------------------------
# RuntimeHitlLedger — direct coverage
# ---------------------------------------------------------------------------


def test_ledger_hash_chain_links_entries(ledger):
    e1 = ledger.record_escalation(
        run_id="shared",
        trace_id="t1",
        hitl_class=HitlClass.FINANCIAL,
        approver_pool="pool",
        timeout_s=60,
        policy_snapshot="snap",
        envelope={"n": 1},
    )
    e2 = ledger.record_escalation(
        run_id="shared",
        trace_id="t2",
        hitl_class=HitlClass.SAFETY,
        approver_pool="pool",
        timeout_s=120,
        policy_snapshot="snap",
        envelope={"n": 2},
    )
    # Second entry links to first.
    assert e1.prev_hash == ""
    assert e2.prev_hash == e1.entry_hash
    assert e1.entry_hash != e2.entry_hash


def test_ledger_list_by_run_orders_by_created(ledger):
    ledger.record_escalation(
        run_id="R", trace_id="a", hitl_class=HitlClass.FINANCIAL,
        approver_pool="p", timeout_s=1, policy_snapshot="s",
    )
    ledger.record_escalation(
        run_id="R", trace_id="b", hitl_class=HitlClass.SAFETY,
        approver_pool="p", timeout_s=1, policy_snapshot="s",
    )
    ledger.record_escalation(
        run_id="OTHER", trace_id="c", hitl_class=HitlClass.FINANCIAL,
        approver_pool="p", timeout_s=1, policy_snapshot="s",
    )
    entries = ledger.list_by_run("R")
    assert len(entries) == 2
    assert [e.trace_id for e in entries] == ["a", "b"]


def test_ledger_envelope_round_trip(ledger):
    env = {"amount": 42, "nested": {"k": [1, 2, 3]}, "flag": True}
    e = ledger.record_escalation(
        run_id="r", trace_id="t", hitl_class=HitlClass.FINANCIAL,
        approver_pool="p", timeout_s=1, policy_snapshot="s", envelope=env,
    )
    fetched = ledger.get(e.ledger_id)
    assert fetched is not None
    assert fetched.envelope == env


def test_ledger_get_missing_returns_none(ledger):
    assert ledger.get("nope") is None


def test_ledger_record_approved_rejects_missing(ledger):
    with pytest.raises(KeyError):
        ledger.record_approved("nope", approver_id="x")


def test_ledger_record_approved_rejects_already_resolved(ledger):
    e = ledger.record_escalation(
        run_id="r", trace_id="t", hitl_class=HitlClass.FINANCIAL,
        approver_pool="p", timeout_s=1, policy_snapshot="s",
    )
    ledger.record_approved(e.ledger_id, approver_id="alice")
    with pytest.raises(ValueError, match="already resolved"):
        ledger.record_approved(e.ledger_id, approver_id="bob")


def test_ledger_default_path_constant():
    assert DEFAULT_LEDGER_PATH == Path("artifacts/runtime/hitl_ledger.db")


def test_hash_payload_stable():
    p = {"b": 2, "a": 1}
    assert _hash_payload(p) == _hash_payload({"a": 1, "b": 2})


# ---------------------------------------------------------------------------
# hitl_spans — direct coverage (exercises emit paths with real OTel if present)
# ---------------------------------------------------------------------------


def test_hitl_spans_emit_no_raise():
    """All four emitters must succeed regardless of OTel availability."""
    hitl_spans.emit_escalate(
        run_id="r", trace_id="t", hitl_class="financial",
        approver_pool="p", timeout_s=1, policy_snapshot="s",
    )
    hitl_spans.emit_approved(
        run_id="r", trace_id="t", approver_id="a", latency_ms=10, rationale_len=5,
    )
    hitl_spans.emit_denied(
        run_id="r", trace_id="t", approver_id="a", latency_ms=10, reason_code="X",
    )
    hitl_spans.emit_timeout(run_id="r", trace_id="t", timeout_s=1, fallback_taken="DENY")


def test_latency_ms_none_resolved_at():
    from agentic_core.L3_orchestration.exit_control.exit_controller import _latency_ms

    assert _latency_ms(100.0, None) == 0
    assert _latency_ms(100.0, 100.5) == 500
    assert _latency_ms(200.0, 100.0) == 0  # clamped at zero


def test_hitl_span_name_constants():
    assert hitl_spans.SPAN_ESCALATE == "hitl.escalate"
    assert hitl_spans.SPAN_APPROVED == "hitl.approved"
    assert hitl_spans.SPAN_DENIED == "hitl.denied"
    assert hitl_spans.SPAN_TIMEOUT == "hitl.timeout"


def test_hitl_spans_no_otel_fallback(monkeypatch):
    """When OTel is unavailable (_TRACER=None), emitters still succeed."""
    monkeypatch.setattr(hitl_spans, "_OTEL_AVAILABLE", False)
    monkeypatch.setattr(hitl_spans, "_TRACER", None)
    hitl_spans.emit_escalate(
        run_id="r", trace_id="t", hitl_class="financial",
        approver_pool="p", timeout_s=1, policy_snapshot="s",
    )
    # No assertion — just must not raise.


# ---------------------------------------------------------------------------
# Integration — full escalate → approve → resume
# ---------------------------------------------------------------------------


def test_e2e_escalate_approve_cycle(controller, span_capture):
    d = controller.classify(
        {"novelty_score": 0.95, "is_financial": False},
        run_id="run-E2E",
        trace_id="tr-E2E",
    )
    assert d.action is ExitAction.ESCALATE_HITL
    assert d.hitl_class is HitlClass.NOVEL_CONTEXT
    assert d.timeout_s == 900

    final = controller.record_approval(
        d.ledger_id, approver_id="carol", rationale="reviewed"
    )
    assert final.state is LedgerState.APPROVED
    assert [n for n, _ in span_capture] == ["escalate", "approved"]
