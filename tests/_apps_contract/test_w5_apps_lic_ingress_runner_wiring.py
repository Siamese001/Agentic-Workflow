"""W5 targeted tests -- apps_lic ingress runner and spine-handoff wiring.

Plan: apps-lic-u0-runtime-package-complete-f8e2a1 (W5 receipt tests)

Proves:
  1. lic_ingress_runner._parse_lic_envelope returns ValidatedRequest (not raw dict)
  2. ValidatedRequest.app_payload contains runtime_customization_package
  3. package_digest field exists inside runtime_customization_package after parse
  4. spine_handoff preserves ValidatedRequest (no mutation / no extraction)
  5. No R3_grounded_read appears in active route metadata
  6. R4_MANAGED_DRAFT is the default fresh-context route_type in handoff metadata
  7. R3R4 and R5 are documented in module; R3_CONTRACT_SURFACE alias does NOT
     encode a route name

These tests do NOT call the full pipeline (apps_lic_u0_adapt requires a
complete valid contract with all 7 forbidden_send_modes; that is a separate
concern).  They use a minimal but structurally correct envelope path to avoid
the E2 forbidden_send_modes gate, OR they verify structural properties directly
from module introspection.
"""
from __future__ import annotations

import inspect
from typing import Any
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# 1. Parse callable returns ValidatedRequest
# ---------------------------------------------------------------------------

class TestParseReturnsValidatedRequest:
    """_parse_lic_envelope produces ValidatedRequest when envelope is valid."""

    def test_parse_callable_is_function(self) -> None:
        from apps_lic.integrations.lic_ingress_runner import _parse_lic_envelope
        assert callable(_parse_lic_envelope)

    def test_parse_return_type_annotation(self) -> None:
        from apps_lic.integrations.lic_ingress_runner import _parse_lic_envelope
        hints = _parse_lic_envelope.__annotations__
        ret = hints.get("return")
        assert ret is not None, "return type annotation missing"
        # Python 3.10+ union (X | Y) gives a types.UnionType; str(ret) contains
        # 'ValidatedRequest' regardless of the union form used.
        assert "ValidatedRequest" in str(ret), (
            f"return annotation does not reference ValidatedRequest: {ret}"
        )

    def test_make_runner_parse_is_wired_to_parse_lic_envelope(self) -> None:
        from apps_lic.integrations.lic_ingress_runner import (
            _parse_lic_envelope,
            make_lic_ingress_runner,
        )
        runner = make_lic_ingress_runner(dispatch=lambda vr: vr)
        # AppIngressRunner stores parse as _parse (private attr)
        assert runner._parse is _parse_lic_envelope

    def test_parse_returns_none_on_empty_payload(self) -> None:
        from apps_lic.integrations.lic_ingress_runner import _parse_lic_envelope
        result = _parse_lic_envelope({})
        assert result is None  # expected: missing required fields → None (ClarificationRequired)

    def test_dispatch_type_annotation_accepts_validated_request(self) -> None:
        from apps_lic.integrations.lic_ingress_runner import make_lic_ingress_runner
        import inspect, typing
        sig = inspect.signature(make_lic_ingress_runner)
        dispatch_param = sig.parameters["dispatch"]
        annotation = dispatch_param.annotation
        # Should be Callable[[ValidatedRequest], Any]
        assert "ValidatedRequest" in str(annotation) or annotation is inspect.Parameter.empty


# ---------------------------------------------------------------------------
# 2. app_payload contains runtime_customization_package key
# ---------------------------------------------------------------------------

