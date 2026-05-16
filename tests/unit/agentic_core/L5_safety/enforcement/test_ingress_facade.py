"""W3B: stable ``ingress`` facade matches implementation and preserves gate behavior."""

from __future__ import annotations

from typing import Any

import pytest

from agentic_core.L5_safety.enforcement import ingress as ingress_facade
from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    IngressEnvelopeCheck,
    RejectionReasonCode,
)
from agentic_core.L5_safety.enforcement.rate_limit import UnboundedRateLimiter


def test_facade_types_are_implementation_singletons() -> None:
    from agentic_core.L5_safety.enforcement import ingress_envelope_check as impl

    assert ingress_facade.IngressEnvelopeCheck is impl.IngressEnvelopeCheck
    assert ingress_facade.StampedRequest is impl.StampedRequest
    assert ingress_facade.ClarificationRequired is impl.ClarificationRequired
    assert ingress_facade.IngressRejected is impl.IngressRejected
    assert ingress_facade.RejectionSlip is impl.RejectionSlip


def _gate(**overrides: Any) -> IngressEnvelopeCheck:
    defaults: dict[str, Any] = {
        "rate_limiter": UnboundedRateLimiter(),
        "enable_safety_screen": False,
    }
    defaults.update(overrides)
    return IngressEnvelopeCheck(**defaults)


def test_facade_gate_happy_path_matches_direct_constructed_gate() -> None:
    gate = _gate()
    env = {
        "schema_version": "1.0",
        "caller_identity": "svc-test",
        "request_payload": {"intent": "ping"},
        "tenant_id": "t1",
    }
    out = gate.check(env)
    assert isinstance(out, ingress_facade.StampedRequest)


def test_facade_rejection_type_used_on_malformed_envelope() -> None:
    gate = _gate()
    with pytest.raises(ingress_facade.IngressRejected) as exc:
        gate.check({})
    assert exc.value.slip.reason_code is RejectionReasonCode.MALFORMED_ENVELOPE


def test_rejection_response_still_maps_facade_exceptions() -> None:
    from agentic_core.L5_safety.enforcement.rejection_response import RejectionResponse

    gate = _gate()
    with pytest.raises(ingress_facade.IngressRejected) as exc:
        gate.check({})
    rr = RejectionResponse.from_exception(exc.value)
    assert rr.reason_code == RejectionReasonCode.MALFORMED_ENVELOPE.value
