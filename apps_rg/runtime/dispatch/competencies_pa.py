"""Compatibility re-export — SSOT: apps_rg.runtime.sections.competencies_pa."""

from apps_rg.runtime.bindings.section_prompt_adapter import compile_section_prompt
from apps_rg.runtime.sections.competencies_pa import compile_competencies_prompt

__all__ = ["compile_competencies_prompt", "compile_section_prompt"]
