"""Unit tests for agentic_core.runtime.judges.panel.adapter_protocol.

Wave 6.1 (plan adg-testing-hotspots-wave-plan-a7f3c1) — untested P2 core module.
The module exposes a transport-only judge adapter contract. ``JudgeProviderAdapter``
is a pure ``typing.Protocol`` (no runtime surface — not tested), but the module
also ships a concrete frozen ``DeclaredTransportPolicy`` dataclass and the
``AdapterInvokeError`` exception type. Covers the concrete surface: dataclass
defaults, frozen immutability, value equality, and the exception hierarchy.
"""

from __future__ import annotations

import dataclasses

import pytest

from agentic_core.runtime.judges.panel.adapter_protocol import (
    AdapterInvokeError,
    DeclaredTransportPolicy,
    JudgeProviderAdapter,
)


class TestDeclaredTransportPolicyDefaults:
    def test_required_fields_and_defaults(self) -> None:
        policy = DeclaredTransportPolicy(max_output_tokens=2048, json_output_lock="strict")
        assert policy.max_output_tokens == 2048
        assert policy.json_output_lock == "strict"
        assert policy.temperature is None
        assert policy.system_includes_score_schema is True

    def test_optional_overrides(self) -> None:
        policy = DeclaredTransportPolicy(
            max_output_tokens=512,
            json_output_lock="loose",
            temperature=0.2,
            system_includes_score_schema=False,
        )
        assert policy.temperature == pytest.approx(0.2)
        assert policy.system_includes_score_schema is False


class TestDeclaredTransportPolicyImmutability:
    def test_frozen_blocks_mutation(self) -> None:
        policy = DeclaredTransportPolicy(max_output_tokens=1, json_output_lock="strict")
        with pytest.raises(dataclasses.FrozenInstanceError):
            policy.max_output_tokens = 2  # type: ignore[misc]

    def test_value_equality(self) -> None:
        a = DeclaredTransportPolicy(max_output_tokens=10, json_output_lock="strict", temperature=0.0)
        b = DeclaredTransportPolicy(max_output_tokens=10, json_output_lock="strict", temperature=0.0)
        assert a == b

    def test_value_inequality_on_temperature(self) -> None:
        a = DeclaredTransportPolicy(max_output_tokens=10, json_output_lock="strict", temperature=0.0)
        b = DeclaredTransportPolicy(max_output_tokens=10, json_output_lock="strict", temperature=1.0)
        assert a != b


class TestAdapterInvokeError:
    def test_is_exception_subclass(self) -> None:
        assert issubclass(AdapterInvokeError, Exception)

    def test_raisable_with_message(self) -> None:
        with pytest.raises(AdapterInvokeError, match="transport down"):
            raise AdapterInvokeError("transport down")


class TestProtocolSurface:
    def test_protocol_is_runtime_unenforced(self) -> None:
        # typing.Protocol without @runtime_checkable: isinstance must reject.
        class _Stub:
            provider_key = "stub"

        with pytest.raises(TypeError):
            isinstance(_Stub(), JudgeProviderAdapter)  # type: ignore[misc]

    def test_protocol_declares_expected_members(self) -> None:
        assert hasattr(JudgeProviderAdapter, "declared_policy")
        assert hasattr(JudgeProviderAdapter, "invoke")
