"""TOMBSTONE — agentic_core.runtime.entrypoints.apps_rg_integrated_pipeline

This module is HARD-RETIRED as part of plan kill-shadow-pipelines-a7f3c2 W5.
NC-2 negative control requires this module to be non-importable.

Previously preserved for test_w7_l7_runtime_auditability.py (Bundle B retarget).
Audit confirmed: only reference remaining is a comment in
tests/_apps_contract/sample_w7_l7_trace_output.py (not a live import).
Hard tombstone applied 2026-05-14.

**W2 (boundary remediation f8e3c1):** QUARANTINE row in W1 CSV — tombstone satisfies
quarantine intent; no revival without ADR + receipt.

Canonical dispatch path:
    apps_rg.runtime.dispatch.apps_rg_dispatch consumed via
    AppIngressRunner(profile=profile, dispatch=apps_rg_dispatch).run(payload)
"""
from __future__ import annotations

raise ImportError(
    "TOMBSTONE (kill-shadow-pipelines-a7f3c2 W5 NC-2): "
    "agentic_core.runtime.entrypoints.apps_rg_integrated_pipeline is retired. "
    "Use apps_rg.runtime.dispatch.apps_rg_dispatch via "
    "AppIngressRunner(profile=profile, dispatch=apps_rg_dispatch).run(payload). "
    "Tombstoned 2026-05-14 — no live callers confirmed."
)

from typing import Optional

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
from agentic_core.runtime.audit.l7_audit_contracts import L7RuntimeAuditTrace

# Producer imports — these import contracts from runtime/contracts/
from agentic_core.L0_routing.u0_intake_validator import U0IntakeValidator
from agentic_core.L1_cognition.l1_plan_contract import L1Planner
from agentic_core.L0_routing.route_contract import L0Router
from agentic_core.L0_routing.c0_evidence_contract import C0EvidenceCollector
from agentic_core.L2_execution.prompt_assembly_contract import PromptAssembler
from agentic_core.L2_execution.l2_execution_contract import L2Executor
from agentic_core.runtime.exit.x3_disposition import ExitDispositionEmitter
from agentic_core.runtime.audit.l7_audit_emitter import L7AuditEmitter


