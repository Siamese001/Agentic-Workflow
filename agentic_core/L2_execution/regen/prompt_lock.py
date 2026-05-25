"""Generic REGEN_DELTA envelope text (core-owned; apps supply delta lines only)."""

from __future__ import annotations

REGEN_DELTA_HEADER = "REGEN_DELTA_v1"
PROMPT_LOCK_GENERIC = (
    "PROMPT_LOCK: The frozen compiled prompt remains authoritative. "
    "Apply only the bounded judge/gate delta below. Do not restate system rules, "
    "rubrics, schemas, or synthesis instructions."
)

REPAIR_TACTIC_INCREMENTAL_DELTA = "incremental_delta_turn_v1"
CONTRACT_VERSION = "1.0.0"
DEFAULT_MAX_DELTA_LINES = 20
DEFAULT_MAX_DELTA_TOKENS = 512
DEFAULT_MAX_SEMANTIC_REGEN_ATTEMPTS = 1


def format_regen_delta_user_turn(delta_lines: tuple[str, ...]) -> str:
    """Build bounded REGEN_DELTA user message from app mapper lines."""
    body = "\n".join(line.rstrip() for line in delta_lines if line.strip())
    return f"{REGEN_DELTA_HEADER}\n{PROMPT_LOCK_GENERIC}\n{body}"
