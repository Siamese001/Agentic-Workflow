"""Compatibility re-export — SSOT: apps_rg.runtime.sections.ibm_bullets_pa."""

from apps_rg.runtime.bindings.section_prompt_adapter import compile_section_prompt
from apps_rg.runtime.sections.ibm_bullets_pa import compile_ibm_bullets_prompt

__all__ = ["compile_ibm_bullets_prompt", "compile_section_prompt"]