class AppsRgIntegratedPipeline:
    """Internal integrated pipeline for apps_rg.

    Orchestrates the full core consumption flow with L7 auditability.
    This is NOT a public entrypoint — called by AppIngressRunner only.
    """

    def __init__(self) -> None:
        """Initialize pipeline with all stage producers."""
        self.u0_validator = U0IntakeValidator()
        self.l1_planner = L1Planner()
        self.l0_router = L0Router()
        self.c0_collector = C0EvidenceCollector()
        self.prompt_assembler = PromptAssembler()
        self.l2_executor = L2Executor()
        self.exit_emitter = ExitDispositionEmitter()
        self.l7_audit_emitter = L7AuditEmitter()

    def execute(
        self,
        ingress_payload: AppsRgIngressPayload,
    ) -> X3Disposition:
        """Execute full pipeline from ingress to exit.

        Args:
            ingress_payload: apps_rg ingress payload

        Returns:
            X3Disposition final exit contract
        """
        # U0: Validate ingress
        validated_request = self.u0_validator.validate(ingress_payload)

        # L1: Plan
        l1_plan = self.l1_planner.plan(validated_request)

        # L0: Route
        route = self.l0_router.route(l1_plan)

        # C0: Collect evidence (if grounding required)
        evidence_contract: Optional[FinalEvidenceContract] = None
        if route.grounding_required:
            evidence_contract = self.c0_collector.collect(validated_request, route)

        # Prompt Assembly: Compile prompt (if model generation required)
        prompt_artifact: Optional[CompiledPromptArtifact] = None
        if route.model_generation_required and evidence_contract:
            prompt_artifact = self.prompt_assembler.assemble(evidence_contract, route)

        # L2: Execute (if prompt assembled)
        l2_artifact: Optional[SealedL2Artifact] = None
        if prompt_artifact:
            l2_artifact = self.l2_executor.execute(validated_request, prompt_artifact)

        # Exit: Emit disposition
        # If L2 didn't run, create a minimal artifact for exit
        if l2_artifact is None:
            l2_artifact = self._create_abstain_artifact(validated_request)

        x3_disposition = self.exit_emitter.emit(l2_artifact)

        # L7: Emit audit trace (audit evidence only, no mutation)
        self._emit_l7_audit_trace(
            validated_request,
            l1_plan,
            route,
            evidence_contract,
            prompt_artifact,
            l2_artifact,
            x3_disposition,
        )

        return x3_disposition

    def execute_with_audit(
        self,
        ingress_payload: AppsRgIngressPayload,
    ) -> tuple[X3Disposition, L7RuntimeAuditTrace]:
        """Execute pipeline and return both disposition and audit trace.

        Args:
            ingress_payload: apps_rg ingress payload

        Returns:
            Tuple of (X3Disposition, L7RuntimeAuditTrace)
        """
        # U0: Validate ingress
        validated_request = self.u0_validator.validate(ingress_payload)

        # L1: Plan
        l1_plan = self.l1_planner.plan(validated_request)

        # L0: Route
        route = self.l0_router.route(l1_plan)

        # C0: Collect evidence (if grounding required)
        evidence_contract: Optional[FinalEvidenceContract] = None
        if route.grounding_required:
            evidence_contract = self.c0_collector.collect(validated_request, route)

        # Prompt Assembly: Compile prompt (if model generation required)
        prompt_artifact: Optional[CompiledPromptArtifact] = None
        if route.model_generation_required and evidence_contract:
            prompt_artifact = self.prompt_assembler.assemble(evidence_contract, route)

        # L2: Execute (if prompt assembled)
        l2_artifact: Optional[SealedL2Artifact] = None
        if prompt_artifact:
            l2_artifact = self.l2_executor.execute(validated_request, prompt_artifact)

        # Exit: Emit disposition
        if l2_artifact is None:
            l2_artifact = self._create_abstain_artifact(validated_request)

        x3_disposition = self.exit_emitter.emit(l2_artifact)

        # L7: Generate audit trace
        audit_trace = self.l7_audit_emitter.emit_audit_trace(
            validated_request=validated_request,
            l1_plan=l1_plan,
            route=route,
            evidence=evidence_contract,
            prompt_artifact=prompt_artifact,
            sealed_artifact=l2_artifact,
            x3_disposition=x3_disposition,
        )

        return x3_disposition, audit_trace

    def _emit_l7_audit_trace(
        self,
        validated_request: ValidatedRequest,
        l1_plan: L1PlanContract,
        route: RouteContract,
        evidence: Optional[FinalEvidenceContract],
        prompt_artifact: Optional[CompiledPromptArtifact],
        sealed_artifact: SealedL2Artifact,
        x3_disposition: X3Disposition,
    ) -> None:
        """Emit L7 audit trace (fire-and-forget).

        L7 is audit evidence only — does not affect pipeline execution.
        """
        audit_trace = self.l7_audit_emitter.emit_audit_trace(
            validated_request=validated_request,
            l1_plan=l1_plan,
            route=route,
            evidence=evidence,
            prompt_artifact=prompt_artifact,
            sealed_artifact=sealed_artifact,
            x3_disposition=x3_disposition,
        )

        # In production, this would be emitted to OTEL/audit log
        # For now, we generate the trace (fire-and-forget)
        _ = audit_trace  # Trace is generated, caller can collect if needed

    def _create_abstain_artifact(
        self, validated_request: ValidatedRequest
    ) -> SealedL2Artifact:
        """Create minimal L2 artifact for abstain case."""
        from datetime import datetime, timezone

        return SealedL2Artifact(
            request_id=validated_request.request_id,
            run_id=validated_request.run_id,
            app_id=validated_request.app_id,
            trace_id=validated_request.trace_id,
            execution_status="abstained",
            generated_content="",
            execution_timestamp=datetime.now(timezone.utc).isoformat(),
            contract_version="W6.0",
        )
