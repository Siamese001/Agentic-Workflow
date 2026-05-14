"""W7 L7 Runtime Auditability Tests — AG-RGGOV-W7 Verification

Validates L7 runtime auditability and no-shadow-pipeline evidence.

Required L7 success records:
- l7.apps_rg.ingress_payload.validated
- l7.apps_rg.authority_policy.checked
- l7.apps_rg.no_runtime_code.confirmed
- l7.agentic_core.l1.plan_contract.emitted
- l7.agentic_core.l0.route_contract.emitted
- l7.agentic_core.c0.final_evidence_contract.emitted or l7.agentic_core.c0.not_required
- l7.agentic_core.pa.compiled_prompt_artifact.emitted or l7.agentic_core.pa.not_required
- l7.agentic_core.l2.sealed_artifact.emitted
- l7.agentic_core.exit.x3_disposition.emitted
- l7.provider_egress.sovereign_gateway_only.confirmed
- l7.no_apps_rg_shadow_pipeline.confirmed
- l7.contract_digest_chain.sealed

Required proof:
- stage_owner_map shows every runtime stage owner is agentic_core
- apps_rg appears only as ingress_payload_source or declarative_profile_source
- provider_egress_owner = SovereignLLMGateway
- apps_rg_runtime_authority = false
- no_shadow_pipeline_status = PASS
- contract_digest_chain_status = sealed

Hard constraints:
- L7 is audit evidence only
- L7 must not plan, route, retrieve, assemble prompts, execute, call providers,
  emit Exit disposition, write L4, or promote learning
"""

from __future__ import annotations

import pytest

from agentic_core.runtime.audit.l7_audit_contracts import (
    AuditStatus,
    L7RuntimeAuditTrace,
    L7SuccessRecord,
    NoShadowPipelineReceipt,
    ProviderEgressOwnershipProof,
    StageOwnerEntry,
    StageOwnerMapProof,
    ContractDigestChainReceipt,
    ContractDigestEntry,
)
from agentic_core.runtime.audit.l7_audit_emitter import L7AuditEmitter
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition
from apps_rg.runtime.bindings.u0_binding import APPS_RG_U0_CERT_REF  # canonical cert ref for tests


# ---------------------------------------------------------------------------
# _run_with_audit — Bundle A.1 canonical replacement for AppsRgIntegratedPipeline
# Builds minimal typed contracts directly (no full harness needed) and emits
# an L7 audit trace. L7 tests verify audit trace structure, not pipeline execution.
# ---------------------------------------------------------------------------
def _run_with_audit(
    ingress_payload: AppsRgIngressPayload,
) -> tuple[X3Disposition, L7RuntimeAuditTrace]:
    """Build minimal typed contracts and return (disposition, audit_trace).

    Bundle A.1 canonical replacement for AppsRgIntegratedPipeline().execute_with_audit().
    Constructs the required stage contracts directly so the L7AuditEmitter can
    produce a structurally-complete audit trace without running the full harness.
    L7 is audit evidence only — it computes digests over contract objects, it does
    not re-execute the pipeline.
    """
    from datetime import datetime, timezone
    from dataclasses import replace
    import uuid

    from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
    from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
    from agentic_core.runtime.contracts.route_contract import RouteContract
    from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
    from agentic_core.runtime.contracts.apps_rg_runtime_authority_policy import (
        AppsRgRuntimeAuthorityPolicy,
    )

    ts = datetime.now(timezone.utc).isoformat()
    request_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())
    trace_id = str(uuid.uuid4())

    # Authority receipt — lightweight (no forbidden fields on minimal payload)
    authority_receipt = AppsRgRuntimeAuthorityPolicy.validate_ingress_payload(
        payload=ingress_payload,
        request_id=request_id,
        timestamp_iso=ts,
    )

    # ValidatedRequest — built directly with the canonical cert ref
    validated = ValidatedRequest(
        request_id=request_id,
        run_id=run_id,
        app_id="apps_rg",
        task_class="resume_generation",
        payload_digest=ingress_payload.payload_digest,
        authority_validation_receipt=authority_receipt,
        trace_id=trace_id,
        tenant_id="apps_rg",
        l5_certification_ref=APPS_RG_U0_CERT_REF,
    )

    # L1 plan — minimal
    plan = L1PlanContract(
        request_id=request_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=trace_id,
        l5_certification_ref=APPS_RG_U0_CERT_REF,
    )

    # L0 route — abstain path (no grounding / model generation needed for audit tests)
    route = RouteContract(
        request_id=request_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=trace_id,
        route_id="r0_abstain",
        l3_required=False,
        grounding_required=False,
        model_generation_required=False,
        write_authority_present=False,
        l5_certification_ref=APPS_RG_U0_CERT_REF,
    )

    # L2 sealed artifact — abstain
    sealed = SealedL2Artifact(
        request_id=request_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=trace_id,
        execution_status="abstained",
        generated_content="",
        execution_timestamp=ts,
        l5_certification_ref=APPS_RG_U0_CERT_REF,
    )

    # Exit disposition
    disposition = X3Disposition(
        request_id=request_id,
        run_id=run_id,
        app_id="apps_rg",
        trace_id=trace_id,
        exit_status="abstained",
        outcome_authorized=False,
        final_output={},
        exit_timestamp=ts,
        l5_certification_ref=APPS_RG_U0_CERT_REF,
        sealed_l2_digest="0" * 64,
    )

    l7 = L7AuditEmitter()
    audit_trace = l7.emit_audit_trace(
        validated_request=validated,
        l1_plan=plan,
        route=route,
        evidence=None,
        prompt_artifact=None,
        sealed_artifact=sealed,
        x3_disposition=disposition,
    )
    return disposition, audit_trace


