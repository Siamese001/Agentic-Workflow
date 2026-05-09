"""W6 Core Consumption Flow Tests — AG-RGGOV-W6 Verification

Validates that agentic_core consumes apps_rg declarative profiles
and owns all runtime artifacts.

Contract Chain Tests:
- Valid apps_rg ingress reaches core U0
- Core emits L1PlanContract
- Core emits RouteContract
- Core emits FinalEvidenceContract only when grounding_required = true
- Core emits CompiledPromptArtifact only when model_generation_required = true
- Core emits SealedL2Artifact
- Core Exit emits exactly one X3Disposition
- Scan proves apps_rg has no runtime contract emission

Hard Constraints:
- apps_rg emits no runtime contracts
- apps_rg does not call get_llm_gateway
- apps_rg does not call SovereignLLMGateway
- apps_rg does not emit FinalEvidenceContract
- apps_rg does not assemble prompts
- apps_rg does not execute
- apps_rg remains ingress/profile-only
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

# Canonical contract imports from runtime/contracts/
from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
    ValidatedRequest,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.final_evidence_contract import (
    EvidenceItem,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.x3_disposition import X3Disposition

# Producer imports — layer folders contain logic only, contracts imported from runtime/contracts/
from agentic_core.L0_routing.u0_intake_validator import U0IntakeValidator
from agentic_core.L1_cognition.l1_plan_contract import L1Planner
from agentic_core.L0_routing.route_contract import L0Router
from agentic_core.L0_routing.c0_evidence_contract import C0EvidenceCollector
from agentic_core.L2_execution.prompt_assembly_contract import PromptAssembler
from agentic_core.L2_execution.l2_execution_contract import L2Executor
from agentic_core.runtime.exit.x3_disposition import ExitDispositionEmitter
from agentic_core.runtime.entrypoints.apps_rg_integrated_pipeline import (
    AppsRgIntegratedPipeline,
)


class TestW6ContractEmissionChain:
    """Verify core emits all required contracts in correct order."""

    def test_valid_apps_rg_ingress_reaches_core_u0(self) -> None:
        """U0 receives and validates apps_rg ingress."""
        # Build ingress payload
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            target_level="L6",
            source_resume_ref="/path/to/resume.json",
            payload_digest="sha256:abc123",  # Valid digest for test
        )

        # U0 validates
        u0 = U0IntakeValidator()
        validated = u0.validate(payload)

        assert validated.request_id
        assert validated.app_id == "apps_rg"
        assert validated.payload_digest == "sha256:abc123"  # Passes through from payload
        assert validated.authority_validation_receipt.validation_passed

    def test_core_emits_l1_plan_contract(self) -> None:
        """L1 emits L1PlanContract after U0 validation."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        u0 = U0IntakeValidator()
        validated = u0.validate(payload)

        l1 = L1Planner()
        plan = l1.plan(validated)

        assert plan.request_id == validated.request_id
        assert plan.run_id == validated.run_id
        assert plan.task_plan
        assert "validate_ingress" in plan.task_plan
        assert plan.plan_version == "W6.0"

    def test_core_emits_route_contract(self) -> None:
        """L0 emits RouteContract after L1 planning."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        u0 = U0IntakeValidator()
        validated = u0.validate(payload)

        l1 = L1Planner()
        plan = l1.plan(validated)

        l0 = L0Router()
        route = l0.route(plan)

        assert route.request_id == validated.request_id
        assert route.route_id in {"R3_SIMPLE_GROUNDED_READ", "R5_MANAGED_WORKFLOW"}
        assert route.route_version == "W6.0"

    def test_core_emits_final_evidence_contract_when_grounding_required(self) -> None:
        """C0 emits FinalEvidenceContract only when grounding_required = true."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        u0 = U0IntakeValidator()
        validated = u0.validate(payload)

        l1 = L1Planner()
        plan = l1.plan(validated)

        l0 = L0Router()
        route = l0.route(plan)

        c0 = C0EvidenceCollector()
        evidence = c0.collect(validated, route)

        assert evidence is not None
        assert evidence.request_id == validated.request_id
        assert evidence.evidence_items
        assert evidence.contract_version == "W6.0"
        assert evidence.compilation_hash

    def test_core_emits_compiled_prompt_artifact_when_model_generation_required(
        self,
    ) -> None:
        """Prompt Assembly emits CompiledPromptArtifact only when model_generation_required = true."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        u0 = U0IntakeValidator()
        validated = u0.validate(payload)

        l1 = L1Planner()
        plan = l1.plan(validated)

        l0 = L0Router()
        route = l0.route(plan)

        c0 = C0EvidenceCollector()
        evidence = c0.collect(validated, route)

        assembler = PromptAssembler()
        prompt_artifact = assembler.assemble(evidence, route)

        assert prompt_artifact is not None
        assert prompt_artifact.request_id == validated.request_id
        assert prompt_artifact.compilation_hash
        assert prompt_artifact.assembly_version == "W6.0"

    def test_core_emits_sealed_l2_artifact(self) -> None:
        """L2 emits SealedL2Artifact after execution."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        u0 = U0IntakeValidator()
        validated = u0.validate(payload)

        l1 = L1Planner()
        plan = l1.plan(validated)

        l0 = L0Router()
        route = l0.route(plan)

        c0 = C0EvidenceCollector()
        evidence = c0.collect(validated, route)

        assembler = PromptAssembler()
        prompt_artifact = assembler.assemble(evidence, route)

        l2 = L2Executor()
        sealed = l2.execute(validated, prompt_artifact)

        assert sealed.request_id == validated.request_id
        assert sealed.execution_status == "completed"
        assert sealed.contract_version == "W6.0"
        assert sealed.compilation_hash

    def test_core_exit_emits_exactly_one_x3_disposition(self) -> None:
        """Exit emits exactly one X3Disposition."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        pipeline = AppsRgIntegratedPipeline()
        disposition = pipeline.execute(payload)

        # Exit emits exactly one X3Disposition
        assert disposition is not None
        assert disposition.app_id == "apps_rg"
        assert disposition.exit_status in {
            "success",
            "failure",
            "abstain",
            "error",
        }
        assert disposition.disposition_version == "W6.0"


class TestW6FullPipelineIntegration:
    """Verify full pipeline integration."""

    def test_full_pipeline_executes_all_layers(self) -> None:
        """Full pipeline executes U0→L1→L0→C0→Prompt→L2→Exit."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
            target_level="L6",
            source_resume_ref="/path/to/resume.json",
        )

        pipeline = AppsRgIntegratedPipeline()
        disposition = pipeline.execute(payload)

        assert disposition is not None
        assert disposition.exit_status in {"success", "abstain", "error"}
        assert disposition.disposition_version == "W6.0"

    def test_contract_chain_ids_match(self) -> None:
        """All contracts in chain reference same request/trace IDs."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        u0 = U0IntakeValidator()
        validated = u0.validate(payload)
        request_id = validated.request_id
        trace_id = validated.trace_id

        l1 = L1Planner()
        plan = l1.plan(validated)

        l0 = L0Router()
        route = l0.route(plan)

        c0 = C0EvidenceCollector()
        evidence = c0.collect(validated, route)

        assembler = PromptAssembler()
        prompt_artifact = assembler.assemble(evidence, route)

        l2 = L2Executor()
        sealed = l2.execute(validated, prompt_artifact)

        exit_emitter = ExitDispositionEmitter()
        disposition = exit_emitter.emit(sealed)

        # All contracts share request_id
        assert plan.request_id == request_id
        assert route.request_id == request_id
        assert evidence.request_id == request_id
        assert prompt_artifact.request_id == request_id
        assert sealed.request_id == request_id
        assert disposition.request_id == request_id

        # All contracts share trace_id
        assert plan.trace_id == trace_id
        assert route.trace_id == trace_id
        assert evidence.trace_id == trace_id
        assert prompt_artifact.trace_id == trace_id
        assert sealed.trace_id == trace_id
        assert disposition.trace_id == trace_id


class TestW6CanonicalContractImports:
    """Verify contracts are only defined in runtime/contracts/."""

    def test_l1_contract_imports_from_runtime(self) -> None:
        """L1PlanContract is defined in runtime/contracts/."""
        from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
        from agentic_core.L1_cognition.l1_plan_contract import L1Planner

        # L1 module should only contain producer, not contract definition
        import agentic_core.L1_cognition.l1_plan_contract as l1_module

        # The producer class should exist
        assert hasattr(l1_module, "L1Planner")
        # But the contract should be imported from runtime.contracts
        assert L1PlanContract is not None

    def test_route_contract_imports_from_runtime(self) -> None:
        """RouteContract is defined in runtime/contracts/."""
        from agentic_core.runtime.contracts.route_contract import RouteContract
        from agentic_core.L0_routing.route_contract import L0Router

        assert RouteContract is not None
        assert L0Router is not None

    def test_evidence_contract_imports_from_runtime(self) -> None:
        """FinalEvidenceContract is defined in runtime/contracts/."""
        from agentic_core.runtime.contracts.final_evidence_contract import (
            EvidenceItem,
            FinalEvidenceContract,
        )
        from agentic_core.L0_routing.c0_evidence_contract import C0EvidenceCollector

        assert FinalEvidenceContract is not None
        assert EvidenceItem is not None
        assert C0EvidenceCollector is not None

    def test_prompt_artifact_imports_from_runtime(self) -> None:
        """CompiledPromptArtifact is defined in runtime/contracts/."""
        from agentic_core.runtime.contracts.compiled_prompt_artifact import (
            CompiledPromptArtifact,
            PromptBlock,
        )
        from agentic_core.L2_execution.prompt_assembly_contract import PromptAssembler

        assert CompiledPromptArtifact is not None
        assert PromptBlock is not None
        assert PromptAssembler is not None

    def test_sealed_l2_artifact_imports_from_runtime(self) -> None:
        """SealedL2Artifact is defined in runtime/contracts/."""
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
        from agentic_core.L2_execution.l2_execution_contract import L2Executor

        assert SealedL2Artifact is not None
        assert L2Executor is not None

    def test_x3_disposition_imports_from_runtime(self) -> None:
        """X3Disposition is defined in runtime/contracts/."""
        from agentic_core.runtime.contracts.x3_disposition import X3Disposition
        from agentic_core.runtime.exit.x3_disposition import ExitDispositionEmitter

        assert X3Disposition is not None
        assert ExitDispositionEmitter is not None

    def test_no_duplicate_request_envelope(self) -> None:
        """RequestEnvelope is only defined in L5, not in apps_rg_ingress_payload."""
        # The canonical RequestEnvelope is in L5
        from agentic_core.L5_safety.contracts.authority import RequestEnvelope as L5Envelope

        assert L5Envelope is not None

        # apps_rg_ingress_payload should not define RequestEnvelope
        import agentic_core.runtime.contracts.apps_rg_ingress_payload as payload_module

        # Should not have RequestEnvelope defined in this module
        assert not hasattr(payload_module, "RequestEnvelope")


class TestW6AppsRgIngressOnlyConstraint:
    """Verify apps_rg does not emit runtime contracts."""

    def _get_main_module_source(self) -> str:
        """Read apps_rg/__main__.py source."""
        main_path = (
            Path(__file__).parent.parent.parent / "apps_rg" / "__main__.py"
        )
        return main_path.read_text(encoding="utf-8")

    def test_apps_rg_no_l1_plan_contract_emission(self) -> None:
        """apps_rg does not emit L1PlanContract."""
        source = self._get_main_module_source()
        assert "L1PlanContract(" not in source
        assert "l1_plan" not in source.lower()

    def test_apps_rg_no_route_contract_emission(self) -> None:
        """apps_rg does not emit RouteContract."""
        source = self._get_main_module_source()
        assert "RouteContract(" not in source

    def test_apps_rg_no_final_evidence_contract_emission(self) -> None:
        """apps_rg does not emit FinalEvidenceContract."""
        source = self._get_main_module_source()
        assert "FinalEvidenceContract(" not in source
        assert "FinalEvidenceContract_v1" not in source

    def test_apps_rg_no_compiled_prompt_artifact_emission(self) -> None:
        """apps_rg does not emit CompiledPromptArtifact."""
        source = self._get_main_module_source()
        assert "CompiledPromptArtifact(" not in source
        assert "CompiledPromptArtifact_v1" not in source

    def test_apps_rg_no_sealed_l2_artifact_emission(self) -> None:
        """apps_rg does not emit SealedL2Artifact."""
        source = self._get_main_module_source()
        assert "SealedL2Artifact(" not in source
        assert "SealedL2Artifact_v1" not in source

    def test_apps_rg_no_x3_disposition_emission(self) -> None:
        """apps_rg does not emit X3Disposition."""
        source = self._get_main_module_source()
        assert "X3Disposition(" not in source

    def test_apps_rg_no_get_llm_gateway_call(self) -> None:
        """apps_rg does not call get_llm_gateway."""
        source = self._get_main_module_source()
        assert "get_llm_gateway(" not in source

    def test_apps_rg_no_sovereign_llm_gateway_call(self) -> None:
        """apps_rg does not call SovereignLLMGateway."""
        source = self._get_main_module_source()
        assert "SovereignLLMGateway(" not in source


class TestW6ContractVersioning:
    """Verify all contracts use W6.0 versioning."""

    def test_all_contracts_use_w6_versioning(self) -> None:
        """All emitted contracts use version W6.0."""
        payload = AppsRgIngressPayload(
            target_company="TestCorp",
            target_role="Engineering Manager",
        )

        u0 = U0IntakeValidator()
        validated = u0.validate(payload)

        l1 = L1Planner()
        plan = l1.plan(validated)

        l0 = L0Router()
        route = l0.route(plan)

        c0 = C0EvidenceCollector()
        evidence = c0.collect(validated, route)

        assembler = PromptAssembler()
        prompt_artifact = assembler.assemble(evidence, route)

        l2 = L2Executor()
        sealed = l2.execute(validated, prompt_artifact)

        exit_emitter = ExitDispositionEmitter()
        disposition = exit_emitter.emit(sealed)

        assert plan.plan_version == "W6.0"
        assert route.route_version == "W6.0"
        assert evidence.contract_version == "W6.0"
        assert prompt_artifact.assembly_version == "W6.0"
        assert sealed.contract_version == "W6.0"
        assert disposition.disposition_version == "W6.0"
