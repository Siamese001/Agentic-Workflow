"""apps_rg U0 payload reflection harness — fail-closed behaviour tests.

Covers the 12 reflection-side invariants required by the harness spec:
    1. valid payload produces ValidatedRequest + PASS receipt
    2. every raw JSON pointer is accounted for (no SILENTLY_DROPPED, no UNKNOWN_MAPPING)
    3. silently dropped fields fail closed (synthetic injection)
    4. unknown fields fail unless explicitly allowed by schema + field map
    5. missing jd_hash fails
    6. unknown generation_mode fails
    7. missing policy refs fail
    8. missing replay_key fails
    9. invalid jd_payload fails
   10. input_payload_digest is deterministic
   11. validated_request_digest is deterministic
   12. every DEFERRED pointer carries an explicit reason

Plan: .windsurf/plans/apps-rg-u0-reflection-harness-79d032.md (W3.P3.2)
"""
from __future__ import annotations

import copy
from typing import Any

import pytest

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.u0 import (
    AppsRgU0AdapterError,
    AppsRgU0ReflectionFailure,
    AppsRgU0ReflectionReceipt,
    InvalidJdPayloadError,
    MissingJdHashError,
    MissingPolicyRefsError,
    MissingReplayKeyError,
    SilentlyDroppedFieldError,
    UnknownFieldMappingError,
    UnknownGenerationModeError,
    apps_rg_u0_adapt,
)
from tests._apps_contract._apps_rg_u0_fixture_builder import (
    VALID_PAYLOAD,
    load_fixture,
)


# ---------------------------------------------------------------------------
# 1. Valid payload → ValidatedRequest + PASS receipt
# ---------------------------------------------------------------------------


def test_valid_payload_produces_validated_request_and_pass_receipt() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    validated, receipt = apps_rg_u0_adapt(raw)

    assert isinstance(validated, ValidatedRequest)
    assert isinstance(receipt, AppsRgU0ReflectionReceipt)
    assert receipt.pass_status is True
    assert receipt.silently_dropped == ()
    assert receipt.unknown_mappings == ()


def test_validated_request_carries_required_identity_fields() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    validated, _ = apps_rg_u0_adapt(raw)

    assert validated.app_id == "apps_rg"
    assert validated.task_class == "resume_generation"
    assert validated.request_id == raw["transport"]["request_id"]
    assert validated.run_id == raw["transport"]["run_id"]
    assert validated.trace_id == raw["transport"]["trace_id"]
    assert validated.tenant_id == raw["transport"]["tenant_id"]
    assert validated.replay_key == raw["replay"]["replay_key"]
    assert validated.target_level == raw["target"]["level"]


def test_validated_request_preserves_full_app_payload() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    validated, _ = apps_rg_u0_adapt(raw)

    # Every top-level key from the input MUST appear under app_payload.
    # app_payload may have ADDITIONAL keys from Pydantic default-valued fields
    # (e.g. runtime_customization_package added in Wave 2.5).
    assert set(raw.keys()).issubset(set(validated.app_payload.keys()))
    # Domain-specific nested data must round-trip verbatim.
    assert validated.app_payload["jd_payload"]["jd_hash"] == raw["jd_payload"]["jd_hash"]
    assert validated.app_payload["target"]["company"] == raw["target"]["company"]
    assert validated.app_payload["generation_mode"] == raw["generation_mode"]


# ---------------------------------------------------------------------------
# 2. Every raw JSON pointer is accounted for
# ---------------------------------------------------------------------------


def test_every_raw_json_pointer_is_accounted_for() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    _, receipt = apps_rg_u0_adapt(raw)

    # Coverage invariant: total pointers == sum of all four buckets.
    assert receipt.pointers_total == (
        receipt.pointers_mapped
        + receipt.pointers_derived
        + receipt.pointers_rejected
        + receipt.pointers_deferred
    )
    # No leakage in either failure bucket.
    assert receipt.silently_dropped == ()
    assert receipt.unknown_mappings == ()


