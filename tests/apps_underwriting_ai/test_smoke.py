"""Smoke tests for apps_underwriting_ai skeleton.

Verifies the 5-stage pipeline runs end-to-end via both drivers and emits a
well-formed DecisionPacket.
"""

from __future__ import annotations

from apps_underwriting_ai.engines.underwriting_engine import UnderwritingEngine
from apps_underwriting_ai.integrations.execution_adapter import (
    ExecutionAdapter,
    ExecutionRequest,
)
from apps_underwriting_ai.integrations.governed_underwriting_run import (
    governed_underwriting_run,
)
from apps_underwriting_ai.integrations.spine_handoff import SpineHandoff
from apps_underwriting_ai.outputs.decision_renderer import DecisionRenderer
from apps_underwriting_ai.types.underwriting_types import (
    DecisionVerdict,
    UnderwritingRequest,
)


def _make_request() -> UnderwritingRequest:
    return UnderwritingRequest(
        request_id="smoke-0001",
        applicant_id="applicant-smoke",
        product_class="auto",
        documents=({"kind": "id_card"}, {"kind": "income_proof"}),
        metadata={"source": "smoke"},
    )


def test_imperative_driver_runs_end_to_end() -> None:
    request = _make_request()
    result = UnderwritingEngine().run(request, trace_id="trace-smoke")
    assert result.request_id == "smoke-0001"
    assert result.trace_id == "trace-smoke"
    assert result.decision.verdict in {
        DecisionVerdict.APPROVE,
        DecisionVerdict.REFER,
        DecisionVerdict.INSUFFICIENT_EVIDENCE,
    }
    # Reconciliation should reflect document count.
    assert result.reconciliation.reconciled_count == 2
    assert result.reconciliation.unresolved_count == 0


def test_governed_run_matches_imperative_path() -> None:
    result = governed_underwriting_run(
        request_id="smoke-0002",
        applicant_id="applicant-smoke",
        product_class="auto",
        documents=({"kind": "id_card"},),
        trace_id="trace-smoke-2",
    )
    assert result.request_id == "smoke-0002"
    assert result.trace_id == "trace-smoke-2"
    assert result.reconciliation.reconciled_count == 1


def test_execution_adapter_dispatches() -> None:
    adapter = ExecutionAdapter()
    req = ExecutionRequest(
        request_id="smoke-0003",
        applicant_id="applicant-smoke",
        product_class="auto",
        documents=(),
        metadata={},
        trace_id="trace-smoke-3",
    )
    result = adapter.execute(req)
    # Empty documents but stage 4 collects 5 evidence dimensions and stage 3
    # emits a 3-key feature vector → APPROVE under the skeleton heuristic.
    assert result.decision.verdict == DecisionVerdict.APPROVE
    assert len(result.register.records) == 5
    assert result.features.feature_vector["document_count"] == 0.0


def test_decision_renderer_emits_markdown_and_json() -> None:
    result = UnderwritingEngine().run(_make_request())
    md = DecisionRenderer().to_markdown(result)
    assert "Underwriting Decision" in md
    assert result.decision.verdict.value in md

    j = DecisionRenderer().to_json(result)
    assert "\"request_id\"" in j
    assert "\"verdict\"" in j


def test_spine_handoff_packages_envelope() -> None:
    result = UnderwritingEngine().run(_make_request())
    envelope = SpineHandoff().package(result)
    assert envelope.app == "apps_underwriting_ai"
    assert envelope.route == "R3_grounded_read"
    assert envelope.request_id == result.request_id
    assert envelope.payload["verdict"] == result.decision.verdict.value
