"""Runtime-hardened tests for policy-hash enforcement helpers."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(scope="module")
def enforcement_package():
    return pytest.importorskip("agentic_core.L0_routing.enforcement")


class TestPolicyHashEnforcer:
    def test_active_merkle_root_returns_value(self, enforcement_package):
        assert enforcement_package.active_merkle_root() is not None

    def test_policy_hash_violation_initialization(self, enforcement_package):
        instance = enforcement_package.PolicyHashViolation("test violation")

        assert isinstance(instance, Exception)

    def test_policy_hash_validation_result_initialization(self, enforcement_package):
        instance = enforcement_package.PolicyHashValidationResult(
            passed=True,
            packet_id="packet123",
            policy_hash_present=True,
            policy_hash_matches=True,
            active_root="root123",
            packet_hash="hash123",
        )

        assert instance is not None
        assert instance.packet_id == "packet123"

    def test_policy_hash_validation_result_format_contains_core_fields(self, enforcement_package):
        instance = enforcement_package.PolicyHashValidationResult(
            passed=True,
            packet_id="packet123",
            policy_hash_present=True,
            policy_hash_matches=True,
            active_root="root123",
            packet_hash="hash123",
        )
        formatted = instance.format()

        assert isinstance(formatted, str)
        assert "packet123" in formatted
        assert "root123" in formatted
        assert len(formatted) > 50
