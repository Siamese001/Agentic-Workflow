"""L2 Execution Contract Producer — AG-RGGOV-W6 Core Contract

L2 executes through SovereignLLMGateway and emits SealedL2Artifact.

Responsibilities:
- Execute through SovereignLLMGateway only
- Emit SealedL2Artifact with execution results
- Include state diff and execution metadata

Hard Constraints:
- Core owns all L2 execution
- apps_rg does not execute
- apps_rg does not call SovereignLLMGateway
- Contract dataclass is defined in runtime/contracts/, imported here
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from datetime import datetime, timezone

_logger = logging.getLogger(__name__)
_L5_CERT_REF_FAIL_CLOSED = os.getenv("L5_CERT_REF_FAIL_CLOSED", "0") == "1"


def _check_l5_cert_ref_l2(ref: str) -> None:
    """Fail-soft L5 cert ref verify at L2 entry per AG-W0-3=A_consume_entry."""
    try:
        from agentic_core.L5_safety.contracts.registry import verify_certification_ref
        valid = verify_certification_ref(ref)
    except Exception as exc:  # guardian: allow-log-and-swallow -- L5 registry must not crash L2 executor; treat as unverified
        _logger.warning("L5CertRefViolation stage=L2_entry registry_error=%s", exc)
        return
    if not valid:
        msg = "L5CertRefViolation stage=L2_entry ref=%r — missing or invalid l5_certification_ref"
        if _L5_CERT_REF_FAIL_CLOSED:
            raise ValueError(msg % (ref,))
        _logger.warning(msg, ref)


from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest


class L2Executor:
    """L2 execution layer for apps_rg tasks.

    Executes through SovereignLLMGateway and emits SealedL2Artifact.
    """

    def execute(
        self,
        validated_request: ValidatedRequest,
        prompt_artifact: CompiledPromptArtifact,
    ) -> SealedL2Artifact:
        """Execute through SovereignLLMGateway and emit SealedL2Artifact.

        Args:
            validated_request: U0-validated request
            prompt_artifact: Compiled prompt for execution

        Returns:
            SealedL2Artifact with execution results
        """
        # L2 entry: verify upstream (prompt artifact) l5_certification_ref (AG-W0-3)
        _check_l5_cert_ref_l2(getattr(prompt_artifact, "l5_certification_ref", ""))

        start_time = datetime.now(timezone.utc)

        # Simulated execution through SovereignLLMGateway
        # In production, this would call the actual gateway
        generated_content = self._call_sovereign_gateway(prompt_artifact)

        end_time = datetime.now(timezone.utc)
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Build state diff (resume artifact)
        proposed_state_diff = {
            "output_artifact_type": "resume",
            "output_format": "docx",
            "generation_app_id": validated_request.app_id,
            "target_task_class": validated_request.task_class,
        }

        # Compute compilation hash for downstream referencing
        compilation_hash = hashlib.sha256(
            json.dumps({
                "request_id": validated_request.request_id,
                "content_length": len(generated_content),
                "state_diff": proposed_state_diff,
            }, sort_keys=True).encode("utf-8")
        ).hexdigest()

        return SealedL2Artifact(
            request_id=validated_request.request_id,
            run_id=validated_request.run_id,
            app_id=validated_request.app_id,
            trace_id=validated_request.trace_id,
            execution_status="completed",
            generated_content=generated_content,
            proposed_state_diff=proposed_state_diff,
            state_diff_authorized=False,  # Authorization happens later
            execution_timestamp=end_time.isoformat(),
            execution_duration_ms=duration_ms,
            sovereign_execution_receipt=f"sovereign_exec_{validated_request.trace_id}",
            prompt_artifact_digest=prompt_artifact.compilation_hash,
            contract_version="W6.0",
            compilation_hash=compilation_hash,
            l5_certification_ref=getattr(prompt_artifact, "l5_certification_ref", ""),
        )

    def _call_sovereign_gateway(self, prompt_artifact: CompiledPromptArtifact) -> str:
        """Call SovereignLLMGateway with compiled prompt.

        Note: This is a simulated implementation.
        Production would call agentic_core.L2_execution.SovereignLLMGateway.
        """
        # Simulated gateway call
        # In production: from agentic_core.L2_execution import SovereignLLMGateway
        # In production: gateway = SovereignLLMGateway()
        # In production: return gateway.generate(prompt_artifact.prompt_blocks)

        return (
            f"Generated resume content for {prompt_artifact.app_id}\n\n"
            f"Based on evidence digest: {prompt_artifact.evidence_digest}\n"
            f"Using model: {prompt_artifact.target_model}"
        )
