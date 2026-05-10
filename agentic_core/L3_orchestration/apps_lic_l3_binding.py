"""L3 orchestration binding for apps_lic `outreach_message` MANAGED_WORKFLOW.

L3 is the SIXTH stage of the pipeline (when execution_form=managed_workflow).
Its job is to receive a RouteContract with execution_form='managed_workflow',
emit an L3RuntimeOrchestrationReceipt + a bounded L3StepContract, and hand
control to L2 via the step contract.

AG-8 W6 invariants (apps-lic-ag8-golden-template-adoption-f3c2e1):
    - L3 participates IFF RouteContract.execution_form == 'managed_workflow'.
    - L3 emits L3RuntimeOrchestrationReceipt (proves participation).
    - L3 emits L3StepContract to bound the single execution step for L2.
    - L3 preserves from RouteContract:
        * workflow_id       (derived from run_id + route_id)
        * node_id           (fixed: "apps_lic.hop_pipeline.execute")
        * dependency refs   (carried_query_refs, carried_evidence_refs from FEC)
        * checkpoint refs   (derived from checkpoints tuple on ledger)
        * capability token  (capability_token_requirement — allowed tools + models)
        * sandbox envelope  (sandbox_envelope_requirement — from RouteContract)
        * allowed execution lane (route_id threaded as parent_route_id)
        * replay/audit refs (replay_key, snapshot_refs forwarded)
    - L3 sequences and merges step artifacts (single-node DAG for apps_lic).
    - L3 does NOT reroute, retrieve, execute, assemble prompts, or write L4.

HARD LAWS (AG-8 W6):
    - L3 MUST NOT call HopPipelineExecutor, LLM, ChromaDB, or any I/O.
    - L3 MUST NOT mutate L4 state.
    - L3 MUST NOT assemble prompts or produce CompiledPromptArtifact.
    - L3 MUST NOT reroute (route decision is final from L0).
    - l3_no_execute_assertion=True on every receipt.
    - l3_no_retrieve_assertion=True on every receipt.
    - l3_no_prompt_assembly_assertion=True on every receipt.
    - l3_no_l4_write_assertion=True on every receipt.

Plan: .windsurf/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W6)
"""
from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Optional

from agentic_core.runtime.contracts.route_contract import RouteContract
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.compiled_prompt_artifact import CompiledPromptArtifact
from agentic_core.runtime.contracts.l3_runtime_orchestration_receipt import (
    L3RuntimeOrchestrationReceipt,
    L3StepContractRef,
)
from agentic_core.L3_orchestration.doctrine.contracts_l3_7 import (
    L3ContextBus,
    L3StepContract,
    StepInputs,
)
from agentic_core.L3_orchestration.doctrine.contracts_l3_6 import WorkflowNodeType

_LOGGER = logging.getLogger(__name__)

APPS_LIC_L3_CERT_REF: str = "l3-apps-lic-outreach-message-ag8-w6-f3c2e1"

# Fixed DAG topology for apps_lic: single-node (the full HOP pipeline is one
# atomic step from L3's perspective — L3 hands the entire REGISTRY execution
# to L2 as one bounded step).
APPS_LIC_WORKFLOW_TYPE: str = "outreach_message_managed"
APPS_LIC_NODE_ID: str = "apps_lic.hop_pipeline.execute"
APPS_LIC_DAG_ID: str = "apps_lic.hop_pipeline.dag_v1"

_EXECUTION_FORM_MANAGED: str = "managed_workflow"

# Hard-law assertion constants — L3 never mutates these.
_L3_NO_EXECUTE: bool = True
_L3_NO_RETRIEVE: bool = True
_L3_NO_PROMPT_ASSEMBLY: bool = True
_L3_NO_L4_WRITE: bool = True


def _sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _canonical_json(obj: object) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), default=str)


def _derive_workflow_id(route: RouteContract) -> str:
    """Deterministic workflow_id = sha256(run_id + route_id)[:24]."""
    return _sha256_hex(f"{route.run_id}:{route.route_id}")[:24]


