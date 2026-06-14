"""Unit tests for agentic_core.L0_routing.intake.reason_codes.

W2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 L0 routing chokepoint (x2.0).
``reason_codes`` (fan_in=19) is the machine-readable ingress reject/throttle vocabulary.
Every reject verdict MUST carry one of these — pin the enum + retriable subset.
"""

from __future__ import annotations

from agentic_core.L0_routing.intake.reason_codes import (
    RETRIABLE_REASON_CODES,
    IngressReasonCode,
)


class TestIngressReasonCode:
    def test_is_str_enum(self) -> None:
        assert isinstance(IngressReasonCode.EMPTY_PAYLOAD, str)
        assert IngressReasonCode.EMPTY_PAYLOAD == "EMPTY_PAYLOAD"

    def test_value_equals_name_for_all(self) -> None:
        for code in IngressReasonCode:
            assert code.value == code.name

    def test_exactly_eighteen_codes(self) -> None:
        assert len(list(IngressReasonCode)) == 18

    def test_spec_families_present(self) -> None:
        names = {c.name for c in IngressReasonCode}
        # one representative from each E1..E6 family
        for expected in [
            "UNSUPPORTED_TRANSPORT", "AUTH_REQUIRED", "QUOTA_EXCEEDED",
            "UNSUPPORTED_MODALITY", "NORMALIZATION_UNSAFE", "TRACE_BINDING_FAILED",
        ]:
            assert expected in names


class TestRetriableReasonCodes:
    def test_exact_retriable_set(self) -> None:
        assert RETRIABLE_REASON_CODES == frozenset({
            IngressReasonCode.QUOTA_EXCEEDED,
            IngressReasonCode.BURST_LIMIT,
            IngressReasonCode.INTERNAL_INGRESS_ERROR,
        })

    def test_permanent_rejects_not_retriable(self) -> None:
        for code in [
            IngressReasonCode.MALFORMED_ENVELOPE,
            IngressReasonCode.AUTH_EXPIRED,
            IngressReasonCode.DUPLICATE_REQUEST,
            IngressReasonCode.PAYLOAD_TOO_LARGE,
        ]:
            assert code not in RETRIABLE_REASON_CODES
