"""Integration adapter contract tests for apps_underwriting_ai.

Tests the active integration surface after W1 deletion of parallel paths:
- ObservabilityAdapter (unchanged, still active)
- U0 binding integration contract (new canonical ingress path)

Deleted integrations (ExecutionAdapter, governed_underwriting_run,
UnderwritingIngressRunner, SpineHandoff) were removed in plan
apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W1.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_underwriting_ai.integrations.observability_adapter import (
    ObservabilityAdapter,
)
from apps_underwriting_ai.runtime.bindings.u0_binding import (
    U0ValidationError,
    u0_validate_underwriting,
)
from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (
    UnderwritingIngressEnvelope,
    ValidatedUnderwritingRequest,
)


# -- ObservabilityAdapter ---------------------------------------------------


def test_observability_adapter_emit_does_not_raise() -> None:
    adapter = ObservabilityAdapter()
    adapter.emit("test.event", request_id="o-1")
    adapter.emit_stage_start("stage_x", "o-1")
    adapter.emit_stage_complete("stage_x", "o-1", duration_ms=12.5)
    adapter.emit_decision("o-1", "approve", evidence_count=5)


def test_observability_adapter_app_constant() -> None:
    assert ObservabilityAdapter.APP == "apps_underwriting_ai"


# -- U0 binding integration contract ----------------------------------------


def _envelope(**kwargs) -> UnderwritingIngressEnvelope:
    defaults = dict(
        request_id="i-1",
        applicant_id="a-1",
        product_class="auto",
        documents=({"kind": "id_card"},),
        metadata={},
        trace_id="",
    )
    defaults.update(kwargs)
    return UnderwritingIngressEnvelope(**defaults)


def test_u0_binding_returns_validated_request() -> None:
    result = u0_validate_underwriting(_envelope())
    assert isinstance(result, ValidatedUnderwritingRequest)
    assert result.request_id == "i-1"
    assert result.app_id == "apps_underwriting_ai"
    assert result.task_class == "underwriting_decision"


def test_u0_binding_metadata_passthrough() -> None:
    result = u0_validate_underwriting(
        _envelope(trace_id="trace-i-2", metadata={"channel": "web"})
    )
    assert result.trace_id == "trace-i-2"
    assert result.metadata == {"channel": "web"}


def test_u0_binding_runtime_package_has_all_contracts() -> None:
    result = u0_validate_underwriting(_envelope())
    pkg = result.runtime_customization_package
    assert len(pkg) == 17, f"Expected 17 config keys, got {len(pkg)}: {sorted(pkg)}"


def test_u0_binding_rejects_missing_request_id() -> None:
    with pytest.raises(U0ValidationError, match="request_id"):
        u0_validate_underwriting(_envelope(request_id=""))


def test_u0_binding_rejects_missing_applicant_id() -> None:
    with pytest.raises(U0ValidationError, match="applicant_id"):
        u0_validate_underwriting(_envelope(applicant_id=""))


def test_u0_binding_rejects_missing_product_class() -> None:
    with pytest.raises(U0ValidationError, match="product_class"):
        u0_validate_underwriting(_envelope(product_class=""))


def test_u0_binding_from_yaml_file(tmp_path: Path) -> None:
    yaml_text = (
        "request_id: y-1\napplicant_id: a-1\nproduct_class: auto\n"
        "documents:\n  - kind: id_card\n"
    )
    p = tmp_path / "req.yaml"
    p.write_text(yaml_text, encoding="utf-8")
    import yaml
    payload = yaml.safe_load(p.read_text(encoding="utf-8"))
    env = UnderwritingIngressEnvelope(
        request_id=str(payload["request_id"]),
        applicant_id=str(payload["applicant_id"]),
        product_class=str(payload["product_class"]),
        documents=tuple(payload.get("documents", ())),
        metadata=payload.get("metadata") or {},
    )
    result = u0_validate_underwriting(env)
    assert result.request_id == "y-1"
    assert len(result.documents) == 1


def test_u0_binding_from_json_file(tmp_path: Path) -> None:
    payload = json.dumps({
        "request_id": "j-1",
        "applicant_id": "a-1",
        "product_class": "auto",
        "documents": [{"kind": "id_card"}, {"kind": "income_proof"}],
    })
    p = tmp_path / "req.json"
    p.write_text(payload, encoding="utf-8")
    data = json.loads(p.read_text(encoding="utf-8"))
    env = UnderwritingIngressEnvelope(
        request_id=str(data["request_id"]),
        applicant_id=str(data["applicant_id"]),
        product_class=str(data["product_class"]),
        documents=tuple(data.get("documents", ())),
        metadata=data.get("metadata") or {},
    )
    result = u0_validate_underwriting(env)
    assert result.request_id == "j-1"
    assert len(result.documents) == 2
