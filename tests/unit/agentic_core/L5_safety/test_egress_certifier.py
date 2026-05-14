"""W3 tests for EgressCertifier interface and MetadataOnlyEgressCertifier.

Covers:
  - Interface exists and is a runtime-checkable Protocol
  - certify_egress() returns EgressCertificationReceipt
  - Valid metadata-only input succeeds
  - Missing redaction_policy_ref fails closed
  - Invalid request_digest format fails
  - Invalid response_digest format fails
  - Raw prompt field rejected
  - Raw response field rejected
  - Provider SDK imports absent from source
  - No network/filesystem behavior in source
  - No app literals in source
  - No runtime disposition tokens in source
  - MetadataOnlyEgressCertifier satisfies EgressCertifier protocol
  - concrete provider_ref rejected
  - Unknown egress_status fails closed
  - Known egress_status variants accepted
  - W2 producer tests still pass (import smoke)
  - W1 contract tests still pass (import smoke)
"""
from __future__ import annotations

import ast
import importlib
import inspect
import pathlib

import pytest

from agentic_core.L5_safety.certification.egress_certifier import (
    EgressCertifier,
    MetadataOnlyEgressCertifier,
    _ALLOWED_EGRESS_STATUSES,
    _check_no_raw_payload,
)
from agentic_core.L5_safety.contracts.l5_certification_contracts import (
    EgressCertificationReceipt,
)
from agentic_core.L5_safety.exceptions import (
    L5CertificationError,
    L5DigestMismatchError,
    L5MalformedReceiptError,
)

_REPO_ROOT = pathlib.Path(__file__).parent.parent.parent.parent.parent
_EGRESS_SRC = (
    _REPO_ROOT
    / "agentic_core"
    / "L5_safety"
    / "certification"
    / "egress_certifier.py"
)
_INIT_SRC = (
    _REPO_ROOT
    / "agentic_core"
    / "L5_safety"
    / "certification"
    / "__init__.py"
)

_VALID_DIGEST = "a" * 64
_VALID_DIGEST2 = "b" * 64


def _make_certifier() -> MetadataOnlyEgressCertifier:
    return MetadataOnlyEgressCertifier()


def _valid_kwargs(**overrides) -> dict:
    base = dict(
        provider_ref="urn:provider:governed-gateway:v1",
        call_purpose_ref="urn:purpose:resume-generation:v1",
        request_digest=_VALID_DIGEST,
        response_digest=_VALID_DIGEST2,
        redaction_policy_ref="urn:policy:redaction:standard:v2",
        egress_status="EGRESS_CERTIFIED",
    )
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Interface existence
# ---------------------------------------------------------------------------


class TestEgressCertifierInterface:
    def test_interface_is_importable(self):
        from agentic_core.L5_safety.certification import egress_certifier as mod

        assert hasattr(mod, "EgressCertifier")
        assert hasattr(mod, "MetadataOnlyEgressCertifier")

    def test_egress_certifier_is_protocol(self):
        assert hasattr(EgressCertifier, "__protocol_attrs__") or (
            hasattr(EgressCertifier, "_is_protocol") or
            hasattr(EgressCertifier, "_is_runtime_protocol")
        )

    def test_egress_certifier_has_certify_egress_method(self):
        assert callable(getattr(EgressCertifier, "certify_egress", None))

    def test_metadata_only_satisfies_protocol(self):
        certifier = _make_certifier()
        assert isinstance(certifier, EgressCertifier)

    def test_package_init_exports_egress_certifier(self):
        from agentic_core.L5_safety.certification import (
            EgressCertifier as EC,
            MetadataOnlyEgressCertifier as MOC,
        )

        assert EC is EgressCertifier
        assert MOC is MetadataOnlyEgressCertifier


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------