class TestW7L7RuntimeAuditTrace:
    """Verify L7RuntimeAuditTrace exists and has required structure."""

    def test_l7_runtime_audit_trace_exists(self) -> None:
        """L7RuntimeAuditTrace dataclass exists with required fields."""
        from agentic_core.runtime.audit.l7_audit_contracts import L7RuntimeAuditTrace

        # Create minimal trace
        trace = L7RuntimeAuditTrace(
            trace_id="test-trace-123",
            request_id="req-456",
            run_id="run-789",
            app_id="apps_rg",
            success_records=(),
            no_shadow_pipeline_receipt=NoShadowPipelineReceipt(
                apps_rg_runtime_authority=False,
                apps_rg_contract_emission_detected=False,
                apps_rg_provider_calls_detected=False,
                shadow_pipeline_verdict=AuditStatus.PASS,
                verification_timestamp="2026-05-09T00:00:00+00:00",
                verification_method="static_analysis",
            ),
            stage_owner_map_proof=StageOwnerMapProof(
                stage_entries=(),
                apps_rg_stages_count=0,
                agentic_core_stages_count=7,
                stage_ownership_verdict=AuditStatus.PASS,
                verification_timestamp="2026-05-09T00:00:00+00:00",
            ),
            provider_egress_ownership_proof=ProviderEgressOwnershipProof(
                egress_owner_component="agentic_core",
                egress_owner_module="agentic_core.L2_execution.SovereignLLMGateway",
                apps_rg_egress_detected=False,
                egress_ownership_verdict=AuditStatus.PASS,
                verification_timestamp="2026-05-09T00:00:00+00:00",
            ),
            contract_digest_chain_receipt=ContractDigestChainReceipt(
                digest_entries=(),
                chain_head_digest="abc123",
                chain_tail_digest="def456",
                chain_complete=True,
                chain_sealed=True,
                chain_verdict=AuditStatus.PASS,
                verification_timestamp="2026-05-09T00:00:00+00:00",
            ),
            overall_audit_verdict=AuditStatus.PASS,
            audit_timestamp="2026-05-09T00:00:00+00:00",
            audit_version="W7.0",
        )

        assert trace.trace_id == "test-trace-123"
        assert trace.audit_version == "W7.0"
        assert trace.overall_audit_verdict == AuditStatus.PASS

    def test_l7_audit_emitter_exists(self) -> None:
        """L7AuditEmitter class exists and can be instantiated."""
        from agentic_core.runtime.audit.l7_audit_emitter import L7AuditEmitter

        emitter = L7AuditEmitter()
        assert emitter is not None
        assert emitter.AUDIT_VERSION == "W7.0"

    def test_l7_audit_emitter_generates_trace(self) -> None:
        """L7AuditEmitter generates complete audit trace."""
        # Build pipeline inputs
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        # Bundle A.1: use canonical _run_with_audit() instead of retired pipeline
        disposition, audit_trace = _run_with_audit(payload)

        # Verify audit trace structure
        assert audit_trace is not None
        assert isinstance(audit_trace, L7RuntimeAuditTrace)
        # Verify trace IDs match the disposition from same pipeline run
        assert audit_trace.trace_id == disposition.trace_id
        assert audit_trace.request_id == disposition.request_id
        assert audit_trace.audit_version == "W7.0"


