"""
Sovereign Event Contracts - SSOT for all event types and severity levels.
Modularized from core_contracts.py for DDD bounded context isolation.
"""
import logging
from enum import Enum
from typing import List, Dict

# === SOVEREIGN SEVERITY LEVELS ===
class sovereign_severity(str, Enum):
    """Canonical SSOT for event severity levels with observability log mapping."""
    
    CRITICAL = "CRITICAL"
    """Immediate threat to sovereignty — system may be compromised"""
    
    ERROR = "ERROR"
    """Healing required — constitutional violation detected"""
    
    WARNING = "WARNING"
    """Degradation risk — attention needed but not blocking"""
    
    INFO = "INFO"
    """Normal sovereign operation — audit trail"""
    
    DEBUG = "DEBUG"
    """Detailed internal diagnostics — verbose"""

# Backward compatibility alias
SovereignSeverity = sovereign_severity

# Registry for validation and observability mapping
sovereign_severities = {e.value for e in sovereign_severity}
severity_log_levels = {
    sovereign_severity.CRITICAL: logging.CRITICAL,
    sovereign_severity.ERROR: logging.ERROR,
    sovereign_severity.WARNING: logging.WARNING,
    sovereign_severity.INFO: logging.INFO,
    sovereign_severity.DEBUG: logging.DEBUG,
}

# === SOVEREIGN EVENT TYPE REGISTRY ===
class sovereign_event_type(str, Enum):
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
SovereignEventType = sovereign_event_type

# === CATEGORY MAPPING FOR ANALYTICS ===
sovereign_event_categories: Dict[str, List[sovereign_event_type]] = {
    "GOVERNANCE": [
        sovereign_event_type.AUDIT_STARTED, 
        sovereign_event_type.AUDIT_COMPLETED,
        sovereign_event_type.SOVEREIGNTY_COMPROMISED, 
        sovereign_event_type.SOVEREIGNTY_RESTORED,
        sovereign_event_type.SOVEREIGNTY_ACHIEVED,
        sovereign_event_type.SOVEREIGNTY_PERFECT
    ],
    "GUARDIAN": [
        sovereign_event_type.GUARDIAN_BLOCKED_COMMIT, 
        sovereign_event_type.GUARDIAN_VIOLATION,
        sovereign_event_type.GUARDIAN_CLEAN
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
        sovereign_event_type.HEALING_CYCLE_COMPLETE
    ],
    "REASONING": [
        sovereign_event_type.REASONING_START, 
        sovereign_event_type.REASONING_END,
        sovereign_event_type.REASONING_STEP, 
        sovereign_event_type.HYPOTHESIS_FORMED,
        sovereign_event_type.HYPOTHESIS_VALIDATED, 
        sovereign_event_type.HYPOTHESIS_REJECTED,
        sovereign_event_type.DARK_REASONING_DETECTED
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
        sovereign_event_type.LAYER_CROSS_IMPORT
    ],
    "SYSTEM": [
        sovereign_event_type.SYSTEM_BOOT,
        sovereign_event_type.CONSTITUTION_LOAD
    ],
    "MCP": [
        sovereign_event_type.MCP_INTEGRATION_STARTED,
        sovereign_event_type.MCP_INTEGRATION_SUCCESS,
        sovereign_event_type.MCP_INTEGRATION_FAILED
    ]
}

# Public exports
__all__ = [
    # Snake case (canonical)
    "sovereign_severity",
    "sovereign_event_type", 
    "sovereign_severities",
    "severity_log_levels",
    "sovereign_event_categories",
    # PascalCase aliases (backward compat)
    "SovereignSeverity",
    "SovereignEventType",
]