class TestMetadataOnlyCertifierHappyPath:
    def test_valid_input_returns_egress_certification_receipt(self):
        cert = _make_certifier()
        result = cert.certify_egress(**_valid_kwargs())
        assert isinstance(result, EgressCertificationReceipt)

    def test_certified_true_when_status_egress_certified(self):
        cert = _make_certifier()
        result = cert.certify_egress(**_valid_kwargs(egress_status="EGRESS_CERTIFIED"))
        assert result.certified is True

    def test_certified_false_when_status_not_certified(self):
        cert = _make_certifier()
        result = cert.certify_egress(
            **_valid_kwargs(egress_status="EGRESS_NOT_CERTIFIED")
        )
        assert result.certified is False

    def test_provider_ref_preserved(self):
        cert = _make_certifier()
        result = cert.certify_egress(**_valid_kwargs())
        assert result.provider_ref == "urn:provider:governed-gateway:v1"

    def test_redaction_policy_ref_preserved(self):
        cert = _make_certifier()
        result = cert.certify_egress(**_valid_kwargs())
        assert result.redaction_policy_ref == "urn:policy:redaction:standard:v2"

    def test_response_digest_preserved(self):
        cert = _make_certifier()
        result = cert.certify_egress(**_valid_kwargs())
        assert result.response_digest == _VALID_DIGEST2

    def test_optional_fields_accepted(self):
        cert = _make_certifier()
        result = cert.certify_egress(
            **_valid_kwargs(
                l5_governance_context_digest="c" * 64,
                redaction_receipt_ref="urn:receipt:redaction:abc123",
                egress_policy_ref="urn:policy:egress:v3",
                schema_version="v1.0",
                notes="test run",
            )
        )
        assert isinstance(result, EgressCertificationReceipt)

    def test_all_known_egress_statuses_accepted(self):
        cert = _make_certifier()
        for status in _ALLOWED_EGRESS_STATUSES:
            result = cert.certify_egress(**_valid_kwargs(egress_status=status))
            assert isinstance(result, EgressCertificationReceipt)

    def test_empty_optional_fields_accepted(self):
        cert = _make_certifier()
        result = cert.certify_egress(
            **_valid_kwargs(
                l5_governance_context_digest="",
                redaction_receipt_ref="",
                egress_policy_ref="",
                schema_version="",
                notes="",
            )
        )
        assert isinstance(result, EgressCertificationReceipt)


# ---------------------------------------------------------------------------
# Fail-closed: missing required fields
# ---------------------------------------------------------------------------


class TestMetadataOnlyCertifierFailClosed:
    def test_missing_redaction_policy_ref_fails_closed(self):
        cert = _make_certifier()
        with pytest.raises(L5CertificationError):
            cert.certify_egress(**_valid_kwargs(redaction_policy_ref=""))

    def test_missing_response_digest_fails_closed(self):
        cert = _make_certifier()
        with pytest.raises(L5CertificationError):
            cert.certify_egress(**_valid_kwargs(response_digest=""))

    def test_missing_provider_ref_fails_closed(self):
        cert = _make_certifier()
        with pytest.raises(L5MalformedReceiptError):
            cert.certify_egress(**_valid_kwargs(provider_ref=""))

    def test_invalid_response_digest_format_fails(self):
        cert = _make_certifier()
        with pytest.raises(L5DigestMismatchError):
            cert.certify_egress(**_valid_kwargs(response_digest="not-a-digest"))

    def test_invalid_request_digest_format_fails(self):
        cert = _make_certifier()
        with pytest.raises(L5DigestMismatchError):
            cert.certify_egress(**_valid_kwargs(request_digest="short"))

    def test_invalid_governance_context_digest_format_fails(self):
        cert = _make_certifier()
        with pytest.raises(L5DigestMismatchError):
            cert.certify_egress(
                **_valid_kwargs(l5_governance_context_digest="UPPERCASE" * 8)
            )

    def test_uppercase_response_digest_rejected(self):
        cert = _make_certifier()
        with pytest.raises(L5DigestMismatchError):
            cert.certify_egress(**_valid_kwargs(response_digest="A" * 64))

    def test_unknown_egress_status_fails_closed(self):
        cert = _make_certifier()
        with pytest.raises(L5MalformedReceiptError):
            cert.certify_egress(**_valid_kwargs(egress_status="ALLOW"))

    def test_runtime_disposition_as_egress_status_fails_closed(self):
        cert = _make_certifier()
        with pytest.raises(L5MalformedReceiptError):
            cert.certify_egress(**_valid_kwargs(egress_status="DENY"))


# ---------------------------------------------------------------------------
# Concrete provider_ref rejection
# ---------------------------------------------------------------------------