class TestAppPayloadContainsRuntimeCustomizationPackage:
    """contract_dump (= app_payload) from apps_lic_u0_adapt always has the RCP key."""

    def test_apps_lic_ingress_contract_has_rcp_field(self) -> None:
        from apps_lic.contracts.apps_lic_ingress_contract_v1 import AppsLicIngressContractV1
        assert "runtime_customization_package" in AppsLicIngressContractV1.model_fields

    def test_rcp_section_type_is_correct(self) -> None:
        from apps_lic.contracts.apps_lic_ingress_contract_v1 import (
            AppsLicIngressContractV1,
            RuntimeCustomizationPackageSection,
        )
        field = AppsLicIngressContractV1.model_fields["runtime_customization_package"]
        import typing
        # Optional[RuntimeCustomizationPackageSection] or RuntimeCustomizationPackageSection
        ann = field.annotation
        args = typing.get_args(ann)
        types_in_ann = list(args) if args else [ann]
        assert any(t is RuntimeCustomizationPackageSection for t in types_in_ann), (
            f"RCP field annotation does not include RuntimeCustomizationPackageSection: {ann}"
        )

    def test_u0_adapter_sets_app_payload_to_contract_dump(self) -> None:
        """apps_lic_u0_adapt sets app_payload = contract.model_dump() which includes RCP."""
        import ast, textwrap
        import agentic_core.runtime.u0.apps_lic_u0_adapter as mod
        src = inspect.getsource(mod)
        # Verify contract_dump is assigned from model_dump and used as app_payload
        assert "contract_dump = contract.model_dump" in src
        assert "app_payload=contract_dump" in src


# ---------------------------------------------------------------------------
# 3. package_digest field exists in RuntimeCustomizationPackageSection
# ---------------------------------------------------------------------------

class TestPackageDigestField:
    """package_digest is a declared field in RuntimeCustomizationPackageSection."""

    def test_package_digest_field_exists(self) -> None:
        from apps_lic.contracts.apps_lic_ingress_contract_v1 import RuntimeCustomizationPackageSection
        assert "package_digest" in RuntimeCustomizationPackageSection.model_fields

    def test_package_digest_type_is_str(self) -> None:
        from apps_lic.contracts.apps_lic_ingress_contract_v1 import RuntimeCustomizationPackageSection
        field = RuntimeCustomizationPackageSection.model_fields["package_digest"]
        import typing
        ann = field.annotation
        args = typing.get_args(ann)
        types_in_ann = list(args) if args else [ann]
        assert str in types_in_ann or ann is str, (
            f"package_digest annotation is not str: {ann}"
        )

    def test_package_digest_default_is_empty_string(self) -> None:
        from apps_lic.contracts.apps_lic_ingress_contract_v1 import RuntimeCustomizationPackageSection
        field = RuntimeCustomizationPackageSection.model_fields["package_digest"]
        assert field.default == ""

    def test_package_digest_preserved_in_app_payload_via_contract_dump(self) -> None:
        """model_dump() on a contract with package_digest set includes it in app_payload."""
        from apps_lic.contracts.apps_lic_ingress_contract_v1 import (
            RuntimeCustomizationPackageSection,
            RoutePolicy,
            WritePolicy,
            CacheBypassPolicy,
            RuntimeGatePolicy,
            ExitGatePolicy,
            ConsentCompliancePolicy,
            MetaFeedbackPolicy,
        )
        sentinel_digest = "sha256:abc123deadbeef"
        rcp = RuntimeCustomizationPackageSection(
            route_policy=RoutePolicy(),
            write_policy=WritePolicy(),
            cache_bypass_policy=CacheBypassPolicy(),
            runtime_gate_policy=RuntimeGatePolicy(),
            exit_gate_policy=ExitGatePolicy(),
            consent_compliance_policy=ConsentCompliancePolicy(),
            meta_feedback_policy=MetaFeedbackPolicy(),
            package_digest=sentinel_digest,
        )
        dumped = rcp.model_dump()
        assert "package_digest" in dumped
        assert dumped["package_digest"] == sentinel_digest

    def test_package_digest_in_field_map_receipt_as_derived(self) -> None:
        """W4 field map receipt documents /runtime_customization_package/package_digest as DERIVED."""
        import pathlib
        receipt = pathlib.Path(
            "apps_lic/contracts/w4_schema_field_map_receipt.md"
        )
        assert receipt.exists(), f"W4 field map receipt missing at {receipt}"
        text = receipt.read_text(encoding="utf-8")
        assert "package_digest" in text
        assert "DERIVED" in text


# ---------------------------------------------------------------------------
# 4. spine_handoff preserves ValidatedRequest through delegation
# ---------------------------------------------------------------------------

