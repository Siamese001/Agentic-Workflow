"""Reference runtime emitter for the E2E proof harness (per 99.1, 99.2, 99.4).

The emitter is a deterministic, in-memory simulator of the governed runtime.
It honors every authority boundary listed in 99.6 (no L4 writes outside UWG,
no L6 spans before Exit disposition, no layer emitting another layer's
contracts) and produces the full contract chain from 99.3 plus an OTEL span
tree from 99.4.

The emitter is the layer the validators stand on top of. When canonical
agentic_core layers gain the ability to emit these contracts directly, this
emitter remains the reference oracle that the live emitters are diff'd against.
"""

from __future__ import annotations

import dataclasses as _dc
from typing import Any

from .contracts import (
    ClaimSupport,
    CommitRequest,
    ContractRoot,
    EvidenceRef,
    ExecutionForm,
    ExitReviewPacket,
    FinalEvidenceContract,
    L1PlanContract,
    L2ExecutionRequest,
    L3StepContract,
    L3WorkflowContract,
    OTELSpan,
    OutputAction,
    PromptEnvelope,
    RouteContract,
    RouteId,
    RuntimeExhaustBundle,
    SealedL2Artifact,
    SupportLevel,
    UWGCommitReceipt,
    ValidatedRequest,
    XDisposition,
    X3DispositionReceipt,
)
from .digests import digest, short_id
from .scenarios import Scenario


# ---------------------------------------------------------------------------
# Public output container
# ---------------------------------------------------------------------------


