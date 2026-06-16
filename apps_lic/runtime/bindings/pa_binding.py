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
from typing import Any, Mapping

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
from apps_lic.engines.recipient_classification import (
    CLASS_UNKNOWN,
    STATUS_DERIVED as RECIPIENT_CLASS_DERIVED,
)
from apps_lic.config.model_profiles import (
    resolve_generator_model,
    resolve_generator_provider,
    resolve_generator_provider_profile,
)
from apps_lic.runtime.bindings.c0_binding import (
    c0_recipient_class_status_from_fec,
    c0_recipient_class_value_from_fec,
)
from apps_lic.runtime.bindings.pa_schema_receipts import (
    PromptSchemaReceipt,
    build_prompt_schema_receipt,
    output_contract_guidance,
)
from apps_lic.types.recipient_archetype_mapping import (
    RecipientArchetypePromptProfile,
    build_archetype_prompt_lines,
    map_lic_recipient_class_to_archetype,
    recipient_archetype_profile,
    resolve_recipient_template_policy,
)


APPS_LIC_PA_CERT_REF: str = "pa-apps-lic-outreach-message-ag8-w5-f3c2e1"

APPS_LIC_TARGET_MODEL: str = resolve_generator_model()
APPS_LIC_TARGET_PROVIDER: str = resolve_generator_provider()
APPS_LIC_PROVIDER_PROFILE: str = resolve_generator_provider_profile()

# PA enforces this budget to stay within the --max-model-len 8192 token window.
_EVIDENCE_CHAR_BUDGET: int = 16_000


def _recipient_class_from_fec(fec: FinalEvidenceContract) -> str:
    status = c0_recipient_class_status_from_fec(fec)
    raw = c0_recipient_class_value_from_fec(fec).strip().upper()
    allowed = {
        "CEO",
        "RECRUITER",
        "SENIOR_TA",
        "HIRING_MANAGER",
        "EXECUTIVE",
        "C_LEVEL",
        "VP_ENG",
        "CTO",
        "REFERRAL_CONTACT",
    }
    if status != RECIPIENT_CLASS_DERIVED or raw == CLASS_UNKNOWN or raw not in allowed:
        raise ValueError(
            "pa_compose_apps_lic: C0-derived recipient class is required before PA; "
            f"status={status!r} value={raw!r}"
        )
    return raw


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


