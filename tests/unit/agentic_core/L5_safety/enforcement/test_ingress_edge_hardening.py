"""Edge-case + adversarial hardening tests for the ingress gate.

Complements ``test_ingress_envelope_check.py`` (happy-path / contract) and
``test_ingress_spec_output_contract.py`` (W1+W2 spec gaps) with adversarial
inputs, concurrency, determinism, and verifier-driven verdict checks.
"""

from __future__ import annotations

import threading
from typing import Any

import pytest

from agentic_core.L5_safety.enforcement.identity_verifier import (
    IdentityVerificationError,
    IdentityVerifier,
    VerifiedIdentity,
)
from agentic_core.L5_safety.enforcement.ingress_envelope_check import (
    IngressEnvelopeCheck,
    IngressRejected,
    RejectionReasonCode,
    StampedRequest,
)
from agentic_core.L5_safety.enforcement.rate_limit import (
    TokenBucketConfig,
    TokenBucketRateLimiter,
    UnboundedRateLimiter,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ok_envelope(**overrides: Any) -> dict[str, Any]:
    env: dict[str, Any] = {
        "schema_version": "1.0",
        "caller_identity": "user-alice",
        "request_payload": {"intent": "do the thing"},
        "tenant_id": "tenant-alpha",
    }
    env.update(overrides)
    return env


def _gate(**overrides: Any) -> IngressEnvelopeCheck:
    defaults: dict[str, Any] = {
        "rate_limiter": UnboundedRateLimiter(),
        "enable_safety_screen": False,
    }
    defaults.update(overrides)
    return IngressEnvelopeCheck(**defaults)


# ---------------------------------------------------------------------------
# Attachment hardening — bool, control chars, path separators, length
# ---------------------------------------------------------------------------


def test_attachment_size_true_rejected_even_though_bool_is_int_in_python() -> None:
    """isinstance(True, int) is True; gate must still reject."""
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "a.txt", "size": True}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_size_false_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "a.txt", "size": False}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_size_string_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "a.txt", "size": "100"}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_filename_with_null_byte_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "evil\x00.txt", "size": 4}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_filename_with_path_separator_rejected() -> None:
    for bad in ("../etc/passwd", "subdir/file.txt", "C:\\Windows\\file"):
        with pytest.raises(IngressRejected) as exc:
            _gate().check(_ok_envelope(attachments=[{"filename": bad, "size": 4}]))
        assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_filename_with_newline_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "a\nb.txt", "size": 1}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_filename_too_long_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments=[{"filename": "x" * 1024 + ".txt", "size": 1}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


def test_attachment_content_type_truncated_to_bound() -> None:
    out = _gate().check(
        _ok_envelope(attachments=[{"filename": "a.txt", "size": 1, "content_type": "x" * 1000}])
    )
    assert isinstance(out, StampedRequest)
    assert len(out.attachment_manifest[0]["content_type"]) <= 256


def test_attachment_size_zero_accepted() -> None:
    """Zero-byte files are legitimate (touch markers, empty CSV headers, etc)."""
    out = _gate().check(_ok_envelope(attachments=[{"filename": "empty.txt", "size": 0}]))
    assert isinstance(out, StampedRequest)
    assert out.attachment_manifest[0]["size"] == 0


def test_attachment_float_size_truncated_to_int() -> None:
    out = _gate().check(_ok_envelope(attachments=[{"filename": "a.txt", "size": 12.7}]))
    assert isinstance(out, StampedRequest)
    assert out.attachment_manifest[0]["size"] == 12


def test_attachment_size_at_exact_limit_accepted() -> None:
    out = _gate(max_attachment_bytes=100).check(
        _ok_envelope(attachments=[{"filename": "a.txt", "size": 100}])
    )
    assert isinstance(out, StampedRequest)


def test_attachment_size_one_over_limit_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate(max_attachment_bytes=100).check(_ok_envelope(attachments=[{"filename": "a.txt", "size": 101}]))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_OVERSIZED


def test_attachment_count_at_exact_limit_accepted() -> None:
    atts = [{"filename": f"f{i}.bin", "size": 1} for i in range(4)]
    out = _gate(max_attachments=4).check(_ok_envelope(attachments=atts))
    assert isinstance(out, StampedRequest)
    assert len(out.attachment_manifest) == 4


# ---------------------------------------------------------------------------
# Modality edge cases
# ---------------------------------------------------------------------------


def test_modality_whitespace_normalized() -> None:
    out = _gate().check(_ok_envelope(modality="  IMAGE  "))
    assert isinstance(out, StampedRequest)
    assert out.modality == "image"


def test_modality_empty_string_rejected() -> None:
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(modality=""))
    assert exc.value.slip.reason_code is RejectionReasonCode.UNSUPPORTED_MODALITY


