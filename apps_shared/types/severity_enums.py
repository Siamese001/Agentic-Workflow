"""
Pure enum types extracted from sovereign_severity_types.py.
ADG declaration-only — no _emit_* calls, no Pydantic models, no lifecycle_trace_contract imports.
"""

from __future__ import annotations

import logging
from enum import Enum


class sovereign_severity(str, Enum):
    """Canonical SSOT for event severity levels with observability log mapping."""

    CRITICAL = "CRITICAL"
    "Immediate threat to sovereignty — system may be compromised"
    ERROR = "ERROR"
    "Healing required — constitutional violation detected"
    WARNING = "WARNING"
    "Degradation risk — attention needed but not blocking"
    INFO = "INFO"
    "Normal sovereign operation — audit trail"
    DEBUG = "DEBUG"
    "Detailed internal diagnostics — verbose"


SovereignSeverity = sovereign_severity

sovereign_severities = {e.value for e in sovereign_severity}

severity_log_levels = {
    sovereign_severity.CRITICAL: logging.CRITICAL,
    sovereign_severity.ERROR: logging.ERROR,
    sovereign_severity.WARNING: logging.WARNING,
    sovereign_severity.INFO: logging.INFO,
    sovereign_severity.DEBUG: logging.DEBUG,
}


def to_log_level(sev: sovereign_severity) -> int:
    """Convert a sovereign_severity to a stdlib logging level integer."""
    return severity_log_levels.get(sev, logging.INFO)


class sovereign_event_type(str, Enum):
    """Canonical SSOT for all SovereignEvent types with human-readable intent."""

    AUDIT_STARTED = "AUDIT_STARTED"
    "Sovereign Auditor v3 begins multi-dimensional compliance sweep"
    AUDIT_COMPLETED = "AUDIT_COMPLETED"
    "Sovereign Auditor v3 finishes audit with final sovereignty score"
    SOVEREIGNTY_COMPROMISED = "SOVEREIGNTY_COMPROMISED"
    "Overall health score drops below 95% — healing required"
    SOVEREIGNTY_RESTORED = "SOVEREIGNTY_RESTORED"
    "Healing cycle restores health to ≥95%"
    SOVEREIGNTY_ACHIEVED = "SOVEREIGNTY_ACHIEVED"
    "Overall health reaches ≥95% — threshold for active operations met"
    SOVEREIGNTY_PERFECT = "SOVEREIGNTY_PERFECT"
    "Overall health reaches 100.0% — perfect constitutional alignment"
    GUARDIAN_BLOCKED_COMMIT = "GUARDIAN_BLOCKED_COMMIT"
    "Pre-commit hook blocked commit due to constitutional violations"
    GUARDIAN_VIOLATION = "GUARDIAN_VIOLATION"
    "Guardian detected violation during enforcement check"
    GUARDIAN_CLEAN = "GUARDIAN_CLEAN"
    "Guardian validation passed — commit approved"
    HEALING_CYCLE_STARTED = "HEALING_CYCLE_STARTED"
    "L0 Healing Engine begins new self-correction cycle"
    HEALING_ACTION_APPLIED = "HEALING_ACTION_APPLIED"
    "Healing fix successfully applied via Transaction Manager"
    HEALING_ACTION_FAILED = "HEALING_ACTION_FAILED"
    "Healing fix failed — atomicity preserved via rollback"
    HEALING_TRANSACTION_START = "HEALING_TRANSACTION_START"
    "Healing transaction initiated with ACID guarantees"
    HEALING_TRANSACTION_COMMIT = "HEALING_TRANSACTION_COMMIT"
    "Healing transaction committed successfully"
    HEALING_TRANSACTION_ROLLBACK = "HEALING_TRANSACTION_ROLLBACK"
    "Healing transaction rolled back due to failure"
    HEALING_FIX_APPLIED = "HEALING_FIX_APPLIED"
    "Individual healing fix applied to codebase"
    HEALING_FIX_REVERTED = "HEALING_FIX_REVERTED"
    "Healing fix reverted due to validation failure"
    HEALING_CYCLE_COMPLETE = "HEALING_CYCLE_COMPLETE"
    "Healing cycle concludes with final remediation count"
    REASONING_START = "REASONING_START"
    "Reasoning chain begins execution for a goal"
    REASONING_END = "REASONING_END"
    "Reasoning chain completes with final conclusion"
    REASONING_STEP = "REASONING_STEP"
    "Individual reasoning step executed in thought chain"
    HYPOTHESIS_FORMED = "HYPOTHESIS_FORMED"
    "New hypothesis created during reasoning process"
    HYPOTHESIS_VALIDATED = "HYPOTHESIS_VALIDATED"
    "Hypothesis confirmed through evidence validation"
    HYPOTHESIS_REJECTED = "HYPOTHESIS_REJECTED"
    "Hypothesis disproven and discarded"
    DARK_REASONING_DETECTED = "DARK_REASONING_DETECTED"
    "Unlogged reasoning detected — observability gap identified"
    VIOLATION_DETECTED = "VIOLATION_DETECTED"
    "Guardian detects constitutional violation (SSOT, DDD, observability, etc.)"
    SSOT_INLINE_MODEL = "SSOT_INLINE_MODEL"
    "Inline Pydantic model detected outside schemas/ — SSOT violation"
    SSOT_RAW_PROMPT = "SSOT_RAW_PROMPT"
    "Raw prompt string found — should use prompt_governance SSOT"
    SSOT_HARDCODED_CONFIG = "SSOT_HARDCODED_CONFIG"
    "Hardcoded configuration value — should use sovereign_config SSOT"
    SSOT_UNDERSCORE_FIELD = "SSOT_UNDERSCORE_FIELD"
    "Underscore field detected in dataclass/BaseModel — naming violation"
    DDD_VIOLATION = "DDD_VIOLATION"
    "Domain-Driven Design principle violated"
    DDD_AGGREGATE_BYPASS = "DDD_AGGREGATE_BYPASS"
    "Aggregate boundary bypassed — direct entity access detected"
    DDD_UBIQUITOUS_LANGUAGE_MISSING = "DDD_UBIQUITOUS_LANGUAGE_MISSING"
    "Domain ubiquitous language not used — terminology violation"
    LAYER_CROSS_IMPORT = "LAYER_CROSS_IMPORT"
    "L1 agent directly imports L2 implementation — DIP violation"
    SYSTEM_BOOT = "SYSTEM_BOOT"
    "Agentic system initialization started"
    CONSTITUTION_LOAD = "CONSTITUTION_LOAD"
    "Sovereign domain constitution loaded into memory"
    MCP_INTEGRATION_STARTED = "MCP_INTEGRATION_STARTED"
    "Model Context Protocol integration initiated"
    MCP_INTEGRATION_SUCCESS = "MCP_INTEGRATION_SUCCESS"
    "MCP integration completed successfully"
    MCP_INTEGRATION_FAILED = "MCP_INTEGRATION_FAILED"
    "MCP integration failed with error"


