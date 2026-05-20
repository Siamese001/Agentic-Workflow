"""
Smoke test for W2 authority contracts — agentic_core/runtime/contracts/tests/test_contracts_smoke.py

Minimal proof that all four W2 contracts:
1. Import cleanly
2. Instantiate without error
3. Satisfy basic round-trip invariants

Run: python -m pytest agentic_core/runtime/contracts/tests/test_contracts_smoke.py -v
"""
from __future__ import annotations

import pytest
from dataclasses import asdict

# Contract modules under test
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.apps_rg_profile_manifest import (
    AppsRgProfileManifest,
    ProfileEntry,
)
from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
    AppsRgRuntimeAuthorityPolicy,
    AuthorityAllowRule,
    AuthorityDenyRule,
    AuthorityValidationReceipt,
    RuntimeAuthorityScanReceipt,
)
from agentic_core.runtime.contracts.l7_runtime_audit_trace import (
    L7RuntimeAuditTrace,
    AuthoritySpanType,
    AuditTraceReceipt,
)


class TestAppsRgIngressPayload:
    """Smoke tests for AppsRgIngressPayload contract."""

    def test_payload_instantiation(self) -> None:
        from agentic_core.runtime.contracts.apps_rg_profile_manifest import AppsRgProfileManifest
        payload = AppsRgIngressPayload(
            source_resume_text="Resume content here",
            job_description_text="Job description here",
            profile_refs=AppsRgProfileManifest(manifest_digest="sha256:test"),
        )
        assert payload.app_id == "apps_rg"
        assert payload.task_class == "resume_generation"
        assert payload.source_resume_text == "Resume content here"

    def test_payload_requires_resume_source(self) -> None:
        """Payload must have at least one resume source."""
        with pytest.raises(ValueError, match="at least one of source_resume_ref or source_resume_text"):
            AppsRgIngressPayload(
                source_resume_ref=None,
                source_resume_text=None,
            )

    def test_validated_request_fields(self) -> None:
        from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import AuthorityValidationReceipt
        receipt = AuthorityValidationReceipt(
            allowed=True, passed=True, request_id="req_001", policy_version="1.0.0"
        )
        validated = ValidatedRequest(
            request_id="req_001",
            run_id="run_002",
            app_id="apps_rg",
            task_class="resume_generation",
            payload_digest="sha256:abc",
            authority_validation_receipt=receipt,
            trace_id="trace_001",
        )
        assert validated.run_id == "run_002"
        assert validated.app_id == "apps_rg"
        assert validated.authority_validation_receipt.allowed is True


class TestAppsRgProfileManifest:
    """Smoke tests for AppsRgProfileManifest contract."""

    def test_manifest_instantiation(self) -> None:
        manifest = AppsRgProfileManifest(
            manifest_digest="sha256:abc123",
            profiles={},
        )
        assert manifest.manifest_digest == "sha256:abc123"
        assert manifest.profiles == {}
        assert manifest.planning_profile_ref == "rg_planning_profile.yaml"  # default

    def test_profile_entry_addition(self) -> None:
        entry = ProfileEntry(
            profile_id="standard_resume",
            source_path="apps_rg/profiles/standard.yaml",
            content_digest="sha256:def456",
        )
        manifest = AppsRgProfileManifest(
            manifest_digest="sha256:abc123",
            profiles={"standard_resume": entry},
        )
        assert "standard_resume" in manifest.profiles
        assert manifest.profiles["standard_resume"].content_digest == "sha256:def456"

    def test_validate_all_present(self) -> None:
        entry = ProfileEntry(
            profile_id="standard_resume",
            source_path="apps_rg/profiles/standard.yaml",
            content_digest="sha256:def456",
        )
        manifest = AppsRgProfileManifest(
            manifest_digest="sha256:abc123",
            profiles={"standard_resume": entry},
        )
        assert manifest.validate_all_present(["standard_resume"]) is True
        assert manifest.validate_all_present(["missing"]) is False


