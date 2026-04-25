"""End-to-end test of the runtime HITL escalation path.

Exercises the full stack:

    envelope
      → classify_exit (L3)
          → classify_escalation_class (L5 policy)
          → RuntimeHitlLedger.record_escalation (L3)
          → hitl.escalate OTel span
    adapter.enqueue  (Notion adapter + fake transport)
    human resolves   (simulated via fake transport)
    adapter.poll     → outcome
    controller.record_approval (L3)
          → ledger UPDATE
          → hitl.approved OTel span

This is the first end-to-end integration test (plan P3.4). Governed-app
integration lives in W5; this test stands in for a "first app integration"
by composing the components without touching any ``apps_*`` directory.

Hermetic: no network, no real Notion.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L3_orchestration.exit_control import hitl_spans
from agentic_core.L3_orchestration.exit_control.exit_controller import (
    ExitAction,
    ExitController,
)
from agentic_core.L3_orchestration.exit_control.runtime_hitl_ledger import (
    LedgerState,
    RuntimeHitlLedger,
)
from agentic_core.L5_safety.adapters.human_approval_adapter import (
    ApprovalOutcomeKind,
)
from agentic_core.L5_safety.adapters.notion_approval_adapter import (
    NotionApprovalAdapter,
)
from agentic_core.L5_safety.exit_control.hitl_classes import HitlClass
from agentic_core.L5_safety.exit_control.hitl_policy import load_policy

from tests.agentic_core.L5_safety.adapters.test_notion_adapter import (
    FakeNotionTransport,
)


POLICY_YAML = """
version: 1
thresholds:
  novelty_min: 0.72
  confidence_max: 0.60
classes:
  financial:       {timeout_s: 3600,  fallback: DENY, approver_pool: finance_oncall}
  safety:          {timeout_s: 1800,  fallback: DENY, approver_pool: safety_oncall}
  regulated:       {timeout_s: 7200,  fallback: DENY, approver_pool: compliance_oncall}
  novel_context:   {timeout_s: 900,   fallback: DENY, approver_pool: ops_oncall}
  low_confidence:  {timeout_s: 600,   fallback: DENY, approver_pool: ops_oncall}
  policy_override: {timeout_s: 86400, fallback: DENY, approver_pool: policy_board}
precedence:
  - policy_override
  - regulated
  - safety
  - financial
  - novel_context
  - low_confidence
"""


@pytest.fixture
def stack(tmp_path: Path, monkeypatch):
    # Policy
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(POLICY_YAML, encoding="utf-8")
    policy = load_policy(policy_file, policy_snapshot="e2e-snap")

    # Ledger (fresh SQLite file)
    ledger = RuntimeHitlLedger(tmp_path / "ledger.db")
    controller = ExitController(policy, ledger)

    # Adapter (fake Notion transport)
    transport = FakeNotionTransport()
    adapter = NotionApprovalAdapter(database_id="db-runtime-hitl", transport=transport)

    # Span capture
    spans: list[tuple[str, dict]] = []

    def capture(name: str):
        def _emit(**kwargs):
            spans.append((name, kwargs))

        return _emit

    monkeypatch.setattr(hitl_spans, "emit_escalate", capture("escalate"))
    monkeypatch.setattr(hitl_spans, "emit_approved", capture("approved"))
    monkeypatch.setattr(hitl_spans, "emit_denied", capture("denied"))
    monkeypatch.setattr(hitl_spans, "emit_timeout", capture("timeout"))

    yield {
        "policy": policy,
        "ledger": ledger,
        "controller": controller,
        "adapter": adapter,
        "transport": transport,
        "spans": spans,
    }
    ledger.close()


def test_e2e_approve_path(stack):
    controller = stack["controller"]
    adapter = stack["adapter"]
    transport = stack["transport"]
    spans = stack["spans"]

    # 1. Governed run emits a sealed envelope that triggers escalation.
    envelope = {"is_financial": True, "amount": 50_000, "payee": "acme"}
    decision = controller.classify(envelope, run_id="run-e2e-1", trace_id="tr-e2e-1")
    assert decision.action is ExitAction.ESCALATE_HITL
    assert decision.hitl_class is HitlClass.FINANCIAL
    assert decision.timeout_s == 3600

    # 2. Controller's ledger entry is handed to the adapter for enqueue.
    entry = stack["ledger"].get(decision.ledger_id)
    assert entry is not None
    handle = adapter.enqueue(entry)
    assert handle.ledger_id == decision.ledger_id
    assert handle.adapter_kind == "notion"

    # 3. Human approves in Notion (simulated).
    assert adapter.poll(handle) is None  # still pending
    transport.resolve(
        handle.external_id,
        ApprovalOutcomeKind.APPROVED,
        approver_id="alice",
        rationale="reviewed budget",
    )

    # 4. Adapter poll returns APPROVED; controller records it.
    outcome = adapter.poll(handle)
    assert outcome is not None and outcome.kind is ApprovalOutcomeKind.APPROVED

    final = controller.record_approval(
        decision.ledger_id,
        approver_id=outcome.approver_id or "unknown",
        rationale=outcome.rationale,
    )
    assert final.state is LedgerState.APPROVED
    assert final.approver_id == "alice"

    # 5. Spans: escalate + approved (no denied/timeout).
    names = [n for n, _ in spans]
    assert names == ["escalate", "approved"]
    approved_kw = spans[1][1]
    assert approved_kw["rationale_len"] == len("reviewed budget")


def test_e2e_timeout_path(stack):
    controller = stack["controller"]
    adapter = stack["adapter"]
    spans = stack["spans"]

    envelope = {"novelty_score": 0.95}
    decision = controller.classify(envelope, run_id="run-e2e-2", trace_id="tr-e2e-2")
    assert decision.hitl_class is HitlClass.NOVEL_CONTEXT

    entry = stack["ledger"].get(decision.ledger_id)
    assert entry is not None
    handle = adapter.enqueue(entry)

    # No human acts. Orchestrator-side timer expires → controller records timeout.
    assert adapter.poll(handle) is None
    final = controller.record_timeout(decision.ledger_id)
    assert final.state is LedgerState.TIMEOUT

    # Default fallback per policy is DENY — caller dispatches DENY route.
    assert decision.fallback == "DENY"

    names = [n for n, _ in spans]
    assert names == ["escalate", "timeout"]


def test_e2e_deny_path_bypasses_adapter(stack):
    """Envelope with deny=True returns DENY without touching the adapter/ledger."""
    controller = stack["controller"]
    spans = stack["spans"]

    envelope = {"deny": True, "deny_reason": "guardrail_blocked"}
    decision = controller.classify(envelope, run_id="run-e2e-3", trace_id="tr-e2e-3")
    assert decision.action is ExitAction.DENY
    assert decision.deny_reason == "guardrail_blocked"
    assert decision.ledger_id is None
    assert stack["ledger"].list_pending() == []
    assert spans == []


def test_e2e_commit_path_bypasses_adapter(stack):
    """Low-risk envelope → COMMIT; no ledger write, no spans, no adapter call."""
    controller = stack["controller"]
    spans = stack["spans"]

    envelope = {"confidence_score": 0.99, "novelty_score": 0.0}
    decision = controller.classify(envelope, run_id="run-e2e-4", trace_id="tr-e2e-4")
    assert decision.action is ExitAction.COMMIT
    assert stack["ledger"].list_pending() == []
    assert spans == []