class TestProviderRefSymbolicEnforcement:
    @pytest.mark.parametrize(
        "bad_ref",
        [
            "openai",
            "anthropic",
            "boto3",
            "gpt-4",
            "claude-3",
            "https://api.openai.com/v1",
            "http://localhost:8000/v1",
            "gemini-pro",
        ],
    )
    def test_concrete_provider_ref_rejected(self, bad_ref):
        cert = _make_certifier()
        with pytest.raises(L5MalformedReceiptError):
            cert.certify_egress(**_valid_kwargs(provider_ref=bad_ref))

    def test_symbolic_urn_accepted(self):
        cert = _make_certifier()
        result = cert.certify_egress(
            **_valid_kwargs(provider_ref="urn:provider:internal-gateway:v2")
        )
        assert isinstance(result, EgressCertificationReceipt)

    def test_symbolic_registry_key_accepted(self):
        cert = _make_certifier()
        result = cert.certify_egress(
            **_valid_kwargs(provider_ref="governed-gateway/qwen-32b-awq/v1")
        )
        assert isinstance(result, EgressCertificationReceipt)


# ---------------------------------------------------------------------------
# Raw payload rejection
# ---------------------------------------------------------------------------


class TestRawPayloadRejection:
    def test_raw_prompt_field_name_rejected(self):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({"prompt": "some raw prompt text"})

    def test_raw_response_field_name_rejected(self):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({"response": "some raw response text"})

    def test_raw_prompt_text_field_rejected(self):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({"prompt_text": "text here"})

    def test_raw_response_text_field_rejected(self):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({"response_text": "text here"})

    def test_completion_field_rejected(self):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({"completion": "text here"})

    def test_system_prompt_field_rejected(self):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({"system_prompt": "you are an assistant"})

    def test_clean_metadata_fields_pass(self):
        _check_no_raw_payload(
            {
                "provider_ref": "urn:p:v1",
                "request_digest": _VALID_DIGEST,
                "response_digest": _VALID_DIGEST2,
                "redaction_policy_ref": "urn:pol:v1",
            }
        )


# ---------------------------------------------------------------------------
# Source-level boundary checks
# ---------------------------------------------------------------------------


