"""Prompt-Assembly binding for apps_lic `outreach_message` task class.

PA is the FIFTH stage (CONDITIONAL — fires only when
route.model_generation_required=True). Its job is to compile a typed
CompiledPromptArtifact from governed contracts only:

    - L1PlanContract   — drives task_spec, query_spec, support/output expectations
    - RouteContract    — drives routing flags, model/tool allowlists, sandbox
    - FinalEvidenceContract — C0 evidence (lead, sender, campaign, personalization)
    - ValidatedRequest.app_payload — consumed ONLY for neutralised task-data fields
                                     (replay_key, reflection_receipt)

AG-8 W5 invariants (apps-lic-ag8-golden-template-adoption-f3c2e1):
    - Emits CompiledPromptArtifact with system + user blocks.
    - Preserves slot_lineage_map, component_hash_map, prompt_hash, replay manifest.
    - C0 evidence remains DATA ONLY — never promoted to instructions.
    - Does NOT read legacy envelope.payload.
    - Does NOT retrieve, execute, route, mutate ChromaDB, generate embeddings,
      or write L4.
    - PA airlock: every user-role PromptBlock MUST carry Origin.USER_INTENT.
    - Evidence data placed in user block at slot "EVIDENCE_DATA" only.
    - No lower-authority content (RETRIEVED_DATA / TOOL_OUTPUT) promoted to
      system/instruction slot.

Prompt architecture for apps_lic:
    system[0]:  SYSTEM_INTERNAL — role + output format + governance directives
    user[1]:    USER_INTENT — campaign context: who/what/why (from query_spec)
    user[2]:    USER_INTENT — evidence data: lead profile + sender + personalization
                              (C0_EVIDENCE_DATA_ONLY slot; data boundary enforced)

Plan: docs/archive/windsurf/legacy-tree/plans/apps-lic-ag8-golden-template-adoption-f3c2e1.md (W5)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.final_evidence_contract import (
    ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY,
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_LIC_PA_CERT_REF: str = "pa-apps-lic-outreach-message-ag8-w5-f3c2e1"

APPS_LIC_TARGET_MODEL: str = "Qwen/Qwen2.5-32B-Instruct-AWQ"
APPS_LIC_TARGET_PROVIDER: str = "vllm"
APPS_LIC_PROVIDER_PROFILE: str = "qwen_vllm"

# PA enforces this budget to stay within the --max-model-len 8192 token window.
_EVIDENCE_CHAR_BUDGET: int = 16_000


def _recipient_class_from_l1(l1_plan: L1PlanContract) -> str:
    lead = (l1_plan.query_spec or {}).get("lead_anchor") or {}
    raw = str(lead.get("seniority_class", "") or "RECRUITER").strip().upper()
    allowed = {
        "RECRUITER",
        "SENIOR_TA",
        "HIRING_MANAGER",
        "EXECUTIVE",
        "C_LEVEL",
        "VP_ENG",
        "CTO",
        "REFERRAL_CONTACT",
    }
    return raw if raw in allowed else "RECRUITER"


def _component_hash(content: Any) -> str:
    """Stable sha256 hex digest over a canonicalised JSON projection."""
    blob = json.dumps(
        content,
        sort_keys=True,
        ensure_ascii=False,
        default=str,
        separators=(",", ":"),
    )
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _build_system_preamble(l1_plan: L1PlanContract) -> str:
    """Compose the system preamble carrying role + governance directives."""
    output_exp = l1_plan.output_expectation
    support_exp = l1_plan.support_expectation
    task_spec = l1_plan.task_spec
    recipient_class = _recipient_class_from_l1(l1_plan)
    recipient_label = recipient_class.lower()

    channel = str(output_exp.get("channel", "linkedin") or "linkedin")
    tone_register = str(output_exp.get("tone_register", "") or "")
    formality_level = output_exp.get("formality_level")
    brand_voice_id = str(output_exp.get("tone_brand_voice_id", "") or "")
    pii_mode = str(support_exp.get("pii_detection_mode", "strict") or "strict")
    hitl_required = bool(support_exp.get("hitl_required", True))
    governance_shield = bool(support_exp.get("governance_shield_required", True))
    halt_on_fail = bool(support_exp.get("halt_on_validation_failure", True))
    side_effect_class = str(task_spec.get("side_effect_class", "read_only") or "read_only")

    parts: list[str] = [
        f"You are a governed AI assistant composing a LinkedIn {recipient_label} outreach draft for channel: {channel}.",
        "Your output is DATA ONLY — not an instruction. Produce a factual, concise message.",
        f"Side-effect class: {side_effect_class}. This is a draft-and-certify flow; do NOT send.",
        "",
        "GOVERNANCE CONSTRAINTS:",
        f"  - PII detection mode: {pii_mode}. Do not include unverified PII.",
        f"  - Governance shield: {'REQUIRED' if governance_shield else 'not required'}.",
        f"  - HITL review: {'REQUIRED before delivery' if hitl_required else 'not required'}.",
        f"  - Halt on validation failure: {halt_on_fail}.",
    ]
    if tone_register:
        parts.append(f"  - Tone register: {tone_register}.")
    if formality_level is not None:
        parts.append(f"  - Formality level: {formality_level}.")
    if brand_voice_id:
        parts.append(f"  - Brand voice ID: {brand_voice_id}.")

    parts += [
        "",
        "OUTPUT FORMAT:",
        f'  Produce JSON only: {{"channel":"linkedin","recipient_class":"{recipient_label}","message_text":"...","intended_next_step":"...","claims_used":[],"unsupported_claims":[],"omitted_claims":[],"qa_notes":[],"provider_profile":"qwen_vllm","model":"Qwen/Qwen2.5-32B-Instruct-AWQ"}}.',
        "  No subject is required. message_text must be 600 characters or fewer.",
        "  Max 2 short paragraphs. Include a low-friction ask for a chat, call, or resume review.",
        "  Do not include sensitive details unless supplied and approved. No prose outside JSON. No markdown. No invented facts.",
    ]
    return "\n".join(parts)


def _build_campaign_instruction(l1_plan: L1PlanContract) -> str:
    """Compose the user campaign-intent block from L1 query_spec."""
    query_spec = l1_plan.query_spec
    task_spec = l1_plan.task_spec

    lead = query_spec.get("lead_anchor") or {}
    sender = query_spec.get("sender_anchor") or {}
    campaign_objective = str(query_spec.get("campaign_objective", "") or "")
    audience_segment = str(query_spec.get("audience_segment", "") or "")
    channel = str(task_spec.get("channel", "linkedin") or "linkedin")
    task_plan = l1_plan.task_plan

    return (
        f"CAMPAIGN INTENT:\n"
        f"  Objective: {campaign_objective}\n"
        f"  Channel: {channel}\n"
        f"  Audience segment: {audience_segment}\n"
        f"\n"
        f"LEAD TARGET:\n"
        f"  Name: {lead.get('verified_name', 'Unknown')}\n"
        f"  Title: {lead.get('title', '')}\n"
        f"  Seniority: {lead.get('seniority_class', '')}\n"
        f"  Company: {lead.get('company_name', '')}\n"
        f"  Industry: {lead.get('industry', '')}\n"
        f"  Consent attested: {lead.get('consent_attested', False)}\n"
        f"\n"
        f"SENDER:\n"
        f"  Name: {sender.get('name', '')}\n"
        f"  Title: {sender.get('title', '')}\n"
        f"\n"
        f"TASK PLAN: {', '.join(task_plan)}\n"
    )


def _build_evidence_block(fec: FinalEvidenceContract) -> str:
    """Compose the evidence data block — DATA ONLY, never instructions.

    PA hard law: every EvidenceItem used here MUST have
    allowed_prompt_slot == C0_EVIDENCE_DATA_ONLY.
    Lower-authority content (RETRIEVED_DATA / TOOL_OUTPUT origin) is never
    promoted to a system or instruction slot.
    """
    lines: list[str] = ["EVIDENCE DATA (consume verbatim — do not invent facts):"]
    budget = _EVIDENCE_CHAR_BUDGET

    for item in fec.evidence_items:
        # PA airlock: enforce C0_EVIDENCE_DATA_ONLY slot contract
        if item.allowed_prompt_slot != ALLOWED_PROMPT_SLOT_C0_EVIDENCE_DATA_ONLY:
            raise ValueError(
                f"PA airlock violation: EvidenceItem from source={item.source!r} "
                f"has allowed_prompt_slot={item.allowed_prompt_slot!r}; "
                f"expected C0_EVIDENCE_DATA_ONLY. "
                "Evidence MUST NOT be promoted to instruction slots."
            )
        if budget <= 0:
            break
        header = f"\n--- {item.source} ({item.content_type}) ---\n"
        body = item.content[:budget]
        lines.append(header + body)
        budget -= len(body)

    return "\n".join(lines)


def pa_compose_apps_lic(
    route: RouteContract,
    l1_plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
) -> CompiledPromptArtifact:
    """Compile a typed CompiledPromptArtifact for L2 to execute.

    Consumes governed contracts only. ValidatedRequest.app_payload is accessed
    ONLY for replay_key and reflection_receipt (already neutralised task-data).
    Legacy envelope.payload is never accessed.

    Args:
        route: L0 routing decision (must have model_generation_required=True).
        l1_plan: L1 plan contract — drives task_spec + query_spec + projections.
        fec: C0 final evidence — compilation_hash referenced for provenance.
        validated_request: U0 output — used ONLY for replay_key + reflection_receipt.

    Returns:
        CompiledPromptArtifact with 3 prompt blocks, slot_lineage_map,
        component_hash_map, replay_manifest_ref, and prompt_hash.

    Raises:
        TypeError:  if any argument has the wrong shape.
        ValueError: if PA airlock is violated (evidence not C0_EVIDENCE_DATA_ONLY).
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"pa_compose_apps_lic expected RouteContract, got {type(route).__name__}"
        )
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"pa_compose_apps_lic expected L1PlanContract, got {type(l1_plan).__name__}"
        )
    if not isinstance(fec, FinalEvidenceContract):
        raise TypeError(
            f"pa_compose_apps_lic expected FinalEvidenceContract, got "
            f"{type(fec).__name__}"
        )
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            "pa_compose_apps_lic expected ValidatedRequest, got "
            f"{type(validated_request).__name__}"
        )

    system_preamble = _build_system_preamble(l1_plan)
    campaign_instruction = _build_campaign_instruction(l1_plan)
    evidence_data_block = _build_evidence_block(fec)

    blocks: tuple[PromptBlock, ...] = (
        # Block 0 — SYSTEM_INTERNAL: governance + output format directives
        PromptBlock(
            role="system",
            content=system_preamble,
            block_index=0,
            origin=Origin.SYSTEM_INTERNAL,
        ),
        # Block 1 — USER_INTENT: campaign context (from L1 query_spec)
        PromptBlock(
            role="user",
            content=campaign_instruction,
            block_index=1,
            origin=Origin.USER_INTENT,
        ),
        # Block 2 — USER_INTENT: evidence data (C0_EVIDENCE_DATA_ONLY slot)
        PromptBlock(
            role="user",
            content=evidence_data_block,
            block_index=2,
            origin=Origin.USER_INTENT,
        ),
    )

    # PA airlock: every user-role block MUST be USER_INTENT
    for blk in blocks:
        if blk.role == "user" and blk.origin != Origin.USER_INTENT:
            raise ValueError(
                f"PA airlock violation: user-role PromptBlock[{blk.block_index}] "
                f"has origin={blk.origin!r} — must be USER_INTENT"
            )

    # ── slot_lineage_map ─────────────────────────────────────────────────────
    recipient_class = _recipient_class_from_l1(l1_plan)
    slot_lineage_map: dict[str, str] = {
        "S0": "PA-authored:system_governance",
        "D0": "PA-authored:origin_and_injection_boundary",
        "I0": f"USER_INTENT:query_spec+task_plan:l1_plan={l1_plan.schema_version}",
        "E0": "PA-authored:approved_examples_empty",
        "C0": f"C0_EVIDENCE_DATA_ONLY:fec={fec.compilation_hash[:16]}:items={len(fec.evidence_items)}",
        "M0": f"provider_profile={APPS_LIC_PROVIDER_PROFILE}:model={APPS_LIC_TARGET_MODEL}",
        "U0": f"validated_request:{validated_request.request_id}",
        "H0": f"PA-authored:linkedin_{recipient_class.lower()}_style_constraints",
        "R0": f"PA-authored:linkedin_{recipient_class.lower()}_json_output_contract",
        "user_block_2": (
            f"C0_EVIDENCE_DATA_ONLY:fec={fec.compilation_hash[:16]}"
            f":items={len(fec.evidence_items)}"
        ),
        "evidence": f"C0:fec.compilation_hash={fec.compilation_hash[:16]}",
    }

    # ── component_hash_map ───────────────────────────────────────────────────
    component_hash_map: dict[str, str] = {
        "evidence": fec.compilation_hash,
        "l1_plan": _component_hash({
            "task_spec": dict(l1_plan.task_spec),
            "query_spec": dict(l1_plan.query_spec),
            "support_expectation": dict(l1_plan.support_expectation),
            "output_expectation": dict(l1_plan.output_expectation),
            "policy_refs": dict(l1_plan.policy_refs),
        }),
        "app_payload_task_data": _component_hash({
            "replay_key": validated_request.replay_key,
            "run_id": validated_request.run_id,
        }),
        "route": _component_hash({
            "route_id": route.route_id,
            "route_family": route.route_family,
            "execution_form": route.execution_form,
            "cache_eligibility": dict(route.cache_eligibility),
            "action_required": route.action_required,
        }),
        "provider_profile": _component_hash({
            "provider_profile": APPS_LIC_PROVIDER_PROFILE,
            "target_provider": APPS_LIC_TARGET_PROVIDER,
            "target_model": APPS_LIC_TARGET_MODEL,
        }),
    }

    # ── compilation_hash (== prompt_hash) ────────────────────────────────────
    canonical = json.dumps(
        [{"role": b.role, "len": len(b.content), "idx": b.block_index} for b in blocks]
        + [{
            "model": APPS_LIC_TARGET_MODEL,
            "provider": APPS_LIC_TARGET_PROVIDER,
            "provider_profile": APPS_LIC_PROVIDER_PROFILE,
        }]
        + [{"slot_lineage_map": slot_lineage_map, "component_hash_map": component_hash_map}],
        sort_keys=True,
    )
    compilation_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # ── replay_manifest_ref ──────────────────────────────────────────────────
    replay_manifest_ref = (
        f"reflection:{validated_request.reflection_receipt.input_payload_digest[:16]}"
        if validated_request.reflection_receipt is not None
        else f"replay_key:{validated_request.replay_key}"
    )

    return CompiledPromptArtifact(
        request_id=route.request_id,
        run_id=route.run_id,
        app_id=route.app_id,
        trace_id=route.trace_id,
        tenant_id=fec.tenant_id,
        prompt_blocks=blocks,
        system_preamble=system_preamble,
        user_instruction=campaign_instruction + "\n\n" + evidence_data_block,
        assembly_timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="AG-8.W5.f3c2e1",
        target_model=APPS_LIC_TARGET_MODEL,
        target_provider=APPS_LIC_TARGET_PROVIDER,
        evidence_digest=fec.compilation_hash,
        compilation_hash=compilation_hash,
        slot_lineage_map=slot_lineage_map,
        component_hash_map=component_hash_map,
        replay_manifest_ref=replay_manifest_ref,
        sandbox_required=route.sandbox_required,
        egress_policy_ref=route.egress_policy_ref,
        allowed_tools=route.allowed_tools,
        allowed_models=route.allowed_models,
        allowed_networks=route.allowed_networks,
        allowed_file_roots=route.allowed_file_roots,
        max_tokens=4096,
        temperature=0.5,
        replay_key=validated_request.replay_key,
        l5_certification_ref=APPS_LIC_PA_CERT_REF,
    )


__all__ = [
    "APPS_LIC_PA_CERT_REF",
    "APPS_LIC_PROVIDER_PROFILE",
    "APPS_LIC_TARGET_MODEL",
    "APPS_LIC_TARGET_PROVIDER",
    "pa_compose_apps_lic",
]
