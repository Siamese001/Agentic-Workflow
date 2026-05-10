"""Prompt-Assembly binding for apps_rg `resume_generation` task class.

Per plan apps-rg-runtime-wiring-completion-d4e8a1 §6 W3.P4.

PA is the FIFTH stage (CONDITIONAL — fires only when
route.model_generation_required=True). Its job is to compile a typed
CompiledPromptArtifact from:
- The L1 plan (provides task_plan + capabilities)
- The L0 route (provides routing flags + reason codes)
- The C0 evidence (JD, resume, brief)
- The original payload (target_company / target_role / target_level)
- The apps_rg style profile (forbidden phrases + power verbs from
  rg_prompt_profile.yaml)

Per AG-RGGOV-6: prompt assembly logic lives in core, NOT in apps_rg.
This binding lives in agentic_core/prompt_governance/ ✅.

The compiled artifact carries target_model='Qwen/Qwen2.5-32B-Instruct-AWQ'
+ target_provider='vllm' — matching the canonical Docker stack
(memory 01483ea2). L2 will dispatch to that endpoint in W3.P5.

W3.P4 SCOPE: shape-valid prompt with real placeholder substitution +
style-constraint injection. Multi-turn refinement, tool-call composition,
and dynamic style-mining live in W5.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from agentic_core.runtime.contracts.apps_rg_ingress_payload import (
    AppsRgIngressPayload,
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


APPS_RG_PA_CERT_REF: str = "pa-apps-rg-resume-generation-w3p4"

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


def _build_user_instruction(
    payload: AppsRgIngressPayload,
    fec: FinalEvidenceContract,
    l1_plan: L1PlanContract,
) -> str:
    """Compose the user instruction with placeholders substituted."""
    target_company = payload.target_company or "the target company"
    target_role = payload.target_role or "the target role"
    target_level = payload.target_level or "unspecified"

    # vLLM serving at --max-model-len 8192 tokens (~24K chars for evidence
    # after system prompt + response reservation). The model itself supports
    # 32K natively; increase --max-model-len when VRAM allows.
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
        f"Tailor a resume for the following position:\n"
        f"  Company: {target_company}\n"
        f"  Role:    {target_role}\n"
        f"  Level:   {target_level}\n"
        f"\n"
        f"Task plan from L1: {', '.join(l1_plan.task_plan)}\n"
        f"\n"
        f"Source materials (consume verbatim — do not invent facts):\n"
        f"{''.join(inlined) if inlined else '[no evidence supplied]'}\n"
        f"\n"
        f"Produce a JSON resume document with sections: executive_summary, "
        f"experience, skills, education, certifications. Cite source materials "
        f"in the experience section's `evidence_anchor` field per bullet. "
        f"Output JSON only — no markdown, no prose preamble."
    )


def pa_compose_apps_rg(
    route: RouteContract,
    l1_plan: L1PlanContract,
    fec: FinalEvidenceContract,
    payload: AppsRgIngressPayload,
) -> CompiledPromptArtifact:
    """Compile a typed CompiledPromptArtifact for L2 to execute.

    Args:
        route: L0 routing decision (must have model_generation_required=True).
        l1_plan: L1 plan contract — drives task plan injection.
        fec: C0 final evidence — its compilation_hash is referenced in
             evidence_digest for provenance.
        payload: Original ingress payload — provides target_*.

    Returns:
        CompiledPromptArtifact with system + user blocks, target model/provider
        bound, and provenance digests linked.

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
    if not isinstance(payload, AppsRgIngressPayload):
        raise TypeError(
            f"pa_compose_apps_rg expected AppsRgIngressPayload, got {type(payload).__name__}"
        )

    repo_root = _resolve_repo_root()
    style_text = _load_style_profile_text(repo_root)
    forbidden, power = _extract_style_directives(style_text)

    system_preamble = _build_system_preamble(forbidden, power)
    user_instruction = _build_user_instruction(payload, fec, l1_plan)

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

    # Compilation hash binds prompt content for L2 provenance + reuse caching.
    canonical = json.dumps(
        [{"role": b.role, "len": len(b.content), "idx": b.block_index} for b in blocks]
        + [{"model": APPS_RG_TARGET_MODEL, "provider": APPS_RG_TARGET_PROVIDER}],
        sort_keys=True,
    )
    compilation_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

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
        schema_version="W3.P4",
        target_model=APPS_RG_TARGET_MODEL,
        target_provider=APPS_RG_TARGET_PROVIDER,
        evidence_digest=fec.compilation_hash,
        compilation_hash=compilation_hash,
        # W2 P2.2: thread capability/sandbox/egress from RouteContract
        sandbox_required=route.sandbox_required,
        egress_policy_ref=route.egress_policy_ref,
        allowed_tools=route.allowed_tools,
        allowed_models=route.allowed_models,
        allowed_networks=route.allowed_networks,
        allowed_file_roots=route.allowed_file_roots,
        max_tokens=4096,
        temperature=0.4,  # lower for factual resume generation
        l5_certification_ref=APPS_RG_PA_CERT_REF,
    )


__all__ = [
    "APPS_RG_PA_CERT_REF",
    "APPS_RG_TARGET_MODEL",
    "APPS_RG_TARGET_PROVIDER",
    "pa_compose_apps_rg",
]
