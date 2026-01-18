from __future__ import annotations
"""
Sovereign Event Contracts - SSOT for all event types and Severity levels.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
import logging
from enum import Enum
from typing import List, Dict

# === SOVEREIGN SEVERITY LEVELS ===
class SovereignSeverity(str, Enum):
    """Canonical SSOT for event Severity levels with observability log mapping."""
    
    CRITICAL = "CRITICAL"
    """Immediate threat to sovereignty — system may be compromised"""
    
    ERROR = "ERROR"
    """Healing required — constitutional Violation detected"""
    
    WARNING = "WARNING"
    """Degradation risk — attention needed but not blocking"""
    
    INFO = "INFO"
    """Normal sovereign operation — audit trail"""
    
    DEBUG = "DEBUG"
    """Detailed internal diagnostics — verbose"""

# Backward compatibility alias

# Registry for validation and observability mapping
sovereign_severities = {e.value for e in SovereignSeverity}
severity_log_levels = {
    SovereignSeverity.CRITICAL: logging.CRITICAL,
    SovereignSeverity.ERROR: logging.ERROR,
    SovereignSeverity.WARNING: logging.WARNING,
    SovereignSeverity.INFO: logging.INFO,
    SovereignSeverity.DEBUG: logging.DEBUG,
}

# === SOVEREIGN EVENT TYPE REGISTRY ===
class SovereignEventType(str, Enum):
    """Canonical SSOT for all SovereignEvent types with human-readable intent."""
    
    # === GOVERNANCE ===
    AUDIT_STARTED = "AUDIT_STARTED"
    AUDIT_COMPLETED = "AUDIT_COMPLETED"
    SOVEREIGNTY_COMPROMISED = "SOVEREIGNTY_COMPROMISED"
    SOVEREIGNTY_RESTORED = "SOVEREIGNTY_RESTORED"
    SOVEREIGNTY_ACHIEVED = "SOVEREIGNTY_ACHIEVED"
    SOVEREIGNTY_PERFECT = "SOVEREIGNTY_PERFECT"
    
    # === GUARDIAN ===
    GUARDIAN_BLOCKED_COMMIT = "GUARDIAN_BLOCKED_COMMIT"
    GUARDIAN_VIOLATION = "GUARDIAN_VIOLATION"
    GUARDIAN_CLEAN = "GUARDIAN_CLEAN"
    
    # === HEALING ===
    HEALING_CYCLE_STARTED = "HEALING_CYCLE_STARTED"
    HEALING_ACTION_APPLIED = "HEALING_ACTION_APPLIED"
    HEALING_ACTION_FAILED = "HEALING_ACTION_FAILED"
    HEALING_TRANSACTION_START = "HEALING_TRANSACTION_START"
    HEALING_TRANSACTION_COMMIT = "HEALING_TRANSACTION_COMMIT"
    HEALING_TRANSACTION_ROLLBACK = "HEALING_TRANSACTION_ROLLBACK"
    HEALING_FIX_APPLIED = "HEALING_FIX_APPLIED"
    HEALING_FIX_REVERTED = "HEALING_FIX_REVERTED"
    HEALING_CYCLE_COMPLETE = "HEALING_CYCLE_COMPLETE"
    
    # === REASONING ===
    REASONING_START = "REASONING_START"
    REASONING_END = "REASONING_END"
    REASONING_STEP = "REASONING_STEP"
    HYPOTHESIS_FORMED = "HYPOTHESIS_FORMED"
    HYPOTHESIS_VALIDATED = "HYPOTHESIS_VALIDATED"
    HYPOTHESIS_REJECTED = "HYPOTHESIS_REJECTED"
    DARK_REASONING_DETECTED = "DARK_REASONING_DETECTED"
    
    # === VIOLATION ===
    VIOLATION_DETECTED = "VIOLATION_DETECTED"
    SSOT_INLINE_MODEL = "SSOT_INLINE_MODEL"
    SSOT_RAW_PROMPT = "SSOT_RAW_PROMPT"
    SSOT_HARDCODED_CONFIG = "SSOT_HARDCODED_CONFIG"
    SSOT_UNDERSCORE_FIELD = "SSOT_UNDERSCORE_FIELD"
    DDD_VIOLATION = "DDD_VIOLATION"
    DDD_AGGREGATE_BYPASS = "DDD_AGGREGATE_BYPASS"
    DDD_UBIQUITOUS_LANGUAGE_MISSING = "DDD_UBIQUITOUS_LANGUAGE_MISSING"
    LAYER_CROSS_IMPORT = "LAYER_CROSS_IMPORT"
    
    # === SYSTEM ===
    SYSTEM_BOOT = "SYSTEM_BOOT"
    CONSTITUTION_LOAD = "CONSTITUTION_LOAD"
    
    # === MCP ===
    MCP_INTEGRATION_STARTED = "MCP_INTEGRATION_STARTED"
    MCP_INTEGRATION_SUCCESS = "MCP_INTEGRATION_SUCCESS"
    MCP_INTEGRATION_FAILED = "MCP_INTEGRATION_FAILED"

# Backward compatibility alias

# === CATEGORY MAPPING FOR ANALYTICS ===
sovereign_event_categories: Dict[str, List[SovereignEventType]] = {
    "GOVERNANCE": [
        SovereignEventType.AUDIT_STARTED, 
        SovereignEventType.AUDIT_COMPLETED,
        SovereignEventType.SOVEREIGNTY_COMPROMISED, 
        SovereignEventType.SOVEREIGNTY_RESTORED,
        SovereignEventType.SOVEREIGNTY_ACHIEVED,
        SovereignEventType.SOVEREIGNTY_PERFECT
    ],
    "GUARDIAN": [
        SovereignEventType.GUARDIAN_BLOCKED_COMMIT, 
        SovereignEventType.GUARDIAN_VIOLATION,
        SovereignEventType.GUARDIAN_CLEAN
    ],
    "HEALING": [
        SovereignEventType.HEALING_CYCLE_STARTED,
        SovereignEventType.HEALING_ACTION_APPLIED, 
        SovereignEventType.HEALING_ACTION_FAILED,
        SovereignEventType.HEALING_TRANSACTION_START, 
        SovereignEventType.HEALING_TRANSACTION_COMMIT,
        SovereignEventType.HEALING_TRANSACTION_ROLLBACK,
        SovereignEventType.HEALING_FIX_APPLIED,
        SovereignEventType.HEALING_FIX_REVERTED,
        SovereignEventType.HEALING_CYCLE_COMPLETE
    ],
    "REASONING": [
        SovereignEventType.REASONING_START, 
        SovereignEventType.REASONING_END,
        SovereignEventType.REASONING_STEP, 
        SovereignEventType.HYPOTHESIS_FORMED,
        SovereignEventType.HYPOTHESIS_VALIDATED, 
        SovereignEventType.HYPOTHESIS_REJECTED,
        SovereignEventType.DARK_REASONING_DETECTED
    ],
    "VIOLATION": [
        SovereignEventType.VIOLATION_DETECTED, 
        SovereignEventType.SSOT_INLINE_MODEL,
        SovereignEventType.SSOT_RAW_PROMPT, 
        SovereignEventType.SSOT_HARDCODED_CONFIG,
        SovereignEventType.SSOT_UNDERSCORE_FIELD, 
        SovereignEventType.DDD_VIOLATION,
        SovereignEventType.DDD_AGGREGATE_BYPASS, 
        SovereignEventType.DDD_UBIQUITOUS_LANGUAGE_MISSING,
        SovereignEventType.LAYER_CROSS_IMPORT
    ],
    "SYSTEM": [
        SovereignEventType.SYSTEM_BOOT,
        SovereignEventType.CONSTITUTION_LOAD
    ],
    "MCP": [
        SovereignEventType.MCP_INTEGRATION_STARTED,
        SovereignEventType.MCP_INTEGRATION_SUCCESS,
        SovereignEventType.MCP_INTEGRATION_FAILED
    ]
}

# Public exports
__all__ = [
    # Snake case (canonical)
    "SovereignSeverity",
    "SovereignEventType", 
    "sovereign_severities",
    "severity_log_levels",
    "sovereign_event_categories",
    # PascalCase aliases (backward compat)
    "SovereignSeverity",
    "SovereignEventType",
]
