"""L3 orchestration binding for apps_rg resume MANAGED_WORKFLOW (plan l0-l3-parent-gap W3.2)."""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import WorkflowNodeType
from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import (
    L3ContextBus,
    L3StepContract,
    StepInputs,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
    L3RuntimeOrchestrationReceipt,
    L3StepContractRef,
)
from agentic_core.runtime.contracts.route_contract import RouteContract

_LOGGER = logging.getLogger(__name__)

APPS_RG_L3_CERT_REF: str = "l3-apps-rg-resume-generation-w3"
APPS_RG_WORKFLOW_TYPE: str = "resume_generation_managed"
APPS_RG_NODE_ID: str = "apps_rg.modular_resume.execute"
APPS_RG_DAG_ID: str = "apps_rg.resume_generation.dag_v1"
_EXECUTION_FORM_MANAGED: str = "managed_workflow"


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _derive_workflow_id(route: RouteContract) -> str:
    return _sha256_hex(f"{route.run_id}:{route.route_id}")[:24]


def _derive_dag_sha256(workflow_id: str) -> str:
    payload = _canonical_json(
        {
            "dag_id": APPS_RG_DAG_ID,
            "workflow_type": APPS_RG_WORKFLOW_TYPE,
            "node_id": APPS_RG_NODE_ID,
            "workflow_id": workflow_id,
        }
    )
    return f"sha256:{_sha256_hex(payload)}"


def _build_step_inputs(
    fec: FinalEvidenceContract,
    prompt: Optional[CompiledPromptArtifact],
) -> StepInputs:
    evidence_refs: list[str] = []
    if fec.compilation_hash:
        evidence_refs.append(f"fec:{fec.compilation_hash[:24]}")
    for item in fec.evidence_items:
        if item.chunk_digest and item.chunk_digest != "NOT_APPLICABLE":
            evidence_refs.append(f"chunk:{item.chunk_digest[:24]}")
    prompt_artifact_refs: list[str] = []
    if prompt is not None and prompt.compilation_hash:
        prompt_artifact_refs.append(f"pa:{prompt.compilation_hash[:24]}")
    return StepInputs(
        query_refs=tuple(evidence_refs[:8]),
        evidence_refs=tuple(evidence_refs),
        graph_refs=tuple(),
        prompt_artifact_refs=tuple(prompt_artifact_refs),
        prior_artifact_refs=tuple(),
    )


def _build_step_contract(
    *,
    route: RouteContract,
    fec: FinalEvidenceContract,
    prompt: Optional[CompiledPromptArtifact],
    workflow_id: str,
    dag_sha256: str,
) -> L3StepContract:
    attempt_id = "a001"
    step_inputs = _build_step_inputs(fec, prompt)
    policy_hash = _sha256_hex(
        _canonical_json(
            {
                "route_id": route.route_id,
                "execution_form": route.execution_form,
                "tenant_id": route.tenant_id,
            }
        )
    )
    blueprint_hash = _sha256_hex(
        _canonical_json(
            {
                "dag_id": APPS_RG_DAG_ID,
                "node_id": APPS_RG_NODE_ID,
                "dag_sha256": dag_sha256,
            }
        )
    )
    route_digest = (route.route_digest or _sha256_hex(
        _canonical_json({"route_id": route.route_id, "run_id": route.run_id})
    ))[:24]
    snapshot_id = _sha256_hex(
        _canonical_json(
            {"run_id": route.run_id, "request_id": route.request_id, "workflow_id": workflow_id}
        )
    )[:16]
    idempotency_key = _sha256_hex(
        _canonical_json({"node_id": APPS_RG_NODE_ID, "attempt_id": attempt_id, "graph_hash": dag_sha256})
    )[:24]
    step_payload = _canonical_json(
        {
            "workflow_id": workflow_id,
            "node_id": APPS_RG_NODE_ID,
            "attempt_id": attempt_id,
            "policy_hash": policy_hash,
            "blueprint_hash": blueprint_hash,
            "route_digest": route_digest,
        }
    )
    step_contract_hash = _sha256_hex(step_payload)
    return L3StepContract(
        step_contract_id=f"sc:{step_contract_hash[:24]}",
        workflow_id=workflow_id,
        node_id=APPS_RG_NODE_ID,
        attempt_id=attempt_id,
        parent_route_id=route.route_id,
        route_digest=route_digest,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        snapshot_id=snapshot_id,
        replay_key=route.replay_key or f"rk:{route.run_id}",
        idempotency_key=idempotency_key,
        node_type=WorkflowNodeType.L2_MODEL_STEP,
        current_work_order=(
            f"Execute apps_rg modular resume Phase-1 lanes for run_id={route.run_id}. "
            "Bounded L2 packet only; no durable L4 commit from L3."
        ),
        inputs=step_inputs,
        expected_output_contract="SealedL2Artifact",
        capability_token_requirement="cap:apps_rg_resume_v1",
        sandbox_envelope_requirement="sbx:apps_rg_resume_v1",
        timeout_ms=600_000,
        retry_policy="max_attempts=1,no_retry_on_l4_write",
        fallback_permission="stub_fallback_only",
        telemetry_keys=(
            f"workflow_id={workflow_id}",
            f"node_id={APPS_RG_NODE_ID}",
            f"run_id={route.run_id}",
        ),
        expected_receipts=("SealedL2Artifact", "provider_receipt", "replay_manifest"),
        step_contract_hash=step_contract_hash,
        no_durable_commit_authority=True,
        l5_certification_ref=APPS_RG_L3_CERT_REF,
    )