def test_receipt_counts_include_at_least_one_mapped_and_one_derived() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    _, receipt = apps_rg_u0_adapt(raw)
    assert receipt.pointers_mapped >= 1, "expected at least one MAPPED pointer"
    assert receipt.pointers_derived >= 1, "expected at least one DERIVED pointer"


# ---------------------------------------------------------------------------
# 3. Silently dropped fields fail closed
# ---------------------------------------------------------------------------


def test_silently_dropped_field_fails_closed_when_pydantic_allows_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the field-map loader to drop one expected pointer entry. The
    adapter MUST then surface the same pointer as silently_dropped and raise
    SilentlyDroppedFieldError. This proves the reflection check is the
    authoritative gate even when Pydantic is happy.
    """

    from agentic_core.runtime.u0 import apps_rg_u0_adapter as adapter_module

    real_loader = adapter_module._load_field_map

    def _loader_with_one_dropped() -> dict[str, Any]:
        full = real_loader()
        modified = copy.deepcopy(full)
        # Remove a known pointer that the valid fixture exercises.
        modified["mappings"].pop("/transport/app_id", None)
        return modified

    monkeypatch.setattr(adapter_module, "_load_field_map", _loader_with_one_dropped)

    raw = load_fixture("valid_ingress_contract.v1.json")
    with pytest.raises(SilentlyDroppedFieldError) as exc_info:
        apps_rg_u0_adapt(raw)

    assert "/transport/app_id" in exc_info.value.silently_dropped
    assert exc_info.value.unknown_mappings == ()


def test_unknown_mapping_status_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Patch the field map to give a pointer an unknown status — the adapter
    MUST surface UnknownFieldMappingError."""

    from agentic_core.runtime.u0 import apps_rg_u0_adapter as adapter_module

    real_loader = adapter_module._load_field_map

    def _loader_with_unknown_status() -> dict[str, Any]:
        full = real_loader()
        modified = copy.deepcopy(full)
        modified["mappings"]["/generation_mode"] = {
            "status": "INVENTED_STATUS",
            "target": "n/a",
            "reason": "n/a",
        }
        return modified

    monkeypatch.setattr(adapter_module, "_load_field_map", _loader_with_unknown_status)

    raw = load_fixture("valid_ingress_contract.v1.json")
    with pytest.raises(UnknownFieldMappingError) as exc_info:
        apps_rg_u0_adapt(raw)

    assert "/generation_mode" in exc_info.value.unknown_mappings


# ---------------------------------------------------------------------------
# 4. Unknown fields fail unless explicitly allowed
# ---------------------------------------------------------------------------


def test_unknown_top_level_field_fails_closed() -> None:
    """The Pydantic ``extra='forbid'`` config rejects unknown top-level keys
    at validation time. This is the first line of defence; the reflection
    adapter is the second (see test_silently_dropped_*)."""

    raw = load_fixture("invalid_unmapped_field.json")
    with pytest.raises(AppsRgU0AdapterError):
        apps_rg_u0_adapt(raw)


# ---------------------------------------------------------------------------
# 5. Missing jd_hash fails
# ---------------------------------------------------------------------------


def test_missing_jd_hash_fails_closed() -> None:
    raw = load_fixture("invalid_missing_jd_hash.json")
    with pytest.raises(MissingJdHashError) as exc_info:
        apps_rg_u0_adapt(raw)
    assert "jd_hash" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# 6. Unknown generation_mode fails
# ---------------------------------------------------------------------------


def test_unknown_generation_mode_fails_closed() -> None:
    raw = load_fixture("invalid_unknown_generation_mode.json")
    with pytest.raises(UnknownGenerationModeError):
        apps_rg_u0_adapt(raw)


# ---------------------------------------------------------------------------
# 7. Missing policy refs fail
# ---------------------------------------------------------------------------


