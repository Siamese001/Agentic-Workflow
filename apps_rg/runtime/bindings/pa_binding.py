"""apps_rg PA binding — prompt assembly cert ref and section prompt helpers.

PA_BOUNDARY_CERT_S3 and related types used by tests verifying the PA
boundary contract for apps_rg section-level prompt assembly.

**W3:** ``governed_pa_l2_exit`` — composes ``CompiledPromptArtifact`` inputs consumed by the
package-driven L2 spine via ``apps_rg.runtime.bindings.l2_binding`` (child plan f8e3c1).
"""
from __future__ import annotations

from agentic_core.config.model_catalog import QWEN_LOCAL_MODEL_ID

from apps_rg.runtime.w3_execution_path_labels import (
    BUCKET_GOVERNED_PA_L2_EXIT,
    PLAN_SLUG,
    validate_bucket,
)

W3_EXECUTION_PATH_BUCKET = BUCKET_GOVERNED_PA_L2_EXIT
W3_EXECUTION_PATH_PLAN_SLUG = PLAN_SLUG
validate_bucket(W3_EXECUTION_PATH_BUCKET, context=__name__)

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
from typing import Any, Mapping, Optional

from agentic_core.runtime.contracts.apps_rg_ingress_payload import ValidatedRequest
from agentic_core.runtime.contracts.compiled_prompt_artifact import (
    CompiledPromptArtifact,
    PromptBlock,
)
from agentic_core.runtime.contracts.final_evidence_contract import FinalEvidenceContract
from agentic_core.runtime.contracts.l1_plan_contract import L1PlanContract
from agentic_core.runtime.contracts.origin import Origin
from agentic_core.runtime.contracts.route_contract import RouteContract

__all__ = [
    "PA_BOUNDARY_CERT_S3",
    "APPS_RG_PA_CERT_REF",
    "APPS_RG_TARGET_MODEL",
    "APPS_RG_TARGET_PROVIDER",
    "SectionPromptArtifact",
    "_build_bullet_rewrite_prompt",
    "_build_c0_evidence_block",
    "_build_system_preamble",
    "_build_u0_task_block",
    "_build_user_instruction",
    "_component_hash",
    "_load_pa_prompt_profile",
    "build_section_prompt_artifact",
    "build_section_prompt_artifact_for_bullet",
    "pa_compose_apps_rg",
    "pa_compose_apps_rg_section",
    "reset_pa_prompt_profile_cache",
]

PA_BOUNDARY_CERT_S3: str = "pa-s3-tiered-prompt-patching-apps-rg-resume-shipping"
APPS_RG_PA_CERT_REF: str = "pa-apps-rg-resume-generation-w3"
APPS_RG_TARGET_MODEL: str = QWEN_LOCAL_MODEL_ID
APPS_RG_TARGET_PROVIDER: str = "vllm_local"

_PA_PROFILE_CACHE: dict[str, Any] = {}
_PA_PROMPT_PROFILE_RELPATH: str = "apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json"
_pa_prompt_profile_cache: dict[str, Any] | None = None

_PROVIDER_MODEL_REGISTRY: dict[str, tuple[str, str]] = {
    "apps_rg::provider_model::resume_generation::v1": (APPS_RG_TARGET_MODEL, APPS_RG_TARGET_PROVIDER),
}


@dataclass
class SectionPromptArtifact:
    """Typed prompt artifact for a single resume section or bullet (S3 tiered PA)."""

    section_id: str
    treatment: str
    rewrite_allowed: bool
    preserve_verbatim: bool
    evidence_required: bool
    copy_only: bool
    source_span_required: bool
    jd_alignment_required: bool
    blocked_items_required: bool
    support_status_required: bool
    prompt_directive: str
    anti_invention_rules: list[str]
    role_id: str | None = None
    employer: str | None = None
    bullet_ordinal: int | None = None
    source_text: str | None = None
    jd_context_ref: str | None = None
    phrase_word_bounds: dict | None = None
    support_status_values: list[str] = field(
        default_factory=lambda: ["SUPPORTED", "INSUFFICIENT_SOURCE_SUPPORT", "BLOCKED"]
    )
    prompt_text: str = ""
    system_preamble: str = ""
    u0_task_block: str = ""
    evidence_slot: str = "c0_evidence_data_only"
    compilation_hash: str = ""
    profile_ref: str = ""