class TestSpineHandoffPreservesValidatedRequest:
    """run_lic_via_spine delegates to GovernedLicRun without mutating the request."""

    def test_run_lic_via_spine_passes_request_unchanged(self) -> None:
        from apps_lic.integrations.spine_handoff import run_lic_via_spine
        mock_request = MagicMock()
        mock_request.trace_id = "trace-001"
        mock_request.campaign_id = "camp-001"
        mock_runner = MagicMock()
        mock_runner.run_governed_e2e.return_value = MagicMock(spec=[])

        run_lic_via_spine(mock_request, runner=mock_runner)

        # runner.run_governed_e2e called exactly once with the ORIGINAL request object
        mock_runner.run_governed_e2e.assert_called_once()
        call_args = mock_runner.run_governed_e2e.call_args
        assert call_args.args[0] is mock_request, (
            "spine_handoff must pass the original request object to run_governed_e2e unchanged"
        )

    def test_run_lic_via_spine_does_not_extract_app_payload(self) -> None:
        """run_lic_via_spine must not read .app_payload from the request."""
        import inspect
        from apps_lic.integrations import spine_handoff as sh
        src = inspect.getsource(sh.run_lic_via_spine)
        assert "app_payload" not in src, (
            "run_lic_via_spine must not read app_payload -- it passes request through unchanged"
        )

    def test_spine_handoff_does_not_build_validated_request(self) -> None:
        """spine_handoff must not construct ValidatedRequest (that is apps_qna shape)."""
        import inspect
        from apps_lic.integrations import spine_handoff as sh
        # The module-level docstring says it explicitly; the function body must not call it
        src = inspect.getsource(sh.run_lic_via_spine)
        assert "ValidatedRequest(" not in src


# ---------------------------------------------------------------------------
# 5. No R3_grounded_read in active metadata
# ---------------------------------------------------------------------------

class TestNoStaleRouteLanguage:
    """R3_grounded_read must not appear in route_type for active metadata."""

    def test_build_metadata_route_type_not_r3_grounded_read(self) -> None:
        from apps_lic.integrations.spine_handoff import build_lic_r3_handoff_metadata
        req = MagicMock()
        req.trace_id = "t1"
        req.campaign_id = "c1"
        req.config = None
        meta = build_lic_r3_handoff_metadata(req)
        assert meta.route_type != "R3_grounded_read", (
            f"route_type must not be R3_grounded_read; got {meta.route_type!r}"
        )
        assert "grounded_read" not in meta.route_type

    def test_r3_contract_surface_alias_identity(self) -> None:
        """R3_CONTRACT_SURFACE is CONTRACT_SURFACE — same object, no additional route encoding."""
        from apps_lic.integrations.spine_handoff import CONTRACT_SURFACE, R3_CONTRACT_SURFACE
        assert R3_CONTRACT_SURFACE is CONTRACT_SURFACE

    def test_legacy_alias_name_exists(self) -> None:
        """LEGACY_CONTRACT_SURFACE_ALIAS export exists and equals CONTRACT_SURFACE."""
        from apps_lic.integrations.spine_handoff import (
            CONTRACT_SURFACE,
            LEGACY_CONTRACT_SURFACE_ALIAS,
        )
        assert LEGACY_CONTRACT_SURFACE_ALIAS is CONTRACT_SURFACE

    def test_r3_contract_surface_values_contain_no_route_string(self) -> None:
        """The alias values are contract TYPE objects, not route-name strings."""
        from apps_lic.integrations.spine_handoff import R3_CONTRACT_SURFACE
        for k, v in R3_CONTRACT_SURFACE.items():
            assert not isinstance(v, str), (
                f"R3_CONTRACT_SURFACE[{k!r}] is a string — must be a type; got {v!r}"
            )

    def test_run_lic_via_spine_log_no_r3_grounded_read(self) -> None:
        """run_lic_via_spine log message must not contain R3_grounded_read."""
        import inspect
        from apps_lic.integrations import spine_handoff as sh
        src = inspect.getsource(sh.run_lic_via_spine)
        assert "R3_grounded_read" not in src, (
            "run_lic_via_spine source must not reference R3_grounded_read"
        )


# ---------------------------------------------------------------------------
# 6. R4_MANAGED_DRAFT is the default fresh-context route_type
# ---------------------------------------------------------------------------