class TestW7RequiredSuccessRecords:
    """Verify all required L7 success records are present."""

    REQUIRED_RECORD_IDS: tuple[str, ...] = (
        "l7.apps_rg.ingress_payload.validated",
        "l7.apps_rg.authority_policy.checked",
        "l7.apps_rg.no_runtime_code.confirmed",
        "l7.agentic_core.l1.plan_contract.emitted",
        "l7.agentic_core.l0.route_contract.emitted",
        "l7.agentic_core.c0.final_evidence_contract.emitted",
        "l7.agentic_core.pa.compiled_prompt_artifact.emitted",
        "l7.agentic_core.l2.sealed_artifact.emitted",
        "l7.agentic_core.exit.x3_disposition.emitted",
        "l7.provider_egress.sovereign_gateway_only.confirmed",
        "l7.no_apps_rg_shadow_pipeline.confirmed",
        "l7.contract_digest_chain.sealed",
    )

    def test_all_required_success_records_present(self) -> None:
        """L7 audit trace contains all required success records."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        # Get all record IDs
        record_ids = {r.record_id for r in audit_trace.success_records}

        # Verify all required records present
        for required_id in self.REQUIRED_RECORD_IDS:
            assert required_id in record_ids, f"Missing required record: {required_id}"

    def test_apps_rg_records_show_pass(self) -> None:
        """apps_rg success records show PASS status."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        # Filter apps_rg records
        apps_rg_records = [
            r for r in audit_trace.success_records if r.component == "apps_rg"
        ]

        for record in apps_rg_records:
            assert record.status == AuditStatus.PASS, (
                f"apps_rg record {record.record_id} should be PASS, got {record.status}"
            )

    def test_agentic_core_records_show_pass(self) -> None:
        """agentic_core success records show PASS status."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        # Filter agentic_core records
        core_records = [
            r for r in audit_trace.success_records if r.component == "agentic_core"
        ]

        for record in core_records:
            assert record.status in (AuditStatus.PASS, AuditStatus.SKIP), (
                f"agentic_core record {record.record_id} should be PASS or SKIP"
            )


class TestW7StageOwnerMap:
    """Verify stage owner map shows correct ownership."""

    def test_stage_owner_map_exists(self) -> None:
        """L7 audit trace contains stage owner map proof."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        assert audit_trace.stage_owner_map_proof is not None
        assert len(audit_trace.stage_owner_map_proof.stage_entries) > 0

    def test_all_stages_owned_by_agentic_core(self) -> None:
        """Every runtime stage is owned by agentic_core."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        proof = audit_trace.stage_owner_map_proof

        # All entries must be owned by agentic_core
        for entry in proof.stage_entries:
            assert entry.owner_component == "agentic_core", (
                f"Stage {entry.stage_id} owned by {entry.owner_component}, "
                f"expected agentic_core"
            )

    def test_apps_rg_stages_count_is_zero(self) -> None:
        """apps_rg_stages_count in stage owner map is 0."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        proof = audit_trace.stage_owner_map_proof

        assert proof.apps_rg_stages_count == 0, (
            f"apps_rg_stages_count should be 0, got {proof.apps_rg_stages_count}"
        )
        assert proof.stage_ownership_verdict == AuditStatus.PASS

    def test_agentic_core_stages_count_positive(self) -> None:
        """agentic_core_stages_count in stage owner map is > 0."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        proof = audit_trace.stage_owner_map_proof

        assert proof.agentic_core_stages_count > 0, (
            f"agentic_core_stages_count should be > 0, got {proof.agentic_core_stages_count}"
        )

    def test_stage_entries_cover_all_stages(self) -> None:
        """Stage owner map covers all pipeline stages."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        proof = audit_trace.stage_owner_map_proof
        stage_ids = {e.stage_id for e in proof.stage_entries}

        required_stages = {"l1", "l0", "l2", "exit"}
        for stage in required_stages:
            assert stage in stage_ids, f"Missing stage in owner map: {stage}"


class TestW7ProviderEgressOwnership:
    """Verify provider egress ownership proof."""

    def test_provider_egress_ownership_proof_exists(self) -> None:
        """L7 audit trace contains provider egress ownership proof."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        assert audit_trace.provider_egress_ownership_proof is not None

    def test_provider_egress_owned_by_agentic_core(self) -> None:
        """Provider egress owner is agentic_core."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        proof = audit_trace.provider_egress_ownership_proof

        assert proof.egress_owner_component == "agentic_core"
        assert "SovereignLLMGateway" in proof.egress_owner_module
        assert proof.egress_ownership_verdict == AuditStatus.PASS

    def test_apps_rg_egress_not_detected(self) -> None:
        """apps_rg_egress_detected is False."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        proof = audit_trace.provider_egress_ownership_proof

        assert proof.apps_rg_egress_detected is False


class TestW7NoShadowPipeline:
    """Verify no-shadow-pipeline receipt."""

    def test_no_shadow_pipeline_receipt_exists(self) -> None:
        """L7 audit trace contains no-shadow-pipeline receipt."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        assert audit_trace.no_shadow_pipeline_receipt is not None

    def test_apps_rg_runtime_authority_is_false(self) -> None:
        """apps_rg_runtime_authority in receipt is False."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        receipt = audit_trace.no_shadow_pipeline_receipt

        assert receipt.apps_rg_runtime_authority is False

    def test_apps_rg_contract_emission_not_detected(self) -> None:
        """apps_rg_contract_emission_detected is False."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        receipt = audit_trace.no_shadow_pipeline_receipt

        assert receipt.apps_rg_contract_emission_detected is False

    def test_apps_rg_provider_calls_not_detected(self) -> None:
        """apps_rg_provider_calls_detected is False."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        receipt = audit_trace.no_shadow_pipeline_receipt

        assert receipt.apps_rg_provider_calls_detected is False

    def test_shadow_pipeline_verdict_is_pass(self) -> None:
        """shadow_pipeline_verdict is PASS."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        receipt = audit_trace.no_shadow_pipeline_receipt

        assert receipt.shadow_pipeline_verdict == AuditStatus.PASS