class RunArtifacts:
    """Bag of artifacts emitted for one scenario run.

    Attributes are populated by ``emit_run`` in 99.3 contract-chain order.
    Validators read them; tests assert against them.
    """

    def __init__(self) -> None:
        self.scenario_id: str = ""
        self.route_id: RouteId = RouteId.R5_FALLBACK
        self.expected_path: tuple[str, ...] = ()
        self.observed_path: list[str] = []
        self.contracts: dict[str, Any] = {}
        self.spans: list[OTELSpan] = []
        self.claim_support_map: list[ClaimSupport] = []
        self.replay_inputs: dict[str, Any] = {}
        self.bundle_payload_summary: dict[str, Any] = {}

    def add_contract(self, name: str, contract_obj: Any) -> None:
        """Store a contract by canonical name and append it to ``observed_path``."""
        self.contracts[name] = _to_jsonable(contract_obj)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def emit_run(scenario: Scenario, *, seed: int = 0) -> RunArtifacts:
    """Run the reference emitter for one scenario.

    ``seed`` is mixed into request_id/run_id only — never into
    contract digests, so the same scenario produces the same digests across
    invocations regardless of seed (deterministic replay friendly).
    """
    artifacts = RunArtifacts()
    artifacts.scenario_id = scenario.scenario_id
    artifacts.route_id = scenario.route_id
    artifacts.expected_path = scenario.expected_path

    root = _build_root(scenario, seed=seed)

    # 1. U0 intake
    validated = _emit_validated_request(scenario, root)
    artifacts.add_contract("ValidatedRequest", validated)
    _add_span(artifacts, "intake.validate_envelope", root, parent=None)
    _add_span(artifacts, "intake.bind_identity_session", root, parent="intake.validate_envelope")
    artifacts.observed_path.append("intake.validate_envelope")

    # 2. L1 cognition
    l1_plan = _emit_l1_plan(scenario, root, validated)
    artifacts.add_contract("L1PlanContract", l1_plan)
    _add_span(artifacts, "l1.parse_intent", root, parent="intake.validate_envelope")
    _add_span(artifacts, "l1.emit_plan_contract", root, parent="l1.parse_intent")
    artifacts.observed_path.append("l1.emit_plan_contract")

    # 3. L0 routing
    route = _emit_route(scenario, root, l1_plan)
    artifacts.add_contract("RouteContract", route)
    _add_span(artifacts, "l0.route.select", root, parent="l1.emit_plan_contract")
    _add_span(
        artifacts,
        "l0.route.emit_contract",
        root,
        parent="l0.route.select",
        attributes={"route_id": route.route_id.value},
    )
    artifacts.observed_path.append("l0.route.emit_contract")

    # Terminal RET routes (R1A, R1B, R5, HITL) skip C0/PA/L2 entirely.
    is_terminal_ret = scenario.route_id in {
        RouteId.R1A_EXACT_CACHE,
        RouteId.R1B_SEMANTIC_CACHE,
        RouteId.R5_FALLBACK,
        RouteId.HITL_POSTURE,
    }

    final_evidence: FinalEvidenceContract | None = None
    prompt_envelope: PromptEnvelope | None = None
    sealed: SealedL2Artifact | None = None

    # 4. C0 grounding
    if scenario.grounding_required and not is_terminal_ret:
        final_evidence = _emit_final_evidence(scenario, root, route)
        artifacts.add_contract("FinalEvidenceContract", final_evidence)
        for span_name in ("c0.plan", "c0.fetch", "c0.shape", "c0.contract"):
            extra = {"evidence_contract_ref": final_evidence.digest} if span_name == "c0.contract" else None
            _add_span(artifacts, span_name, root, parent="l0.route.emit_contract", attributes=extra)
        artifacts.observed_path.append("c0.contract")

    # 5. L3 managed workflow
    if scenario.route_id == RouteId.R3R4_MANAGED_WORKFLOW:
        workflow = _emit_l3_workflow(root, route)
        artifacts.add_contract("L3WorkflowContract", workflow)
        _add_span(artifacts, "l3.workflow.build", root, parent="l0.route.emit_contract")
        _add_span(artifacts, "l3.step.dispatch", root, parent="l3.workflow.build")
        artifacts.observed_path.append("l3.workflow.build")
        artifacts.observed_path.append("l3.step.dispatch")

    # 6. PA prompt assembly
    if not is_terminal_ret:
        prompt_envelope = _emit_prompt_envelope(scenario, root, route, final_evidence)
        artifacts.add_contract("PromptEnvelope", prompt_envelope)
        pa_parent = "c0.contract" if final_evidence else "l0.route.emit_contract"
        for span_name in (
            "prompt_assembly.load_bom",
            "prompt_assembly.compose_slots",
            "prompt_assembly.emit_artifact",
        ):
            _add_span(artifacts, span_name, root, parent=pa_parent)
        artifacts.observed_path.append("prompt_assembly.emit_artifact")

    # 7. L2 execution
    if not is_terminal_ret:
        l2_request = _emit_l2_request(root, route, prompt_envelope)
        artifacts.add_contract("L2ExecutionRequest", l2_request)
        sealed = _emit_sealed_artifact(scenario, root, l2_request, final_evidence)
        artifacts.add_contract("SealedL2Artifact", sealed)
        parent = "prompt_assembly.emit_artifact"
        for span_name in ("l2.e1.prep", "l2.e2.valid", "l2.e3.exec", "l2.e5.seal"):
            extra_attrs = _l2_span_attributes(span_name, scenario, sealed)
            _add_span(artifacts, span_name, root, parent=parent, attributes=extra_attrs)
            parent = span_name
        artifacts.observed_path.append("l2.e5.seal")
    else:
        # Terminal-RET still produces a "sealed" RET packet referencing RouteContract.
        sealed = _emit_terminal_ret_packet(scenario, root, route)
        artifacts.add_contract("SealedL2Artifact", sealed)

    # 8. Exit normalize/evaluate/disposition
    exit_packet = _emit_exit_packet(scenario, root, sealed)
    artifacts.add_contract("ExitReviewPacket", exit_packet)
    _add_span(
        artifacts,
        "exit.normalize",
        root,
        parent="l2.e5.seal" if not is_terminal_ret else "l0.route.emit_contract",
    )
    _add_span(artifacts, "exit.evaluate", root, parent="exit.normalize")

    disposition = _emit_disposition(scenario, root, exit_packet)
    artifacts.add_contract("X3DispositionReceipt", disposition)
    _add_span(
        artifacts,
        "exit.disposition",
        root,
        parent="exit.evaluate",
        attributes={"disposition": disposition.disposition.value},
    )
    artifacts.observed_path.append("exit.disposition")

    # 9. UWG commit path
    if (
        scenario.route_id == RouteId.UWG_COMMIT_PATH
        and disposition.disposition == XDisposition.X3C_COMMIT_ELIGIBLE
    ):
        commit_req = _emit_commit_request(root, disposition)
        artifacts.add_contract("CommitRequest", commit_req)
        uwg_receipt = _emit_uwg_receipt(root, commit_req)
        artifacts.add_contract("UWGCommitReceipt", uwg_receipt)
        _add_span(
            artifacts,
            "uwg.validate",
            root,
            parent="exit.disposition",
            attributes={"commit_request_id": commit_req.digest},
        )
        _add_span(
            artifacts,
            "uwg.commit",
            root,
            parent="uwg.validate",
            attributes={"commit_request_id": commit_req.digest, "uwg_receipt": uwg_receipt.digest},
        )
        artifacts.observed_path.append("uwg.commit")

    # 10. L6 exhaust — ALWAYS after disposition is sealed
    exhaust = _emit_exhaust(root, disposition, len(artifacts.spans) + 1)
    artifacts.add_contract("RuntimeExhaustBundle", exhaust)
    _add_span(artifacts, "l6.ingest", root, parent="exit.disposition")
    artifacts.observed_path.append("l6.ingest")

    # Claim support map (99.7) — always emitted; trivially populated for non-grounded routes.
    artifacts.claim_support_map = _build_claim_support(scenario, sealed, final_evidence)

    # Replay inputs (99.5)
    artifacts.replay_inputs = _build_replay_inputs(root, route, final_evidence, prompt_envelope, sealed)

    # Bundle summary
    artifacts.bundle_payload_summary = {
        "scenario_id": scenario.scenario_id,
        "route_id": scenario.route_id.value,
        "contracts": list(artifacts.contracts.keys()),
        "span_count": len(artifacts.spans),
    }

    return artifacts