class TestSourceBoundaryChecks:
    def _source_text(self) -> str:
        return _EGRESS_SRC.read_text(encoding="utf-8")

    def _init_text(self) -> str:
        return _INIT_SRC.read_text(encoding="utf-8")

    def test_no_openai_import_in_source(self):
        src = self._source_text()
        assert "openai" not in src

    def test_no_anthropic_import_in_source(self):
        src = self._source_text()
        assert "anthropic" not in src

    def test_no_boto3_import_in_source(self):
        src = self._source_text()
        assert "boto3" not in src

    def test_no_httpx_import_in_source(self):
        src = self._source_text()
        assert "httpx" not in src

    def test_no_requests_import_in_source(self):
        src = self._source_text()
        assert "requests" not in src

    def test_no_socket_import_in_source(self):
        src = self._source_text()
        tree = ast.parse(src)
        imported = {
            node.names[0].name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        assert "socket" not in imported

    def test_no_urllib_open_in_source(self):
        src = self._source_text()
        assert "urllib.request.urlopen" not in src
        assert "urlopen(" not in src

    def test_no_open_filesystem_call_in_source(self):
        src = self._source_text()
        assert "open(" not in src
        assert "pathlib.Path(" not in src

    def test_no_apps_literals_in_source(self):
        src = self._source_text()
        for literal in ("apps_rg", "apps_research", "apps_lic", "apps_qna"):
            assert literal not in src

    def test_no_runtime_disposition_tokens_in_source(self):
        src = self._source_text()
        forbidden = (
            "GateVerdict",
            "CommitRequest",
            "L5_CERTIFICATION_READY",
            "allow_l2_execution",
            "allow_model_call",
            "allow_tool_call",
            "require_HITL",
            "downstream_disposition",
        )
        for token in forbidden:
            assert token not in src, f"Forbidden token {token!r} found in source"

    def test_no_w3_interface_in_w2_producer_source(self):
        producer_src = (
            _REPO_ROOT
            / "agentic_core"
            / "L5_safety"
            / "certification"
            / "l5_packet_producer.py"
        ).read_text(encoding="utf-8")
        assert "EgressCertifier" not in producer_src
        assert "certify_egress" not in producer_src

    def test_init_exports_w3_classes(self):
        init = self._init_text()
        assert "EgressCertifier" in init
        assert "MetadataOnlyEgressCertifier" in init

    def test_no_network_call_patterns_in_source(self):
        src = self._source_text()
        for pattern in ("connect(", "send(", "recv(", "fetch(", "post(", "get("):
            assert pattern not in src

    def test_no_resume_cv_literals_in_source(self):
        src = self._source_text()
        assert "resume" not in src.lower().replace("redaction_receipt_ref", "")
        assert " CV " not in src


# ---------------------------------------------------------------------------
# W2 and W1 regression smoke
# ---------------------------------------------------------------------------


class TestW2W1RegressionSmoke:
    def test_w2_producer_importable(self):
        from agentic_core.L5_safety.certification.l5_packet_producer import (
            L5PacketProducer,
        )

        assert callable(L5PacketProducer)

    def test_w1_contracts_importable(self):
        from agentic_core.L5_safety.contracts.l5_certification_contracts import (
            ChildCertifierReceipt,
            EgressCertificationReceipt,
            L5CertificationPacket,
        )

        assert ChildCertifierReceipt
        assert EgressCertificationReceipt
        assert L5CertificationPacket

    def test_exceptions_importable(self):
        from agentic_core.L5_safety.exceptions import (
            L5CertificationError,
            L5AuthorityWideningError,
            L5DigestMismatchError,
            L5MalformedReceiptError,
        )

        assert issubclass(L5AuthorityWideningError, L5CertificationError)
        assert issubclass(L5DigestMismatchError, L5CertificationError)
        assert issubclass(L5MalformedReceiptError, L5CertificationError)


# ---------------------------------------------------------------------------
# W4 — Egress receipt is frozen (immutable after construction)
# ---------------------------------------------------------------------------


class TestW4EgressReceiptFrozen:
    def test_returned_receipt_is_frozen(self):
        import dataclasses
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(**_valid_kwargs())
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            result.provider_ref = "mutated"  # type: ignore[misc]

    def test_returned_receipt_has_no_dict(self):
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(**_valid_kwargs())
        assert not hasattr(result, "__dict__"), (
            "EgressCertificationReceipt with slots=True must not have __dict__"
        )

    def test_certified_field_immutable(self):
        import dataclasses
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(**_valid_kwargs(egress_status="EGRESS_CERTIFIED"))
        with pytest.raises((dataclasses.FrozenInstanceError, AttributeError)):
            result.certified = False  # type: ignore[misc]


# ---------------------------------------------------------------------------
# W4 — Optional digest fields accepted when empty
# ---------------------------------------------------------------------------


class TestW4OptionalDigestFieldsAccepted:
    def test_empty_request_digest_accepted(self):
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(**_valid_kwargs(request_digest=""))
        assert isinstance(result, EgressCertificationReceipt)

    def test_empty_l5_governance_context_digest_accepted(self):
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(**_valid_kwargs(l5_governance_context_digest=""))
        assert isinstance(result, EgressCertificationReceipt)

    def test_valid_request_digest_64_hex_accepted(self):
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(**_valid_kwargs(request_digest="c" * 64))
        assert isinstance(result, EgressCertificationReceipt)

    def test_valid_l5_governance_context_digest_accepted(self):
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(**_valid_kwargs(l5_governance_context_digest="d" * 64))
        assert isinstance(result, EgressCertificationReceipt)


# ---------------------------------------------------------------------------
# W4 — Extended concrete provider_ref parametrization
# ---------------------------------------------------------------------------


class TestW4ExtendedProviderRefRejection:
    @pytest.mark.parametrize(
        "bad_ref",
        [
            "mistral-7b",
            "llama-3-70b",
            "https://api.anthropic.com/v1",
            "http://api.openai.com",
        ],
    )
    def test_extended_concrete_refs_rejected(self, bad_ref: str):
        cert = MetadataOnlyEgressCertifier()
        with pytest.raises(L5MalformedReceiptError):
            cert.certify_egress(**_valid_kwargs(provider_ref=bad_ref))

    def test_governed_gateway_slash_ref_accepted(self):
        cert = MetadataOnlyEgressCertifier()
        result = cert.certify_egress(
            **_valid_kwargs(provider_ref="governed-gateway/model-ref/v2")
        )
        assert isinstance(result, EgressCertificationReceipt)


# ---------------------------------------------------------------------------
# W4 — Extended raw payload field name coverage
# ---------------------------------------------------------------------------


class TestW4ExtendedRawPayloadRejection:
    @pytest.mark.parametrize(
        "field_name",
        [
            "raw_prompt",
            "raw_response",
            "message_content",
            "user_message",
        ],
    )
    def test_extended_raw_payload_fields_rejected(self, field_name: str):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({field_name: "some content here"})

    def test_multiple_raw_fields_rejected(self):
        with pytest.raises(L5MalformedReceiptError, match="raw payload"):
            _check_no_raw_payload({"prompt": "x", "response": "y"})

    def test_empty_dict_accepted(self):
        _check_no_raw_payload({})

    def test_metadata_only_dict_accepted(self):
        _check_no_raw_payload({
            "provider_ref": "urn:p:v1",
            "call_purpose_ref": "urn:purpose:v1",
            "request_digest": _VALID_DIGEST,
            "response_digest": _VALID_DIGEST2,
            "redaction_policy_ref": "urn:pol:v1",
            "egress_status": "EGRESS_CERTIFIED",
        })


# ---------------------------------------------------------------------------
# W4 — Source has no pathlib/os/subprocess/shutil (no filesystem/network)
# ---------------------------------------------------------------------------


class TestW4SourceNoFilesystemNetworkImports:
    def _src(self) -> str:
        return _EGRESS_SRC.read_text(encoding="utf-8")

    def test_no_pathlib_import(self):
        src = self._src()
        assert "import pathlib" not in src
        assert "pathlib.Path" not in src

    def test_no_os_import(self):
        import ast
        tree = ast.parse(self._src())
        imported = {
            node.names[0].name
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
        }
        assert "os" not in imported
        assert "os.path" not in imported

    def test_no_subprocess_import(self):
        src = self._src()
        assert "subprocess" not in src

    def test_no_shutil_import(self):
        src = self._src()
        assert "shutil" not in src

    def test_no_tempfile_import(self):
        src = self._src()
        assert "tempfile" not in src

    def test_no_json_import(self):
        src = self._src()
        assert "import json" not in src

    def test_no_threading_import(self):
        src = self._src()
        assert "threading" not in src


# ---------------------------------------------------------------------------
# W4 — egress_status vocabulary is exactly the declared frozenset
# ---------------------------------------------------------------------------


class TestW4EgressStatusVocabulary:
    def test_allowed_statuses_has_exactly_four_members(self):
        assert len(_ALLOWED_EGRESS_STATUSES) == 4

    def test_allowed_statuses_contains_expected_values(self):
        expected = {
            "EGRESS_CERTIFIED",
            "EGRESS_NOT_CERTIFIED",
            "EGRESS_PENDING_REVIEW",
            "EGRESS_GAP_EVIDENCE",
        }
        assert _ALLOWED_EGRESS_STATUSES == expected

    def test_certified_true_only_for_egress_certified(self):
        cert = MetadataOnlyEgressCertifier()
        for status in _ALLOWED_EGRESS_STATUSES:
            result = cert.certify_egress(**_valid_kwargs(egress_status=status))
            expected_certified = status == "EGRESS_CERTIFIED"
            assert result.certified == expected_certified, (
                f"egress_status={status!r} must yield certified={expected_certified}, "
                f"got certified={result.certified}"
            )

    @pytest.mark.parametrize("bad_status", [
        "L5_CERTIFIED", "L5_NOT_CERTIFIED", "ALLOW", "DENY",
        "EGRESS_APPROVED", "UNKNOWN", "",
    ])
    def test_non_vocabulary_egress_status_fails_closed(self, bad_status: str):
        cert = MetadataOnlyEgressCertifier()
        with pytest.raises(L5MalformedReceiptError):
            cert.certify_egress(**_valid_kwargs(egress_status=bad_status))
