"""vLLM invariant contract + verifier tests: merged from 2-file family.

Covers:
  invariant_contract:  InvariantViolation canonical JSON, hashing, as_dict, enum stability
  invariant_verifier:  verify_gateway_invariants — all per-invariant pass/fail cases
"""

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from agentic_core.L2_execution.types.vllm_invariant_contract_types import (
    InvariantId,
    InvariantSeverity,
    InvariantViolation,
)
from agentic_core.L2_execution.types.vllm_invariant_verifier_types import (
    verify_gateway_invariants,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_vllm_contracts")
_emit_applies_guardrail("p0", "test_vllm_contracts", "p0_governance")
_emit_reads_policy_state("p0", "test_vllm_contracts", "policy_binding")
_emit_snapshots_state("p0", "test_vllm_contracts", "state_snapshot")
emit_replay_key("p0", "test_vllm_contracts")
emit_determinism_digest("p0", "test_vllm_contracts")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.unit_min_deps


# ===========================================================================
# invariant_contract tests
# ===========================================================================


def test_invariant_violation_canonical_json_stable():
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test message",
        context={"key1": "value1", "key2": "value2"},
    )

    json1 = violation.canonical_json()
    json2 = violation.canonical_json()

    assert json1 == json2
    assert isinstance(json1, str)


def test_invariant_violation_canonical_json_sorted_keys():
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value,
        severity=InvariantSeverity.WARN.value,
        message="Test",
        context={"z": 1, "a": 2, "m": 3},
    )

    json_str = violation.canonical_json()
    parsed = json.loads(json_str)

    assert list(parsed.keys()) == ["context", "invariant_id", "message", "severity"]
    assert list(parsed["context"].keys()) == ["a", "m", "z"]


def test_invariant_violation_hash_deterministic():
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value,
        severity=InvariantSeverity.FAIL.value,
        message="Missing fingerprint",
        context={"provider": "test"},
    )

    hash1 = violation.violation_hash()
    hash2 = violation.violation_hash()

    assert hash1 == hash2
    assert len(hash1) == 64  # SHA256 hex digest
    assert all(c in "0123456789abcdef" for c in hash1)


def test_invariant_violation_hash_changes_on_content_change():
    violation1 = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value,
        severity=InvariantSeverity.FAIL.value,
        message="Message 1",
        context={},
    )

    violation2 = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value,
        severity=InvariantSeverity.FAIL.value,
        message="Message 2",
        context={},
    )

    assert violation1.violation_hash() != violation2.violation_hash()


def test_invariant_violation_as_dict_includes_hash():
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test",
        context={"key": "value"},
    )

    result = violation.as_dict()

    assert "violation_hash" in result
    assert result["violation_hash"] == violation.violation_hash()
    assert result["invariant_id"] == violation.invariant_id
    assert result["severity"] == violation.severity
    assert result["message"] == violation.message
    assert result["context"] == violation.context


def test_invariant_id_enum_values_stable():
    assert InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value == "INV_NO_GPU_IMPORTS_IN_L0_L6"
    assert (
        InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value
        == "INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS"
    )
    assert InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value == "INV_LOCAL_REQUEST_TEMPERATURE_ZERO"
    assert InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value == "INV_LOCAL_REQUEST_SEED_PRESENT"
    assert InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value == "INV_TELEMETRY_HAS_FINGERPRINT_HASH"
    assert InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value == "INV_REPLAY_HASH_PRESENT_WHEN_ENABLED"
    assert InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value == "INV_GEMINI_FALLBACK_REQUIRES_REASON"


def test_invariant_severity_enum_values():
    assert InvariantSeverity.INFO.value == "INFO"
    assert InvariantSeverity.WARN.value == "WARN"
    assert InvariantSeverity.FAIL.value == "FAIL"


def test_invariant_violation_frozen():
    violation = InvariantViolation(
        invariant_id=InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value,
        severity=InvariantSeverity.FAIL.value,
        message="Test",
        context={},
    )

    with pytest.raises(Exception):  # FrozenInstanceError or AttributeError
        violation.message = "Changed"