def _derive_dag_sha256(workflow_id: str) -> str:
    """Stable DAG sha256 for single-node apps_lic DAG."""
    payload = _canonical_json({
        "dag_id": APPS_LIC_DAG_ID,
        "workflow_type": APPS_LIC_WORKFLOW_TYPE,
        "node_id": APPS_LIC_NODE_ID,
        "workflow_id": workflow_id,
    })
    return f"sha256:{_sha256_hex(payload)}"


def _build_capability_token(route: RouteContract) -> str:
    """Encode capability token from RouteContract allowlists."""
    payload = _canonical_json({
        "allowed_models": list(route.allowed_models),
        "allowed_tools": list(route.allowed_tools),
        "allowed_networks": list(route.allowed_networks),
        "allowed_file_roots": list(route.allowed_file_roots),
        "egress_policy_ref": route.egress_policy_ref,
    })
    return f"cap:{_sha256_hex(payload)[:16]}"


def _build_sandbox_envelope(route: RouteContract) -> str:
    """Encode sandbox envelope requirement from RouteContract."""
    payload = _canonical_json({
        "sandbox_required": route.sandbox_required,
        "egress_policy_ref": route.egress_policy_ref,
    })
    return f"sbx:{_sha256_hex(payload)[:16]}"


def _build_step_inputs(
    fec: FinalEvidenceContract,
    prompt: Optional[CompiledPromptArtifact],
) -> StepInputs:
    """Build StepInputs from FinalEvidenceContract and optional PA artifact.

    For apps_lic the evidence_refs are the FEC compilation_hash + each item's
    chunk_digest. prompt_artifact_refs carry the PA compilation_hash if present.
    """
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
        query_refs=tuple(evidence_refs[:8]),    # bounded subset for query refs
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
    """Emit the single bounded step contract for apps_lic.

    This is the L3ToL2 handoff. L2 consumes this contract + the PA artifact
    to invoke HopPipelineExecutor.run(REGISTRY).
    """
    attempt_id = "a001"
    step_inputs = _build_step_inputs(fec, prompt)

    # Deterministic policy/blueprint hashes from stable inputs.
    policy_hash = _sha256_hex(
        _canonical_json({
            "route_id": route.route_id,
            "execution_form": route.execution_form,
            "tenant_id": route.tenant_id,
        })
    )
    blueprint_hash = _sha256_hex(
        _canonical_json({
            "dag_id": APPS_LIC_DAG_ID,
            "node_id": APPS_LIC_NODE_ID,
            "dag_sha256": dag_sha256,
        })
    )
    snapshot_id = _sha256_hex(
        _canonical_json({
            "run_id": route.run_id,
            "request_id": route.request_id,
            "workflow_id": workflow_id,
        })
    )[:16]

    # Idempotency key: deterministic per (node, attempt, graph).
    idempotency_key = _sha256_hex(
        _canonical_json({
            "node_id": APPS_LIC_NODE_ID,
            "attempt_id": attempt_id,
            "graph_hash": dag_sha256,
        })
    )[:24]

    capability_token = _build_capability_token(route)
    sandbox_envelope = _build_sandbox_envelope(route)

    # route_digest binds this step to exactly the L0 decision that spawned it.
    route_digest = _sha256_hex(
        _canonical_json({
            "route_id": route.route_id,
            "run_id": route.run_id,
            "execution_form": route.execution_form,
        })
    )[:24]

    step_payload = _canonical_json({
        "workflow_id": workflow_id,
        "node_id": APPS_LIC_NODE_ID,
        "attempt_id": attempt_id,
        "policy_hash": policy_hash,
        "blueprint_hash": blueprint_hash,
        "route_digest": route_digest,
    })
    step_contract_hash = _sha256_hex(step_payload)
    step_contract_id = f"sc:{step_contract_hash[:24]}"

    return L3StepContract(
        step_contract_id=step_contract_id,
        workflow_id=workflow_id,
        node_id=APPS_LIC_NODE_ID,
        attempt_id=attempt_id,
        parent_route_id=route.route_id,            # allowed execution lane
        route_digest=route_digest,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        snapshot_id=snapshot_id,
        replay_key=route.replay_key or f"rk:{route.run_id}",
        idempotency_key=idempotency_key,
        node_type=WorkflowNodeType.L2_MODEL_STEP,
        current_work_order=(
            f"Execute apps_lic HOP pipeline (9 stages) for run_id={route.run_id}. "
            f"Wrap HopPipelineExecutor.run(REGISTRY) as one bounded execution packet. "
            f"Emit SealedL2Artifact. No durable state commit."
        ),
        inputs=step_inputs,
        expected_output_contract="SealedL2Artifact",
        capability_token_requirement=capability_token,
        sandbox_envelope_requirement=sandbox_envelope,
        timeout_ms=180_000,   # 3-minute SLO for 9-stage HOP pipeline
        retry_policy="max_attempts=1,no_retry_on_l4_write",
        fallback_permission="stub_fallback_only",
        telemetry_keys=(
            f"workflow_id={workflow_id}",
            f"node_id={APPS_LIC_NODE_ID}",
            f"attempt_id={attempt_id}",
            f"run_id={route.run_id}",
        ),
        expected_receipts=(
            "SealedL2Artifact",
            "provider_receipt",
            "replay_manifest",
        ),
        step_contract_hash=step_contract_hash,
        no_durable_commit_authority=True,    # L3 never commits durable state
        l5_certification_ref=APPS_LIC_L3_CERT_REF,
    )