def _build_system_preamble(
    l1_plan: L1PlanContract,
    *,
    recipient_class: str,
    sender_proof_envelope: Mapping[str, Any] | None = None,
    length_budget: Mapping[str, Any] | None = None,
    archetype_profile: RecipientArchetypePromptProfile | None = None,
    prompt_schema_receipt: PromptSchemaReceipt | None = None,
) -> str:
    """Compose the system preamble carrying role + governance directives."""
    output_exp = l1_plan.output_expectation
    support_exp = l1_plan.support_expectation
    task_spec = l1_plan.task_spec
    recipient_label = recipient_class.lower()

    channel = str(output_exp.get("channel", "linkedin") or "linkedin")
    output_format = output_exp.get("output_format") or {}
    include_subject_line = bool(
        channel == "linkedin_inmail"
        or (
            isinstance(output_format, Mapping)
            and output_format.get("include_subject_line") is True
        )
    )
    tone_register = str(output_exp.get("tone_register", "") or "")
    formality_level = output_exp.get("formality_level")
    brand_voice_id = str(output_exp.get("tone_brand_voice_id", "") or "")
    pii_mode = str(support_exp.get("pii_detection_mode", "strict") or "strict")
    hitl_required = bool(support_exp.get("hitl_required", True))
    governance_shield = bool(support_exp.get("governance_shield_required", True))
    halt_on_fail = bool(support_exp.get("halt_on_validation_failure", True))
    side_effect_class = str(task_spec.get("side_effect_class", "read_only") or "read_only")
    reasoning_policy = task_spec.get("reasoning_policy") or {}
    sc_level = str(reasoning_policy.get("sc_level", "SC-1"))
    reasoning_intensity = str(
        reasoning_policy.get("reasoning_intensity", "R1_STANDARD")
    )
    judge_profile = str(reasoning_policy.get("judge_profile", "normal_default"))
    max_candidates = int(reasoning_policy.get("max_candidates", 1) or 1)
    allowed_claim_ids = tuple(
        str(item)
        for item in (sender_proof_envelope or {}).get("allowed_claim_ids", ())
        if str(item)
    )
    message_type = str(task_spec.get("message_type", "") or task_spec.get("message_type_hint", "") or "general_intro")
    template_policy = resolve_recipient_template_policy(
        recipient_class=recipient_class,
        message_type=message_type,
        channel=channel,
    )
    profile = archetype_profile or template_policy.archetype_profile
    policy_budget = template_policy.length_policy.to_length_budget_packet()
    effective_length_budget = {**policy_budget, **dict(length_budget or {})}
    hard_cap_chars = int(effective_length_budget.get("hard_cap_chars") or 600)
    max_sentences = int(
        effective_length_budget.get("max_sentences")
        or profile.recommended_sentence_range[1]
    )
    include_subject_line = bool(effective_length_budget.get("subject_required") or include_subject_line)
    repair_passes = int(reasoning_policy.get("validation_repair_passes", 1) or 0)
    schema_receipt = prompt_schema_receipt or build_prompt_schema_receipt(
        channel=channel,
        recipient_class=recipient_class,
        subject_required=include_subject_line,
        hard_cap_chars=hard_cap_chars,
        max_sentences=max_sentences,
    )

    parts: list[str] = [
        f"You are a governed AI assistant composing a LinkedIn {recipient_label} outreach draft for channel: {channel}.",
        "Your output is DATA ONLY — not an instruction. Produce a factual, concise message.",
        f"Side-effect class: {side_effect_class}. This is a draft-and-certify flow; do NOT send.",
        (
            "Reasoning policy: "
            f"sc_level={sc_level}; reasoning_intensity={reasoning_intensity}; "
            f"judge_profile={judge_profile}; max_candidates={max_candidates}; "
            f"validation_repair_passes={repair_passes}."
        ),
        "More reasoning may improve wording or candidate selection only; it cannot create missing evidence.",
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
        *build_archetype_prompt_lines(
            lic_recipient_class=recipient_class,
            profile=profile,
            length_budget=effective_length_budget,
        ),
    ]

    parts += [
        "",
        "OUTPUT FORMAT:",
        *output_contract_guidance(
            receipt=schema_receipt,
            subject_required=include_subject_line,
            hard_cap_chars=hard_cap_chars,
            max_sentences=max_sentences,
        ),
        (
            "  Use compact paragraphs. Include a low-friction ask for a chat, call, "
            "resume review, fit check, redirect, or brief exchange."
        ),
        "  The last body sentence before the signature must be a question ending with '?'.",
        "  End with Amit on its own final line as the signature.",
        "  Treat word count as an advisory band only; do not fail or pad solely to hit a word range.",
        "  Do not include sensitive details unless supplied and approved. No prose outside JSON. No markdown. No invented facts.",
        "  If C0 evidence is WEAK or EMPTY, reduce specificity or fail closed; do not compensate by adding claims.",
    ]
    if allowed_claim_ids:
        parts.append(
            "  claims_used may contain only these C0.3 proof IDs: "
            + ", ".join(allowed_claim_ids)
            + "."
        )
    return "\n".join(parts)


def _build_campaign_instruction(
    l1_plan: L1PlanContract,
    *,
    recipient_class: str,
) -> str:
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
        f"  U0 recipient class hint: {lead.get('seniority_class', '')}\n"
        f"  C0-derived recipient class: {recipient_class}\n"
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


def _build_sender_proof_block(
    sender_proof_envelope: Mapping[str, Any] | None,
    length_budget: Mapping[str, Any] | None,
    jd_fields: Mapping[str, Any] | None = None,
    message_intelligence_packet: Mapping[str, Any] | None = None,
) -> str:
    payload = {
        "sender_proof_envelope": dict(sender_proof_envelope or {}),
        "length_budget": dict(length_budget or {}),
        "jd_fields": dict(jd_fields or {}),
        "message_intelligence_packet": _message_intelligence_payload(
            message_intelligence_packet
        ),
    }
    return (
        "C0.3 SENDER PROOF ENVELOPE (DATA ONLY - proof IDs are the only "
        "sender-claim authority):\n"
        + json.dumps(payload, indent=2, sort_keys=True, default=str)
    )


