"""W3/W4 section prompt adapter — apps_rg PA compile seam for dispatch.

Authority model (hardening):
  - apps_rg owns prompt template content on disk.
  - Prompt assembly (PA) compiles slots into a ``CompiledPromptArtifact`` (fenced, hashed).
  - L2 executes the provider packet; X2 / X1D / Exit judge downstream.

Executive summary (W4) compiles through ``apps_rg.runtime.dispatch.executive_summary_pa``,
which builds ``PromptAssemblyInput`` and calls ``compile_section_prompt`` here.

This module only reads section contract YAML and invokes the apps_rg-local ``PromptCompiler``.
It does not retrieve C0, call model providers, mutate ``prompt_registry.yaml``, write durable
state, or substitute inline prompts on compile failure.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping

import yaml

from apps_rg.prompt_assembly.compiler import compile_prompt
from apps_rg.prompt_assembly.contracts import (
    CompiledPromptArtifact,
    PromptAssemblyError,
    PromptAssemblyInput,
)


@dataclass(frozen=True)
class SectionCompiledPrompt:
    """Adapter result: compiled artifact plus section SSOT refs (not on ``CompiledPromptArtifact``)."""

    section_id: str
    apps_rg_prompt_template_ref: str
    artifact: CompiledPromptArtifact


_ADAPTER_ROOT = Path(__file__).resolve().parent
_APPS_RG_ROOT = _ADAPTER_ROOT.parent.parent
_SECTION_CONTRACT_DIR = _APPS_RG_ROOT / "prompt_assembly" / "section_prompt_contracts"


def _load_contract(section_id: str) -> dict[str, Any]:
    path = _SECTION_CONTRACT_DIR / f"{section_id}.contract.yaml"
    if not path.is_file():
        raise PromptAssemblyError(
            code="SECTION_CONTRACT_NOT_FOUND",
            message=f"Missing section contract file for section_id={section_id!r}",
            context={"path": str(path)},
        )
    with path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, Mapping):
        raise PromptAssemblyError(
            code="SECTION_CONTRACT_INVALID",
            message=f"Section contract is not a mapping: {path}",
        )
    return dict(data)


def compile_section_prompt(
    assembly_input: PromptAssemblyInput,
    *,
    section_id: str,
    companion_u_tier: str | None = None,
) -> SectionCompiledPrompt:
    """Validate ``section_id`` against its stub contract and compile ``assembly_input``.

    Raises ``PromptAssemblyError`` on locked (non-LLM) sections, companion misuse, or
    ``template_id`` mismatch vs contract ``pa_template_ref``. Compiler failures propagate
    (no fallback to inline prompts).
    """
    contract = _load_contract(section_id)
    file_section = contract.get("section_id")
    if file_section != section_id:
        raise PromptAssemblyError(
            code="SECTION_CONTRACT_ID_MISMATCH",
            message=f"contract section_id {file_section!r} != arg {section_id!r}",
        )

    if contract.get("llm_generation_allowed") is False:
        raise PromptAssemblyError(
            code="SECTION_NON_LLM_LOCKED",
            message="Section is LOCKED_DETERMINISTIC / non-LLM; adapter compile is forbidden",
            context={"section_id": section_id},
        )

    expected = (contract.get("pa_template_ref") or "").strip()
    if expected and assembly_input.template_id != expected:
        raise PromptAssemblyError(
            code="PA_TEMPLATE_REF_MISMATCH",
            message=(
                f"PromptAssemblyInput.template_id={assembly_input.template_id!r} "
                f"does not match contract pa_template_ref={expected!r}"
            ),
            context={"section_id": section_id},
        )

    if companion_u_tier is not None:
        if not contract.get("companion_context_allowed"):
            raise PromptAssemblyError(
                code="COMPANION_NOT_ALLOWED",
                message="companion_u_tier supplied but contract disallows companion context",
                context={"section_id": section_id},
            )
        if contract.get("companion_context_authority") != "U_TIER_CONTEXT_ONLY":
            raise PromptAssemblyError(
                code="COMPANION_AUTHORITY_INVALID",
                message="Companion context requires companion_context_authority=U_TIER_CONTEXT_ONLY",
                context={"section_id": section_id},
            )
        fence = (
            "<U_TIER_COMPANION_CONTEXT>\n"
            f"{companion_u_tier.strip()}\n"
            "</U_TIER_COMPANION_CONTEXT>\n\n"
        )
        assembly_input = replace(assembly_input, u0_user_task=fence + assembly_input.u0_user_task)

    artifact = compile_prompt(assembly_input, base_path=_APPS_RG_ROOT / "prompt_assembly")
    apps_rg_ref = str(contract.get("apps_rg_prompt_template_ref") or "")
    return SectionCompiledPrompt(
        section_id=section_id,
        apps_rg_prompt_template_ref=apps_rg_ref,
        artifact=artifact,
    )


__all__ = ["SectionCompiledPrompt", "compile_section_prompt"]
