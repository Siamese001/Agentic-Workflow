"""Integration adapter contract tests for apps_underwriting_ai."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_underwriting_ai.integrations.execution_adapter import (
    ExecutionAdapter,
    ExecutionRequest,
)
from apps_underwriting_ai.integrations.governed_underwriting_run import (
    governed_underwriting_run,
)
from apps_underwriting_ai.integrations.observability_adapter import (
    ObservabilityAdapter,
)
from apps_underwriting_ai.integrations.spine_handoff import (
    SpineHandoff,
    SpineHandoffEnvelope,
)
from apps_underwriting_ai.integrations.underwriting_ingress_runner import (
    UnderwritingIngressRunner,
)
from apps_underwriting_ai.types.underwriting_types import UnderwritingResult


# -- ExecutionAdapter ---------------------------------------------------------


def test_execution_adapter_returns_underwriting_result() -> None:
    adapter = ExecutionAdapter()
    req = ExecutionRequest(
        request_id="i-1",
        applicant_id="a-1",
        product_class="auto",
    )
    result = adapter.execute(req)
    assert isinstance(result, UnderwritingResult)
    assert result.request_id == "i-1"


def test_execution_request_metadata_passthrough() -> None:
    adapter = ExecutionAdapter()
    req = ExecutionRequest(
        request_id="i-2",
        applicant_id="a-1",
        product_class="auto",
        metadata={"channel": "web"},
        trace_id="trace-i-2",
    )
    result = adapter.execute(req)
    assert result.trace_id == "trace-i-2"


# -- governed_underwriting_run -----------------------------------------------


def test_governed_run_minimal_args() -> None:
    result = governed_underwriting_run(
        request_id="g-1",
        applicant_id="a-1",
        product_class="auto",
    )
    assert isinstance(result, UnderwritingResult)
    assert result.request_id == "g-1"


def test_governed_run_passes_trace_id() -> None:
    result = governed_underwriting_run(
        request_id="g-2",
        applicant_id="a-1",
        product_class="auto",
        trace_id="trace-g-2",
    )
    assert result.trace_id == "trace-g-2"


# -- UnderwritingIngressRunner ----------------------------------------------


def test_ingress_runner_loads_yaml(tmp_path: Path) -> None:
    payload = (
        "request_id: y-1\napplicant_id: a-1\nproduct_class: auto\n"
        "documents:\n  - kind: id_card\n"
    )
    p = tmp_path / "req.yaml"
    p.write_text(payload, encoding="utf-8")
    result = UnderwritingIngressRunner().run_from_file(p)
    assert result.request_id == "y-1"
    assert result.reconciliation.reconciled_count == 1


def test_ingress_runner_loads_json(tmp_path: Path) -> None:
    payload = json.dumps(
        {
            "request_id": "j-1",
            "applicant_id": "a-1",
            "product_class": "auto",
            "documents": [{"kind": "id_card"}, {"kind": "income_proof"}],
        }
    )
    p = tmp_path / "req.json"
    p.write_text(payload, encoding="utf-8")
    result = UnderwritingIngressRunner().run_from_file(p)
    assert result.request_id == "j-1"
    assert result.reconciliation.reconciled_count == 2


def test_ingress_runner_raises_on_missing_file(tmp_path: Path) -> None:
    p = tmp_path / "missing.yaml"
    with pytest.raises(FileNotFoundError):
        UnderwritingIngressRunner().run_from_file(p)


def test_ingress_runner_raises_on_unsupported_extension(tmp_path: Path) -> None:
    p = tmp_path / "req.txt"
    p.write_text("anything", encoding="utf-8")
    with pytest.raises(ValueError, match="unsupported"):
        UnderwritingIngressRunner().run_from_file(p)


def test_ingress_runner_raises_on_missing_request_id(tmp_path: Path) -> None:
    p = tmp_path / "req.yaml"
    p.write_text("applicant_id: a-1\nproduct_class: auto\n", encoding="utf-8")
    with pytest.raises(ValueError, match="request_id"):
        UnderwritingIngressRunner().run_from_file(p)


def test_ingress_runner_raises_on_missing_applicant_id(tmp_path: Path) -> None:
    p = tmp_path / "req.yaml"
    p.write_text("request_id: r-1\nproduct_class: auto\n", encoding="utf-8")
    with pytest.raises(ValueError, match="applicant_id"):
        UnderwritingIngressRunner().run_from_file(p)


def test_ingress_runner_raises_on_missing_product_class(tmp_path: Path) -> None:
    p = tmp_path / "req.yaml"
    p.write_text("request_id: r-1\napplicant_id: a-1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="product_class"):
        UnderwritingIngressRunner().run_from_file(p)


# -- SpineHandoff ------------------------------------------------------------


def test_spine_handoff_returns_envelope() -> None:
    result = governed_underwriting_run(
        request_id="s-1", applicant_id="a-1", product_class="auto"
    )
    envelope = SpineHandoff().package(result)
    assert isinstance(envelope, SpineHandoffEnvelope)
    assert envelope.app == "apps_underwriting_ai"
    assert envelope.route == "R3_grounded_read"
    assert envelope.request_id == "s-1"


def test_spine_handoff_envelope_payload_keys() -> None:
    result = governed_underwriting_run(
        request_id="s-2", applicant_id="a-1", product_class="auto"
    )
    envelope = SpineHandoff().package(result)
    for key in (
        "verdict",
        "rationale",
        "evidence_refs",
        "feature_summary",
        "trace_id",
    ):
        assert key in envelope.payload


# -- ObservabilityAdapter ---------------------------------------------------


def test_observability_adapter_emit_does_not_raise() -> None:
    adapter = ObservabilityAdapter()
    adapter.emit("test.event", request_id="o-1")
    adapter.emit_stage_start("stage_x", "o-1")
    adapter.emit_stage_complete("stage_x", "o-1", duration_ms=12.5)
    adapter.emit_decision("o-1", "approve", evidence_count=5)


def test_observability_adapter_app_constant() -> None:
    assert ObservabilityAdapter.APP == "apps_underwriting_ai"
