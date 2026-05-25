"""Typed enums for same-authority regen contracts (ADR-085)."""

from __future__ import annotations

from enum import Enum


class TriggerSource(str, Enum):
    X2 = "X2"
    X3_JUDGE = "X3_JUDGE"
    OUTPUT_SCHEMA = "OUTPUT_SCHEMA"
    APP_MAPPER = "APP_MAPPER"


class DefectClass(str, Enum):
    SOFT_REPAIRABLE = "SOFT_REPAIRABLE"
    FAIL_TERMINAL = "FAIL_TERMINAL"
    NEEDS_HELP = "NEEDS_HELP"
    UNKNOWN = "UNKNOWN"


class AnchorClassification(str, Enum):
    LAST_APPROVED = "last_approved"
    DEGRADED_ANCHOR_ALLOWED = "degraded_anchor_allowed"
    REFUSE_UNSAFE = "refuse_unsafe"


class RegenRefusalCode(str, Enum):
    MISSING_FROZEN_COMPILE_REF = "missing_frozen_compile_ref"
    MISSING_ANCHOR_OUTPUT = "missing_anchor_output"
    EMPTY_DELTA_LINES = "empty_delta_lines"
    PROVIDER_SUBSTITUTION = "provider_substitution"
    PROMPT_RECOMPILE = "prompt_recompile"
    FULL_REWRITE_DELTA = "full_rewrite_delta"
    UNKNOWN_VALIDATION_STATUS = "unknown_validation_status"
    MOCKED_PROVIDER_ALLOW = "mocked_provider_allow"
    MISSING_AUTHORITY_REFS = "missing_authority_refs"
    AUTHORITY_BLOCKED = "authority_blocked"
    SEMANTIC_REGEN_BUDGET_EXHAUSTED = "semantic_regen_budget_exhausted"
    RECURSIVE_REGEN_FORBIDDEN = "recursive_regen_forbidden"
    ANCHOR_UNSAFE = "anchor_unsafe"
    ANCHOR_X2_RED_NOT_SOFT_REPAIRABLE = "anchor_x2_red_not_soft_repairable"
    DELTA_LINE_BUDGET_EXCEEDED = "delta_line_budget_exceeded"
    DELTA_TOKEN_BUDGET_EXCEEDED = "delta_token_budget_exceeded"
    DELTA_SHAPE_FORBIDDEN = "delta_shape_forbidden"
    DELTA_INSTRUCTION_RESET = "delta_instruction_reset"