# ===========================================================================
# invariant_verifier tests
# ===========================================================================


@dataclass
class MinimalLocalRequest:
    max_tokens: int | None = None
    temperature: float | None = None
    seed: int | None = None


def test_verify_no_violations_on_valid_local_request():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123", "failure_type": None}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert violations == []


def test_inv_missing_max_tokens():
    local_request = MinimalLocalRequest(max_tokens=None, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_LOCAL_REQUEST_HAS_EXPLICIT_MAX_TOKENS.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "max_tokens" in violations[0].message.lower()


def test_inv_temperature_not_zero():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.7, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_LOCAL_REQUEST_TEMPERATURE_ZERO.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "0.7" in violations[0].message


def test_inv_missing_seed():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=None)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_LOCAL_REQUEST_SEED_PRESENT.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "seed" in violations[0].message.lower()


def test_inv_missing_fingerprint_hash():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {}  # Missing fingerprint_hash

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_TELEMETRY_HAS_FINGERPRINT_HASH.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "fingerprint_hash" in violations[0].message.lower()


def test_inv_gemini_fallback_requires_reason():
    telemetry_dict = {"fingerprint_hash": "abc123", "failure_type": None}

    violations = verify_gateway_invariants(
        provider_selected="gemini-2.5-pro",
        local_request=None,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "failure_type" in violations[0].message.lower()


def test_gemini_fallback_with_reason_no_violation():
    telemetry_dict = {"fingerprint_hash": "abc123", "failure_type": "TOKEN_BUDGET_EXCEEDED"}

    violations = verify_gateway_invariants(
        provider_selected="gemini-2.5-pro",
        local_request=None,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    gemini_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_GEMINI_FALLBACK_REQUIRES_REASON.value
    ]
    assert gemini_violations == []


def test_multiple_violations_sorted_deterministically():
    local_request = MinimalLocalRequest(max_tokens=None, temperature=0.7, seed=None)
    telemetry_dict = {}  # Missing fingerprint_hash

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations) == 4
    invariant_ids = [v.invariant_id for v in violations]
    assert invariant_ids == sorted(invariant_ids)


def test_violations_are_deterministic():
    local_request = MinimalLocalRequest(max_tokens=None, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations1 = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    violations2 = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
    )

    assert len(violations1) == len(violations2)
    for v1, v2 in zip(violations1, violations2):
        assert v1.invariant_id == v2.invariant_id
        assert v1.severity == v2.severity
        assert v1.message == v2.message
        assert v1.violation_hash() == v2.violation_hash()


def test_inv_replay_hash_missing_when_enabled():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        replay_hash_enabled=True,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "replay_hash" in violations[0].message.lower()


def test_inv_replay_hash_present_when_enabled_no_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123", "replay_hash": "def456"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        replay_hash_enabled=True,
    )

    replay_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    ]
    assert replay_violations == []


def test_inv_replay_hash_disabled_no_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        replay_hash_enabled=False,
    )

    replay_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_REPLAY_HASH_PRESENT_WHEN_ENABLED.value
    ]
    assert replay_violations == []


def test_inv_gpu_import_policy_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        gpu_import_policy_ok=False,
    )

    assert len(violations) == 1
    assert violations[0].invariant_id == InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value
    assert violations[0].severity == InvariantSeverity.FAIL.value
    assert "gpu import policy" in violations[0].message.lower()


def test_inv_gpu_import_policy_ok_no_violation():
    local_request = MinimalLocalRequest(max_tokens=100, temperature=0.0, seed=42)
    telemetry_dict = {"fingerprint_hash": "abc123"}

    violations = verify_gateway_invariants(
        provider_selected="Qwen2.5-7B-Instruct",
        local_request=local_request,
        telemetry_dict=telemetry_dict,
        fingerprint=None,
        gpu_import_policy_ok=True,
    )

    gpu_violations = [
        v for v in violations if v.invariant_id == InvariantId.INV_NO_GPU_IMPORTS_IN_L0_L6.value
    ]
    assert gpu_violations == []
