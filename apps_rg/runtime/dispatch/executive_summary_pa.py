"""Compatibility re-export — SSOT: apps_rg.runtime.sections.executive_summary_pa."""

from apps_rg.runtime.sections.executive_summary_pa import (
    SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR,
    SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER,
    SRFS_FORBIDDEN_PHRASES_ALWAYS,
    SRFS_SENTENCE_RESP_SEP_MARKER,
    SRFS_STYLE_ONESHOT_MARKER,
    SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER,
    build_executive_summary_assembly_input,
    compile_executive_summary_prompt,
    format_graph_only_quality_guardrails_block,
    format_srfs_forbidden_phrase_guardrails_block,
    format_srfs_role_adaptive_appendix,
    format_srfs_style_only_quality_oneshot_block,
    load_executive_summary_template_slots,
)

__all__ = [
    "SRFS_BASE_RESUME_STYLE_ONESHOT_EXEMPLAR",
    "SRFS_FORBIDDEN_PHRASE_CONTRACT_MARKER",
    "SRFS_FORBIDDEN_PHRASES_ALWAYS",
    "SRFS_SENTENCE_RESP_SEP_MARKER",
    "SRFS_STYLE_ONESHOT_MARKER",
    "SRFS_THREE_SENTENCE_EXEC_ARCH_MARKER",
    "build_executive_summary_assembly_input",
    "compile_executive_summary_prompt",
    "format_graph_only_quality_guardrails_block",
    "format_srfs_forbidden_phrase_guardrails_block",
    "format_srfs_role_adaptive_appendix",
    "format_srfs_style_only_quality_oneshot_block",
    "load_executive_summary_template_slots",
]