def reset_pa_prompt_profile_cache() -> None:
    """Clear cached PA profiles (test helper)."""
    _PA_PROFILE_CACHE.clear()
    global _pa_prompt_profile_cache
    _pa_prompt_profile_cache = None


def _load_pa_prompt_profile() -> dict[str, Any]:
    """Load S3 tiered PA prompt profile JSON (cached)."""
    global _pa_prompt_profile_cache
    if _pa_prompt_profile_cache is not None:
        return _pa_prompt_profile_cache
    apps_root = Path(__file__).resolve().parents[2]
    profile_path = apps_root / "config" / "domain_contract" / "resume_pa_prompt_profile.v1.json"
    if not profile_path.is_file():
        raise FileNotFoundError(
            f"PA prompt profile not found: {profile_path}. "
            "S3 requires apps_rg/config/domain_contract/resume_pa_prompt_profile.v1.json"
        )
    with open(profile_path, encoding="utf-8") as f:
        data = json.load(f)
    _pa_prompt_profile_cache = data
    return data


def _load_pa_yaml_profile(profile_path: Optional[str] = None) -> dict[str, Any]:
    """Load legacy rg_prompt_profile YAML for governed spine compose helpers."""
    key = profile_path or "default"
    if key in _PA_PROFILE_CACHE:
        return _PA_PROFILE_CACHE[key]
    try:
        import yaml

        path = Path(profile_path) if profile_path else (
            Path(__file__).resolve().parents[3] / "rg_prompt_profile.yaml"
        )
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    except Exception:  # guardian: allow-broad-exception -- P2 burndown: fail-soft optional boundary
        data = {}
    _PA_PROFILE_CACHE[key] = data
    return data


def _build_system_preamble(profile: dict[str, Any]) -> str:
    return str(profile.get("system_preamble", "You are a professional resume writer."))


def _build_u0_task_block(section_id: str, profile: dict[str, Any]) -> str:
    task = profile.get("task_block", "Generate the {section_id} section.")
    return task.format(section_id=section_id)


def _build_bullet_rewrite_prompt(
    section_id: str,
    bullet_text: str,
    profile: dict[str, Any],
) -> str:
    template = profile.get(
        "bullet_rewrite_template",
        "Rewrite the following bullet for {section_id}: {bullet_text}",
    )
    return template.format(section_id=section_id, bullet_text=bullet_text)


def build_section_prompt_artifact(
    section_id: str,
    *,
    role_id: str | None = None,
    employer: str | None = None,
    source_text: str | None = None,
    jd_context_ref: str | None = None,
) -> SectionPromptArtifact:
    """Build a tiered SectionPromptArtifact for a non-bullet section."""
    from apps_rg.runtime.schemas.section_treatment_profile import get_section_policy

    policy = get_section_policy(section_id)
    treatment = policy["treatment"]
    pa_profile = _load_pa_prompt_profile()
    treatment_instructions = pa_profile.get("treatment_instructions", {})
    instr_key = treatment if treatment != "TIERED_BY_ORDINAL" else "HEAVY"
    instr = treatment_instructions.get(instr_key, {})
    if treatment == "JD_RANKED_NOUN_PHRASES":
        instr = treatment_instructions.get("JD_RANKED_NOUN_PHRASES", instr)
    anti_invention_rules: list[str] = list(pa_profile.get("anti_invention_rules", []))
    output_schema: dict = pa_profile.get("output_artifact_schema", {})
    support_status_values: list[str] = list(
        output_schema.get(
            "support_status_values",
            ["SUPPORTED", "INSUFFICIENT_SOURCE_SUPPORT", "BLOCKED"],
        )
    )
    phrase_word_bounds: dict | None = None
    if treatment == "JD_RANKED_NOUN_PHRASES":
        phrase_word_bounds = {
            "min": policy.get("min_phrase_words", 2),
            "max": policy.get("max_phrase_words", 4),
        }
    elif instr.get("phrase_word_bounds"):
        phrase_word_bounds = dict(instr["phrase_word_bounds"])
    return SectionPromptArtifact(
        section_id=section_id,
        treatment=treatment,
        rewrite_allowed=bool(policy.get("rewrite_allowed", False)),
        preserve_verbatim=bool(policy.get("preserve_verbatim", False)),
        evidence_required=bool(policy.get("evidence_required", False)),
        copy_only=bool(instr.get("copy_only", policy.get("preserve_verbatim", False))),
        source_span_required=bool(instr.get("source_span_required", False)),
        jd_alignment_required=bool(instr.get("jd_alignment_required", False)),
        blocked_items_required=bool(instr.get("blocked_items_required", False)),
        support_status_required=bool(instr.get("support_status_required", False)),
        prompt_directive=str(instr.get("prompt_directive", "")),
        anti_invention_rules=anti_invention_rules,
        role_id=role_id,
        employer=employer,
        source_text=source_text,
        jd_context_ref=jd_context_ref,
        phrase_word_bounds=phrase_word_bounds,
        support_status_values=support_status_values,
    )


