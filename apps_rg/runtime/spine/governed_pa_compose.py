"""Governed PA compose — apps_rg domain slots + core ``assemble_prompt`` (W5).

Section lanes: ``apps_rg.prompt_assembly.compiler`` produces slot payloads / BOM only.
Integrated spine: ``agentic_core.prompt_governance.orchestrator.assemble_prompt`` runs
PA.0–PA.8 (via ``run_prompt_assembly_pipeline``) and returns HMAC-signed manifest.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract as RuntimeFEC,
    SUPPORT_STATUS_PASS,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.route_contract import RouteContract

GOVERNED_PA_MODE_INTEGRATED = "core_assemble_prompt"
GOVERNED_PA_MODE_SECTION_BOM = "section_slot_bom"
GOVERNED_PA_MODE_SECTION_CORE_SIGNED = "section_slot_bom_core_signed"
SPINE_PA_CORE_RECEIPT = "spine_pa_core_signing_receipt.json"


def governed_pa_compose_enabled() -> bool:
    if os.environ.get("APPS_RG_GOVERNED_PA_SKIP", "").strip().lower() in (
        "1",
        "true",
        "yes",
    ):
        return False
    return True


def _sha256_hex64(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _sha256_json_hex64(payload: Any) -> str:
    return _sha256_hex64(json.dumps(payload, sort_keys=True, default=str))


def _l1_planning_capsule_from_plan(plan: L1PlanContract) -> dict[str, Any]:
    task_spec = dict(plan.task_spec or {})
    capsule = task_spec.get("apps_rg_planning_capsule")
    return dict(capsule) if isinstance(capsule, Mapping) else {}


def _l1_planning_component_hashes(capsule: Mapping[str, Any]) -> dict[str, str]:
    if not capsule:
        return {}
    return {
        "l1_planning_capsule": _sha256_json_hex64(capsule),
        "l1_prompt_plan": _sha256_json_hex64(capsule.get("prompt_plan", [])),
        "l1_completion_criteria": _sha256_json_hex64(capsule.get("completion_criteria", [])),
        "l1_cognition_plan_requested": _sha256_json_hex64(capsule.get("cognition_plan", [])),
    }


def _stable_app_payload_for_hash(payload: Mapping[str, Any]) -> dict[str, Any]:
    stable = json.loads(json.dumps(dict(payload or {}), sort_keys=True, default=str))
    receipt = stable.get("package_validation_receipt")
    if isinstance(receipt, dict):
        receipt.pop("timestamp_iso", None)
    return stable


def _policy_hashes(route: RouteContract, plan: L1PlanContract) -> tuple[str, str]:
    policy = str(getattr(route, "route_digest", "") or "")[:32]
    blueprint = str(plan.profile_manifest_digest or "")[:32]
    if not policy:
        policy = _sha256_hex64(json.dumps({"route_id": route.route_id}, sort_keys=True))[:32]
    if not blueprint:
        blueprint = policy
    return policy, blueprint


def _map_support_status(status: str) -> Any:
    from apps_rg.runtime.spine.governed_pa_c0_contracts import SupportStatus

    mapping = {
        "PASS": SupportStatus.PASS,
        "WEAK": SupportStatus.WEAK,
        "WEAK_WITH_CAVEATS": SupportStatus.WEAK_WITH_CAVEATS,
        "EMPTY": SupportStatus.EMPTY,
        "BLOCKED": SupportStatus.BLOCKED,
        "CONFLICTED": SupportStatus.CONFLICTED,
        "UNKNOWN": SupportStatus.EMPTY,
        "NOT_APPLICABLE": SupportStatus.EMPTY,
    }
    return mapping.get(str(status or "").upper(), SupportStatus.EMPTY)


def runtime_fec_to_orchestrator_contract(
    fec: RuntimeFEC,
    *,
    route: RouteContract,
    plan: L1PlanContract,
) -> Any:
    """Adapt runtime ``FinalEvidenceContract`` for core PA orchestrator."""
    from apps_rg.runtime.spine.governed_pa_c0_contracts import (
        CandidateChunk,
        ChunkBoundaryRisk,
        FinalEvidenceContract,
        HydratedChunk,
        HydrationManifest,
        QualityFlags,
        RetrievalLane,
        SourceClass,
    )

    policy_hash, blueprint_hash = _policy_hashes(route, plan)
    hydrated: list[HydratedChunk] = []
    for idx, item in enumerate(fec.evidence_items or ()):
        chunk_id = str(getattr(item, "evidence_id", "") or getattr(item, "source", "") or f"ev-{idx}")
        text = str(getattr(item, "content", "") or "").strip() or f"[{chunk_id}]"
        source_path = str(getattr(item, "source", "") or chunk_id)
        manifest = HydrationManifest(
            source_id=chunk_id,
            file_path=source_path,
            section="apps_rg",
        )
        candidate = CandidateChunk(
            chunk_id=chunk_id,
            source_class=SourceClass.PRIOR_ARTIFACTS,
            text=text,
            manifest=manifest,
            found_by_lanes=(RetrievalLane.DENSE,),
        )
        quality = QualityFlags(
            span_resolves=True,
            source_version_current=True,
            acl_clear=True,
            parent_context_available=True,
            citation_anchor_stable=True,
            chunk_boundary_risk=ChunkBoundaryRisk.LOW,
        )
        hydrated.append(
            HydratedChunk(
                candidate=candidate,
                canonical_source_path=source_path,
                section_hierarchy=(),
                chunk_version="v1",
                citation_anchor_candidates=(chunk_id,),
                quality=quality,
            )
        )

    status = _map_support_status(str(fec.support_status or ""))
    support_score = 1.0 if str(fec.support_status or "") in (SUPPORT_STATUS_PASS, "PASS") else 0.5
    if not hydrated and status.name == "PASS":
        support_score = 0.0
        status = _map_support_status("EMPTY")

    return FinalEvidenceContract(
        contract_id=f"fec-{fec.request_id or route.request_id}",
        route_id=route.route_id,
        route_replay_key=plan.replay_key or route.replay_key or fec.request_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        status=status,
        support_score=support_score,
        must_use=tuple(hydrated),
        supporting=(),
    )


def runtime_route_to_orchestrator_route(route: RouteContract) -> Any:
    from apps_rg.runtime.spine.governed_pa_c0_contracts import (
        FreshnessClass,
        RouteContract as OrchRoute,
        SupportTarget,
    )

    policy_hash, blueprint_hash = _policy_hashes(route, L1PlanContract(
        request_id=route.request_id,
        run_id=route.run_id,
        app_id=route.app_id,
        trace_id=route.trace_id,
        l5_certification_ref=route.l5_certification_ref,
    ))
    l5_ref = str(getattr(route, "l5_certification_ref", "") or "").strip()
    execution_form = str(route.execution_form or "SINGLE_STEP").upper()
    if execution_form == "MANAGED_WORKFLOW":
        execution_form = "MANAGED_WORKFLOW_STEP"

    return OrchRoute(
        route_id=route.route_id,
        grounding_required=bool(route.grounding_required),
        execution_form=execution_form,
        freshness_class=FreshnessClass.CURRENT,
        support_target=SupportTarget.SOURCE_SUMMARY,
        tenant_scope=str(route.tenant_id or "apps_rg"),
        route_replay_key=route.replay_key or route.request_id,
        policy_hash=policy_hash,
        blueprint_hash=blueprint_hash,
        hmac_sig=str(route.hmac_sig or route.signature or ""),
        app_id=route.app_id,
        task_class="resume_generation",
        l5_certification_ref=l5_ref,
    )


def runtime_plan_to_orchestrator_plan(
    plan: L1PlanContract,
    validated_request: ValidatedRequest,
) -> Any:
    from apps_rg.runtime.spine.governed_pa_c0_contracts import L1PlanContract as OrchPlan

    qs = dict(plan.query_spec or {})
    tgt = qs.get("target") if isinstance(qs.get("target"), dict) else {}
    company = str(tgt.get("company", "") or "")
    role = str(tgt.get("role", "") or "")
    level = str(tgt.get("level", "") or plan.target_level or "")
    lines = [
        f"Target company: {company}",
        f"Target role: {role}",
        f"Target level: {level}",
    ]
    ts = dict(plan.task_spec or {})
    if ts.get("generation_mode"):
        lines.append(f"Generation mode: {ts.get('generation_mode')}")
    user_task = "\n".join(lines)
    return OrchPlan(
        task_spec=json.dumps(dict(plan.task_spec or {}), sort_keys=True),
        query_spec=json.dumps(dict(plan.query_spec or {}), sort_keys=True),
        grounding_required=bool(plan.grounding_required),
        user_task_text=user_task or str(validated_request.request_id),
    )


def envelope_to_runtime_compiled_prompt(
    envelope: Any,
    *,
    route: RouteContract,
    plan: L1PlanContract,
    fec: RuntimeFEC,
    validated_request: ValidatedRequest,
) -> CompiledPromptArtifact:
    """Map core ``CompiledPromptEnvelope`` to runtime ``CompiledPromptArtifact``."""
    from apps_rg.runtime.bindings.pa_binding import (
        APPS_RG_TARGET_MODEL,
        APPS_RG_TARGET_PROVIDER,
    )

    pe = envelope.envelope
    blocks = (
        PromptBlock(
            role="system",
            content=pe.system_message,
            block_index=0,
            origin=Origin.SYSTEM_INTERNAL,
        ),
        PromptBlock(
            role="user",
            content=pe.user_message,
            block_index=1,
            origin=Origin.USER_INTENT,
        ),
    )
    gate_refs: list[str] = []
    if route.hmac_sig:
        gate_refs.append(f"route_hmac:{route.hmac_sig[:32]}")
    gate_refs.append(f"pa_manifest:{envelope.manifest_hash}")
    gate_refs.append(f"pa_hmac:{envelope.hmac_signature[:32]}")
    gate_refs.extend(list(route.gate_verdict_refs or ()))

    plan_key = {
        "task_spec": dict(plan.task_spec or {}),
        "query_spec": dict(plan.query_spec or {}),
        "support_expectation": dict(plan.support_expectation or {}),
        "output_expectation": dict(plan.output_expectation or {}),
    }
    app_payload = _stable_app_payload_for_hash(
        getattr(validated_request, "app_payload", None) or {}
    )
    route_key = {
        "route_id": route.route_id,
        "route_family": route.route_family,
        "execution_form": route.execution_form,
        "provider_model_requirement_ref": route.provider_model_requirement_ref,
    }
    ev_digest = str(
        getattr(fec, "final_evidence_digest", "")
        or getattr(fec, "compilation_hash", "")
        or ""
    )
    component_hash_map = {
        "style_profile": _sha256_json_hex64(
            {
                "governed_pa_mode": GOVERNED_PA_MODE_INTEGRATED,
                "target_model": APPS_RG_TARGET_MODEL,
                "target_provider": APPS_RG_TARGET_PROVIDER,
            }
        ),
        "evidence": _sha256_hex64(ev_digest),
        "l1_plan": _sha256_json_hex64(plan_key),
        "app_payload": _sha256_json_hex64(app_payload),
        "route": _sha256_json_hex64(route_key),
        "governed_pa": _sha256_hex64(envelope.hmac_signature),
    }
    capsule = _l1_planning_capsule_from_plan(plan)
    component_hash_map.update(_l1_planning_component_hashes(capsule))
    slot_lineage_map: dict[str, str] = {
        "system_block_0": "PA-authored|SYSTEM_INTERNAL|core_assemble_prompt",
        "user_block_1": "USER_INTENT|L1_PLAN_PROJECTIONS|core_assemble_prompt",
        "l1_planning_capsule": "L1_PLAN_PROJECTIONS|PLANNING_ADVISORY_ONLY",
        "evidence": f"C0:{ev_digest}",
    }
    for idx, row in enumerate(envelope.slot_manifest):
        if not isinstance(row, dict):
            continue
        slot_id = str(row.get("slot_id") or row.get("slot") or "").strip()
        if not slot_id:
            continue
        status = str(row.get("status") or "resolved")
        slot_lineage_map[f"slot_{idx}"] = f"{slot_id}|{status}"
    rk = plan.replay_key or getattr(validated_request, "replay_key", "") or ""

    return CompiledPromptArtifact(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        prompt_blocks=blocks,
        system_preamble=pe.system_message,
        user_instruction=pe.user_message,
        assembly_timestamp=envelope.replay_metadata.get("signed_at", ""),
        target_model=APPS_RG_TARGET_MODEL,
        target_provider=APPS_RG_TARGET_PROVIDER,
        evidence_digest=str(getattr(fec, "final_evidence_digest", "") or ""),
        compilation_hash=envelope.manifest_hash,
        slot_lineage_map=slot_lineage_map,
        component_hash_map=component_hash_map,
        replay_manifest_ref=f"replay_key:{envelope.replay_key or rk}",
        per_input_hash_map=dict(getattr(plan, "per_input_hash_map", None) or {}),
        tenant_id=str(validated_request.tenant_id or ""),
        l5_certification_ref=validated_request.l5_certification_ref,
        gate_verdict_refs=tuple(gate_refs),
        replay_key=rk,
        signature=envelope.hmac_signature,
    )


def governed_pa_compose_integrated(
    route: RouteContract,
    plan: L1PlanContract,
    fec: RuntimeFEC,
    validated_request: ValidatedRequest,
    *,
    secret_key: bytes | None = None,
) -> CompiledPromptArtifact:
    """Integrated apps_rg PA — core ``assemble_prompt`` (PA.0–PA.8)."""
    from agentic_core.prompt_governance import assemble_prompt

    orch_fec = runtime_fec_to_orchestrator_contract(fec, route=route, plan=plan)
    orch_route = runtime_route_to_orchestrator_route(route)
    orch_plan = runtime_plan_to_orchestrator_plan(plan, validated_request)

    if secret_key is None:
        env_key = os.environ.get("PROMPT_ASSEMBLY_HMAC_KEY", "").strip()
        secret_key = env_key.encode("utf-8") if env_key else b"apps-rg-w5-proof-harness"

    envelope = assemble_prompt(
        final_contract=orch_fec,
        route=orch_route,
        plan=orch_plan,
        request_id=validated_request.request_id,
        secret_key=secret_key,
    )
    artifact = envelope_to_runtime_compiled_prompt(
        envelope,
        route=route,
        plan=plan,
        fec=fec,
        validated_request=validated_request,
    )
    return artifact


def section_slot_bom_from_compiled(section_compiled: Any) -> dict[str, Any]:
    """Extract domain slot BOM from apps_rg ``SectionCompiledPrompt`` / compiler output."""
    art = section_compiled.artifact
    slots = []
    for payload in getattr(art, "slot_payloads", None) or ():
        slots.append(
            {
                "slot_id": getattr(payload, "slot_id", ""),
                "authority_class": getattr(getattr(payload, "authority_class", None), "name", ""),
                "content_hash": getattr(payload, "content_hash", ""),
                "source_tag": getattr(payload, "source_tag", None),
            }
        )
    return {
        "schema_version": "apps_rg_section_slot_bom_v1",
        "governed_pa_mode": GOVERNED_PA_MODE_SECTION_BOM,
        "section_id": getattr(section_compiled, "section_id", ""),
        "apps_rg_prompt_template_ref": getattr(section_compiled, "apps_rg_prompt_template_ref", ""),
        "template_id": getattr(art, "template_id", ""),
        "prompt_hash": getattr(art, "prompt_hash", ""),
        "canonical_slot_order": list(getattr(art, "canonical_slot_order", None) or []),
        "slot_payloads": slots,
        "component_hash_map": getattr(art, "component_hash_map", None),
        "provider_render_manifest": dict(getattr(art, "provider_render_manifest", None) or {}),
        "core_assemble_prompt_invoked": False,
        "producer": "apps_rg.prompt_assembly.compiler",
    }


def governed_pa_sign_section_core(
    runtime_payload: dict[str, Any],
    *,
    artifact_dir: Path | None = None,
) -> dict[str, Any] | None:
    """Run core ``assemble_prompt`` for HMAC/manifest; keep section slot BOM as primary."""
    from pathlib import Path as _Path

    from apps_rg.runtime.spine.spine_contract_loaders import load_spine_contracts_for_section

    if not governed_pa_compose_enabled():
        return None
    if not runtime_payload.get("product_visible", True):
        return None
    bridge = runtime_payload.get("section_fec_bridge")
    if not isinstance(bridge, dict):
        return None
    ad = artifact_dir or _Path(str(runtime_payload.get("artifact_dir") or "."))
    if not ad.is_dir():
        return None
    loaded = load_spine_contracts_for_section(ad, runtime_payload)
    if loaded is None:
        return None
    route, plan, fec, vr = loaded
    core_artifact = governed_pa_compose_integrated(route, plan, fec, vr)
    signing = {
        "schema_version": "apps_rg_spine_pa_core_signing_v1",
        "core_assemble_prompt_invoked": True,
        "pa_manifest_hash": core_artifact.compilation_hash,
        "pa_hmac": core_artifact.signature,
        "gate_verdict_refs": list(core_artifact.gate_verdict_refs or ()),
        "replay_key": core_artifact.replay_key,
    }
    receipt_path = ad / SPINE_PA_CORE_RECEIPT
    receipt_path.write_text(
        json.dumps(signing, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    runtime_payload["spine_pa_core_signing_receipt_ref"] = SPINE_PA_CORE_RECEIPT
    runtime_payload["pa_manifest_hash"] = core_artifact.compilation_hash
    runtime_payload["pa_hmac"] = core_artifact.signature
    summary = dict(runtime_payload.get("compiled_prompt_artifact_summary") or {})
    summary.update(
        {
            "compilation_hash": core_artifact.compilation_hash,
            "signature": core_artifact.signature,
            "gate_verdict_refs": list(core_artifact.gate_verdict_refs or ()),
        }
    )
    runtime_payload["compiled_prompt_artifact_summary"] = summary
    return signing


def stamp_section_governed_pa_receipt(
    runtime_payload: dict[str, Any],
    section_compiled: Any,
    *,
    artifact_dir: Path | None = None,
) -> dict[str, Any]:
    """Attach section slot BOM receipt; invoke core PA signing when front-spine + FEC present."""
    from pathlib import Path as _Path

    bom = section_slot_bom_from_compiled(section_compiled)
    runtime_payload["governed_pa_receipt"] = bom
    runtime_payload["governed_pa_mode"] = GOVERNED_PA_MODE_SECTION_BOM

    bridge = runtime_payload.get("section_fec_bridge")
    if (
        not governed_pa_compose_enabled()
        or not isinstance(bridge, dict)
        or not runtime_payload.get("product_visible", True)
    ):
        return bom

    ad = artifact_dir or _Path(str(runtime_payload.get("artifact_dir") or ""))
    signing = governed_pa_sign_section_core(runtime_payload, artifact_dir=ad if ad.is_dir() else None)
    if signing:
        bom["core_assemble_prompt_invoked"] = True
        bom["pa_manifest_hash"] = signing["pa_manifest_hash"]
        bom["pa_hmac"] = signing["pa_hmac"]
        bom["governed_pa_mode"] = GOVERNED_PA_MODE_SECTION_CORE_SIGNED
        runtime_payload["governed_pa_receipt"] = bom
        runtime_payload["governed_pa_mode"] = GOVERNED_PA_MODE_SECTION_CORE_SIGNED
        from apps_rg.runtime.spine.spine_span_emit import emit_spine_span_event

        emit_spine_span_event(
            ad if ad.is_dir() else None,
            layer_key="PA",
            binding_seam="apps_rg/runtime/spine/governed_pa_compose.py",
            status="core_signed",
            extra={"pa_manifest_hash": signing["pa_manifest_hash"][:16]},
            product_visible=bool(runtime_payload.get("product_visible", True)),
        )
    return bom


__all__ = [
    "GOVERNED_PA_MODE_INTEGRATED",
    "GOVERNED_PA_MODE_SECTION_BOM",
    "GOVERNED_PA_MODE_SECTION_CORE_SIGNED",
    "SPINE_PA_CORE_RECEIPT",
    "envelope_to_runtime_compiled_prompt",
    "governed_pa_compose_enabled",
    "governed_pa_compose_integrated",
    "governed_pa_sign_section_core",
    "runtime_fec_to_orchestrator_contract",
    "runtime_plan_to_orchestrator_plan",
    "runtime_route_to_orchestrator_route",
    "section_slot_bom_from_compiled",
    "stamp_section_governed_pa_receipt",
]