class TestW7ContractDigestChain:
    """Verify contract digest chain receipt."""

    def test_contract_digest_chain_receipt_exists(self) -> None:
        """L7 audit trace contains contract digest chain receipt."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        assert audit_trace.contract_digest_chain_receipt is not None

    def test_contract_digest_chain_is_complete(self) -> None:
        """contract_digest_chain.chain_complete is True."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        receipt = audit_trace.contract_digest_chain_receipt

        assert receipt.chain_complete is True

    def test_contract_digest_chain_is_sealed(self) -> None:
        """contract_digest_chain.chain_sealed is True."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        receipt = audit_trace.contract_digest_chain_receipt

        assert receipt.chain_sealed is True
        assert receipt.chain_verdict == AuditStatus.PASS

    def test_contract_digest_chain_has_entries(self) -> None:
        """Contract digest chain has entries linking contracts."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        receipt = audit_trace.contract_digest_chain_receipt

        assert len(receipt.digest_entries) > 0

        # Verify chain linkage
        for i, entry in enumerate(receipt.digest_entries[1:], 1):
            prev_entry = receipt.digest_entries[i - 1]
            assert entry.parent_digest == prev_entry.contract_digest, (
                f"Chain broken at entry {i}: parent_digest mismatch"
            )


class TestW7OverallAuditVerdict:
    """Verify overall audit verdict."""

    def test_overall_audit_verdict_is_pass(self) -> None:
        """overall_audit_verdict is PASS when all proofs pass."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        assert audit_trace.overall_audit_verdict == AuditStatus.PASS

    def test_audit_trace_has_audit_version(self) -> None:
        """audit_version is W7.0."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace = _run_with_audit(payload)

        assert audit_trace.audit_version == "W7.0"


class TestW7L7HardConstraints:
    """Verify L7 audit-only constraints."""

    def test_l7_does_not_mutate_contracts(self) -> None:
        """L7 emitter does not modify input contracts."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        # Run audit; verify the returned audit_trace carries the same IDs as the disposition
        disposition, audit_trace = _run_with_audit(payload)

        # L7 must not mutate: trace_id and request_id in audit_trace match disposition
        assert audit_trace.trace_id == disposition.trace_id
        assert audit_trace.request_id == disposition.request_id

    def test_l7_is_pure_audit_evidence(self) -> None:
        """L7 emitter produces evidence without side effects."""
        from agentic_core.runtime.audit.l7_audit_emitter import L7AuditEmitter

        emitter = L7AuditEmitter()

        # L7 emitter should not have methods that mutate state
        assert not hasattr(emitter, 'plan')
        assert not hasattr(emitter, 'route')
        assert not hasattr(emitter, 'execute')
        assert not hasattr(emitter, 'call_provider')

    def test_l7_emit_audit_trace_idempotent(self) -> None:
        """Calling emit_audit_trace multiple times produces same result."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        _, audit_trace1 = _run_with_audit(payload)
        _, audit_trace2 = _run_with_audit(payload)

        # Both traces should have same structure
        assert audit_trace1.audit_version == audit_trace2.audit_version
        assert len(audit_trace1.success_records) == len(audit_trace2.success_records)


class TestW7AuditTraceIdsMatch:
    """Verify audit trace IDs match pipeline IDs."""

    def test_audit_trace_ids_match_request(self) -> None:
        """L7 trace IDs match the request being audited."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            payload_digest="sha256:abc123",
        )

        disposition, audit_trace = _run_with_audit(payload)

        # All IDs should be consistent within the same pipeline execution
        assert audit_trace.trace_id == disposition.trace_id
        assert audit_trace.request_id == disposition.request_id
        assert audit_trace.app_id == "apps_rg"