def build_section_prompt_artifact_for_bullet(
    section_id: str,
    ordinal: int,
    *,
    role_id: str | None = None,
    employer: str | None = None,
    source_text: str | None = None,
    jd_context_ref: str | None = None,
) -> SectionPromptArtifact:
    """Build a tiered SectionPromptArtifact for a bullet ordinal."""
    from apps_rg.runtime.schemas.section_treatment_profile import (
        get_bullet_treatment,
        get_section_policy,
    )

    resolved_treatment = get_bullet_treatment(section_id, ordinal)
    pa_profile = _load_pa_prompt_profile()
    treatment_instructions = pa_profile.get("treatment_instructions", {})
    instr = treatment_instructions.get(resolved_treatment, {})
    policy = get_section_policy(section_id)
    anti_invention_rules: list[str] = list(pa_profile.get("anti_invention_rules", []))
    output_schema: dict = pa_profile.get("output_artifact_schema", {})
    support_status_values: list[str] = list(
        output_schema.get(
            "support_status_values",
            ["SUPPORTED", "INSUFFICIENT_SOURCE_SUPPORT", "BLOCKED"],
        )
    )
    return SectionPromptArtifact(
        section_id=section_id,
        treatment=resolved_treatment,
        rewrite_allowed=bool(policy.get("rewrite_allowed", False)),
        preserve_verbatim=bool(policy.get("preserve_verbatim", False)),
        evidence_required=bool(policy.get("evidence_required", False)),
        copy_only=bool(instr.get("copy_only", False)),
        source_span_required=bool(instr.get("source_span_required", False)),
        jd_alignment_required=bool(instr.get("jd_alignment_required", False)),
        blocked_items_required=bool(instr.get("blocked_items_required", False)),
        support_status_required=bool(instr.get("support_status_required", False)),
        prompt_directive=str(instr.get("prompt_directive", "")),
        anti_invention_rules=anti_invention_rules,
        role_id=role_id,
        employer=employer,
        bullet_ordinal=ordinal,
        source_text=source_text,
        jd_context_ref=jd_context_ref,
        phrase_word_bounds=instr.get("phrase_word_bounds"),
        support_status_values=support_status_values,
    )


def _component_hash(*components: str) -> str:
    """Produce a short SHA-256 hash of joined component strings."""
    import hashlib
    payload = "\n".join(components)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:32]


def _build_c0_evidence_block(evidence_items: list[Any]) -> str:
    """Render C0 evidence items into a prompt-safe evidence block string."""
    if not evidence_items:
        return ""
    lines: list[str] = ["[C0 EVIDENCE]"]
    for item in evidence_items:
        content = getattr(item, "content", "") or str(item)
        source = getattr(item, "source_class", "unknown")
        lines.append(f"- [{source}] {content}")
    return "\n".join(lines)


