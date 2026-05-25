"""Structural delta shape guards (app-agnostic heuristics)."""

from __future__ import annotations

import re

from agentic_core.L2_execution.regen.regen_types import RegenRefusalCode

_FORBIDDEN_SECTION_MARKERS = re.compile(
    r"(?im)^\s*(system|developer|rubric|schema|output_schema|graph_only)\s*:",
)
_INSTRUCTION_RESET = re.compile(
    r"(?i)(ignore\s+previous|disregard\s+above|new\s+instructions|forget\s+the\s+prompt|"
    r"reset\s+all\s+instructions|start\s+over\s+completely)",
)
_FULL_REWRITE_MARKERS = re.compile(
    r"(?i)^(you\s+are\s+|#+\s*system\b|```)",
)


def estimate_token_count(text: str) -> int:
    """Conservative token estimate when no tokenizer is wired."""
    if not text:
        return 0
    return max(1, len(text) // 4)


def validate_delta_shape(
    delta_lines: tuple[str, ...],
    *,
    max_delta_lines: int,
    max_delta_tokens: int,
    anchor_output_text: str = "",
    full_rewrite_line_threshold: int = 40,
) -> RegenRefusalCode | None:
    """Return refusal code when delta fails shape guards; else None."""
    lines = tuple(ln for ln in delta_lines if ln and ln.strip())
    if not lines:
        return RegenRefusalCode.EMPTY_DELTA_LINES
    if len(lines) > max_delta_lines:
        return RegenRefusalCode.DELTA_LINE_BUDGET_EXCEEDED

    joined = "\n".join(lines)
    tokens = estimate_token_count(joined)
    if tokens > max_delta_tokens:
        return RegenRefusalCode.DELTA_TOKEN_BUDGET_EXCEEDED

    if _FORBIDDEN_SECTION_MARKERS.search(joined):
        return RegenRefusalCode.DELTA_SHAPE_FORBIDDEN

    if _INSTRUCTION_RESET.search(joined):
        return RegenRefusalCode.DELTA_INSTRUCTION_RESET

    if len(lines) >= full_rewrite_line_threshold:
        return RegenRefusalCode.FULL_REWRITE_DELTA

    if _FULL_REWRITE_MARKERS.search(joined):
        return RegenRefusalCode.FULL_REWRITE_DELTA

    if anchor_output_text and len(joined) > max(len(anchor_output_text) * 2, 8000):
        return RegenRefusalCode.FULL_REWRITE_DELTA

    return None
