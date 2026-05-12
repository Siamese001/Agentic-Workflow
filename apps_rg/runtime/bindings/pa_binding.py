"""Prompt-Assembly binding for apps_rg `resume_generation` task class.

MIGRATED from agentic_core/prompt_governance/apps_rg_pa_binding.py
Per plan apps-rg-golden-state-section-generation-a4f9e1 W2D.

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
            section = None
    return forbidden, power


def _extract_format_constraints(profile_text: str) -> dict[str, object]:
    """Parse format_constraints block from profile YAML without a yaml dep.

    Returns a dict with keys:
      exec_sentence_count (int)
      exec_structure (list[str])
      competency_count (int)
      role_bullets (list[dict]  — [{company_match, bullet_count}])
    Falls back to best-practice defaults if section is absent.
    """
    defaults: dict[str, object] = {
        "exec_sentence_count": 5,
        "exec_structure": [
            "positioning: who the candidate is + primary expertise tailored to this role",
            "method: how they architect or govern — SEPARATE sentence from scope",
            "scope: full leadership scope (strategy through delivery, team scale, commercialization) — SEPARATE sentence from method",
            "outcomes: exactly 3-4 quantified metrics verbatim from source resume",
            "credentials: single highest-signal credential",
        ],
        "competency_count": 12,
        "role_bullets": [
            {"company_match": "Unify", "bullet_count": 6},
            {"company_match": "IBM", "bullet_count": 5},
            {"company_match": "InsurTech", "bullet_count": 3},
            {"company_match": "Ernst & Young", "bullet_count": 3},
            {"company_match": "Early Career", "bullet_count": 1},
        ],
    }
    in_format = False
    in_exec = False
    in_roles = False
    in_competencies = False
    exec_structure: list[str] = []
    role_bullets: list[dict] = []
    current_role: dict | None = None
    exec_sentence_count = int(defaults["exec_sentence_count"])  # type: ignore[arg-type]
    competency_count = int(defaults["competency_count"])  # type: ignore[arg-type]

    for raw in profile_text.splitlines():
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("format_constraints:"):
            in_format = True
            continue
        if in_format and indent == 0 and not stripped.startswith("format_constraints"):
            in_format = False
        if not in_format:
            continue
        if stripped.startswith("executive_summary:"):
            in_exec = True
            in_roles = False
            in_competencies = False
            continue
        if stripped.startswith("experience_bullets:"):
            in_exec = False
            in_roles = True
            in_competencies = False
            continue
        if stripped.startswith("competencies:"):
            in_exec = False
            in_roles = False
            in_competencies = True
            continue
        if in_exec:
            if stripped.startswith("sentence_count:"):
                try:
                    exec_sentence_count = int(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass
            elif stripped.startswith("- ") and exec_structure is not None:
                exec_structure.append(stripped[2:].strip().strip('"'))
        if in_roles:
            if stripped.startswith("- company_match:"):
                if current_role:
                    role_bullets.append(current_role)
                current_role = {"company_match": stripped.split(":", 1)[1].strip().strip('"'), "bullet_count": 4}
            elif stripped.startswith("bullet_count:") and current_role:
                try:
                    current_role["bullet_count"] = int(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass
        if in_competencies:
            if stripped.startswith("entry_count:"):
                try:
                    competency_count = int(stripped.split(":", 1)[1].strip())
                except ValueError:
                    pass

    if current_role:
        role_bullets.append(current_role)

    return {
        "exec_sentence_count": exec_sentence_count,
        "exec_structure": exec_structure or list(defaults["exec_structure"]),  # type: ignore[arg-type]
        "competency_count": competency_count,
        "role_bullets": role_bullets or list(defaults["role_bullets"]),  # type: ignore[arg-type]
    }


def _extract_section_guidance(profile_text: str) -> dict[str, dict[str, list[str]]]:
    """Parse section_guidance block from profile YAML without a yaml dep.

    Returns dict keyed by section name (e.g. 'executive_summary', 'experience_unify'),
    each value a dict with 'rigor_rules', 'voice_rules', 'ats_rules' lists.
    Falls back to empty dict if section absent.
    """
    result: dict[str, dict[str, list[str]]] = {}
    in_section_guidance = False
    current_section: str | None = None
    current_rule_type: str | None = None

    for raw in profile_text.splitlines():
        indent = len(raw) - len(raw.lstrip())
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if stripped.startswith("section_guidance:"):
            in_section_guidance = True
            continue
        if in_section_guidance and indent == 0 and not stripped.startswith("section_guidance"):
            in_section_guidance = False
        if not in_section_guidance:
            continue

        if indent == 2 and stripped.endswith(":") and not stripped.startswith("-"):
            current_section = stripped.rstrip(":")
            result[current_section] = {"rigor_rules": [], "voice_rules": [], "ats_rules": []}
            current_rule_type = None
            continue

        if indent == 4 and stripped.endswith(":") and not stripped.startswith("-") and current_section:
            rule_key = stripped.rstrip(":")
            if rule_key in ("rigor_rules", "voice_rules", "ats_rules"):
                current_rule_type = rule_key
            else:
                current_rule_type = None
            continue

        if indent == 6 and stripped.startswith("- ") and current_section and current_rule_type:
            value = stripped[2:].strip().strip('"').strip("'")
            if value:
                result[current_section][current_rule_type].append(value)

    return result


def _build_section_rigor_block(section_guidance: dict[str, dict[str, list[str]]]) -> str:
    """Build per-section rigor instructions injected into Qwen's system prompt.

    Only emits substantive content — skips empty sections.
    Sentence/structure counts are handled by _build_format_block;
    this block covers CONTENT rigor (evidence grounding, voice, ATS).
    """
    if not section_guidance:
        return ""

    SECTION_LABELS = {
        "executive_summary": "EXECUTIVE SUMMARY CONTENT RIGOR",
        "experience_unify": "EXPERIENCE — UNIFY CONSULTING (current role)",
        "experience_ibm": "EXPERIENCE — IBM",
        "experience_insurtech": "EXPERIENCE — INSURTECH CLOUD SOLUTIONS",
        "experience_ey": "EXPERIENCE — ERNST & YOUNG",
        "experience_early_career": "EXPERIENCE — EARLY CAREER",
        "competencies": "COMPETENCIES/SKILLS CONTENT RIGOR",
    }
    ORDER = ["executive_summary", "experience_unify", "experience_ibm",
             "experience_insurtech", "experience_ey", "experience_early_career", "competencies"]

    lines: list[str] = ["SECTION CONTENT RIGOR (applies to every section — grounded in source materials only):"]
    for key in ORDER:
        guidance = section_guidance.get(key)
        if not guidance:
            continue
        label = SECTION_LABELS.get(key, key.upper())
        all_rules: list[str] = (
            guidance.get("rigor_rules", [])
            + guidance.get("voice_rules", [])
            + guidance.get("ats_rules", [])
        )
        if not all_rules:
            continue
        lines.append(f"  {label}:")
        for r in all_rules:
            lines.append(f"    - {r}")
    return "\n".join(lines)


def _build_format_block(fmt: dict[str, object] | None) -> str:
    """Build the MANDATORY FORMAT instructions block from parsed profile constraints."""
    if not fmt:
        return ""
    n = int(fmt.get("exec_sentence_count", 5))  # type: ignore[arg-type]
    structure: list[str] = list(fmt.get("exec_structure", []))  # type: ignore[arg-type]
    comp_n = int(fmt.get("competency_count", 12))  # type: ignore[arg-type]
    role_bullets: list[dict] = list(fmt.get("role_bullets", []))  # type: ignore[arg-type]

    struct_lines = " ".join(
        f"Sentence {i+1} ({s.split(':')[0].strip()}): {s.split(':', 1)[1].strip() if ':' in s else s}."
        for i, s in enumerate(structure)
    )

    role_lines = " ".join(
        f"{r['company_match']}: 1 intro sentence + EXACTLY {r['bullet_count']} bullets."
        for r in role_bullets
    )

    return (
        f"EXECUTIVE SUMMARY — EXACTLY {n} SENTENCES, NO EXCEPTIONS: "
        f"Write {n} period-terminated sentences as one dense paragraph. Count them before writing. "
        f"{struct_lines} "
        f"Output format — CRITICAL: {{\"content\": [\"<all {n} sentences as ONE string>\"]}}. "
        f"The content array has EXACTLY ONE element — one string containing all {n} sentences. "
        f"Do NOT split sentences into separate array elements."
        f"\n"
        f"EXPERIENCE SECTION — MANDATORY SENTENCE/BULLET COUNTS (sentence-based, not word/token-based): "
        f"Each role: 1 intro sentence + exact bullet count per role below. "
        f"{role_lines} "
        f"Each bullet: bold keyword label followed by colon and achievement sentence. "
        f"SCHEMA per role: {{\"title\": \"...\", \"company\": \"...\", \"location\": \"...\", \"dates\": \"...\", "
        f"\"intro\": \"<one sentence>\", \"bullets\": [{{\"evidence_anchor\": \"Label\", \"description\": \"Label: achievement\"}}]}}. "
        f"Do NOT use a top-level 'description' array. Use 'intro' + 'bullets'."
        f"\n"
        f"COMPETENCIES/SKILLS SECTION — MANDATORY: "
        f"Output EXACTLY {comp_n} entries in the 'skills' array. "
        f"Each entry: short noun phrase (2-4 words) matching JD language. "
        f"Competencies communicate to the recruiter; embed matching JD keywords in experience bullets for full ATS credit."
    )


def _build_system_preamble(
    forbidden: list[str],
    power: list[str],
    fmt: dict[str, object] | None = None,
    section_guidance: dict[str, dict[str, list[str]]] | None = None,
) -> str:
    """Compose the system preamble carrying style + role guidance."""
    parts: list[str] = [
        "You are a senior resume writer producing a tailored executive resume for an SVP/C-suite candidate.",
        "Write in the third person voice of the candidate. Every factual claim MUST be grounded in the supplied source materials — no fabrication, no rounding, no inference.",
        "Output a JSON document matching the resume schema. No prose outside JSON.",
        _build_format_block(fmt),
    ]
    rigor_block = _build_section_rigor_block(section_guidance or {})
    if rigor_block:
        parts.append(rigor_block)
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

    # Grounded runs (strategic_tailor / tailor_existing) MUST emit a header object
    # extracted from source resume identity fields.  generate_scratch runs omit it.
    _gm_raw = (validated_request.app_payload or {}).get("generation_mode") or ""
    generation_mode: str = (
        _gm_raw.value if hasattr(_gm_raw, "value") else str(_gm_raw)
    )
    _GROUNDED_MODES = {"strategic_tailor", "tailor_existing"}
    is_grounded = generation_mode in _GROUNDED_MODES

    if is_grounded:
        header_instruction = (
            f"\n"
            f"HEADER SECTION — MANDATORY FOR GROUNDED RUNS:\n"
            f"Extract candidate identity fields verbatim from the source resume. "
            f"Do NOT invent or modify any field. Emit a top-level \"header\" key with "
            f"this exact schema:\n"
            f"  {{\"name\": \"<full name from resume>\", "
            f"\"phone\": \"<phone or null>\", "
            f"\"email\": \"<email or null>\", "
            f"\"linkedin\": \"<linkedin URL or null>\", "
            f"\"github\": \"<github URL or null>\", "
            f"\"location\": \"<city, state or null>\"}}\n"
            f"If a field is absent in the source resume, set it to null. "
            f"Do NOT substitute target_company or target_role values."
        )
        sections_str = "header, executive_summary, experience, skills, education, certifications"
    else:
        header_instruction = ""
        sections_str = "executive_summary, experience, skills, education, certifications"

    return (
        f"Tailor a resume for the following position:\n"
        f"  Company: {target_company}\n"
        f"  Role:    {target_role}\n"
        f"  Level:   {target_level}\n"
        f"\n"
        f"Task plan from L1: {', '.join(l1_plan.task_plan)}\n"
        f"\n"
        f"AG-2 provenance directives:\n{directives_block}\n"
        f"{header_instruction}"
        f"\n"
        f"Produce output in formats: {formats_str}. Default to a JSON resume "
        f"document with sections: {sections_str}. Output JSON only — no markdown, no prose preamble."
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
    fmt = _extract_format_constraints(style_text)
    section_guidance = _extract_section_guidance(style_text)

    system_preamble = _build_system_preamble(forbidden, power, fmt, section_guidance)
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

    # Per-input hashes — deposited into component_hash_map so Exit G24 can read
    # them without a separate contract field.  Keys are apps_rg-specific but the
    # container (component_hash_map) is the existing generic field on the artifact.
    _app_payload: Mapping[str, Any] = validated_request.app_payload or {}
    _jd_section = _app_payload.get("jd_payload") or {}
    _resume_section = _app_payload.get("resume_payload") or {}
    _target_section = _app_payload.get("target") or {}
    _target_spec_str = "|".join([
        str(_target_section.get("company", "")),
        str(_target_section.get("role", "")),
        str(_target_section.get("level", "")),
    ])
    component_hash_map["jd_hash"] = str(_jd_section.get("jd_hash") or "")
    component_hash_map["resume_hash"] = str(_resume_section.get("resume_hash") or "")
    component_hash_map["target_role_spec_hash"] = hashlib.sha256(
        _target_spec_str.encode("utf-8")
    ).hexdigest()

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
        max_tokens=8192,  # vLLM max_model_len=16384; prompt ~4k tokens leaves 12k headroom
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
