"""Native core contract chain proof — AppBindingPackage → U0/L1/L0-shaped carriers.

Filesystem + YAML only; **no** ``import apps_*``. Used by the opt-in
``apps_rg`` native-core E2E certification harness (not the default product entry).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

from agentic_core.L0_routing.u0_intake_validator import AuthorityValidationReceipt
from agentic_core.runtime.bindings.app_binding_package import AppBindingPackage
from agentic_core.runtime.bindings.app_binding_validation import infer_repo_root
from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import GraphTraversePolicy, RouteContract

# Proof selects a single stable managed-workflow profile row by ID (explicit; no resolver).
NATIVE_PROOF_ROUTE_PROFILE_ID = "arpf::apps_rg::resume_generation::default_single_step::v1"
NATIVE_PROOF_L5_CERT_REF = "test:valid:w6"
NATIVE_PROOF_TASK_CLASS = "resume_generation"

_EXEC_FORM_NORMALIZE = {
    "SINGLE_STEP": "single_step",
    "MANAGED_WORKFLOW": "managed_workflow",
    "MULTI_TURN": "multi_turn",
}


class NativeContractChainError(ValueError):
    """Raised when binding-derived artifacts cannot build a native proof chain."""


@dataclass(frozen=True, slots=True)
class NativeCoreContractChainProof:
    """U0/L1/L0-shaped objects derived only from generic binding package sections."""

    validated_request: ValidatedRequest
    l1_plan_contract: L1PlanContract
    route_contract: RouteContract


@dataclass(frozen=True, slots=True)
class NativeCoreRuntimeExhaustL6Proof:
    """Post-exit exhaust + observer-only L6 handoff (proof harness)."""

    stage_map: dict[str, str]
    contract_inventory: tuple[str, ...]
    x1_ref: str
    x2_ref: str
    x3_ref: str
    l6_handoff_refs: tuple[str, ...]
    l6_approval_authority: str
    learning_mutation_performed: bool
    promotion_allowed: bool
    memory_promotion_refs: tuple[str, ...]
    current_run_boundary_receipt_ref: str


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise NativeContractChainError(f"expected mapping YAML at {path}")
    return raw


def _route_profiles_list(repo_root: Path, authority_rel: str) -> list[dict[str, Any]]:
    abs_path = (repo_root / authority_rel).resolve()
    if not abs_path.is_file():
        raise NativeContractChainError(f"route_profiles missing: {abs_path}")
    data = yaml.safe_load(abs_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise NativeContractChainError("route_profiles.yaml must be a list")
    return [x for x in data if isinstance(x, dict)]


def _select_route_profile(
    entries: list[dict[str, Any]],
    *,
    route_profile_id: str,
) -> dict[str, Any]:
    for entry in entries:
        if str(entry.get("route_profile_id") or "").strip() == route_profile_id:
            return entry
    raise NativeContractChainError(f"route_profile_id not found: {route_profile_id!r}")


def _graph_policy_from_entry(entry: Mapping[str, Any]) -> GraphTraversePolicy | None:
    block = entry.get("graph_traverse")
    if not isinstance(block, dict):
        return None
    rel_types = block.get("allowed_relation_types") or []
    if not isinstance(rel_types, list):
        rel_types = []
    return GraphTraversePolicy(
        graph_expansion_allowed=bool(block.get("graph_expansion_allowed", False)),
        max_hops=int(block.get("max_hops") or 0),
        max_nodes=int(block.get("max_nodes") or 0),
        max_edges=int(block.get("max_edges") or 0),
        allowed_relation_types=tuple(str(x) for x in rel_types),
        contradiction_scan_enabled=bool(block.get("contradiction_scan_enabled", False)),
        supersession_scan_enabled=bool(block.get("supersession_scan_enabled", False)),
        graph_adapter_ref=str(block.get("graph_adapter_ref") or ""),
        live_wiring_deferred=bool(block.get("live_wiring_deferred", True)),
        wiring_gate=str(block.get("wiring_gate") or ""),
    )


def build_native_core_contract_chain_from_binding(
    package: AppBindingPackage,
    *,
    repo_root: Path | None = None,
    request_id: str = "native-proof-req",
    run_id: str = "native-proof-run",
    trace_id: str = "native-proof-trace",
    route_profile_id: str = NATIVE_PROOF_ROUTE_PROFILE_ID,
) -> NativeCoreContractChainProof:
    """Derive ValidatedRequest + L1PlanContract + RouteContract from binding YAML only."""
    rr = repo_root if repo_root is not None else infer_repo_root(package.package_root)
    if rr is None:
        raise NativeContractChainError("cannot infer repo_root for native proof chain")

    sections = package.section_paths
    l1_path = sections.get("l1_static_plan_profile")
    l0_path = sections.get("l0_managed_route_profile")
    if l1_path is None or not l1_path.is_file():
        raise NativeContractChainError("missing l1_static_plan_profile section file")
    if l0_path is None or not l0_path.is_file():
        raise NativeContractChainError("missing l0_managed_route_profile section file")

    l1_doc = _load_yaml(l1_path)
    l0_doc = _load_yaml(l0_path)

    posture = l1_doc.get("planning_posture")
    if not isinstance(posture, dict) or not posture.get("mode"):
        raise NativeContractChainError("l1_static_plan_profile: missing planning_posture.mode")
    hops = l1_doc.get("plan_hops")
    if not isinstance(hops, list) or not hops:
        raise NativeContractChainError("l1_static_plan_profile: missing plan_hops")

    stable_refs = l1_doc.get("digest_stable_refs") or {}
    if not isinstance(stable_refs, dict):
        raise NativeContractChainError("l1_static_plan_profile: digest_stable_refs must be a mapping")
    rg_plan_rel = str(stable_refs.get("rg_planning_profile_ssot") or "").strip()
    if not rg_plan_rel:
        raise NativeContractChainError("l1_static_plan_profile: missing rg_planning_profile_ssot ref")
    rg_plan_path = rr / rg_plan_rel
    if not rg_plan_path.is_file():
        raise NativeContractChainError(f"L1 digest ref file missing: {rg_plan_path}")
    profile_manifest_digest = _sha256_file(rg_plan_path)

    authority_rel = str(l0_doc.get("route_profiles_authority_path") or "").strip()
    if not authority_rel:
        raise NativeContractChainError("l0_managed_route_profile: missing route_profiles_authority_path")

    forbidden_frags = [
        str(x).strip().upper()
        for x in (l0_doc.get("binding_v1_posture") or {}).get("forbids_routes_matching", [])
        if str(x).strip()
    ]

    entries = _route_profiles_list(rr, authority_rel)
    profile = _select_route_profile(entries, route_profile_id=route_profile_id)
    spine = profile.get("spine")
    if not isinstance(spine, dict):
        raise NativeContractChainError("route profile spine missing")

    route_id = str(spine.get("route_id") or "").strip()
    route_family = str(spine.get("route_family") or "").strip()
    exec_raw = str(spine.get("execution_form") or "").strip()
    blob = f"{route_id}::{route_family}".upper()
    for frag in forbidden_frags:
        if frag and frag in blob:
            raise NativeContractChainError(f"route profile violates forbidden fragment {frag!r}")

    execution_form = _EXEC_FORM_NORMALIZE.get(exec_raw, exec_raw.lower())

    l3_required = bool(spine.get("l3_required", False))
    rid_upper = route_id.upper()
    grounding_required = "GROUNDED" in rid_upper or "R3" in rid_upper or "GENERATIVE" in rid_upper
    model_generation_required = "GENERATIVE" in rid_upper or "GROUNDED" in rid_upper or bool(
        profile.get("personalization_default"),
    )

    mw = profile.get("managed_workflow") if isinstance(profile.get("managed_workflow"), dict) else {}
    workflow_ref = str(mw.get("workflow_ref") or "")
    workflow_manifest_ref = str(mw.get("workflow_manifest_ref") or "")
    workflow_registry_ref = str(mw.get("workflow_registry_ref") or "")

    graph_policy = _graph_policy_from_entry(profile)

    now_iso = datetime.now(timezone.utc).isoformat()
    auth_rcpt = AuthorityValidationReceipt(validation_timestamp=now_iso)

    validated = ValidatedRequest(
        request_id=request_id,
        run_id=run_id,
        app_id=package.app_id,
        task_class=NATIVE_PROOF_TASK_CLASS,
        payload_digest="sha256:native-proof-binding",
        authority_validation_receipt=auth_rcpt,
        trace_id=trace_id,
        tenant_id=package.app_id,
        l5_certification_ref=NATIVE_PROOF_L5_CERT_REF,
        app_payload={},
        replay_key=f"replay:{request_id}",
    )

    task_plan = tuple(
        str(h.get("hop_id") or "").strip()
        for h in hops
        if isinstance(h, dict) and str(h.get("hop_id") or "").strip()
    )
    if not task_plan:
        raise NativeContractChainError("could not derive task_plan hop ids")

    l1_contract = L1PlanContract(
        request_id=request_id,
        run_id=run_id,
        app_id=package.app_id,
        trace_id=trace_id,
        task_plan=task_plan,
        grounding_required=grounding_required,
        model_generation_required=model_generation_required,
        write_authority_present=False,
        profile_manifest_digest=profile_manifest_digest,
        route_profile_ref=authority_rel,
        tenant_id=package.app_id,
        replay_key=validated.replay_key,
        l5_certification_ref=NATIVE_PROOF_L5_CERT_REF,
    )

    route = RouteContract(
        request_id=request_id,
        run_id=run_id,
        app_id=package.app_id,
        trace_id=trace_id,
        route_id=route_id,
        l3_required=l3_required,
        grounding_required=grounding_required,
        model_generation_required=model_generation_required,
        write_authority_present=False,
        tenant_id=package.app_id,
        route_family=route_family,
        execution_form=execution_form,
        workflow_ref=workflow_ref,
        workflow_manifest_ref=workflow_manifest_ref,
        workflow_registry_ref=workflow_registry_ref,
        route_profile_ref=authority_rel,
        route_policy_ref=authority_rel,
        replay_key=validated.replay_key,
        l5_certification_ref=NATIVE_PROOF_L5_CERT_REF,
        graph_traverse_policy=graph_policy,
    )

    return NativeCoreContractChainProof(
        validated_request=validated,
        l1_plan_contract=l1_contract,
        route_contract=route,
    )


_OTEL_SPAN_KEYS = (
    "trace_root",
    "route_contract",
    "tool_invocations",
    "evidence_contracts",
    "step_outputs",
    "exit_disposition",
)


def build_ag5_terminal_dict_for_native_proof(
    chain: NativeCoreContractChainProof,
    *,
    replay_key: str = "native-proof-ag5-replay",
    source_type: str = "APP_BINDING_COMPATIBILITY_PACKAGE",
) -> dict[str, Any]:
    """Build an AG-5 terminal envelope dict from the native proof chain (neutral path)."""
    rc = chain.route_contract
    vr = chain.validated_request
    policy_hash = "native-core-proof-policy"
    return {
        "source_type": source_type,
        "route_contract_ref": f"route://native-core-proof/{rc.route_id}",
        "route_id": rc.route_id,
        "replay_key": replay_key,
        "terminal_class": "answer_only",
        "path_class": "neutral",
        "policy_hash": policy_hash,
        "blueprint_hash": "",
        "request_id": vr.request_id,
        "run_id": vr.run_id,
        "trace_root": vr.trace_id,
        "app_id": vr.app_id,
        "task_class": vr.task_class,
        "route_contract": {
            "route_id": rc.route_id,
            "execution_form": rc.execution_form,
            "policy_hash": policy_hash,
        },
        "grader_composition": {"roster": ["native-core-proof-grader"], "threshold_profile": {"p": 1}},
        "track_label": "production",
        "output": {"completion_score": 1.0, "cache_freshness_ok": True},
        "otel_spans": {"spans": {k: {"present": True} for k in _OTEL_SPAN_KEYS}},
        "exec_trace": {"replay_receipts_present": True},
    }


def build_native_runtime_exhaust_l6_proof(
    *,
    exit_disposition_digest: str,
    gate_mesh_ref: str,
    route_contract_ref: str,
    sealed_result_ref: str,
    x1_summary_digest: str,
    x2_summary_digest: str,
) -> NativeCoreRuntimeExhaustL6Proof:
    """Observer-only exhaust proof — no promotion, no learning mutation."""
    x3_ref = f"x3:{exit_disposition_digest}"
    return NativeCoreRuntimeExhaustL6Proof(
        stage_map={
            "U0": "validated_request_emitted",
            "L1": "l1_plan_contract_emitted",
            "L0": "route_contract_emitted",
            "EXIT": "ag5_x3_emitted",
            "L6": "handoff_observer_only",
        },
        contract_inventory=(
            "ValidatedRequest",
            "L1PlanContract",
            "RouteContract",
            "ExitReviewPacket",
            "X1CheckoutResult",
            "X2AggregationResult",
            "ExitDispositionReceipt",
        ),
        x1_ref=f"x1:{x1_summary_digest}",
        x2_ref=f"x2:{x2_summary_digest}",
        x3_ref=x3_ref,
        l6_handoff_refs=(x3_ref, f"mesh:{gate_mesh_ref}", f"route:{route_contract_ref}"),
        l6_approval_authority="NONE",
        learning_mutation_performed=False,
        promotion_allowed=False,
        memory_promotion_refs=(),
        current_run_boundary_receipt_ref=f"boundary:{exit_disposition_digest}",
    )


__all__ = [
    "NATIVE_PROOF_L5_CERT_REF",
    "NATIVE_PROOF_ROUTE_PROFILE_ID",
    "NativeContractChainError",
    "NativeCoreContractChainProof",
    "NativeCoreRuntimeExhaustL6Proof",
    "build_ag5_terminal_dict_for_native_proof",
    "build_native_core_contract_chain_from_binding",
    "build_native_runtime_exhaust_l6_proof",
]