def test_modality_none_in_envelope_uses_default_text() -> None:
    out = _gate().check(_ok_envelope(modality=None))
    assert isinstance(out, StampedRequest)
    assert out.modality == "text"


def test_modality_payload_overrides_when_envelope_unset() -> None:
    payload = {"intent": "describe", "modality": "audio"}
    out = _gate().check(_ok_envelope(request_payload=payload))
    assert isinstance(out, StampedRequest)
    assert out.modality == "audio"


def test_modality_envelope_takes_precedence_over_payload() -> None:
    payload = {"intent": "x", "modality": "audio"}
    out = _gate().check(_ok_envelope(request_payload=payload, modality="image"))
    assert isinstance(out, StampedRequest)
    assert out.modality == "image"


# ---------------------------------------------------------------------------
# Source class edge cases
# ---------------------------------------------------------------------------


def test_source_class_int_value_falls_back_to_unknown() -> None:
    """Non-string source class values must not crash the gate."""
    out = _gate().check(_ok_envelope(ingress_source_class=42))
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == "unknown"


def test_source_class_empty_string_falls_back_to_unknown() -> None:
    out = _gate().check(_ok_envelope(ingress_source_class=""))
    assert isinstance(out, StampedRequest)
    assert out.ingress_source_class == "unknown"


# ---------------------------------------------------------------------------
# raw_payload_ref determinism + adversarial encoding
# ---------------------------------------------------------------------------


def test_raw_payload_ref_dict_key_order_invariant() -> None:
    a = _gate().check(_ok_envelope(request_payload={"a": 1, "b": 2}, request_id="r-a"))
    b = _gate().check(_ok_envelope(request_payload={"b": 2, "a": 1}, request_id="r-b"))
    assert isinstance(a, StampedRequest) and isinstance(b, StampedRequest)
    assert a.raw_payload_ref == b.raw_payload_ref


def test_raw_payload_ref_handles_non_json_serializable_payload() -> None:
    """Sets aren't JSON-serializable; gate must still produce a stable ref."""

    class Custom:
        def __repr__(self) -> str:
            return "<Custom-instance>"

    out = _gate().check(_ok_envelope(request_payload={"intent": "x", "obj": Custom()}))
    assert isinstance(out, StampedRequest)
    assert out.raw_payload_ref.startswith("sha256:")


def test_raw_payload_ref_stable_across_runs_for_string_payload() -> None:
    a = _gate().check(_ok_envelope(request_payload="hello", request_id="r-a"))
    b = _gate().check(_ok_envelope(request_payload="hello", request_id="r-b"))
    assert isinstance(a, StampedRequest) and isinstance(b, StampedRequest)
    assert a.raw_payload_ref == b.raw_payload_ref


def test_raw_payload_ref_handles_unicode_payload() -> None:
    out = _gate().check(_ok_envelope(request_payload={"intent": "héllo 你好 🌍"}))
    assert isinstance(out, StampedRequest)
    assert out.raw_payload_ref.startswith("sha256:")


# ---------------------------------------------------------------------------
# auth_verdict — verifier-driven precedence
# ---------------------------------------------------------------------------


class _FixedVerifier:
    """Test verifier that always returns the same VerifiedIdentity."""

    def __init__(self, caller_id: str, tenant_id: str = "t-1") -> None:
        self._cid = caller_id
        self._tid = tenant_id

    def verify(self, caller_identity: str, envelope: dict) -> VerifiedIdentity:  # noqa: ARG002
        return VerifiedIdentity(caller_id=self._cid, tenant_id=self._tid)


def test_auth_verdict_uses_verified_caller_not_raw_envelope() -> None:
    """If verifier returns svc-foo but envelope says alice, verdict = service_bound."""
    gate = _gate(identity_verifier=_FixedVerifier("svc-foo"))
    out = gate.check(_ok_envelope(caller_identity="alice"))
    assert isinstance(out, StampedRequest)
    assert out.auth_verdict == "service_bound"


def test_auth_verdict_anonymous_when_verified_id_marks_anon() -> None:
    gate = _gate(identity_verifier=_FixedVerifier("chat-anon"))
    out = gate.check(_ok_envelope(caller_identity="user-bob"))
    assert isinstance(out, StampedRequest)
    assert out.auth_verdict == "anonymous"


# ---------------------------------------------------------------------------
# Failing identity verifier raises rejected (not stamp with verdict=rejected)
# ---------------------------------------------------------------------------


class _AlwaysFailVerifier:
    def verify(self, caller_identity: str, envelope: dict) -> VerifiedIdentity:  # noqa: ARG002
        raise IdentityVerificationError("nope")


def test_identity_verifier_failure_rejects_before_stamp() -> None:
    gate = _gate(identity_verifier=_AlwaysFailVerifier())
    with pytest.raises(IngressRejected) as exc:
        gate.check(_ok_envelope())
    assert exc.value.slip.reason_code is RejectionReasonCode.IDENTITY_UNTRUSTED