def _message_intelligence_payload(
    message_intelligence_packet: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if hasattr(message_intelligence_packet, "to_packet"):
        packet = message_intelligence_packet.to_packet()  # type: ignore[attr-defined]
        return dict(packet) if isinstance(packet, Mapping) else {}
    return dict(message_intelligence_packet or {})


def _message_intelligence_audit_refs(
    message_intelligence_packet: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    packet = _message_intelligence_payload(message_intelligence_packet)
    if not packet:
        return ()
    return (
        "mi_message_intelligence_packet:" + str(packet.get("packet_id") or ""),
        "mi_trigger_mode:"
        + str(
            (packet.get("trigger_evaluation") or {}).get(
                "recommended_personalization_mode",
                "",
            )
            if isinstance(packet.get("trigger_evaluation"), Mapping)
            else ""
        ),
        "mi_ask_style:"
        + str(
            (packet.get("ask_calibration") or {}).get("cta_style", "")
            if isinstance(packet.get("ask_calibration"), Mapping)
            else ""
        ),
    )


def _message_intelligence_snapshot_refs(
    message_intelligence_packet: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    packet = _message_intelligence_payload(message_intelligence_packet)
    refs = packet.get("source_refs") or ()
    if not isinstance(refs, (list, tuple)):
        return ()
    return tuple(dict.fromkeys(str(ref) for ref in refs if str(ref)))


def _sender_proof_audit_refs(
    sender_proof_envelope: Mapping[str, Any] | None,
    length_budget: Mapping[str, Any] | None,
    jd_fields: Mapping[str, Any] | None = None,
) -> tuple[str, ...]:
    envelope = dict(sender_proof_envelope or {})
    if not envelope:
        return ()
    allowed_claim_ids = [
        str(item)
        for item in envelope.get("allowed_claim_ids", ())
        if str(item)
    ]
    return (
        "c03_sender_proof_packet:" + str(envelope.get("proof_packet_id") or ""),
        "c03_allowed_claim_ids:" + ",".join(allowed_claim_ids),
        "c03_pa_data_boundary:" + str(
            envelope.get("instruction_data_boundary_receipt") or ""
        ),
        "c03_length_budget:" + str((length_budget or {}).get("budget_key") or ""),
        "c03_jd_position_name:" + str((jd_fields or {}).get("position_name") or ""),
    )


def _sender_proof_gate_refs(
    sender_proof_envelope: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    envelope = dict(sender_proof_envelope or {})
    if not envelope:
        return ()
    return (
        "c03_sender_proof_packet:" + str(envelope.get("proof_packet_id") or ""),
        "c03_sender_proof_claim_ids:"
        + ",".join(str(item) for item in envelope.get("allowed_claim_ids", ())),
    )


def _sender_proof_snapshot_refs(
    sender_proof_envelope: Mapping[str, Any] | None,
) -> tuple[str, ...]:
    envelope = dict(sender_proof_envelope or {})
    lineage = envelope.get("source_lineage") or {}
    refs: list[str] = []
    if isinstance(lineage, Mapping):
        for values in lineage.values():
            if isinstance(values, (list, tuple)):
                refs.extend(str(value) for value in values if str(value))
            elif str(values):
                refs.append(str(values))
    return tuple(dict.fromkeys(refs))


def _jd_fields_from_l1_plan(l1_plan: L1PlanContract) -> dict[str, str]:
    query_spec = getattr(l1_plan, "query_spec", {}) or {}
    if not isinstance(query_spec, Mapping):
        return {}
    personalization = query_spec.get("personalization_inputs") or {}
    if not isinstance(personalization, Mapping):
        return {}
    facts = personalization.get("governed_opportunity_facts") or ()
    fields: dict[str, str] = {}
    iterable_facts = facts if isinstance(facts, (list, tuple)) else ()
    for fact in iterable_facts:
        if not isinstance(fact, Mapping):
            continue
        metadata = fact.get("metadata") or {}
        if not isinstance(metadata, Mapping):
            continue
        for key in ("company", "position_name", "job_title", "requisition_number"):
            value = str(metadata.get(key) or "").strip()
            if value:
                fields.setdefault(key, value)
    return fields


def pa_compose_apps_lic(
    route: RouteContract,
    l1_plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
    *,
    sender_proof_envelope: Mapping[str, Any] | None = None,
    length_budget: Mapping[str, Any] | None = None,
    message_intelligence_packet: Mapping[str, Any] | None = None,
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

    recipient_class = _recipient_class_from_fec(fec)
    recipient_archetype = map_lic_recipient_class_to_archetype(recipient_class)
    channel = str(l1_plan.output_expectation.get("channel", "") or l1_plan.task_spec.get("channel", "linkedin"))
    message_type = str(l1_plan.task_spec.get("message_type", "") or l1_plan.task_spec.get("message_type_hint", "") or "general_intro")
    template_policy = resolve_recipient_template_policy(
        recipient_class=recipient_class,
        message_type=message_type,
        channel=channel,
    )
    archetype_profile = recipient_archetype_profile(recipient_archetype)
    effective_length_budget = {
        **template_policy.length_policy.to_length_budget_packet(),
        **dict(length_budget or {}),
    }
    output_format = l1_plan.output_expectation.get("output_format") or {}
    include_subject_line = bool(
        effective_length_budget.get("subject_required")
        or channel == "linkedin_inmail"
        or (
            isinstance(output_format, Mapping)
            and output_format.get("include_subject_line") is True
        )
    )
    hard_cap_chars = int(effective_length_budget.get("hard_cap_chars") or 600)
    max_sentences = int(
        effective_length_budget.get("max_sentences")
        or archetype_profile.recommended_sentence_range[1]
    )
    prompt_schema_receipt = build_prompt_schema_receipt(
        channel=channel,
        recipient_class=recipient_class,
        subject_required=include_subject_line,
        hard_cap_chars=hard_cap_chars,
        max_sentences=max_sentences,
    )
    jd_fields = _jd_fields_from_l1_plan(l1_plan)
    system_preamble = _build_system_preamble(
        l1_plan,
        recipient_class=recipient_class,
        sender_proof_envelope=sender_proof_envelope,
        length_budget=effective_length_budget,
        archetype_profile=archetype_profile,
        prompt_schema_receipt=prompt_schema_receipt,
    )
    campaign_instruction = _build_campaign_instruction(
        l1_plan,
        recipient_class=recipient_class,
    )
    evidence_data_block = (
        _build_evidence_block(fec)
        + "\n\n"
        + _build_sender_proof_block(
            sender_proof_envelope,
            effective_length_budget,
            jd_fields,
            message_intelligence_packet,
        )
    )

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
    reasoning_policy = l1_plan.task_spec.get("reasoning_policy") or {}
    slot_lineage_map: dict[str, str] = {
        "S0": "PA-authored:system_governance",
        "D0": "PA-authored:origin_and_injection_boundary",
        "I0": f"USER_INTENT:query_spec+task_plan:l1_plan={l1_plan.schema_version}",
        "E0": "PA-authored:approved_examples_empty",
        "C0": f"C0_EVIDENCE_DATA_ONLY:fec={fec.compilation_hash[:16]}:items={len(fec.evidence_items)}",
        "C03": (
            "C0_3_PROOF_GRAPH:"
            + str((sender_proof_envelope or {}).get("proof_packet_id") or "")
        ),
        "MI0": (
            "C0_3_MESSAGE_INTELLIGENCE:"
            + str(_message_intelligence_payload(message_intelligence_packet).get("packet_id") or "")
        ),
        "M0": f"provider_profile={APPS_LIC_PROVIDER_PROFILE}:model={APPS_LIC_TARGET_MODEL}",
        "SC": (
            f"sc_level={reasoning_policy.get('sc_level', 'SC-1')}:"
            f"max_candidates={reasoning_policy.get('max_candidates', 1)}"
        ),
        "RI": (
            "reasoning_intensity="
            f"{reasoning_policy.get('reasoning_intensity', 'R1_STANDARD')}:"
            f"judge_profile={reasoning_policy.get('judge_profile', 'normal_default')}"
        ),
        "U0": f"validated_request:{validated_request.request_id}",
        "A0": (
            "PA-authored:recipient_archetype="
            f"{recipient_archetype}:template={archetype_profile.template_id}"
        ),
        "H0": f"PA-authored:linkedin_{recipient_archetype.lower()}_style_constraints",
        "R0": (
            "PA-authored:output_contract="
            f"{prompt_schema_receipt.output_contract_name}"
            f":output_schema_hash={prompt_schema_receipt.output_schema_hash[:16]}"
            f":mapped_archetype={recipient_archetype}"
        ),
        "slot_registry": (
            f"slot_registry_ref={prompt_schema_receipt.slot_registry_ref}:"
            f"slot_registry_hash={prompt_schema_receipt.slot_registry_hash[:16]}"
        ),
        "template_policy": (
            f"recipient_policy_profile_id={archetype_profile.template_id}:"
            f"template_policy_hash={_component_hash(template_policy.to_hash_payload())[:16]}"
        ),
        "output_schema": (
            f"output_contract={prompt_schema_receipt.output_contract_name}:"
            f"output_schema_hash={prompt_schema_receipt.output_schema_hash[:16]}"
        ),
        "user_block_2": (
            f"C0_EVIDENCE_DATA_ONLY:fec={fec.compilation_hash[:16]}"
            f":items={len(fec.evidence_items)}"
        ),
        "evidence": f"C0:fec.compilation_hash={fec.compilation_hash[:16]}",
        "sender_proof": (
            "C0_3_PROOF_GRAPH:allowed_claim_ids="
            + ",".join(
                str(item)
                for item in (sender_proof_envelope or {}).get("allowed_claim_ids", ())
            )
        ),
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
        "reasoning_policy": _component_hash(reasoning_policy),
        "c03_sender_proof_envelope": _component_hash(dict(sender_proof_envelope or {})),
        "c03_length_budget": _component_hash(dict(effective_length_budget)),
        "message_intelligence_packet": _component_hash(
            _message_intelligence_payload(message_intelligence_packet)
        ),
        "recipient_archetype": _component_hash({
            "lic_recipient_class": recipient_class,
            "mapped_archetype": recipient_archetype,
            "profile": archetype_profile.to_hash_payload(),
            "template_policy": template_policy.to_hash_payload(),
        }),
        "recipient_policy_profile": _component_hash(archetype_profile.to_hash_payload()),
        "template_policy": _component_hash(template_policy.to_hash_payload()),
        "slot_registry_hash": prompt_schema_receipt.slot_registry_hash,
        "prompt_registry_hash": prompt_schema_receipt.prompt_registry_hash,
        "prompt_bom_hash": prompt_schema_receipt.prompt_bom_hash,
        "output_schema_hash": prompt_schema_receipt.output_schema_hash,
        "prompt_schema_receipt": _component_hash(prompt_schema_receipt.to_hash_payload()),
    }

    # ── compilation_hash (== prompt_hash) ────────────────────────────────────
    canonical = json.dumps(
        [{"role": b.role, "len": len(b.content), "idx": b.block_index} for b in blocks]
        + [{
            "model": APPS_LIC_TARGET_MODEL,
            "provider": APPS_LIC_TARGET_PROVIDER,
            "provider_profile": APPS_LIC_PROVIDER_PROFILE,
            "reasoning_policy": reasoning_policy,
            "prompt_schema_receipt": prompt_schema_receipt.to_hash_payload(),
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
        temperature=0.82,
        replay_key=validated_request.replay_key,
        audit_refs=tuple(
            dict.fromkeys(
                (
                    *_sender_proof_audit_refs(
                        sender_proof_envelope,
                        effective_length_budget,
                        jd_fields,
                    ),
                    *_message_intelligence_audit_refs(message_intelligence_packet),
                )
            )
        ),
        gate_verdict_refs=_sender_proof_gate_refs(sender_proof_envelope),
        snapshot_refs=tuple(
            dict.fromkeys(
                (
                    *_sender_proof_snapshot_refs(sender_proof_envelope),
                    *_message_intelligence_snapshot_refs(message_intelligence_packet),
                )
            )
        ),
        l5_certification_ref=APPS_LIC_PA_CERT_REF,
    )


__all__ = [
    "APPS_LIC_PA_CERT_REF",
    "APPS_LIC_PROVIDER_PROFILE",
    "APPS_LIC_TARGET_MODEL",
    "APPS_LIC_TARGET_PROVIDER",
    "pa_compose_apps_lic",
]
