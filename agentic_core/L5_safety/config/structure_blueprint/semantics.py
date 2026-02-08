"""
Semantics Module - COLD PATH (Semantic Analysis Registries)

This module contains semantic analysis data: naming conventions, keyword
affinities, AST domain terms, and territory keywords.

Loaded lazily on first access.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final

# ============================================================================
# NAMING CONVENTIONS
# ============================================================================

NAMING_CONVENTIONS: Final[Mapping[str, Mapping[str, Any]]] = {
    "agent": {
        "pattern": r"^[A-Z][a-zA-Z0-9]*Agent\.py$",
        "description": "PascalCase ending with 'Agent'",
        "examples": ["HealerAgent.py", "NamingAgent.py", "CodeDeduplicationAgent.py"],
        "anti_examples": ["HealerAgent.py", "NamingAgent.py", "Healer.py"],
        "extensions": [".py"],
        "min_words": 2,
        "max_words": 4,
    },
    "script": {
        "pattern": r"^[a-z][a-z0-9_]*_script\.py$",
        "description": "snake_case ending with '_script.py'",
        "examples": ["db_migration_script.py", "daily_cleanup_script.py", "audit_status_script.py"],
        "anti_examples": ["main.py", "utils.py", "script.py", "run.py"],
        "extensions": [".py"],
    },
    "utility": {
        "pattern": r"^[a-z][a-z0-9_]*_util\.py$",
        "description": "snake_case ending with '_util.py'",
        "examples": ["file_util.py", "string_util.py", "path_util.py"],
        "anti_examples": ["utils.py", "helpers.py", "common.py"],
        "extensions": [".py"],
    },
    "config": {
        "pattern": r"^[a-z][a-z0-9_]*_config\.py$",
        "description": "snake_case ending with '_config.py'",
        "examples": ["app_config.py", "db_config.py", "logging_config.py"],
        "anti_examples": ["config.py", "settings.py", "constants.py"],
        "extensions": [".py"],
    },
    "types": {
        "pattern": r"^[a-z][a-z0-9_]*_types\.py$",
        "description": "snake_case ending with '_types.py'",
        "examples": ["agent_types.py", "message_types.py", "state_types.py"],
        "anti_examples": ["types.py", "models.py", "schemas.py"],
        "extensions": [".py"],
    },
    "validator": {
        "pattern": r"^[a-z][a-z0-9_]*_validator\.py$",
        "description": "snake_case ending with '_validator.py'",
        "examples": ["input_validator.py", "schema_validator.py", "path_validator.py"],
        "anti_examples": ["validator.py", "validate.py", "check.py"],
        "extensions": [".py"],
    },
    "mixin": {
        "pattern": r"^[a-z][a-z0-9_]*_mixin\.py$",
        "description": "snake_case ending with '_mixin.py'",
        "examples": ["logging_mixin.py", "caching_mixin.py", "retry_mixin.py"],
        "anti_examples": ["mixin.py", "mixins.py", "base.py"],
        "extensions": [".py"],
    },
}


# ============================================================================
# LAYER KEYWORD AFFINITY
# ============================================================================

LAYER_KEYWORD_AFFINITY: Final[Mapping[str, Sequence[str]]] = {
    "L0_maintenance": [
        "cleanup",
        "maintenance",
        "bootstrap",
        "heal",
        "repair",
        "reconcile",
        "ssot",
        "folder cleanup",
        "hygiene",
        "migration",
        "discovery",
        "manifest",
        "sync",
        "gospel",
    ],
    "L1_cognition": [
        "thought",
        "intent",
        "planning",
        "cognition",
        "reasoning",
        "decision",
        "analysis",
        "understanding",
    ],
    "L2_execution": [
        "tool",
        "mcp",
        "action",
        "execute",
        "invoke",
        "run",
        "embed",
        "search",
        "index",
    ],
    "L3_orchestration": [
        "workflow",
        "orchestrat",
        "meta-learn",
        "pipeline",
        "coordinate",
        "schedule",
        "batch",
        "tier",
    ],
    "L4_state": [
        "state",
        "memory",
        "ledger",
        "cache",
        "redis",
        "pinecone",
        "persist",
        "store",
        "context",
    ],
    "L5_safety": [
        "safety",
        "guard",
        "valid",
        "enforce",
        "protect",
        "sentinel",
        "threat",
        "adversarial",
        "compliance",
        "audit",
        "inspect",
    ],
    "L6_observability": [
        "observ",
        "telemetry",
        "monitor",
        "metric",
        "dashboard",
        "report",
        "log",
        "trace",
        "health",
    ],
}


# ============================================================================
# AST DOMAIN TERMS
# ============================================================================

APP_RG_AST_TERMS: Final[frozenset[str]] = frozenset(
    {
        "resume",
        "cv",
        "skill",
        "experience",
        "education",
        "section",
        "job",
        "outreach",
        "dispatch",
        "generation",
        "formatter",
        "parser",
        "header",
        "summary",
        "achievement",
        "certification",
    },
)

APP_LIC_AST_TERMS: Final[frozenset[str]] = frozenset(
    {
        "linkedin",
        "lic",
        "profile",
        "connection",
        "invite",
        "message",
        "connect",
        "campaign",
        "cadence",
        "note",
        "scrap",
        "navigate",
        "browser",
    },
)

APP_RG_VARIABLE_TERMS: Final[frozenset[str]] = frozenset(
    {
        "resume",
        "cv",
        "skill",
        "experience",
        "education",
        "section",
        "job",
        "header",
        "summary",
        "achievement",
        "certification",
        "applicant",
        "candidate",
        "position",
        "role",
    },
)

APP_LIC_VARIABLE_TERMS: Final[frozenset[str]] = frozenset(
    {
        "profile",
        "linkedin",
        "connection",
        "invite",
        "message",
        "note",
        "campaign",
        "cadence",
        "lead",
        "contact",
        "person",
        "url",
    },
)

APP_RG_STRING_TERMS: Final[frozenset[str]] = frozenset(
    {
        "resume",
        "cv",
        "skill",
        "experience",
        "education",
        "job posting",
        "outreach",
        "candidate",
        "applicant",
    },
)

APP_LIC_STRING_TERMS: Final[frozenset[str]] = frozenset(
    {
        "linkedin",
        "profile",
        "connection",
        "invite",
        "campaign",
        "cadence",
    },
)


# ============================================================================
# AST SCORING WEIGHTS
# ============================================================================

VARIABLE_HIT_WEIGHT: Final[float] = 0.5
STRING_HIT_WEIGHT: Final[float] = 0.25
AST_DOMAIN_HIT_THRESHOLD: Final[float] = 2.0

FORBIDDEN_APP_MODULES: Final[frozenset[str]] = frozenset({"apps_rg", "apps_lic"})


# ============================================================================
# POLYGLOT DOMAIN SIGNALS
# ============================================================================

POLYGLOT_DOMAIN_SIGNALS: Final[Mapping[str, Mapping[str, Any]]] = {
    "apps_rg": {
        "signal_keywords": APP_RG_STRING_TERMS,
        "match_threshold": 2,
        "extensions": [".yaml", ".yml", ".json"],
    },
    "apps_lic": {
        "signal_keywords": APP_LIC_STRING_TERMS,
        "match_threshold": 2,
        "extensions": [".yaml", ".yml", ".json"],
    },
}


# ============================================================================
# CORE TERRITORY KEYWORDS
# ============================================================================

CORE_TERRITORY_KEYWORDS: Final[Mapping[str, Mapping[str, frozenset[str]]]] = {
    "L1_cognition/thought_engine": {
        "primary": frozenset({"think", "reason", "plan", "decompose", "critique", "reflect"}),
    },
    "L2_execution/engine": {
        "primary": frozenset({"tool", "execute", "call", "registry", "runner"}),
    },
    "L2_execution/mcp": {
        "primary": frozenset({"mcp", "client", "fetch", "protocol"}),
    },
    "L3_orchestration/engine": {
        "primary": frozenset({"orchestrate", "workflow", "route", "dispatch", "coordinate", "flow"}),
    },
    "L4_state/memory": {
        "primary": frozenset({"state", "context", "checkpoint", "persist"}),
    },
    "L4_state/ledger": {
        "primary": frozenset({"ledger", "history", "record", "transaction"}),
    },
    "L5_safety/validators": {
        "primary": frozenset({"validate", "enforce", "check", "guard", "policy", "heal"}),
    },
    "L5_safety/guardrails": {
        "primary": frozenset({"guardrail", "safety", "membrane", "airlock", "pii"}),
    },
    "L5_safety/gravity": {
        "primary": frozenset({"gravity", "import", "dependency", "layer"}),
    },
    "config/core": {
        "primary": frozenset({"blueprint", "registry", "sovereign", "canon", "config", "settings"}),
    },
    "schemas/models": {
        "primary": frozenset({"schema", "model", "type", "message"}),
    },
    "prompt_governance/L3_core": {
        "primary": frozenset({"render", "registry", "assemble", "govern"}),
    },
    "prompt_governance/L3_templates": {
        "primary": frozenset({"template", "prompt", "persona", "instructional"}),
    },
    "prompt_governance/L3_security": {
        "primary": frozenset({"security", "injection", "pii", "compliance"}),
    },
    "prompt_governance/L3_integrity": {
        "primary": frozenset({"validate", "optimize", "test", "quality"}),
    },
    "prompt_governance/L3_utilities": {
        "primary": frozenset({"script", "middleware", "monitor", "audit"}),
    },
    "observability": {
        "primary": frozenset({"metric", "trace", "telemetry", "log", "compliance"}),
    },
    "utils": {
        "primary": frozenset({"util", "helper", "extension", "wrapper"}),
    },
}


# ============================================================================
# LAYER FORBIDDEN IMPORTS
# ============================================================================

LAYER_FORBIDDEN_IMPORTS: Final[Mapping[str, frozenset[str]]] = {
    "L1_cognition": frozenset({"L2_execution", "L3_orchestration", "L4_state", "L5_safety"}),
    "L2_execution": frozenset({"L1_cognition", "L3_orchestration", "L5_safety"}),
    "L3_orchestration": frozenset({"L5_safety"}),
    "apps_shared": frozenset({"apps_rg", "apps_lic"}),
    "apps_rg": frozenset({"apps_lic"}),
    "apps_lic": frozenset({"apps_rg"}),
}


# ============================================================================
# TERRITORY ALIGNMENT THRESHOLDS
# ============================================================================

TERRITORY_MISMATCH_THRESHOLD: Final[float] = 2.5
MIN_ALIGNMENT_SCORE: Final[float] = 1.5


# ============================================================================
# HEALING DEFAULTS
# ============================================================================

DEFAULT_APP_HEALING_TARGET: Final[str] = "apps_rg/engines"
DEFAULT_CORE_HEALING_TERRITORY: Final[str] = "L2_execution/engine"


# ============================================================================
# VIOLATION SEVERITY
# ============================================================================

VIOLATION_SEVERITY: Final[Mapping[str, int]] = {
    "GRAVITY VIOLATION": 10,
    "AST DOMAIN VIOLATION": 9,
    "TERRITORY MISMATCH VIOLATION": 8,
    "APP-SPECIFIC IN CORE VIOLATION": 7,
    "TERRITORY ALIGNMENT WEAK": 5,
}


# ============================================================================
# APP DOMAIN PREFIXES
# ============================================================================

APP_DOMAIN_PREFIXES: Final[Sequence[str]] = [
    "Lic",
    "Campaign",
    "Outreach",
]
