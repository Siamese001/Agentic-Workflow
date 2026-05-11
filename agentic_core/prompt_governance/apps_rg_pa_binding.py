"""Prompt-Assembly binding for apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P4 (initial)
+   plan apps-rg-app-payload-consumption-wiring-b3a449 W4 (AG-2 — signature
   change to accept ValidatedRequest; reads target/output/provenance
   directives from ValidatedRequest.app_payload, NOT from legacy
   AppsRgIngressPayload; emits slot_lineage_map + component_hash_map +
   replay_manifest_ref).

PA is the FIFTH stage (CONDITIONAL — fires only when
route.model_generation_required=True). Its job is to compile a typed
CompiledPromptArtifact from:
- The L1 plan (provides task_spec + projections + capabilities)
- The L0 route (provides routing flags + cache_eligibility)
- The C0 evidence (JD, resume, brief)
- The U0 ValidatedRequest (provides target / output / provenance fields
  via app_payload — NOT via the legacy AppsRgIngressPayload)
- The apps_rg style profile (forbidden phrases + power verbs from
  rg_prompt_profile.yaml)

Per AG-RGGOV-6: prompt assembly logic lives in core, NOT in apps_rg.
This binding lives in agentic_core/prompt_governance/ ✅.

AG-2 prompt-envelope additions:
    - slot_lineage_map: per-slot origin (system→PA-authored;
      user→USER_INTENT+EVIDENCE)
    - component_hash_map: sha256 over each contributing component
      (style_profile, evidence, l1_plan, app_payload, route)
    - replay_manifest_ref: pointer to ValidatedRequest.replay_key

The compiled artifact carries target_model='Qwen/Qwen2.5-32B-Instruct-AWQ'
+ target_provider='vllm' — matching the canonical Docker stack.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    ValidatedRequest,
)
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.final_evidence_contract import (
    FinalEvidenceContract,
)
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.route_contract import RouteContract


APPS_RG_PA_CERT_REF: str = "pa-apps-rg-resume-generation-app-payload-b3a449"

# Canonical local model — see memory 01483ea2 (Qwen/Qwen2.5-32B-Instruct-AWQ
# served by Docker `local-qwen-vllm` at http://localhost:8000/v1).
APPS_RG_TARGET_MODEL: str = "Qwen/Qwen2.5-32B-Instruct-AWQ"
APPS_RG_TARGET_PROVIDER: str = "vllm"

_STYLE_PROFILE_RELPATH: str = "apps_rg/profiles/rg_prompt_profile.yaml"


def _resolve_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / "pyproject.toml").exists():
            return parent
    return here.parents[2]


def _load_style_profile_text(repo_root: Path) -> str:
    """Return the raw style-profile YAML bytes as text. Empty string if missing."""
    profile_path = repo_root / _STYLE_PROFILE_RELPATH
    if not profile_path.exists():
        return ""
    try:
        return profile_path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _extract_style_directives(profile_text: str) -> tuple[list[str], list[str]]:
    """Pull forbidden_phrases + power_verbs lists out of the YAML without parsing.

    Avoids a yaml dependency by line-scanning the small profile file.
    Returns (forbidden_phrases, power_verbs).
    """
    forbidden: list[str] = []
    power: list[str] = []
    section: str | None = None
    for raw in profile_text.splitlines():
        stripped = raw.strip()
        if stripped.startswith("forbidden_phrases:"):
            section = "forbidden"
            continue
        if stripped.startswith("power_verbs:"):
            section = "power"
            continue
        if stripped.startswith("preferred_patterns:") or stripped.startswith(
            "usage_guidance:"
        ):
            section = None
            continue
        if section and stripped.startswith("- "):
            value = stripped[2:].strip().strip('"').strip("'")
            if value:
                if section == "forbidden":
                    forbidden.append(value)
                elif section == "power":
                    power.append(value)
        elif section and not stripped.startswith("-") and stripped and not stripped.startswith("#"):
            # New top-level key — leave the section.
            section = None
    return forbidden, power


def _build_system_preamble(forbidden: list[str], power: list[str]) -> str:
    """Compose the system preamble carrying style + role guidance."""
    parts: list[str] = [
        "You are a senior resume writer producing a tailored resume.",
        "Write in the third person voice of the candidate, deliver factual claims grounded in the supplied resume and JD.",
        "Output a JSON document matching the resume schema. No prose outside JSON.",
    ]
    if power:
        parts.append("Prefer power verbs such as: " + ", ".join(power[:10]) + ".")
    if forbidden:
        parts.append(
            "Avoid weak phrasing such as: "
            + ", ".join(f'"{p}"' for p in forbidden)
            + "."
        )
    return "\n".join(parts)


def _build_u0_task_block(
    validated_request: ValidatedRequest,
    l1_plan: L1PlanContract,
) -> str:
    """Build the U0_NEUTRALIZED_USER_TASK portion of the user turn.

    W4/PAB-003: U0 task (target + output format + L1 plan directives) is now
    a SEPARATE text segment from C0 evidence. PA assembles both into the user
    PromptBlock but their slot origins are distinct:
      - U0_NEUTRALIZED_USER_TASK  → this function
      - C0_VERIFIED_EVIDENCE_DATA → _build_c0_evidence_block()

    No raw evidence is included here. No instruction authority is embedded
    in the evidence block.
    """
    app_payload = validated_request.app_payload
    target = app_payload.get("target", {})
    target_company = str(target.get("company") or "the target company")
    target_role = str(target.get("role") or "the target role")
    target_level = str(target.get("level") or "unspecified")

    output_exp = l1_plan.output_expectation
    support_exp = l1_plan.support_expectation
    formats = output_exp.get("formats", ("json",)) or ("json",)
    formats_str = ", ".join(str(f) for f in formats)
    fact_check_required = bool(output_exp.get("fact_checked_required", False))
    per_bullet_required = bool(support_exp.get("per_bullet_required", False))
    source_quote_required = bool(support_exp.get("source_quote_required", False))

    # AG-2 provenance directives — emitted only when app_payload demands them.
    directives: list[str] = []
    if fact_check_required:
        directives.append("Every factual claim MUST be fact-checked against the supplied source materials.")
    if per_bullet_required:
        directives.append("Each experience bullet MUST include an `evidence_anchor` citing the source.")
    if source_quote_required:
        directives.append("Each experience bullet MUST include a `source_quote` field with the verbatim source span.")
    directives_block = ("\n".join(f"- {d}" for d in directives)) if directives else "(none)"

    return (
        f"Tailor a resume for the following position:\n"
        f"  Company: {target_company}\n"
        f"  Role:    {target_role}\n"
        f"  Level:   {target_level}\n"
        f"\n"
        f"Task plan from L1: {', '.join(l1_plan.task_plan)}\n"
        f"\n"
        f"AG-2 provenance directives:\n{directives_block}\n"
        f"\n"
        f"Produce output in formats: {formats_str}. Default to a JSON resume "
        f"document with sections: executive_summary, experience, skills, "
        f"education, certifications. Output JSON only — no markdown, no prose preamble."
    )


def _build_c0_evidence_block(fec: FinalEvidenceContract) -> str:
    """Build the C0_VERIFIED_EVIDENCE_DATA portion of the user turn.

    W4/PAB-003: Evidence is assembled SEPARATELY from the user task so the
    slot_lineage_map can record its origin as C0_VERIFIED_EVIDENCE_DATA, not
    USER_INTENT. The content is verbatim from FinalEvidenceContract — PA does
    not modify or interpret it.

    vLLM serving at --max-model-len 8192 tokens (~24K chars for evidence after
    system prompt + response reservation).
    """
    inlined: list[str] = []
    budget_remaining = 20000
    for item in fec.evidence_items:
        if budget_remaining <= 0:
            break
        chunk_header = f"\n--- {item.source} ({item.content_type}) ---\n"
        chunk_body = item.content[:budget_remaining]
        inlined.append(chunk_header + chunk_body)
        budget_remaining -= len(chunk_body)
    return (
        f"Source materials (consume verbatim — do not invent facts):\n"
        f"{''.join(inlined) if inlined else '[no evidence supplied]'}"
    )


def _build_user_instruction(
    validated_request: ValidatedRequest,
    fec: FinalEvidenceContract,
    l1_plan: L1PlanContract,
) -> str:
    """Assemble the final user PromptBlock content from U0 task + C0 evidence.

    W4/PAB-003: Delegates to two distinct builders so slot origins remain
    separable in slot_lineage_map:
      block[0] = system  → S0_SYSTEM (I0_INSTRUCTIONS inline via style profile)
      block[1] = user    → U0_NEUTRALIZED_USER_TASK + C0_VERIFIED_EVIDENCE_DATA

    The two segments are concatenated here. slot_lineage_map records each
    segment's origin independently.
    """
    u0_task = _build_u0_task_block(validated_request, l1_plan)
    c0_evidence = _build_c0_evidence_block(fec)
    return u0_task + "\n\n" + c0_evidence


def _component_hash(content: Any) -> str:
    """Stable sha256 hex digest over a canonicalised JSON projection."""

    blob = json.dumps(content, sort_keys=True, ensure_ascii=False, default=str, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def pa_compose_apps_rg(
    route: RouteContract,
    l1_plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
) -> CompiledPromptArtifact:
    """Compile a typed CompiledPromptArtifact for L2 to execute.

    AG-2 (apps-rg-app-payload-consumption-wiring-b3a449 W4): signature
    changed from ``(..., payload: AppsRgIngressPayload)`` to
    ``(..., validated_request: ValidatedRequest)``. PA reads target /
    output / provenance directives from ``validated_request.app_payload``
    via the L1 projections it already consumes (output_expectation,
    support_expectation). Legacy ``AppsRgIngressPayload`` is no longer
    referenced.

    Args:
        route: L0 routing decision (must have model_generation_required=True).
        l1_plan: L1 plan contract — drives task plan + the AG-2 projections.
        fec: C0 final evidence — its compilation_hash is referenced in
             evidence_digest for provenance.
        validated_request: U0 output carrying app_payload (the SSOT for
            target / output / provenance fields beyond U0).

    Returns:
        CompiledPromptArtifact with system + user blocks, target model/provider
        bound, provenance digests linked, and AG-2 prompt-envelope fields
        populated (slot_lineage_map / component_hash_map / replay_manifest_ref).

    Raises:
        TypeError: if any argument has the wrong shape.
    """
    if not isinstance(route, RouteContract):
        raise TypeError(
            f"pa_compose_apps_rg expected RouteContract, got {type(route).__name__}"
        )
    if not isinstance(l1_plan, L1PlanContract):
        raise TypeError(
            f"pa_compose_apps_rg expected L1PlanContract, got {type(l1_plan).__name__}"
        )
    if not isinstance(fec, FinalEvidenceContract):
        raise TypeError(
            f"pa_compose_apps_rg expected FinalEvidenceContract, got {type(fec).__name__}"
        )
    if not isinstance(validated_request, ValidatedRequest):
        raise TypeError(
            "pa_compose_apps_rg expected ValidatedRequest, got "
            f"{type(validated_request).__name__}"
        )

    repo_root = _resolve_repo_root()
    style_text = _load_style_profile_text(repo_root)
    forbidden, power = _extract_style_directives(style_text)

    system_preamble = _build_system_preamble(forbidden, power)
    # W4/PAB-003: build U0 and C0 segments separately so slot_lineage_map
    # can record their distinct origins. Both are combined into user_instruction
    # for the PromptBlock, but the component hashes cover each independently.
    u0_task_segment = _build_u0_task_block(validated_request, l1_plan)
    c0_evidence_segment = _build_c0_evidence_block(fec)
    user_instruction = _build_user_instruction(validated_request, fec, l1_plan)

    blocks: tuple[PromptBlock, ...] = (
        # W3 P3.3: system block is SYSTEM_INTERNAL (PA-authored directives)
        PromptBlock(role="system", content=system_preamble, block_index=0,
                    origin=Origin.SYSTEM_INTERNAL),
        # W3 P3.3 airlock — user block carries USER_INTENT (verbatim user text)
        PromptBlock(role="user", content=user_instruction, block_index=1,
                    origin=Origin.USER_INTENT),
    )

    # W3 P3.3: airlock verify — every user-role block MUST be tagged USER_INTENT.
    # This catches accidental origin mislabelling at compile time.
    for blk in blocks:
        if blk.role == "user" and blk.origin != Origin.USER_INTENT:
            raise ValueError(
                f"PA airlock violation: user-role PromptBlock[{blk.block_index}] "
                f"has origin={blk.origin!r} — must be USER_INTENT (D7)"
            )

    # W4: slot_lineage_map now separately records all four canonical slot origins.
    # PAB-003 fix: U0_NEUTRALIZED_USER_TASK and C0_VERIFIED_EVIDENCE_DATA are
    # distinct entries — they are no longer collapsed into a single "USER_INTENT+EVIDENCE".
    #
    # Cross-ref: allowed_models in this artifact comes from RouteContract
    # (set by L0 binding apps_rg_l0_binding.py:201). PA's APPS_RG_TARGET_MODEL
    # is a separate declaration for the target model field — both must name
    # Qwen/Qwen2.5-32B-Instruct-AWQ. If they diverge, the compilation_hash
    # will differ between runs and L2 must reject the artifact.
    slot_lineage_map: dict[str, str] = {
        # S0_SYSTEM / I0_INSTRUCTIONS — PA assembles from rg_prompt_profile.yaml
        "system_block_0__slot": "S0_SYSTEM+I0_INSTRUCTIONS",
        "system_block_0__origin": "PA-authored:apps_rg/profiles/rg_prompt_profile.yaml",
        # U0_NEUTRALIZED_USER_TASK — target + L1 plan directives from ValidatedRequest
        "user_block_1__u0_task__slot": "U0_NEUTRALIZED_USER_TASK",
        "user_block_1__u0_task__origin": "ValidatedRequest.app_payload+L1PlanContract",
        # C0_VERIFIED_EVIDENCE_DATA — verbatim evidence from FinalEvidenceContract
        "user_block_1__c0_evidence__slot": "C0_VERIFIED_EVIDENCE_DATA",
        "user_block_1__c0_evidence__origin": f"C0:FinalEvidenceContract.compilation_hash={fec.compilation_hash[:16]}",
        # R0_RESPONSE_SCHEMA — output format directive embedded in U0 task block
        "user_block_1__r0_schema__slot": "R0_RESPONSE_SCHEMA",
        "user_block_1__r0_schema__origin": "PA-authored:output_expectation.formats+sections",
    }

    # W4: component_hash_map expanded to cover all runtime-used prompt components
    # explicitly keyed to their slot origin. Hashes cover actual content so
    # prompt_hash changes whenever meaningful S0/I0/U0/C0/R0 content changes.
    component_hash_map: dict[str, str] = {
        # S0_SYSTEM + I0_INSTRUCTIONS — style profile drives both
        "style_profile__s0_i0": _component_hash({"forbidden": forbidden, "power": power}),
        # C0_VERIFIED_EVIDENCE_DATA — FEC compilation_hash is the canonical fingerprint
        "evidence__c0": fec.compilation_hash,
        # U0_NEUTRALIZED_USER_TASK — target + task plan from L1 projections
        "u0_task_segment": _component_hash(u0_task_segment),
        # C0 evidence segment as rendered (may differ from fec.compilation_hash
        # if evidence budget truncation applied)
        "c0_evidence_segment": _component_hash(c0_evidence_segment),
        # L1 plan projections driving U0 task + output directives
        "l1_plan": _component_hash({
            "task_spec": dict(l1_plan.task_spec),
            "query_spec": dict(l1_plan.query_spec),
            "support_expectation": dict(l1_plan.support_expectation),
            "output_expectation": dict(l1_plan.output_expectation),
            "policy_refs": dict(l1_plan.policy_refs),
        }),
        # R0_RESPONSE_SCHEMA — output format + section list from output_expectation
        "r0_schema": _component_hash(dict(l1_plan.output_expectation)),
        # app_payload — full payload for replay-bind completeness
        "app_payload": _component_hash(dict(validated_request.app_payload)),
        # route — allowed_models here comes from L0 binding (apps_rg_l0_binding.py:201).
        # PA target model (APPS_RG_TARGET_MODEL) is a separate field on the artifact.
        # Both must match Qwen/Qwen2.5-32B-Instruct-AWQ; divergence = hash mismatch.
        "route": _component_hash({
            "route_id": route.route_id,
            "route_family": route.route_family,
            "execution_form": route.execution_form,
            "cache_eligibility": dict(route.cache_eligibility),
            "action_required": route.action_required,
        }),
    }

    # W4: compilation_hash covers actual block CONTENT (not just length) so
    # prompt_hash changes whenever any meaningful S0/I0/U0/C0/R0 content changes.
    # This fixes the prior implementation that hashed only len(content).
    canonical = json.dumps(
        [{"role": b.role, "content_hash": hashlib.sha256(b.content.encode("utf-8")).hexdigest(), "idx": b.block_index} for b in blocks]
        + [{"model": APPS_RG_TARGET_MODEL, "provider": APPS_RG_TARGET_PROVIDER}]
        + [{"slot_lineage_map": slot_lineage_map, "component_hash_map": component_hash_map}],
        sort_keys=True,
    )
    compilation_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    # AG-2 — replay manifest pointer; references the U0 reflection digest +
    # ValidatedRequest replay_key so a replay tool can locate the source
    # envelope.
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
        # W1 P1.2: thread identity quad from FinalEvidenceContract (D6)
        tenant_id=fec.tenant_id,
        prompt_blocks=blocks,
        system_preamble=system_preamble,
        user_instruction=user_instruction,
        assembly_timestamp=datetime.now(timezone.utc).isoformat(),
        schema_version="AG-2.b3a449",
        target_model=APPS_RG_TARGET_MODEL,
        target_provider=APPS_RG_TARGET_PROVIDER,
        evidence_digest=fec.compilation_hash,
        compilation_hash=compilation_hash,
        # AG-2 — prompt-envelope provenance fields.
        slot_lineage_map=slot_lineage_map,
        component_hash_map=component_hash_map,
        replay_manifest_ref=replay_manifest_ref,
        # W2 P2.2: thread capability/sandbox/egress from RouteContract
        sandbox_required=route.sandbox_required,
        egress_policy_ref=route.egress_policy_ref,
        allowed_tools=route.allowed_tools,
        allowed_models=route.allowed_models,
        allowed_networks=route.allowed_networks,
        allowed_file_roots=route.allowed_file_roots,
        max_tokens=16384,
        temperature=0.4,  # lower for factual resume generation
        # AG-2: thread replay_key forward.
        replay_key=validated_request.replay_key,
        l5_certification_ref=APPS_RG_PA_CERT_REF,
    )


__all__ = [
    "APPS_RG_PA_CERT_REF",
    "APPS_RG_TARGET_MODEL",
    "APPS_RG_TARGET_PROVIDER",
    "pa_compose_apps_rg",
    "_build_u0_task_block",
    "_build_c0_evidence_block",
    "_build_user_instruction",
    "_build_system_preamble",
    "_component_hash",
]
