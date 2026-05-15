"""apps_rg L2 v4 envelope adapter — E1 PREP builder functions.

Builds v4 L2 contracts from CompiledPromptArtifact.
Plan: apps-rg-l2-v4-envelope-adoption-e9f2b1 W2 (E1 PREP phase).
"""
from __future__ import annotations

import hashlib
from typing import Any, Optional

__all__ = [
    "run_apps_rg_l2_envelope",
    "_build_prep_output",
    "_build_frozen_execution_context",
    "_build_work_order_inputs",
    "_build_determinism_bundle",
    "_build_lineage_root",
    "_build_budget_snapshot",
    "_build_capability_scope_summary",
    "_build_approved_work_order",
    "_build_sealed_rejection_packet",
    "_validate_work_order",
    "_execute_approved_work_order",
    "_heal_attempt_failure",
    "_seal_l2_artifact",
]


def _build_lineage_root(prompt_artifact: Any) -> Any:
    """Build a LineageRoot from the compiled prompt artifact."""
    try:
        from agentic_core.L2_execution.types.l2_v3_receipts import LineageRoot
        digest = getattr(prompt_artifact, "evidence_digest", "") or ""
        return LineageRoot(root_hash=digest, lineage_type="compiled_prompt")
    except ImportError:
        return None


def _build_determinism_bundle(prompt_artifact: Any) -> Any:
    """Build a DeterminismBundle from the compiled prompt artifact."""
    try:
        from agentic_core.L2_execution.types.l2_v3_receipts import DeterminismBundle
        h = getattr(prompt_artifact, "compilation_hash", "") or ""
        return DeterminismBundle(compilation_hash=h, seed=0, temperature=0.0)
    except ImportError:
        return None


def _build_work_order_inputs(prompt_artifact: Any, route_contract: Any) -> Any:
    """Build WorkOrderInputs from prompt artifact and route contract."""
    try:
        from agentic_core.L2_execution.types.l2_v4_contracts import WorkOrderInputs
        return WorkOrderInputs(
            prompt_artifact_digest=getattr(prompt_artifact, "evidence_digest", ""),
            route_id=getattr(route_contract, "route_id", ""),
        )
    except ImportError:
        return None


def _build_budget_snapshot(prompt_artifact: Any) -> Any:
    """Build a budget snapshot dict."""
    return {
        "max_tokens": 4096,
        "temperature": 0.0,
        "model_ref": getattr(prompt_artifact, "model_ref", ""),
    }


def _build_capability_scope_summary() -> dict[str, Any]:
    """Return a minimal capability scope summary."""
    return {
        "can_call_llm": True,
        "can_write_l4": False,
        "can_emit_exit_disposition": True,
    }


def _build_frozen_execution_context(
    prompt_artifact: Any,
    route_contract: Any,
    validated_request: Any,
) -> Any:
    """Build FrozenExecutionContext."""
    try:
        from agentic_core.L2_execution.types.l2_v4_contracts import FrozenExecutionContext
        run_id = getattr(validated_request, "run_id", "") or ""
        return FrozenExecutionContext(
            run_id=run_id,
            compilation_hash=getattr(prompt_artifact, "compilation_hash", ""),
            route_id=getattr(route_contract, "route_id", ""),
        )
    except ImportError:
        return None


def _build_prep_output(
    prompt_artifact: Any,
    route_contract: Any,
    validated_request: Any,
) -> Any:
    """Build PrepOutput (E1 PREP phase)."""
    try:
        from agentic_core.L2_execution.types.l2_v4_contracts import PrepOutput
        fec = _build_frozen_execution_context(prompt_artifact, route_contract, validated_request)
        woi = _build_work_order_inputs(prompt_artifact, route_contract)
        lineage = _build_lineage_root(prompt_artifact)
        det = _build_determinism_bundle(prompt_artifact)
        return PrepOutput(
            frozen_execution_context=fec,
            work_order_inputs=woi,
            lineage_root=lineage,
            determinism_bundle=det,
        )
    except ImportError:
        return None


def _build_approved_work_order(prep_output: Any, budget: dict) -> Any:
    """Build an ApprovedWorkOrder from prep output."""
    try:
        from agentic_core.L2_execution.types.l2_v4_contracts import ExecutionForm
        return ExecutionForm(prep_output=prep_output, budget_snapshot=budget)
    except ImportError:
        return None


def _build_sealed_rejection_packet(reason: str, run_id: str = "") -> Any:
    """Build a sealed rejection packet."""
    return {"status": "REJECTED", "reason": reason, "run_id": run_id}


def _validate_work_order(work_order: Any) -> tuple[bool, str]:
    """Validate a work order before execution."""
    if work_order is None:
        return False, "work_order is None"
    return True, ""


def _execute_approved_work_order(work_order: Any, prompt_text: str) -> dict[str, Any]:
    """Execute an approved work order (stub — real execution via L2 layer)."""
    return {
        "generated_content": "",
        "execution_status": "stub",
        "work_order_ref": str(work_order),
    }


def _heal_attempt_failure(
    failure: Exception,
    attempt_number: int,
    max_attempts: int = 3,
) -> bool:
    """Return True if recovery should be attempted."""
    return attempt_number < max_attempts


def _seal_l2_artifact(
    generated_content: str,
    compilation_hash: str,
    run_id: str,
    trace_id: str,
    request_id: str,
    prompt_artifact_digest: str = "",
) -> Any:
    """Seal generated content into a SealedL2Artifact."""
    try:
        from agentic_core.runtime.contracts.sealed_l2_artifact import SealedL2Artifact
        return SealedL2Artifact(
            generated_content=generated_content,
            compilation_hash=compilation_hash,
            prompt_artifact_digest=prompt_artifact_digest,
            run_id=run_id,
            trace_id=trace_id,
            request_id=request_id,
        )
    except ImportError:
        return None


def run_apps_rg_l2_envelope(
    prompt_artifact: Any,
    route_contract: Any,
    validated_request: Any,
    *,
    budget: Optional[dict] = None,
) -> Any:
    """Run the full L2 v4 envelope pipeline for apps_rg."""
    prep = _build_prep_output(prompt_artifact, route_contract, validated_request)
    bud = budget or _build_budget_snapshot(prompt_artifact)
    work_order = _build_approved_work_order(prep, bud)
    valid, reason = _validate_work_order(work_order)
    if not valid:
        run_id = getattr(validated_request, "run_id", "")
        return _build_sealed_rejection_packet(reason, run_id)
    prompt_text = getattr(prompt_artifact, "prompt_text", "") or ""
    result = _execute_approved_work_order(work_order, prompt_text)
    return _seal_l2_artifact(
        generated_content=result.get("generated_content", ""),
        compilation_hash=getattr(prompt_artifact, "compilation_hash", ""),
        run_id=getattr(validated_request, "run_id", ""),
        trace_id=getattr(validated_request, "trace_id", ""),
        request_id=getattr(validated_request, "request_id", ""),
        prompt_artifact_digest=getattr(prompt_artifact, "evidence_digest", ""),
    )