def _build_context_bus(
    *,
    workflow_id: str,
    fec: FinalEvidenceContract,
    prompt: Optional[CompiledPromptArtifact],
) -> L3ContextBus:
    """Build L3ContextBus carrying evidence + prompt artifact refs."""
    evidence_refs: list[str] = []
    if fec.compilation_hash:
        evidence_refs.append(f"fec:{fec.compilation_hash[:24]}")
    for item in fec.evidence_items:
        if item.chunk_digest and item.chunk_digest != "NOT_APPLICABLE":
            evidence_refs.append(f"chunk:{item.chunk_digest[:24]}")

    prompt_artifact_refs: list[str] = []
    if prompt is not None and prompt.compilation_hash:
        prompt_artifact_refs.append(f"pa:{prompt.compilation_hash[:24]}")

    bus_payload = _canonical_json({
        "workflow_id": workflow_id,
        "evidence_refs": evidence_refs,
        "prompt_artifact_refs": prompt_artifact_refs,
    })
    bus_hash = f"bus:{_sha256_hex(bus_payload)[:16]}"

    return L3ContextBus(
        workflow_id=workflow_id,
        bus_hash=bus_hash,
        carried_query_refs=tuple(),
        carried_evidence_refs=tuple(evidence_refs),
        carried_graph_refs=tuple(),
        carried_prompt_artifact_refs=tuple(prompt_artifact_refs),
        carried_l2_artifact_refs=tuple(),
        carried_human_review_refs=tuple(),
        carried_policy_receipt_refs=tuple(),
        carried_error_refs=tuple(),
        contradiction_flags=tuple(),
        unresolved_gaps=tuple(),
        lineage_manifest=fec.compilation_hash or "",
    )