# ---------------------------------------------------------------------------
# Builders for individual contracts
# ---------------------------------------------------------------------------


def _build_root(scenario: Scenario, *, seed: int) -> ContractRoot:
    base = f"{scenario.scenario_id}|{seed}"
    return ContractRoot(
        request_id="req-" + short_id(base + "|req"),
        run_id="run-" + short_id(base + "|run"),
        trace_root="trace-" + short_id(base + "|trace"),
        policy_hash="policy:" + short_id("policy.v1"),
        blueprint_hash="blueprint:" + short_id("blueprint.v1"),
        replay_key="replay-" + short_id(base + "|replay"),
        tenant_id="tenant-default",
        session_id="sess-" + short_id(base + "|sess"),
    )


def _seal(obj: Any) -> str:
    """Compute the canonical digest of a contract, excluding its own digest field.

    All emitter helpers MUST set ``obj.digest = _seal(obj)`` so that
    downstream validators can recompute the same digest from the serialized
    payload-minus-digest.
    """
    payload = _to_jsonable(obj)
    if isinstance(payload, dict):
        payload.pop("digest", None)
    return digest(payload)


def _emit_validated_request(scenario: Scenario, root: ContractRoot) -> ValidatedRequest:
    payload = ValidatedRequest(
        root=root,
        user_intent_text=scenario.user_intent,
        declared_grounding_required=scenario.grounding_required,
        declared_durable_write_requested=scenario.durable_write_requested,
        declared_hitl_required=scenario.hitl_required,
    )
    payload.digest = _seal(payload)
    return payload


def _emit_l1_plan(scenario: Scenario, root: ContractRoot, validated: ValidatedRequest) -> L1PlanContract:
    plan = L1PlanContract(
        root=root,
        grounding_required=scenario.grounding_required,
        support_target="reference_documents" if scenario.grounding_required else "",
        risk_tier="HIGH" if scenario.route_id == RouteId.HITL_POSTURE else "LOW",
        upstream_ref=validated.digest,
    )
    plan.digest = _seal(plan)
    return plan


def _emit_route(scenario: Scenario, root: ContractRoot, plan: L1PlanContract) -> RouteContract:
    execution_form = (
        ExecutionForm.TERMINAL_RET
        if scenario.route_id
        in {
            RouteId.R1A_EXACT_CACHE,
            RouteId.R1B_SEMANTIC_CACHE,
            RouteId.R5_FALLBACK,
            RouteId.HITL_POSTURE,
        }
        else ExecutionForm.MULTI_STEP
        if scenario.route_id == RouteId.R3R4_MANAGED_WORKFLOW
        else ExecutionForm.SINGLE_STEP
    )
    contract = RouteContract(
        root=root,
        route_id=scenario.route_id,
        execution_form=execution_form,
        upstream_ref=plan.digest,
    )
    # route_digest covers the deterministic routing decision (99.5 mode 1).
    contract.route_digest = digest(
        {
            "route_id": contract.route_id.value,
            "execution_form": contract.execution_form.value,
            "upstream_ref": contract.upstream_ref,
            "policy_hash": root.policy_hash,
            "blueprint_hash": root.blueprint_hash,
        }
    )
    contract.digest = _seal(contract)
    return contract


