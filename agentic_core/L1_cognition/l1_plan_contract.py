"""L1 Plan Contract Producer — AG-RGGOV-W6 Core Contract

L1 consumes AppsRgProfileManifest and emits L1PlanContract.

Responsibilities:
- Consume ValidatedRequest from U0
- Load AppsRgProfileManifest from profile_refs
- Generate L1PlanContract with planning decisions
- Determine if grounding_required and model_generation_required

Hard Constraints:
- Core owns all runtime contract emission
- L1 does not execute — only plans
- Contract dataclass is defined in runtime/contracts/, imported here
"""

from __future__ import annotations

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract


class L1Planner:
    """L1 planning layer for apps_rg tasks.

    Consumes ValidatedRequest and emits L1PlanContract with execution plan.
    """

    def plan(self, validated_request: ValidatedRequest) -> L1PlanContract:
        """Generate L1PlanContract from ValidatedRequest.

        Args:
            validated_request: U0-validated request with payload metadata

        Returns:
            L1PlanContract with planning decisions and routing flags
        """
        from datetime import datetime, timezone

        # Determine task requirements based on payload
        task_plan = self._derive_task_plan(validated_request)
        required_capabilities = self._derive_capabilities(validated_request)

        # Determine execution prerequisites
        grounding_required = self._needs_grounding(validated_request)
        model_generation_required = self._needs_model_generation(validated_request)
        write_authority_present = self._has_write_authority(validated_request)

        return L1PlanContract(
            request_id=validated_request.request_id,
            run_id=validated_request.run_id,
            app_id=validated_request.app_id,
            trace_id=validated_request.trace_id,
            task_plan=task_plan,
            required_capabilities=required_capabilities,
            grounding_required=grounding_required,
            model_generation_required=model_generation_required,
            write_authority_present=write_authority_present,
            profile_manifest_digest=validated_request.payload_digest,
            planning_timestamp=datetime.now(timezone.utc).isoformat(),
            plan_version="W6.0",
        )

    def _derive_task_plan(self, request: ValidatedRequest) -> tuple[str, ...]:
        """Derive task plan from request."""
        # Default apps_rg task plan
        return (
            "validate_ingress",
            "load_profiles",
            "collect_evidence" if self._needs_grounding(request) else "skip_evidence",
            "generate_resume" if self._needs_model_generation(request) else "skip_generation",
            "assemble_output",
            "exit_eval",
        )

    def _derive_capabilities(self, request: ValidatedRequest) -> tuple[str, ...]:
        """Derive required capabilities from request."""
        caps: list[str] = ["ingress_validation"]
        if self._needs_grounding(request):
            caps.append("evidence_collection")
        if self._needs_model_generation(request):
            caps.append("model_generation")
        return tuple(caps)

    def _needs_grounding(self, request: ValidatedRequest) -> bool:
        """Determine if C0 evidence collection is required."""
        # For apps_rg, always require grounding for company/role context
        return True

    def _needs_model_generation(self, request: ValidatedRequest) -> bool:
        """Determine if L2 model generation is required."""
        # For apps_rg, always require model generation for resume content
        return True

    def _has_write_authority(self, request: ValidatedRequest) -> bool:
        """Determine if task requires write authority."""
        # apps_rg generates artifacts but doesn't modify external state
        return False