def test_missing_policy_refs_fail_closed() -> None:
    raw = load_fixture("invalid_missing_policy_ref.json")
    with pytest.raises(MissingPolicyRefsError) as exc_info:
        apps_rg_u0_adapt(raw)
    assert "/profile_manifest/" in str(exc_info.value)


def test_each_required_policy_ref_individually_required() -> None:
    """Blank each required policy ref one at a time — each must fail closed."""

    required_keys = (
        "manifest_digest",
        "prompt_registry_ref",
        "hitl_policy_ref",
        "l0_policy_ref",
        "agent_spec_ref",
        "thresholds_ref",
    )
    for key in required_keys:
        raw = copy.deepcopy(VALID_PAYLOAD)
        raw["profile_manifest"][key] = ""
        with pytest.raises(MissingPolicyRefsError):
            apps_rg_u0_adapt(raw)


# ---------------------------------------------------------------------------
# 8. Missing replay_key fails
# ---------------------------------------------------------------------------


def test_missing_replay_key_fails_closed() -> None:
    raw = copy.deepcopy(VALID_PAYLOAD)
    raw["replay"]["replay_key"] = ""
    with pytest.raises(MissingReplayKeyError):
        apps_rg_u0_adapt(raw)


# ---------------------------------------------------------------------------
# 9. Invalid jd_payload structure fails
# ---------------------------------------------------------------------------


def test_invalid_jd_payload_missing_text_fails_closed() -> None:
    raw = copy.deepcopy(VALID_PAYLOAD)
    raw["jd_payload"]["jd_text"] = ""
    with pytest.raises(InvalidJdPayloadError):
        apps_rg_u0_adapt(raw)


def test_invalid_jd_payload_wrong_type_fails_closed() -> None:
    raw = copy.deepcopy(VALID_PAYLOAD)
    raw["jd_payload"] = "not a dict"
    with pytest.raises(InvalidJdPayloadError):
        apps_rg_u0_adapt(raw)


# ---------------------------------------------------------------------------
# 10 + 11. Deterministic digests
# ---------------------------------------------------------------------------


def test_input_payload_digest_is_deterministic() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    _, r1 = apps_rg_u0_adapt(raw)
    _, r2 = apps_rg_u0_adapt(raw)
    assert r1.input_payload_digest == r2.input_payload_digest
    # 64 hex chars, all-lowercase
    assert len(r1.input_payload_digest) == 64
    assert all(c in "0123456789abcdef" for c in r1.input_payload_digest)


def test_validated_request_digest_is_deterministic() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    _, r1 = apps_rg_u0_adapt(raw)
    _, r2 = apps_rg_u0_adapt(raw)
    assert r1.validated_request_digest == r2.validated_request_digest
    assert len(r1.validated_request_digest) == 64


def test_payload_digest_changes_when_payload_changes() -> None:
    """Determinism does not mean stickiness — different inputs must hash differently."""

    raw1 = load_fixture("valid_ingress_contract.v1.json")
    raw2 = copy.deepcopy(raw1)
    raw2["target"]["company"] = "Different Co"
    _, r1 = apps_rg_u0_adapt(raw1)
    _, r2 = apps_rg_u0_adapt(raw2)
    assert r1.input_payload_digest != r2.input_payload_digest


# ---------------------------------------------------------------------------
# 12. Every DEFERRED pointer carries an explicit reason
# ---------------------------------------------------------------------------


def test_every_deferred_pointer_carries_explicit_reason() -> None:
    raw = load_fixture("valid_ingress_contract.v1.json")
    _, receipt = apps_rg_u0_adapt(raw)

    # The receipt count must equal the explicit-reason count — every DEFERRED
    # pointer in the field map MUST have a non-empty reason.
    assert len(receipt.deferred_reasons) == receipt.pointers_deferred
    for pointer, reason in receipt.deferred_reasons:
        assert pointer.startswith("/"), f"pointer must start with /: {pointer}"
        assert reason.strip(), f"DEFERRED reason must not be empty for {pointer}"