def _emit_final_evidence(
    scenario: Scenario, root: ContractRoot, route: RouteContract
) -> FinalEvidenceContract:
    evidence = FinalEvidenceContract(
        root=root,
        upstream_ref=route.digest,
        evidence_refs=[
            EvidenceRef(
                ref_id="ev-1",
                source_uri=f"docs://{scenario.scenario_id.lower()}/source-1",
                span_locator="paragraph:1",
                content_hash=digest({"source": scenario.scenario_id, "paragraph": 1}),
            ),
            EvidenceRef(
                ref_id="ev-2",
                source_uri=f"docs://{scenario.scenario_id.lower()}/source-1",
                span_locator="paragraph:closing",
                content_hash=digest({"source": scenario.scenario_id, "paragraph": "closing"}),
            ),
        ],
    )
    evidence.evidence_contract_hash = digest({"refs": [_to_jsonable(r) for r in evidence.evidence_refs]})
    evidence.digest = _seal(evidence)
    return evidence


def _emit_l3_workflow(root: ContractRoot, route: RouteContract) -> L3WorkflowContract:
    steps = [
        L3StepContract(step_id="s1", depends_on=[], digest=digest({"s": 1})),
        L3StepContract(step_id="s2", depends_on=["s1"], digest=digest({"s": 2})),
        L3StepContract(step_id="s3", depends_on=["s2"], digest=digest({"s": 3})),
    ]
    workflow = L3WorkflowContract(root=root, upstream_ref=route.digest, steps=steps)
    workflow.digest = _seal(workflow)
    return workflow


def _emit_prompt_envelope(
    scenario: Scenario,
    root: ContractRoot,
    route: RouteContract,
    evidence: FinalEvidenceContract | None,
) -> PromptEnvelope:
    envelope = PromptEnvelope(
        root=root,
        upstream_evidence_ref=evidence.digest if evidence else "",
        upstream_route_ref=route.digest,
        bom_digest=digest({"bom": "default.v1"}),
        prompt_hash=digest(
            {
                "system": "policy.v1",
                "evidence": evidence.evidence_contract_hash if evidence else None,
                "user_intent": scenario.user_intent,
            }
        ),
        schema_bound=True,
    )
    envelope.digest = _seal(envelope)
    return envelope


def _emit_l2_request(
    root: ContractRoot,
    route: RouteContract,
    prompt: PromptEnvelope | None,
) -> L2ExecutionRequest:
    req = L2ExecutionRequest(
        root=root,
        upstream_route_ref=route.digest,
        upstream_prompt_ref=prompt.digest if prompt else "",
    )
    req.digest = _seal(req)
    return req


def _emit_sealed_artifact(
    scenario: Scenario,
    root: ContractRoot,
    l2_request: L2ExecutionRequest,
    evidence: FinalEvidenceContract | None,
) -> SealedL2Artifact:
    cited = [r.ref_id for r in evidence.evidence_refs] if evidence else []
    sealed = SealedL2Artifact(
        root=root,
        upstream_ref=l2_request.digest,
        output_text=f"Result for {scenario.scenario_id}: bound to evidence={bool(evidence)}.",
        cited_evidence_refs=cited,
        side_effect=scenario.route_id
        in {RouteId.R4_SINGLE_ACTION, RouteId.R3_PLUS_R4_SINGLE_STEP, RouteId.UWG_COMMIT_PATH},
        direct_l4_write=False,
    )
    sealed.digest = _seal(sealed)
    return sealed


def _emit_terminal_ret_packet(
    scenario: Scenario, root: ContractRoot, route: RouteContract
) -> SealedL2Artifact:
    packet = SealedL2Artifact(
        root=root,
        upstream_ref=route.digest,
        output_text=f"TERMINAL_RET[{scenario.route_id.value}] for {scenario.scenario_id}.",
        cited_evidence_refs=[],
        side_effect=False,
        direct_l4_write=False,
    )
    packet.digest = _seal(packet)
    return packet