# ---------------------------------------------------------------------------
# Concurrency — gate must be safe under multi-thread use
# ---------------------------------------------------------------------------


def test_gate_concurrent_distinct_request_ids_all_stamped() -> None:
    gate = _gate()
    results: list[Any] = []
    errors: list[BaseException] = []
    lock = threading.Lock()

    def worker(rid: int) -> None:
        try:
            out = gate.check(_ok_envelope(request_id=f"req-{rid}"))
            with lock:
                results.append(out)
        except BaseException as exc:  # noqa: BLE001 - test wants any failure
            with lock:
                errors.append(exc)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert not errors, f"unexpected errors under concurrency: {errors}"
    assert len(results) == 50
    assert all(isinstance(r, StampedRequest) for r in results)
    # All distinct request_ids ⇒ all 50 unique stamps.
    assert len({r.request_id for r in results}) == 50


def test_gate_concurrent_same_request_id_one_wins_others_replay() -> None:
    """When 20 workers race the same request_id, exactly 1 wins and 19 are dedup'd."""
    gate = _gate()
    rid = "duplicate-rid-shared"
    results: list[Any] = []
    rejections: list[Any] = []
    lock = threading.Lock()

    def worker() -> None:
        try:
            out = gate.check(_ok_envelope(request_id=rid))
            with lock:
                results.append(out)
        except IngressRejected as exc:
            with lock:
                rejections.append(exc.slip.reason_code)

    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(results) == 1
    assert len(rejections) == 19
    assert all(c is RejectionReasonCode.REPLAY_DUPLICATE for c in rejections)


# ---------------------------------------------------------------------------
# Rate limiter — quota verdict path
# ---------------------------------------------------------------------------


def test_rate_limiter_first_call_passes_then_blocks() -> None:
    cfg = TokenBucketConfig(capacity=1, refill_per_second=0)
    gate = _gate(rate_limiter=TokenBucketRateLimiter(cfg))
    out = gate.check(_ok_envelope(request_id="r-1"))
    assert isinstance(out, StampedRequest)
    assert out.quota_verdict == "allowed"
    with pytest.raises(IngressRejected) as exc:
        gate.check(_ok_envelope(request_id="r-2"))
    assert exc.value.slip.reason_code is RejectionReasonCode.RATE_LIMITED


def test_rate_limit_per_caller_isolated() -> None:
    cfg = TokenBucketConfig(capacity=1, refill_per_second=0)
    gate = _gate(rate_limiter=TokenBucketRateLimiter(cfg))
    out_a = gate.check(_ok_envelope(caller_identity="user-a", request_id="r-1"))
    assert isinstance(out_a, StampedRequest)
    # Different caller — independent bucket — should pass.
    out_b = gate.check(_ok_envelope(caller_identity="user-b", request_id="r-2"))
    assert isinstance(out_b, StampedRequest)


# ---------------------------------------------------------------------------
# Order-of-operations: schema check fires before identity for missing fields
# ---------------------------------------------------------------------------


def test_schema_check_fires_before_identity() -> None:
    """Missing schema_version must trip E2 even if identity is also missing."""
    bad = {"caller_identity": "", "request_payload": {"intent": "x"}}
    gate = _gate()
    with pytest.raises(IngressRejected) as exc:
        gate.check(bad)
    assert exc.value.slip.reason_code is RejectionReasonCode.SCHEMA_INVALID


def test_attachments_check_fires_before_identity() -> None:
    """Bad attachment shape on a verified request must still trip E2_ATTACHMENT."""
    with pytest.raises(IngressRejected) as exc:
        _gate().check(_ok_envelope(attachments="not-a-list"))
    assert exc.value.slip.reason_code is RejectionReasonCode.ATTACHMENT_MALFORMED


# ---------------------------------------------------------------------------
# Determinism — identical request returns identical raw_payload_ref + manifest
# ---------------------------------------------------------------------------


def test_identical_envelope_yields_identical_manifest_and_ref() -> None:
    atts = [{"filename": "a.txt", "size": 4}]
    a = _gate().check(_ok_envelope(attachments=atts, request_id="r-a"))
    b = _gate().check(_ok_envelope(attachments=atts, request_id="r-b"))
    assert isinstance(a, StampedRequest) and isinstance(b, StampedRequest)
    assert a.raw_payload_ref == b.raw_payload_ref
    assert a.attachment_manifest == b.attachment_manifest


# ---------------------------------------------------------------------------
# IdentityVerifier protocol — default Noop tags the source as anonymous when
# caller_identity itself is *-anon (regression for verified-id preference)
# ---------------------------------------------------------------------------


def test_default_noop_verifier_anonymous_caller_yields_anonymous_verdict() -> None:
    out = _gate().check(_ok_envelope(caller_identity="webhook-anon"))
    assert isinstance(out, StampedRequest)
    assert out.auth_verdict == "anonymous"