def _build_user_instruction(
    section_id: str,
    target_company: str = "",
    target_role: str = "",
    generation_mode: str = "strategic_tailor",
    profile: Optional[dict[str, Any]] = None,
) -> str:
    """Build the user-turn instruction block for a section prompt."""
    profile = profile or {}
    template = profile.get(
        "user_instruction_template",
        (
            "Generate the '{section_id}' section of the resume "
            "for {target_company} ({target_role}). "
            "Mode: {generation_mode}."
        ),
    )
    return template.format(
        section_id=section_id,
        target_company=target_company or "the target company",
        target_role=target_role or "the target role",
        generation_mode=generation_mode,
    )


def _sha256_hex64(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _resolve_provider_targets(route: RouteContract) -> tuple[str, str, tuple[str, ...]]:
    """Return (model, provider, extra_gate_verdict_refs)."""
    ref = (route.provider_model_requirement_ref or "").strip()
    if ref and ref in _PROVIDER_MODEL_REGISTRY:
        m, p = _PROVIDER_MODEL_REGISTRY[ref]
        return m, p, ()
    return (
        APPS_RG_TARGET_MODEL,
        APPS_RG_TARGET_PROVIDER,
        ("PA_TEMPORARY_COMPATIBILITY_FALLBACK=provider_model_requirement_ref",),
    )


def _compose_ag2_user_instruction(plan: L1PlanContract, vr: ValidatedRequest) -> str:
    qs = dict(plan.query_spec or {})
    tgt = qs.get("target") if isinstance(qs.get("target"), dict) else {}
    company = str(tgt.get("company", "") or "")
    role = str(tgt.get("role", "") or "")
    level = str(tgt.get("level", "") or plan.target_level or "")
    sup = dict(plan.support_expectation or {})
    lines = [
        f"Target company: {company}",
        f"Target role: {role}",
        f"Target level: {level}",
    ]
    if sup.get("per_bullet_required"):
        lines.append("Provenance: evidence_anchor required per bullet.")
    if sup.get("source_quote_required"):
        lines.append("Provenance: source_quote required for factual claims.")
    if sup.get("fact_checked_required"):
        lines.append("Quality: fact-checked narrative required.")
    out = dict(plan.output_expectation or {})
    fmts = out.get("formats")
    if fmts:
        lines.append(f"Output formats: {', '.join(str(x) for x in fmts)}.")
    return "\n".join(lines)


def pa_compose_apps_rg(
    route: RouteContract,
    plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
) -> CompiledPromptArtifact:
    """AG-2 runtime PA — core ``assemble_prompt`` when governed PA enabled (W5)."""
    from apps_rg.runtime.spine.governed_pa_compose import (
        governed_pa_compose_enabled,
        governed_pa_compose_integrated,
    )

    if governed_pa_compose_enabled():
        return governed_pa_compose_integrated(
            route,
            plan,
            fec,
            validated_request,
        )

    return _pa_compose_apps_rg_legacy(route, plan, fec, validated_request)


def _pa_compose_apps_rg_legacy(
    route: RouteContract,
    plan: L1PlanContract,
    fec: FinalEvidenceContract,
    validated_request: ValidatedRequest,
) -> CompiledPromptArtifact:
    """Legacy two-block PA (pre-W5); used when ``APPS_RG_GOVERNED_PA_SKIP=1``."""
    profile = _load_pa_yaml_profile(None)
    preamble = _build_system_preamble(profile)
    route_hint = (
        f"[L0 route_family={route.route_family} execution_form={route.execution_form} "
        f"route_id={route.route_id}]"
    )
    system_text = f"{preamble}\n\n{route_hint}"
    user_text = _compose_ag2_user_instruction(plan, validated_request)

    blocks = (
        PromptBlock(role="system", content=system_text, block_index=0, origin=Origin.SYSTEM_INTERNAL),
        PromptBlock(role="user", content=user_text, block_index=1, origin=Origin.USER_INTENT),
    )

    slot_lineage_map = {
        "system_block_0": "PA-authored|SYSTEM_INTERNAL",
        "user_block_1": "USER_INTENT|L1_PLAN_PROJECTIONS",
    }

    style_key = json.dumps(profile, sort_keys=True, default=str)
    plan_key = json.dumps(
        {
            "task_spec": dict(plan.task_spec or {}),
            "query_spec": dict(plan.query_spec or {}),
            "support_expectation": dict(plan.support_expectation or {}),
            "output_expectation": dict(plan.output_expectation or {}),
        },
        sort_keys=True,
        default=str,
    )
    app_payload = dict(getattr(validated_request, "app_payload", None) or {})
    app_key = json.dumps(app_payload, sort_keys=True, default=str)
    route_key = json.dumps(
        {
            "route_id": route.route_id,
            "route_family": route.route_family,
            "execution_form": route.execution_form,
            "provider_model_requirement_ref": route.provider_model_requirement_ref,
        },
        sort_keys=True,
    )
    ev_digest = str(getattr(fec, "final_evidence_digest", "") or getattr(fec, "compilation_hash", "") or "")

    component_hash_map = {
        "style_profile": _sha256_hex64(style_key),
        "evidence": _sha256_hex64(ev_digest),
        "l1_plan": _sha256_hex64(plan_key),
        "app_payload": _sha256_hex64(app_key),
        "route": _sha256_hex64(route_key),
    }

    rk = plan.replay_key or getattr(validated_request, "replay_key", "") or ""
    replay_manifest_ref = f"replay_key:{rk}" if rk else f"reflection:{validated_request.request_id}"

    per_input: dict[str, str] = {}
    if isinstance(plan.query_spec, Mapping):
        jh = plan.query_spec.get("jd_hash")
        rh = plan.query_spec.get("resume_hash")
        if jh:
            per_input["jd_hash"] = _sha256_hex64(str(jh))
        if rh:
            per_input["resume_hash"] = _sha256_hex64(str(rh))

    model, provider, compat_refs = _resolve_provider_targets(route)
    gate_refs = tuple(compat_refs)

    comp_in = json.dumps(
        {
            "system": system_text,
            "user": user_text,
            "component_hash_map": component_hash_map,
        },
        sort_keys=True,
    )
    compilation_hash = _sha256_hex64(comp_in)

    ts = datetime.now(timezone.utc).isoformat()
    tenant = getattr(validated_request, "tenant_id", "") or getattr(fec, "tenant_id", "")

    return CompiledPromptArtifact(
        request_id=validated_request.request_id,
        run_id=validated_request.run_id,
        app_id=validated_request.app_id,
        trace_id=validated_request.trace_id,
        prompt_blocks=blocks,
        system_preamble=system_text,
        user_instruction=user_text,
        assembly_timestamp=ts,
        target_model=model,
        target_provider=provider,
        evidence_digest=ev_digest,
        compilation_hash=compilation_hash,
        slot_lineage_map=slot_lineage_map,
        component_hash_map=component_hash_map,
        replay_manifest_ref=replay_manifest_ref,
        per_input_hash_map=per_input,
        tenant_id=str(tenant or ""),
        l5_certification_ref=validated_request.l5_certification_ref,
        gate_verdict_refs=gate_refs,
        replay_key=rk,
    )


def pa_compose_apps_rg_section(
    section_id: str,
    evidence_items: list[Any],
    *,
    target_company: str = "",
    target_role: str = "",
    generation_mode: str = "strategic_tailor",
    profile_path: Optional[str] = None,
) -> SectionPromptArtifact:
    """Compose a section-scoped PA artifact (legacy section runner / unit tests)."""
    profile = _load_pa_yaml_profile(profile_path)
    preamble = _build_system_preamble(profile)
    task_block = _build_u0_task_block(section_id, profile)
    evidence_block = _build_c0_evidence_block(evidence_items)
    user_instruction = _build_user_instruction(
        section_id,
        target_company=target_company,
        target_role=target_role,
        generation_mode=generation_mode,
        profile=profile,
    )

    prompt_text = "\n\n".join(
        part for part in [preamble, task_block, evidence_block, user_instruction] if part
    )

    compilation_hash = _component_hash(preamble, task_block, evidence_block, user_instruction)

    return SectionPromptArtifact(
        section_id=section_id,
        prompt_text=prompt_text,
        system_preamble=preamble,
        u0_task_block=task_block,
        evidence_slot="c0_evidence_data_only",
        compilation_hash=f"sha256:{compilation_hash}",
        profile_ref=profile_path or "default",
    )