def _emit_exit_packet(scenario: Scenario, root: ContractRoot, sealed: SealedL2Artifact) -> ExitReviewPacket:
    classification = "TERMINAL" if scenario.route_id != RouteId.UWG_COMMIT_PATH else "COMMIT_ELIGIBLE"
    packet = ExitReviewPacket(
        root=root,
        upstream_ref=sealed.digest,
        terminal_classification=classification,
        gate_verdicts=[{"gate": "X1", "status": "PASS"}],
    )
    packet.digest = _seal(packet)
    return packet


def _emit_disposition(
    scenario: Scenario, root: ContractRoot, exit_packet: ExitReviewPacket
) -> X3DispositionReceipt:
    disposition_value = (
        XDisposition.X3C_COMMIT_ELIGIBLE
        if scenario.route_id == RouteId.UWG_COMMIT_PATH
        else XDisposition.X3A_APPROVE
    )
    receipt = X3DispositionReceipt(
        root=root,
        upstream_ref=exit_packet.digest,
        disposition=disposition_value,
    )
    receipt.digest = _seal(receipt)
    return receipt


def _emit_commit_request(root: ContractRoot, disposition: X3DispositionReceipt) -> CommitRequest:
    req = CommitRequest(
        root=root,
        upstream_ref=disposition.digest,
        state_diff={"key": "config.example", "from": "v1", "to": "v2"},
    )
    req.digest = _seal(req)
    return req


def _emit_uwg_receipt(root: ContractRoot, commit_req: CommitRequest) -> UWGCommitReceipt:
    receipt = UWGCommitReceipt(
        root=root,
        upstream_ref=commit_req.digest,
        accepted=True,
        l4_audit_append_id="audit-" + short_id(commit_req.digest),
    )
    receipt.digest = _seal(receipt)
    return receipt


def _emit_exhaust(
    root: ContractRoot,
    disposition: X3DispositionReceipt,
    span_count: int,
) -> RuntimeExhaustBundle:
    bundle = RuntimeExhaustBundle(
        root=root,
        upstream_ref=disposition.digest,
        spans_count=span_count,
    )
    bundle.digest = _seal(bundle)
    return bundle


# ---------------------------------------------------------------------------
# OTEL span helpers
# ---------------------------------------------------------------------------


_TIME_NS = 1_700_000_000_000_000_000  # fixed epoch so digests stay stable


def _add_span(
    artifacts: RunArtifacts,
    name: str,
    root: ContractRoot,
    *,
    parent: str | None,
    attributes: dict[str, Any] | None = None,
) -> None:
    parent_span = next((s for s in artifacts.spans if s.name == parent), None) if parent else None
    span_id = "span-" + short_id(f"{root.trace_root}|{name}|{len(artifacts.spans)}")
    base_attrs = {
        "request_id": root.request_id,
        "run_id": root.run_id,
        "trace_root": root.trace_root,
        "tenant_id": root.tenant_id,
        "policy_hash": root.policy_hash,
        "blueprint_hash": root.blueprint_hash,
        "replay_key": root.replay_key,
    }
    if attributes:
        base_attrs.update(attributes)
    artifacts.spans.append(
        OTELSpan(
            span_id=span_id,
            parent_span_id=parent_span.span_id if parent_span else None,
            name=name,
            attributes=base_attrs,
            start_ns=_TIME_NS + len(artifacts.spans),
            end_ns=_TIME_NS + len(artifacts.spans) + 1,
            status="OK",
        )
    )


# ---------------------------------------------------------------------------
# Claim support map (99.7) and replay inputs (99.5)
# ---------------------------------------------------------------------------


