"""apps_rg PA binding — prompt assembly cert ref and section prompt helpers.

PA_BOUNDARY_CERT_S3 and related types used by tests verifying the PA
boundary contract for apps_rg section-level prompt assembly.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

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
    "reset_pa_prompt_profile_cache",
]

PA_BOUNDARY_CERT_S3: str = "pa-apps-rg-section-prompt-boundary-s3"
APPS_RG_PA_CERT_REF: str = "pa-apps-rg-resume-generation-w3"
APPS_RG_TARGET_MODEL: str = "Qwen/Qwen2.5-32B-Instruct-AWQ"
APPS_RG_TARGET_PROVIDER: str = "vllm_local"

_PA_PROFILE_CACHE: dict[str, Any] = {}


@dataclass(frozen=True)
class SectionPromptArtifact:
    """Compiled prompt artifact for a single resume section."""

    section_id: str
    prompt_text: str
    system_preamble: str = ""
    u0_task_block: str = ""
    evidence_slot: str = "c0_evidence_data_only"
    compilation_hash: str = ""
    profile_ref: str = ""


def reset_pa_prompt_profile_cache() -> None:
    """Clear the cached PA prompt profile (test helper)."""
    _PA_PROFILE_CACHE.clear()


def _load_pa_prompt_profile(profile_path: Optional[str] = None) -> dict[str, Any]:
    """Load the PA prompt profile YAML (cached)."""
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
    except Exception:
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
    evidence_text: str = "",
    *,
    profile_path: Optional[str] = None,
) -> SectionPromptArtifact:
    """Build a SectionPromptArtifact for a resume section."""
    import hashlib
    profile = _load_pa_prompt_profile(profile_path)
    preamble = _build_system_preamble(profile)
    task = _build_u0_task_block(section_id, profile)
    prompt = f"{preamble}\n\n{task}\n\nEvidence:\n{evidence_text}"
    digest = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    return SectionPromptArtifact(
        section_id=section_id,
        prompt_text=prompt,
        system_preamble=preamble,
        u0_task_block=task,
        compilation_hash=f"sha256:{digest}",
        profile_ref=profile_path or "default",
    )


def build_section_prompt_artifact_for_bullet(
    section_id: str,
    bullet_text: str,
    *,
    profile_path: Optional[str] = None,
) -> SectionPromptArtifact:
    """Build a SectionPromptArtifact for a bullet rewrite."""
    import hashlib
    profile = _load_pa_prompt_profile(profile_path)
    preamble = _build_system_preamble(profile)
    prompt = _build_bullet_rewrite_prompt(section_id, bullet_text, profile)
    digest = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    return SectionPromptArtifact(
        section_id=section_id,
        prompt_text=prompt,
        system_preamble=preamble,
        compilation_hash=f"sha256:{digest}",
        profile_ref=profile_path or "default",
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


def pa_compose_apps_rg(
    section_id: str,
    evidence_items: list[Any],
    *,
    target_company: str = "",
    target_role: str = "",
    generation_mode: str = "strategic_tailor",
    profile_path: Optional[str] = None,
) -> SectionPromptArtifact:
    """Compose a full PA prompt artifact for apps_rg resume generation.

    This is the primary entry point consumed by the core PA binding shim.

    Parameters
    ----------
    section_id:
        Resume section ID (e.g. "headline", "executive_summary").
    evidence_items:
        C0 evidence items to inject into the prompt.
    target_company:
        Target company name.
    target_role:
        Target role/title.
    generation_mode:
        One of "strategic_tailor", "keyword_match", "generate_scratch".
    profile_path:
        Optional override for the PA prompt profile YAML path.

    Returns
    -------
    SectionPromptArtifact
    """
    profile = _load_pa_prompt_profile(profile_path)
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