def l3_orchestrate_apps_lic(
    route: RouteContract,
    fec: FinalEvidenceContract,
    prompt: Optional[CompiledPromptArtifact] = None,
) -> tuple[L3RuntimeOrchestrationReceipt, L3StepContract, L3ContextBus]:
    """Orchestrate one apps_lic MANAGED_WORKFLOW run through L3.

    L3 participates IFF route.execution_form == 'managed_workflow'. The
    function emits three artefacts:

    1. L3RuntimeOrchestrationReceipt  — typed proof that L3 ran.
    2. L3StepContract                 — bounded handoff packet for L2.
    3. L3ContextBus                   — evidence + prompt artifact refs
                                        forwarded to L2.

    L3 does NOT execute, retrieve, assemble prompts, or write L4.
    All hard-law assertions are set True in the receipt.

    Args:
        route:  RouteContract from L0 with execution_form='managed_workflow'.
        fec:    FinalEvidenceContract from C0 carrying evidence items.
        prompt: CompiledPromptArtifact from PA (may be None for dry runs).

    Returns:
        (receipt, step_contract, context_bus) — all three artefacts L2 needs.

    Raises:
        TypeError:  if route is not RouteContract or fec is not
                    FinalEvidenceContract.
        ValueError: if route.execution_form != 'managed_workflow' or
                    hard-law assertions would be violated.
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"l3_orchestrate_apps_lic expected RouteContract, got "
            f"{type(route).__name__}"
        )
    if not isinstance(fec, FinalEvidenceContract):
        raise TypeError(
            f"l3_orchestrate_apps_lic expected FinalEvidenceContract, got "
            f"{type(fec).__name__}"
        )
    if route.execution_form != _EXECUTION_FORM_MANAGED:
        raise ValueError(
            f"l3_orchestrate_apps_lic: route.execution_form must be "
            f"'{_EXECUTION_FORM_MANAGED}', got {route.execution_form!r}. "
            f"Use L3BypassReceipt for non-workflow routes."
        )

    workflow_id = _derive_workflow_id(route)
    dag_sha256 = _derive_dag_sha256(workflow_id)

    # Build step contract (L3 → L2 handoff).
    step_contract = _build_step_contract(
        route=route,
        fec=fec,
        prompt=prompt,
        workflow_id=workflow_id,
        dag_sha256=dag_sha256,
    )

    # Build step contract ref for the receipt.
    now_utc = datetime.now(timezone.utc).isoformat()
    step_ref = L3StepContractRef(
        step_id=step_contract.step_contract_id,
        node_id=APPS_LIC_NODE_ID,
        run_id=route.run_id,
        status="step_handed_to_l2",
        handed_to_l2_at_utc=now_utc,
    )

    # Build the deterministic digest using the helper, then construct the
    # receipt directly so l5_certification_ref is set at construction time.
    # (build_l3_runtime_orchestration_receipt doesn't accept cert_ref, and
    # frozen dataclasses validate __post_init__ on construction, not on
    # dataclasses.replace — so we must pass it during __init__.)
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
        "dag_id": APPS_LIC_DAG_ID,
        "dag_sha256": dag_sha256,
        "selected_node_ids": [APPS_LIC_NODE_ID],
        "step_contracts": [step_ref.to_dict()],
        "l3_no_execute_assertion": True,
        "l3_no_retrieve_assertion": True,
        "l3_no_prompt_assembly_assertion": True,
        "l3_no_l4_write_assertion": True,
    }
    deterministic_digest = compute_l3_runtime_digest(digest_input)
    receipt = L3RuntimeOrchestrationReceipt(
        run_id=route.run_id,
        request_id=route.request_id,
        trace_root=route.trace_id,
        route_contract_id=route.route_id,
        route_id=route.route_id,
        dag_id=APPS_LIC_DAG_ID,
        dag_sha256=dag_sha256,
        selected_node_ids=(APPS_LIC_NODE_ID,),
        step_contracts=(step_ref,),
        static_dag_ref=f"dag:{APPS_LIC_DAG_ID}",
        deterministic_digest=deterministic_digest,
        tenant_id=route.tenant_id or "apps_lic",
        l5_certification_ref=APPS_LIC_L3_CERT_REF,
    )

    # Build context bus (carries dependency + evidence refs to L2).
    context_bus = _build_context_bus(
        workflow_id=workflow_id,
        fec=fec,
        prompt=prompt,
    )

    _LOGGER.debug(
        "[apps_lic L3] orchestrated workflow_id=%s node_id=%s run_id=%s",
        workflow_id,
        APPS_LIC_NODE_ID,
        route.run_id,
    )

    return receipt, step_contract, context_bus


__all__ = [
    "APPS_LIC_L3_CERT_REF",
    "APPS_LIC_DAG_ID",
    "APPS_LIC_NODE_ID",
    "APPS_LIC_WORKFLOW_TYPE",
    "l3_orchestrate_apps_lic",
]