def l3_orchestrate_apps_rg(
    route: RouteContract,
    fec: FinalEvidenceContract,
    prompt: Optional[CompiledPromptArtifact] = None,
) -> tuple[L3RuntimeOrchestrationReceipt, L3StepContract, L3ContextBus]:
    """Orchestrate apps_rg MANAGED_WORKFLOW through L3 (no execute/retrieve/L4 write)."""
    if route.execution_form != _EXECUTION_FORM_MANAGED:
        raise ValueError(
            f"l3_orchestrate_apps_rg: execution_form must be {_EXECUTION_FORM_MANAGED!r}, "
            f"got {route.execution_form!r}"
        )
    workflow_id = _derive_workflow_id(route)
    dag_sha256 = _derive_dag_sha256(workflow_id)
    step_contract = _build_step_contract(
        route=route,
        fec=fec,
        prompt=prompt,
        workflow_id=workflow_id,
        dag_sha256=dag_sha256,
    )
    now_utc = datetime.now(timezone.utc).isoformat()
    step_ref = L3StepContractRef(
        step_id=step_contract.step_contract_id,
        node_id=APPS_RG_NODE_ID,
        run_id=route.run_id,
        status="step_handed_to_l2",
        handed_to_l2_at_utc=now_utc,
    )
    from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
        L3_RUNTIME_RECEIPT_SCHEMA_VERSION,
        compute_l3_runtime_digest,
    )

    digest_input: dict[str, Any] = {
        "schema_version": L3_RUNTIME_RECEIPT_SCHEMA_VERSION,
        "run_id": route.run_id,
        "request_id": route.request_id,
        "trace_root": route.trace_id,
        "route_contract_id": route.route_id,
        "route_id": route.route_id,
        "dag_id": APPS_RG_DAG_ID,
        "dag_sha256": dag_sha256,
        "selected_node_ids": [APPS_RG_NODE_ID],
        "step_contracts": [step_ref.to_dict()],
        "l3_no_execute_assertion": True,
        "l3_no_retrieve_assertion": True,
        "l3_no_prompt_assembly_assertion": True,
        "l3_no_l4_write_assertion": True,
    }
    receipt = L3RuntimeOrchestrationReceipt(
        run_id=route.run_id,
        request_id=route.request_id,
        trace_root=route.trace_id,
        route_contract_id=route.route_id,
        route_id=route.route_id,
        dag_id=APPS_RG_DAG_ID,
        dag_sha256=dag_sha256,
        selected_node_ids=(APPS_RG_NODE_ID,),
        step_contracts=(step_ref,),
        static_dag_ref=f"dag:{APPS_RG_DAG_ID}",
        deterministic_digest=compute_l3_runtime_digest(digest_input),
        tenant_id=route.tenant_id or "apps_rg",
        l5_certification_ref=APPS_RG_L3_CERT_REF,
    )
    bus = L3ContextBus(
        workflow_id=workflow_id,
        bus_hash=f"bus:{_sha256_hex(_canonical_json({'workflow_id': workflow_id}))[:16]}",
        carried_query_refs=tuple(),
        carried_evidence_refs=step_contract.inputs.evidence_refs,
        carried_graph_refs=tuple(),
        carried_prompt_artifact_refs=step_contract.inputs.prompt_artifact_refs,
        carried_l2_artifact_refs=tuple(),
        carried_human_review_refs=tuple(),
        carried_policy_receipt_refs=tuple(),
        carried_error_refs=tuple(),
        contradiction_flags=tuple(),
        unresolved_gaps=tuple(),
        lineage_manifest=fec.compilation_hash or "",
    )
    from apps_rg.runtime.bindings.l0_l3_otel_spans import emit_l3_orchestration_span

    _ = emit_l3_orchestration_span(
        route=route,
        workflow_id=workflow_id,
        dag_id=APPS_RG_DAG_ID,
    )
    _LOGGER.debug("[apps_rg L3] workflow_id=%s run_id=%s", workflow_id, route.run_id)
    return receipt, step_contract, bus


__all__ = [
    "APPS_RG_L3_CERT_REF",
    "APPS_RG_DAG_ID",
    "APPS_RG_NODE_ID",
    "l3_orchestrate_apps_rg",
]