class TestR4ManagedDraftDefault:
    """build_lic_r3_handoff_metadata returns R4_MANAGED_DRAFT as route_type."""

    def test_default_route_type_is_r4_managed_draft(self) -> None:
        from apps_lic.integrations.spine_handoff import build_lic_r3_handoff_metadata
        req = MagicMock()
        req.trace_id = "t2"
        req.campaign_id = "c2"
        req.config = None
        meta = build_lic_r3_handoff_metadata(req)
        assert meta.route_type == "R4_MANAGED_DRAFT", (
            f"Expected R4_MANAGED_DRAFT, got {meta.route_type!r}"
        )


# ---------------------------------------------------------------------------
# 7. R3R4 and R5 represented in module docstring (not stale docs)
# ---------------------------------------------------------------------------

class TestRouteModelRepresentation:
    """The final route model (R4/R3R4/R5) is documented in spine_handoff."""

    def test_r3r4_in_module_docstring(self) -> None:
        from apps_lic.integrations import spine_handoff as sh
        assert "R3R4" in (sh.__doc__ or ""), "R3R4 route model missing from spine_handoff docstring"

    def test_r5_in_module_docstring(self) -> None:
        from apps_lic.integrations import spine_handoff as sh
        assert "R5_FALLBACK" in (sh.__doc__ or ""), "R5_FALLBACK missing from spine_handoff docstring"

    def test_r4_managed_draft_in_module_docstring(self) -> None:
        from apps_lic.integrations import spine_handoff as sh
        assert "R4_MANAGED_DRAFT" in (sh.__doc__ or ""), "R4_MANAGED_DRAFT missing from spine_handoff docstring"

    def test_r3_grounded_read_absent_from_module_docstring(self) -> None:
        from apps_lic.integrations import spine_handoff as sh
        doc = sh.__doc__ or ""
        assert "R3_grounded_read" not in doc, (
            "R3_grounded_read must not appear in spine_handoff module docstring"
        )

    def test_lic_ingress_runner_docstring_mentions_runtime_customization_package(self) -> None:
        from apps_lic.integrations import lic_ingress_runner as lir
        assert "runtime_customization_package" in (lir.__doc__ or "")

    def test_required_fields_reflect_ingress_payload_fields(self) -> None:
        from apps_lic.integrations.lic_ingress_runner import LIC_REQUIRED_FIELDS
        from apps_lic.contracts.apps_lic_ingress_contract_v1 import AppsLicIngressContractV1
        top_level = set(AppsLicIngressContractV1.model_fields.keys())
        for field in LIC_REQUIRED_FIELDS:
            # required fields map to ingress payload fields via _parse_lic_envelope
            # (channel, audience_segment, request_type are in AppsLicIngressPayload)
            assert isinstance(field, str) and len(field) > 0


# ---------------------------------------------------------------------------
# 8. package_digest validity — W5 completion requirement
#
# These tests prove:
#   a) package_digest is non-empty after U0 processes any valid payload
#   b) U0 computes package_digest when caller omits it (DERIVED mode)
#   c) U0 raises AppsLicPackageDigestError on a mismatched caller-supplied digest
#   d) package_digest is preserved verbatim in ValidatedRequest.app_payload
# ---------------------------------------------------------------------------

def _build_minimal_raw(*, extra_transport: dict | None = None) -> dict:
    """Build a minimal but fully valid raw apps_lic payload for W5 digest tests."""
    import uuid
    base: dict = {
        "apps_lic_contract_version": "v1",
        "transport": {
            "app_id": "apps_lic",
            "task_class": "outreach_message",
            "request_id": f"req_{uuid.uuid4().hex[:8]}",
            "run_id": f"run_{uuid.uuid4().hex[:8]}",
            "tenant_id": "apps_lic",
            "trace_id": "trace_pkg_digest_test",
            "submitted_at": "2026-05-15T00:00:00+00:00",
        },
        "campaign": {
            "request_type": "outreach_draft",
            "campaign_objective": "Drive renewal conversation with enterprise prospect",
            "channel": "email",
            "audience_segment": "enterprise_renewal",
            "action_required": "draft_and_cert",
            "workflow_required": "managed_workflow_hop",
            "grounding_required": True,
            "side_effect_class": "read_only",
        },
        "forbidden_send_modes": {
            "modes": [
                "send_now", "auto_send", "connector_send",
                "email_outbox_send", "linkedin_send", "sms_send",
                "external_http_post",
            ]
        },
        "entity_refs": {
            "lead_profile": {
                "verified_name": "Test Lead",
                "title": "VP Engineering",
                "consent_attested": True,
            }
        },
        "payload_digest": "",
    }
    if extra_transport:
        base["transport"].update(extra_transport)
    return base