SovereignEventType = sovereign_event_type

sovereign_event_categories = {
    "GOVERNANCE": [
        sovereign_event_type.AUDIT_STARTED,
        sovereign_event_type.AUDIT_COMPLETED,
        sovereign_event_type.SOVEREIGNTY_COMPROMISED,
        sovereign_event_type.SOVEREIGNTY_RESTORED,
        sovereign_event_type.SOVEREIGNTY_ACHIEVED,
        sovereign_event_type.SOVEREIGNTY_PERFECT,
    ],
    "GUARDIAN": [
        sovereign_event_type.GUARDIAN_BLOCKED_COMMIT,
        sovereign_event_type.GUARDIAN_VIOLATION,
        sovereign_event_type.GUARDIAN_CLEAN,
    ],
    "HEALING": [
        sovereign_event_type.HEALING_CYCLE_STARTED,
        sovereign_event_type.HEALING_ACTION_APPLIED,
        sovereign_event_type.HEALING_ACTION_FAILED,
        sovereign_event_type.HEALING_TRANSACTION_START,
        sovereign_event_type.HEALING_TRANSACTION_COMMIT,
        sovereign_event_type.HEALING_TRANSACTION_ROLLBACK,
        sovereign_event_type.HEALING_FIX_APPLIED,
        sovereign_event_type.HEALING_FIX_REVERTED,
        sovereign_event_type.HEALING_CYCLE_COMPLETE,
    ],
    "REASONING": [
        sovereign_event_type.REASONING_START,
        sovereign_event_type.REASONING_END,
        sovereign_event_type.REASONING_STEP,
        sovereign_event_type.HYPOTHESIS_FORMED,
        sovereign_event_type.HYPOTHESIS_VALIDATED,
        sovereign_event_type.HYPOTHESIS_REJECTED,
        sovereign_event_type.DARK_REASONING_DETECTED,
    ],
    "VIOLATION": [
        sovereign_event_type.VIOLATION_DETECTED,
        sovereign_event_type.SSOT_INLINE_MODEL,
        sovereign_event_type.SSOT_RAW_PROMPT,
        sovereign_event_type.SSOT_HARDCODED_CONFIG,
        sovereign_event_type.SSOT_UNDERSCORE_FIELD,
        sovereign_event_type.DDD_VIOLATION,
        sovereign_event_type.DDD_AGGREGATE_BYPASS,
        sovereign_event_type.DDD_UBIQUITOUS_LANGUAGE_MISSING,
        sovereign_event_type.LAYER_CROSS_IMPORT,
    ],
    "SYSTEM": [sovereign_event_type.SYSTEM_BOOT, sovereign_event_type.CONSTITUTION_LOAD],
    "MCP": [
        sovereign_event_type.MCP_INTEGRATION_STARTED,
        sovereign_event_type.MCP_INTEGRATION_SUCCESS,
        sovereign_event_type.MCP_INTEGRATION_FAILED,
    ],
}

__all__ = [
    "SovereignEventType",
    "SovereignSeverity",
    "severity_log_levels",
    "sovereign_event_categories",
    "sovereign_event_type",
    "sovereign_severities",
    "sovereign_severity",
    "to_log_level",
]
