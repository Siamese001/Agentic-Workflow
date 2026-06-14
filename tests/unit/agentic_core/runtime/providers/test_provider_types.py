"""Unit tests for agentic_core.runtime.providers.provider_types.

Wave 6.1 (P2 untested-module coverage) — generic provider invocation contracts.
Covers the five str-enums (membership/value), ProviderProfile/TokenUsage/
ProviderInvocationReceipt frozen dataclasses, as_dict shape (enum .value
serialisation, latency rounding, nested TokenUsage), and the gateway error
class hierarchy.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.providers.provider_types import (
    BudgetStatus,
    ProviderCredentialsMissingError,
    ProviderGatewayError,
    ProviderInvocationReceipt,
    ProviderKind,
    ProviderModeBlockedError,
    ProviderMode,
    ProviderNotAllowedError,
    ProviderProfile,
    ProviderProfileNotFoundError,
    SafetyStatus,
    TimeoutStatus,
    TokenUsage,
)


class TestEnums:
    def test_provider_kind_values(self) -> None:
        assert {k.value for k in ProviderKind} == {
            "stub", "local_vllm", "external_api", "deterministic",
        }

    def test_provider_mode_values(self) -> None:
        assert {m.value for m in ProviderMode} == {
            "stub_only", "local_only", "live_allowed",
        }

    def test_budget_status_values(self) -> None:
        assert {b.value for b in BudgetStatus} == {
            "within_budget", "budget_exceeded", "budget_unknown",
        }

    def test_timeout_status_values(self) -> None:
        assert {t.value for t in TimeoutStatus} == {
            "within_limit", "timeout_exceeded", "timeout_unknown",
        }

    def test_safety_status_values(self) -> None:
        assert {s.value for s in SafetyStatus} == {
            "safe", "flagged", "blocked", "unknown",
        }

    def test_str_enum_is_str(self) -> None:
        # str-based enums compare equal to their string value
        assert ProviderKind.STUB == "stub"


class TestProviderProfile:
    def test_required_and_defaults(self) -> None:
        p = ProviderProfile(profile_id="p1", provider_kind=ProviderKind.STUB)
        assert p.model_id is None
        assert p.max_tokens == 4096
        assert p.timeout_seconds == 60
        assert p.temperature_range == (0.0, 1.0)
        assert p.requires_network is False
        assert p.sandbox_safe is True

    def test_frozen(self) -> None:
        p = ProviderProfile(profile_id="p1", provider_kind=ProviderKind.STUB)
        with pytest.raises(dataclasses.FrozenInstanceError):
            p.max_tokens = 1  # type: ignore[misc]


class TestTokenUsage:
    def test_defaults_and_as_dict(self) -> None:
        t = TokenUsage()
        assert t.as_dict() == {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }

    def test_as_dict_values(self) -> None:
        t = TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15)
        assert t.as_dict()["total_tokens"] == 15


def _receipt(**overrides: object) -> ProviderInvocationReceipt:
    base = dict(
        invocation_id="inv-1",
        provider_profile_ref="ref-1",
        provider_kind=ProviderKind.DETERMINISTIC,
        model_ref="m1",
        request_id="req-1",
        run_id="run-1",
        trace_root="t1",
        node_id="n1",
        prompt_artifact_ref="pa-1",
        input_digest="id1",
        output_digest="od1",
        latency_ms=12.3456,
        token_usage=TokenUsage(total_tokens=7),
        budget_status=BudgetStatus.WITHIN_BUDGET,
        timeout_status=TimeoutStatus.WITHIN_LIMIT,
        safety_status=SafetyStatus.SAFE,
    )
    base.update(overrides)
    return ProviderInvocationReceipt(**base)  # type: ignore[arg-type]


class TestProviderInvocationReceipt:
    def test_as_dict_serialises_enums_to_value(self) -> None:
        d = _receipt().as_dict()
        assert d["provider_kind"] == "deterministic"
        assert d["budget_status"] == "within_budget"
        assert d["timeout_status"] == "within_limit"
        assert d["safety_status"] == "safe"

    def test_as_dict_rounds_latency(self) -> None:
        assert _receipt(latency_ms=12.3456).as_dict()["latency_ms"] == 12.35

    def test_as_dict_embeds_token_usage(self) -> None:
        d = _receipt().as_dict()
        assert d["token_usage"] == {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 7,
        }

    def test_as_dict_includes_schema_version(self) -> None:
        assert _receipt().as_dict()["schema_version"] == "rb13.1"

    def test_defaults_error_and_deterministic_digest(self) -> None:
        r = _receipt()
        assert r.error is None
        assert r.deterministic_digest == ""


class TestErrorHierarchy:
    @pytest.mark.parametrize(
        "exc",
        [
            ProviderProfileNotFoundError,
            ProviderNotAllowedError,
            ProviderCredentialsMissingError,
            ProviderModeBlockedError,
        ],
    )
    def test_subclasses_of_gateway_error(self, exc: type) -> None:
        assert issubclass(exc, ProviderGatewayError)
        assert issubclass(ProviderGatewayError, Exception)

    def test_raise_and_catch_as_base(self) -> None:
        with pytest.raises(ProviderGatewayError):
            raise ProviderNotAllowedError("nope")