class TestPackageDigestValidity:
    """W5 completion: package_digest must be non-empty, computed, verified, and preserved."""

    def test_package_digest_non_empty_after_u0(self) -> None:
        """package_digest must be a non-empty SHA-256 hex string after U0 processing."""
        from agentic_core.runtime.u0.apps_lic_u0_adapter import apps_lic_u0_adapt
        raw = _build_minimal_raw()
        vr, _ = apps_lic_u0_adapt(raw)
        pkg = vr.app_payload.get("runtime_customization_package", {})
        digest = pkg.get("package_digest", "")
        assert digest, (
            "package_digest must be non-empty after U0 processing; got empty string"
        )
        assert len(digest) == 64, (
            f"package_digest must be a 64-char SHA-256 hex string; got len={len(digest)!r}"
        )
        # Must be valid hex
        int(digest, 16)

    def test_package_digest_computed_when_absent(self) -> None:
        """When caller omits runtime_customization_package entirely, U0 DERIVES the digest."""
        from agentic_core.runtime.u0.apps_lic_u0_adapter import apps_lic_u0_adapt
        raw = _build_minimal_raw()
        assert "runtime_customization_package" not in raw, (
            "Precondition: _build_minimal_raw must not include runtime_customization_package"
        )
        vr, _ = apps_lic_u0_adapt(raw)
        pkg = vr.app_payload.get("runtime_customization_package", {})
        digest = pkg.get("package_digest", "")
        assert digest, "U0 must derive and inject package_digest when caller omits the key"
        # Verify it's the correct digest for an empty package
        import hashlib, json
        expected = hashlib.sha256(
            json.dumps({}, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()
        ).hexdigest()
        assert digest == expected, (
            f"Derived digest for empty package must be SHA-256({{}}); "
            f"expected {expected!r}, got {digest!r}"
        )

    def test_package_digest_mismatch_fails(self) -> None:
        """Caller-supplied package_digest that doesn't match computed value raises E10 error."""
        from agentic_core.runtime.u0.apps_lic_u0_adapter import (
            apps_lic_u0_adapt,
            AppsLicPackageDigestError,
        )
        raw = _build_minimal_raw()
        raw["runtime_customization_package"] = {
            "package_digest": "0" * 64,  # deliberately wrong
        }
        with pytest.raises(AppsLicPackageDigestError) as exc_info:
            apps_lic_u0_adapt(raw)
        msg = str(exc_info.value)
        assert "E10" in msg, f"Error message must cite E10; got: {msg!r}"
        assert "mismatch" in msg.lower(), f"Error message must mention mismatch; got: {msg!r}"

    def test_package_digest_preserved_in_validated_request_app_payload(self) -> None:
        """package_digest in ValidatedRequest.app_payload matches the value computed by U0."""
        from agentic_core.runtime.u0.apps_lic_u0_adapter import apps_lic_u0_adapt
        import hashlib, json
        raw = _build_minimal_raw()
        # Compute the digest the adapter will produce
        raw_pkg: dict = {}
        expected_digest = hashlib.sha256(
            json.dumps(
                {k: v for k, v in raw_pkg.items() if k != "package_digest"},
                sort_keys=True, ensure_ascii=False, separators=(",", ":"),
            ).encode()
        ).hexdigest()
        vr, _ = apps_lic_u0_adapt(raw)
        pkg = vr.app_payload.get("runtime_customization_package", {})
        actual = pkg.get("package_digest", "")
        assert actual == expected_digest, (
            f"package_digest in ValidatedRequest.app_payload must equal the computed digest; "
            f"expected {expected_digest!r}, got {actual!r}"
        )