def _l2_span_attributes(span_name: str, scenario: Scenario, sealed: SealedL2Artifact) -> dict[str, Any]:
    """Populate the OTEL attributes 99.4 mandates for L2 execution spans.

    - ``l2.e3.exec`` is a model/tool call → must carry provider, model_id,
      latency_ms, tokens, cost, status (per 99.4 §VALIDATION RULE).
    - Side-effect-emitting spans (R4 / R3+R4 / UWG paths) MUST carry
      capability_token_ref + sandbox_envelope_ref.
    - Other L2 spans (prep/valid/seal) carry ``status`` so absence-of-status
      cannot pass silently.
    """
    attrs: dict[str, Any] = {"status": "OK"}
    if span_name == "l2.e3.exec":
        attrs.update(
            {
                "provider": "anthropic",
                "model_id": "claude-3-5-sonnet-20241022",
                "tool_id": "default" if not sealed.side_effect else f"action.{scenario.scenario_id}",
                "latency_ms": 412,
                "tokens_in": 287,
                "tokens_out": 96,
                "cost_usd": 0.0021,
            }
        )
        if sealed.side_effect:
            attrs.update(
                {
                    "capability_token_ref": "cap-"
                    + short_id({"sid": scenario.scenario_id, "tier": "side_effect"}),
                    "sandbox_envelope_ref": "sandbox-"
                    + short_id({"sid": scenario.scenario_id, "lane": "execution"}),
                }
            )
    if span_name == "l2.e5.seal":
        attrs.update(
            {"sealed_digest": sealed.digest, "cited_evidence_count": len(sealed.cited_evidence_refs)}
        )
    return attrs


def _build_claim_support(
    scenario: Scenario,
    sealed: SealedL2Artifact | None,
    evidence: FinalEvidenceContract | None,
) -> list[ClaimSupport]:
    if sealed is None:
        return []
    if not scenario.grounding_required:
        return [
            ClaimSupport(
                claim_id="c0",
                claim_text=sealed.output_text,
                support_target_type="non_grounded",
                supporting_evidence_refs=[],
                cited_span_refs=[],
                citation_anchor_status="NOT_REQUIRED",
                contradiction_refs=[],
                freshness_status="NOT_APPLICABLE",
                authority_status="NOT_APPLICABLE",
                support_level=SupportLevel.INFERENCE,
                output_action=OutputAction.INCLUDE,
            )
        ]
    if evidence is None:
        return []
    return [
        ClaimSupport(
            claim_id="c1",
            claim_text=sealed.output_text,
            support_target_type="reference_document",
            supporting_evidence_refs=[r.ref_id for r in evidence.evidence_refs],
            cited_span_refs=[r.span_locator for r in evidence.evidence_refs],
            citation_anchor_status="RESOLVED",
            contradiction_refs=[],
            freshness_status="FRESH",
            authority_status="AUTHORITATIVE",
            support_level=SupportLevel.DIRECT,
            output_action=OutputAction.INCLUDE,
        )
    ]


def _build_replay_inputs(
    root: ContractRoot,
    route: RouteContract,
    evidence: FinalEvidenceContract | None,
    prompt: PromptEnvelope | None,
    sealed: SealedL2Artifact | None,
) -> dict[str, Any]:
    return {
        "normalized_request_hash": digest({"intent": "deterministic", "policy_hash": root.policy_hash}),
        "input_hash": digest({"request_id": root.request_id, "policy": root.policy_hash}),
        "prompt_hash": prompt.prompt_hash if prompt else None,
        "route_digest": route.route_digest,
        "evidence_contract_hash": evidence.evidence_contract_hash if evidence else None,
        "policy_hash": root.policy_hash,
        "blueprint_hash": root.blueprint_hash,
        "snapshot_manifest": "snapshot:" + short_id("snapshot.v1"),
        "environment_digest": "env:" + short_id("env.v1"),
        "tool_registry_digest": "tools:" + short_id("tools.v1"),
        "model_registry_digest": "models:" + short_id("models.v1"),
        "provider_lane": "provider:lane-A",
        "replay_key": root.replay_key,
        "execution_digest": sealed.digest if sealed else None,
    }


# ---------------------------------------------------------------------------
# Internal: dataclass -> jsonable
# ---------------------------------------------------------------------------


def _to_jsonable(obj: Any) -> Any:
    if _dc.is_dataclass(obj) and not isinstance(obj, type):
        return {k: _to_jsonable(v) for k, v in _dc.asdict(obj).items()}
    if isinstance(obj, dict):
        return {k: _to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_jsonable(v) for v in obj]
    if hasattr(obj, "value") and obj.__class__.__bases__ and obj.__class__.__bases__[0] is not object:
        try:
            return obj.value  # type: ignore[attr-defined]
        except AttributeError:
            return repr(obj)
    return obj


__all__ = ["RunArtifacts", "emit_run"]
