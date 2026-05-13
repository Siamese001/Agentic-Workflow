"""Smoke tests for apps_underwriting_ai U0 binding + sub-engines.

Verifies the U0 ingress validation path works end-to-end and that the
active backing engines (DecisionPacketAssembler, EvidenceRegisterEngine)
are importable.

Parallel-path tests (UnderwritingEngine / ExecutionAdapter /
governed_underwriting_run / SpineHandoff) were removed when those
files were deleted in plan apps-underwriting-ai-kill-parallel-pipelines-a3f7e2 W1.
"""

from __future__ import annotations

from apps_underwriting_ai.runtime.bindings.u0_binding import (
    U0ValidationError,
    u0_validate_underwriting,
)
from apps_underwriting_ai.runtime.contracts.underwriting_ingress_payload import (
    UnderwritingIngressEnvelope,
)


def _make_envelope(**kwargs) -> UnderwritingIngressEnvelope:
    defaults = dict(
        request_id="smoke-0001",
        applicant_id="applicant-smoke",
        product_class="auto",
        documents=({"kind": "id_card"}, {"kind": "income_proof"}),
        metadata={"source": "smoke"},
        trace_id="trace-smoke",
    )
    defaults.update(kwargs)
    return UnderwritingIngressEnvelope(**defaults)


def test_u0_validate_returns_validated_request() -> None:
    envelope = _make_envelope()
    validated = u0_validate_underwriting(envelope)
    assert validated.request_id == "smoke-0001"
    assert validated.applicant_id == "applicant-smoke"
    assert validated.product_class == "auto"
    assert validated.trace_id == "trace-smoke"
    assert validated.task_class == "underwriting_decision"
    assert validated.app_id == "apps_underwriting_ai"


def test_u0_validate_loads_all_17_config_keys() -> None:
    validated = u0_validate_underwriting(_make_envelope())
    pkg = validated.runtime_customization_package
    expected_keys = {
        "app_domain_manifest", "cache_profiles", "capability_profiles",
        "eval_rubrics", "fixtures", "grader_roster", "input_contract",
        "learning_profiles", "negative_controls", "orchestration_profiles",
        "output_schema", "prompt_profiles", "repair_profiles",
        "retrieval_profiles", "route_profiles", "task_classes", "threshold_profiles",
    }
    assert expected_keys == set(pkg.keys()), (
        f"runtime_customization_package missing keys: {expected_keys - set(pkg.keys())}"
    )


def test_u0_validate_extracts_convenience_fields() -> None:
    validated = u0_validate_underwriting(_make_envelope())
    assert isinstance(validated.app_domain_manifest, dict)
    assert isinstance(validated.input_contract, dict)
    assert isinstance(validated.route_profiles, list)
    assert isinstance(validated.threshold_profiles, list)


def test_u0_validate_preserves_documents() -> None:
    docs = ({"kind": "id_card"}, {"kind": "income_proof"}, {"kind": "bank_statement"})
    validated = u0_validate_underwriting(_make_envelope(documents=docs))
    assert len(validated.documents) == 3


def test_u0_validate_rejects_missing_request_id() -> None:
    import pytest
    with pytest.raises(U0ValidationError, match="request_id"):
        u0_validate_underwriting(_make_envelope(request_id=""))


def test_u0_validate_rejects_missing_applicant_id() -> None:
    import pytest
    with pytest.raises(U0ValidationError, match="applicant_id"):
        u0_validate_underwriting(_make_envelope(applicant_id=""))


def test_u0_validate_rejects_missing_product_class() -> None:
    import pytest
    with pytest.raises(U0ValidationError, match="product_class"):
        u0_validate_underwriting(_make_envelope(product_class=""))


def test_u0_validate_rejects_wrong_envelope_type() -> None:
    import pytest
    with pytest.raises(TypeError):
        u0_validate_underwriting({"request_id": "x"})  # type: ignore[arg-type]


def test_u0_validate_u0_cert_ref_set() -> None:
    validated = u0_validate_underwriting(_make_envelope())
    assert validated.u0_cert_ref.startswith("u0-apps-underwriting-ai-")


def test_engines_namespace_importable_without_underwriting_engine() -> None:
    from apps_underwriting_ai.engines import (
        BaseUnderwritingEngine,
        DecisionPacketAssembler,
        EvidenceRegisterEngine,
    )
    assert BaseUnderwritingEngine is not None
    assert DecisionPacketAssembler is not None
    assert EvidenceRegisterEngine is not None