class TestAppsRgRuntimeAuthorityPolicy:
    """Smoke tests for AppsRgRuntimeAuthorityPolicy contract."""

    def test_policy_instantiation(self) -> None:
        policy = AppsRgRuntimeAuthorityPolicy(
            version="1.0.0",
            allow_rules=[],
            deny_rules=[],
        )
        assert policy.version == "1.0.0"

    def test_validate_allows_ingress(self) -> None:
        policy = AppsRgRuntimeAuthorityPolicy(
            version="1.0.0",
            allow_rules=[
                AuthorityAllowRule(pattern="apps_rg.cli", reason="ingress only"),
            ],
            deny_rules=[
                AuthorityDenyRule(pattern=r"apps_rg.*(Planner|Router)", reason="no runtime authority"),
            ],
        )
        receipt = policy.validate("apps_rg.cli.main")
        assert receipt.allowed is True
        assert receipt.matched_rule == "apps_rg.cli"

    def test_validate_denies_orchestrator(self) -> None:
        policy = AppsRgRuntimeAuthorityPolicy(
            version="1.0.0",
            allow_rules=[
                AuthorityAllowRule(pattern="apps_rg.cli", reason="ingress only"),
            ],
            deny_rules=[
                AuthorityDenyRule(pattern=r"apps_rg.*Orchestrator", reason="no runtime authority"),
            ],
        )
        receipt = policy.validate("apps_rg.reasoning.RgResumeOrchestrator")
        assert receipt.allowed is False
        assert receipt.matched_rule is not None
        assert "no runtime authority" in receipt.reason

    def test_scan_receipt_aggregation(self) -> None:
        policy = AppsRgRuntimeAuthorityPolicy(
            version="1.0.0",
            allow_rules=[],
            deny_rules=[
                AuthorityDenyRule(pattern=r".*Router.*", reason="no routing"),
            ],
        )
        # Build module_results dict first, then construct frozen receipt
        module_results = {
            "apps_rg.cli": AuthorityValidationReceipt(
                allowed=True, passed=True, policy_version="1.0.0"
            ),
            "apps_rg.router": AuthorityValidationReceipt(
                allowed=False, passed=False, reason="deny: no routing", policy_version="1.0.0"
            ),
        }
        scan = RuntimeAuthorityScanReceipt(
            scanned_modules=["apps_rg.cli", "apps_rg.router"],
            policy_version="1.0.0",
            module_results=module_results,
        )
        assert scan.total_modules == 2
        assert scan.violation_count == 1
        assert scan.is_compliant() is False


class TestL7RuntimeAuditTrace:
    """Smoke tests for L7RuntimeAuditTrace contract."""

    def test_trace_start_new(self) -> None:
        trace = L7RuntimeAuditTrace.start_new(run_id="run_003")
        assert trace.run_id == "run_003"
        assert trace.trace_id is not None
        assert trace.span_count == 0

    def test_emit_and_finalize_pass(self) -> None:
        trace = L7RuntimeAuditTrace.start_new(run_id="run_004")
        trace.emit(AuthoritySpanType.INGRESS_ACCEPT, detail={"payload_digest": "sha256:abc"})
        trace.emit(AuthoritySpanType.POLICY_PASS, detail={"scan": "clean"})
        trace.emit(AuthoritySpanType.CHAIN_COMPLETE, detail={})
        receipt = trace.finalize()
        assert isinstance(receipt, AuditTraceReceipt)
        assert receipt.is_pass() is True
        assert receipt.violation_count == 0
        assert receipt.spans_count == 3

    def test_emit_violation_and_finalize_fail(self) -> None:
        trace = L7RuntimeAuditTrace.start_new(run_id="run_005")
        trace.emit(AuthoritySpanType.INGRESS_ACCEPT, detail={})
        trace.emit(AuthoritySpanType.AUTHORITY_VIOLATION, detail={"module": "bad_module"})
        trace.emit(AuthoritySpanType.CHAIN_COMPLETE, detail={})
        receipt = trace.finalize()
        assert receipt.is_pass() is False
        assert receipt.violation_count == 1
        assert receipt.status == "FAIL"

    def test_cannot_emit_after_finalize(self) -> None:
        trace = L7RuntimeAuditTrace.start_new(run_id="run_006")
        trace.emit(AuthoritySpanType.INGRESS_ACCEPT, detail={})
        trace.finalize()
        with pytest.raises(RuntimeError, match="Cannot emit to finalized trace"):
            trace.emit(AuthoritySpanType.POLICY_PASS, detail={})

    def test_span_is_violation(self) -> None:
        trace = L7RuntimeAuditTrace.start_new(run_id="run_007")
        span_ok = trace.emit(AuthoritySpanType.POLICY_PASS, detail={})
        assert span_ok.is_violation() is False
        span_bad = trace.emit(AuthoritySpanType.AUTHORITY_VIOLATION, detail={})
        assert span_bad.is_violation() is True

    def test_to_serializable(self) -> None:
        trace = L7RuntimeAuditTrace.start_new(run_id="run_008")
        trace.emit(AuthoritySpanType.INGRESS_ACCEPT, detail={"key": "value"})
        serialized = trace.to_serializable()
        assert serialized["run_id"] == "run_008"
        assert len(serialized["spans"]) == 1
        assert serialized["spans"][0]["span_type"] == "APPS_RG_INGRESS_ACCEPT"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
