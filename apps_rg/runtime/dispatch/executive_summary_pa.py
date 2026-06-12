"""Compatibility re-export - SSOT: apps_rg.runtime.sections.executive_summary_pa."""

from apps_rg.runtime.bindings.section_prompt_adapter import compile_section_prompt
from apps_rg.runtime.sections.executive_summary_pa import (
    GRAPH_EVIDENCE_COMPOSITION_MARKER,
    GRAPH_EVIDENCE_FORBIDDEN_PHRASE_CONTRACT_MARKER,
    GRAPH_EVIDENCE_FORBIDDEN_PHRASES_ALWAYS,
    GRAPH_EVIDENCE_STYLE_MARKER,
    load_executive_summary_example_after,
    build_executive_summary_assembly_input,
    compile_executive_summary_prompt,
    format_graph_evidence_forbidden_phrase_guardrails_block,
    format_graph_evidence_style_quality_block,
    format_graph_only_quality_guardrails_block,
    load_executive_summary_template_slots,
)

__all__ = [
    "GRAPH_EVIDENCE_COMPOSITION_MARKER",
    "GRAPH_EVIDENCE_FORBIDDEN_PHRASE_CONTRACT_MARKER",
    "GRAPH_EVIDENCE_FORBIDDEN_PHRASES_ALWAYS",
    "GRAPH_EVIDENCE_STYLE_MARKER",
    "load_executive_summary_example_after",
    "build_executive_summary_assembly_input",
    "compile_executive_summary_prompt",
    "format_graph_evidence_forbidden_phrase_guardrails_block",
    "format_graph_evidence_style_quality_block",
    "format_graph_only_quality_guardrails_block",
    "load_executive_summary_template_slots",
    "compile_section_prompt",
]
