"""
Classification Module - COLD PATH (Pattern Matching)

This module contains classification patterns, suffix mappings, and folder
purity rules. Regex patterns are stored as strings and compiled lazily.

Loaded lazily on first access.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from functools import lru_cache
from pathlib import Path
from typing import Final

# ============================================================================
# CLASSIFICATION SUFFIX PATTERNS (Strings - Compiled Lazily)
# ============================================================================

CLASSIFICATION_SUFFIX_PATTERNS: Final[Mapping[str, str]] = {
    r"_agent\.py$": "AGENT",
    r"_types\.py$": "TYPES",
    r"_config\.py$": "CONFIG",
    r"_validator\.py$": "VALIDATOR",
    r"_util\.py$": "UTILITY",
    r"_mixin\.py$": "MIXIN",
    r"_strategy\.py$": "STRATEGY",
    r"_adapter\.py$": "ADAPTER",
    r"_protocol\.py$": "PROTOCOL",
    r"Agent\.py$": "AGENT",
    r"Strategy\.py$": "STRATEGY",
    r"Adapter\.py$": "ADAPTER",
    r"I[A-Z].*Protocol\.py$": "PROTOCOL",
}


# ============================================================================
# COMPOUND SUFFIX CONFLICTS
# ============================================================================

COMPOUND_SUFFIX_CONFLICTS: Final[Sequence[tuple[str, str, str, str]]] = [
    (r"_agent_types$", "AGENT", "TYPES", "code_detector_agent_types.py"),
    (r"_agent_config$", "AGENT", "CONFIG", "security_level_agent_config.py"),
    (r"_agent_validator$", "AGENT", "VALIDATOR", "routing_decision_agent_validator.py"),
    (r"_agent_util$", "AGENT", "UTILITY", "extract_pattern_agent_util.py"),
    (r"Agent_types$", "AGENT", "TYPES", "CodeDetectorAgent_types.py"),
    (r"Agent_config$", "AGENT", "CONFIG", "SomeAgent_config.py"),
    (r"_engine_types$", "ENGINE", "TYPES", "safety_engine_types.py"),
    (r"_engine_validator$", "ENGINE", "VALIDATOR", "consensus_engine_validator.py"),
    (r"_engine_config$", "ENGINE", "CONFIG", "engine_config.py"),
    (r"_guardrail_types$", "GUARDRAIL", "TYPES", "mcp_security_guardrail_types.py"),
    (r"_guardrail_mixin$", "GUARDRAIL", "MIXIN", "cost_guardrail_mixin.py"),
    (r"_guardrail_config$", "GUARDRAIL", "CONFIG", "guardrail_config.py"),
    (r"_manager_types$", "MANAGER", "TYPES", "resource_manager_types.py"),
    (r"_manager_config$", "MANAGER", "CONFIG", "sovereign_manager_config.py"),
    (r"_manager_validator$", "MANAGER", "VALIDATOR", "context_manager_validator.py"),
    (r"_strategy_types$", "STRATEGY", "TYPES", "context_pruning_strategy_types.py"),
    (r"_strategy_config$", "STRATEGY", "CONFIG", "mcpservermode_strategy_config.py"),
    (r"_strategy_mixin$", "STRATEGY", "MIXIN", "healing_strategy_mixin.py"),
    (r"_strategy_validator$", "STRATEGY", "VALIDATOR", "reasoningnode_strategy_validator.py"),
    (r"_validator_types$", "VALIDATOR", "TYPES", "code_validator_types.py"),
    (r"_validator_util$", "VALIDATOR", "UTILITY", "check_sovereign_base_validator_util.py"),
    (r"_scanner_types$", "SCANNER", "TYPES", "credential_scanner_types.py"),
    (r"_scanner_util$", "SCANNER", "UTILITY", "sovereign_scanner_util.py"),
    (r"_protocol_types$", "PROTOCOL", "TYPES", "healer_protocol_types.py"),
    (r"_protocol_config$", "PROTOCOL", "CONFIG", "detection_protocol_config.py"),
    (r"_protocol_guardrail$", "PROTOCOL", "GUARDRAIL", "airlock_protocol_guardrail.py"),
    (r"_suite_types$", "SUITE", "TYPES", "security_validation_suite_types.py"),
    (r"_factory_config$", "FACTORY", "CONFIG", "gateway_factory_config.py"),
    (r"_factory_util$", "FACTORY", "UTILITY", "component_factory_util.py"),
    (r"_orchestrator_types$", "ORCHESTRATOR", "TYPES", "recursive_orchestrator_types.py"),
    (r"_shield_validator$", "SHIELD", "VALIDATOR", "governance_shield_validator.py"),
    (r"_sanitizer_util$", "SANITIZER", "UTILITY", "telemetry_sanitizer_util.py"),
    (r"_guard_util$", "GUARD", "UTILITY", "scan_guard_util.py"),
    (r"_guard_mixin$", "GUARD", "MIXIN", "cost_guard_mixin.py"),
    (r"_detector_types$", "DETECTOR", "TYPES", "code_detector_types.py"),
    (r"_detector_config$", "DETECTOR", "CONFIG", "gravity_leak_detector_config.py"),
    (r"_enforcer_types$", "ENFORCER", "TYPES", "code_enforcer_types.py"),
    (r"_enforcer_util$", "ENFORCER", "UTILITY", "root_hygiene_enforcer_util.py"),
    (r"_config_types$", "CONFIG", "TYPES", "blueprint_config_types.py"),
    (r"_config_util$", "CONFIG", "UTILITY", "sync_mcp_config_util.py"),
    (r"_config_detector$", "CONFIG", "DETECTOR", "magic_config_detector.py"),
    (r"_adapter_types$", "ADAPTER", "TYPES", "open_telemetry_tracing_adapter_types.py"),
    (r"_adapter_config$", "ADAPTER", "CONFIG", "storage_adapter_config.py"),
    (r"_adapter_util$", "ADAPTER", "UTILITY", "mcp_adapter_util.py"),
    (r"Adapter_types$", "ADAPTER", "TYPES", "SomeAdapter_types.py"),
    (r"_mixin_agent_mixin$", "MIXIN", "AGENT", "autonomy_mixin_agent_mixin.py"),
    (r"_mixin_agent$", "MIXIN", "AGENT", "some_mixin_agent.py"),
    (r"_agent_mixin$", "AGENT", "MIXIN", "feature_flagged_agent_mixin.py"),
    (r"_mixin_types$", "MIXIN", "TYPES", "healer_mixin_types.py"),
    (r"_mixin_config$", "MIXIN", "CONFIG", "autonomy_mixin_config.py"),
    (r"_mixin_util$", "MIXIN", "UTILITY", "healer_mixin_util.py"),
    (r"_mixin_validator$", "MIXIN", "VALIDATOR", "agent_mixin_validator.py"),
]


# ============================================================================
# SUFFIX TO FOLDER MAPPING
# ============================================================================

SUFFIX_TO_FOLDER: Final[Mapping[str, str]] = {
    "_config.py": "config",
    "_types.py": "types",
    "_protocol.py": "types",
    "_validator.py": "validators",
    "_util.py": "utils",
    "_mixin.py": "GLOBAL_MIXINS",
    "Protocol.py": "GLOBAL_INTERFACES",
    "Agent.py": "reasoning",
    "Inspector.py": "reasoning",
    "Healer.py": "reasoning",
    "Guardian.py": "reasoning",
    "Orchestrator.py": "reasoning",
    "Monitor.py": "enforcement",
    "Strategy.py": "enforcement",
    "_guardrail.py": "enforcement",
    "_strategy.py": "enforcement",
}


# ============================================================================
# FILETYPE TO FOLDER MAPPING (AST-Based)
# ============================================================================

FILETYPE_TO_FOLDER: Final[Mapping[str, str]] = {
    "AGENT": "reasoning",
    "ORCHESTRATOR": "reasoning",
    "CONFIG": "config",
    "TYPES": "types",
    "PROTOCOL": "types",
    "VALIDATOR": "validators",
    "UTILITY": "utils",
    "MIXIN": "GLOBAL_MIXINS",
    "SCRIPT": "scripts",
    "FACTORY": "enforcement",
    "STRATEGY": "enforcement",
    "EXCEPTION": "types",
    "ENGINE": "reasoning",
    "GATEWAY": "enforcement",
    "SERVICE": "utils",
}


# ============================================================================
# FOLDER PURITY RULES (Strings - Compiled Lazily)
# ============================================================================
#
# Canonical summary (documentation only): patterns below are the source of truth.
#
# A) FOLDER_PURITY_RULES (allowed patterns per folder)
# ├── reasoning:       .*Agent\.py$ | .*Executor\.py$ | .*Orchestrator\.py$ | .*Inspector\.py$ | .*Healer\.py$ | .*Guardian\.py$
# ├── validators:      .*_validator\.py$ | .*Validator\.py$
# ├── config:          .*_config\.(py|yaml|json)$
# ├── types:           .*_types\.py$ | .*_protocol\.py$ | I[A-Z].*Protocol\.py$ | .*Error\.py$ | .*Exception\.py$
# ├── utils:           .*_util\.py$ | .*_helper\.py$
# ├── scripts:         ^[a-z][a-z0-9_]*\.py$
# ├── enforcement:
# │   ├── .*_(guardrail|enforcer|gate|strategy)\.py$
# │   └── .*Strategy\.py$ | .*Adapter\.py$ | .*Monitor\.py$ | .*Factory\.py$ | .*Gateway\.py$
# ├── dashboards:      .*\.(html|js|css|yaml|json|py)$
# ├── engines:         .*_(engine|executor|task|impl|router|service|client|node|cache|planner|analyzer|mapper|embedder|scanner|core|system|composer|scorer|detector|builder|normalizer)\.py$
# └── tools:           .*_(tool|impl|client)\.py$
#
# A1) GLOBAL FOLDER PURITY (agentic_core root-level folders)
# ├── base_agents:     ^L[0-9][A-Za-z]+Base\.py$ | ^SovereignBaseAgent\.py$ | ^LightweightBase\.py$
# ├── mixins:          ^[a-z0-9_]+_mixin\.py$
# ├── interfaces:      ^I[A-Z][A-Za-z0-9]+\.py$
# └── agent_configs:   ^[a-z0-9_]+_config\.py$ | ^[a-z0-9_]+\.yaml$ | ^[a-z0-9_]+\.json$
#
# A2) LAYER-SPECIFIC FOLDER PURITY (within L* folders)
# ├── healers:           .*_healer\.py$ | .*Healer\.py$
# ├── caching:           .*_cache\.py$ | .*_cacher\.py$ | .*Cache\.py$
# ├── memory:            .*_memory\.py$ | .*_store\.py$ | .*Memory\.py$
# ├── security:          .*_security\.py$ | .*Security\.py$ | .*_guard\.py$
# ├── golden_evaluation: .*_eval\.py$ | .*_evaluation\.py$ | .*Evaluator\.py$
# ├── exceptions:        .*Error\.py$ | .*Exception\.py$ | .*_exceptions\.py$
# └── core_kernel:       .*_kernel\.py$ | .*_core\.py$
#
# B) INFRASTRUCTURE_PROFILES (permissive): runtime, meta_control, policy => .*\.py$
# C) FOLDER_ALIASES: knowledge -> reasoning; validation -> validators
# D) NO_ROOT_FILES_FOLDERS: security (only approved subfolders; no root files except __init__.py)
#
# E) FOLDER_PURITY_DISALLOWED (forbidden-in-folder patterns)
# ├── engines: forbids Agent/Orchestrator/Strategy/Validator/types/util/config patterns
# └── tools:   forbids Agent/Strategy/Validator/types/util/config patterns
#
# F) FORBIDDEN_COMPOUND_PATTERNS: *_types_config.py, *_validator_util.py, *_types_validator.py, *_config_util.py
#
# NOTE: L5_ENFORCEMENT_ALLOWED_SUFFIXES is governance (suffix allowlist), not folder purity.

FOLDER_PURITY_RULES: Final[Mapping[str, Sequence[str]]] = {
    "reasoning": [
        r".*Agent\.py$",
        r".*Executor\.py$",
        r".*Orchestrator\.py$",
        r".*Inspector\.py$",
        r".*Healer\.py$",
        r".*Guardian\.py$",
    ],
    "validators": [
        r".*_validator\.py$",
        r".*Validator\.py$",
    ],
    "config": [
        r".*_config\.py$",
        r".*_config\.yaml$",
        r".*_config\.json$",
    ],
    "types": [
        r".*_types\.py$",
        r".*_protocol\.py$",
        r"I[A-Z].*Protocol\.py$",
        r".*Error\.py$",
        r".*Exception\.py$",
    ],
    "utils": [
        r".*_util\.py$",
        r".*_helper\.py$",
    ],
    "scripts": [
        r"^[a-z][a-z0-9_]*\.py$",
    ],
    "enforcement": [
        r".*_guardrail\.py$",
        r".*_enforcer\.py$",
        r".*_gate\.py$",
        r".*_strategy\.py$",
        r".*Strategy\.py$",
        r".*Adapter\.py$",
        r".*Monitor\.py$",
        r".*Factory\.py$",
        r".*Gateway\.py$",
    ],
    "dashboards": [
        r".*\.html$",
        r".*\.js$",
        r".*\.css$",
        r".*\.yaml$",
        r".*\.json$",
        r".*\.py$",
    ],
    "engines": [
        r".*_engine\.py$",
        r".*_executor\.py$",
        r".*_task\.py$",
        r".*_impl\.py$",
        r".*_router\.py$",
        r".*_service\.py$",
        r".*_client\.py$",
        r".*_node\.py$",
        r".*_cache\.py$",
        r".*_planner\.py$",
        r".*_analyzer\.py$",
        r".*_mapper\.py$",
        r".*_embedder\.py$",
        r".*_scanner\.py$",
        r".*_core\.py$",
        r".*_system\.py$",
        r".*_composer\.py$",
        r".*_scorer\.py$",
        r".*_detector\.py$",
        r".*_builder\.py$",
        r".*_normalizer\.py$",
    ],
    "tools": [
        r".*_tool\.py$",
        r".*_impl\.py$",
        r".*_client\.py$",
    ],
    # ========================================================================
    # GLOBAL FOLDER PURITY RULES (agentic_core root-level folders)
    # ========================================================================
    "base_agents": [
        r"^L[0-9][A-Za-z]+Base\.py$",
        r"^SovereignBaseAgent\.py$",
        r"^LightweightBase\.py$",
    ],
    "mixins": [
        r"^[a-z0-9_]+_mixin\.py$",
    ],
    "interfaces": [
        r"^I[A-Z][A-Za-z0-9]+\.py$",
    ],
    "agent_configs": [
        r"^[a-z0-9_]+_config\.py$",
        r"^[a-z0-9_]+\.yaml$",
        r"^[a-z0-9_]+\.json$",
    ],
    # ========================================================================
    # LAYER-SPECIFIC FOLDER PURITY RULES (L* subfolders)
    # ========================================================================
    "healers": [
        r".*_healer\.py$",
        r".*Healer\.py$",
    ],
    "caching": [
        r".*_cache\.py$",
        r".*_cacher\.py$",
        r".*Cache\.py$",
    ],
    "memory": [
        r".*_memory\.py$",
        r".*_store\.py$",
        r".*Memory\.py$",
    ],
    "security": [
        r".*_security\.py$",
        r".*Security\.py$",
        r".*_guard\.py$",
    ],
    "golden_evaluation": [
        r".*_eval\.py$",
        r".*_evaluation\.py$",
        r".*Evaluator\.py$",
    ],
    "exceptions": [
        r".*Error\.py$",
        r".*Exception\.py$",
        r".*_exceptions\.py$",
    ],
    "core_kernel": [
        r".*_kernel\.py$",
        r".*_core\.py$",
    ],
}


# ============================================================================
# INFRASTRUCTURE PROFILES (folders exempt from strict purity but still tracked)
# These folders have permissive patterns - any .py file is allowed
# ============================================================================

INFRASTRUCTURE_PROFILES: Final[Mapping[str, Sequence[str]]] = {
    "runtime": [r".*\.py$"],
    "meta_control": [r".*\.py$"],
    "policy": [r".*\.py$"],
}


# ============================================================================
# FOLDER ALIASES (folders that inherit rules from another folder)
# ============================================================================

FOLDER_ALIASES: Final[Mapping[str, str]] = {
    # knowledge/reasoning aliases to reasoning (PascalCase agents allowed)
    "knowledge": "reasoning",
    # prompt_governance/validation aligns to validators treatment
    "validation": "validators",
    # runtime/engine maps to engines rules
    "engine": "engines",
}


# ============================================================================
# NO ROOT FILES FOLDERS (governed folders that forbid direct root files)
# Only __init__.py allowed at root; all other files must be in subfolders
# ============================================================================

NO_ROOT_FILES_FOLDERS: Final[frozenset[str]] = frozenset({
    "security",  # prompt_governance/security - utils must be in security/utils/
    "prompt_governance",  # prompt_governance root - files must be in approved subfolders
})

# Approved subfolders for NO_ROOT_FILES_FOLDERS
APPROVED_SUBFOLDERS: Final[Mapping[str, frozenset[str]]] = {
    "security": frozenset({"utils", "detectors", "schemas", "validators", "adversarial"}),
    "prompt_governance": frozenset({"core", "meta_prompts", "optimization", "registry", "scripts", "security", "templates", "utils", "validation"}),
}


# ============================================================================
# FOLDER PURITY DISALLOWED RULES (files that MUST NOT be in these folders)
# ============================================================================

FOLDER_PURITY_DISALLOWED: Final[Mapping[str, Sequence[str]]] = {
    "engines": [
        r".*Agent\.py$",
        r".*Orchestrator\.py$",
        r".*Strategy\.py$",
        r".*_strategy\.py$",
        r".*Validator\.py$",
        r".*_validator\.py$",
        r".*_types\.py$",
        r".*_util\.py$",
        r".*_config\.py$",
    ],
    "tools": [
        r".*Agent\.py$",
        r".*Validator\.py$",
        r".*_validator\.py$",
        r".*_types\.py$",
        r".*_util\.py$",
        r".*_config\.py$",
        r".*Strategy\.py$",
        r".*_strategy\.py$",
    ],
}


# ============================================================================
# KNOWN ARCHITECTURAL SUFFIXES
# ============================================================================

KNOWN_ARCHITECTURAL_SUFFIXES: Final[Sequence[str]] = [
    "_types",
    "_config",
    "_validator",
    "_util",
    "_mixin",
    "_protocol",
    "_strategy",
    "_adapter",
    "_factory",
    "_orchestrator",
    "_engine",
    "_gateway",
    "_sensor",
]

FORBIDDEN_COMPOUND_PATTERNS: Final[Sequence[str]] = [
    r".*_types_config\.py$",
    r".*_validator_util\.py$",
    r".*_types_validator\.py$",
    r".*_config_util\.py$",
]


# ============================================================================
# L5 ENFORCEMENT SUFFIXES
# ============================================================================

L5_ENFORCEMENT_ALLOWED_SUFFIXES: Final[Sequence[str]] = [
    "_guardrail.py",
    "_enforcer.py",
    "_gate.py",
    "_manager.py",
    "_shield.py",
    "_firewall.py",
    "_sanitizer.py",
    "_governor.py",
    "_policy.py",
    "_guard.py",
]


# ============================================================================
# LAYER PREFIX PATTERN
# ============================================================================

LAYER_PREFIX_PATTERN: Final[str] = r"(?i)(?:^|_)l([0-6])(?:_|[A-Z])"


# ============================================================================
# INTERFACE ROUTING
# ============================================================================

INTERFACE_FILENAME_PATTERN: Final[str] = r"^I[A-Z].*Protocol\.py$"
GLOBAL_INTERFACES_FOLDER: Final[str] = "agentic_core/interfaces"


# ============================================================================
# CANONICAL LOCATION PRIORITY
# ============================================================================

CANONICAL_LOCATION_PRIORITY: Final[Sequence[str]] = [
    "runtime",
    "interfaces",
    "base_agents",
    "mixins",
    "config/core",
    "config",
    "utils",
    "prompt_governance",
    "L5_safety",
    "L6_observability",
    "L4_state",
    "L3_orchestration",
    "L2_execution",
    "L1_cognition",
    "L0_routing",
]

DUPLICATE_DETECTION_EXEMPT: Final[Sequence[str]] = [
    "__init__.py",
    "conftest.py",
    "__main__.py",
]


# ============================================================================
# NON-PYTHON FILE ROUTING
# ============================================================================

NON_PYTHON_FOLDER_ROUTES: Final[Mapping[str, str]] = {
    "dashboard_ssot.yaml": "dashboards",
    ".yaml": "config",
    ".json": "config",
    ".html": "dashboards",
    ".js": "dashboards",
    ".css": "dashboards",
}

DOMAIN_CONTENT_SIGNALS: Final[Mapping[str, str]] = {
    "dashboard": "L6_observability/dashboards",
    "playwright": "L6_observability/dashboards",
    # Location SSOT signals for misclassified utility files
    "meta_learning_engine_util": "L7_meta_learning/utils",
    "meta_learning_storage_util": "L7_meta_learning/utils",
    "state_util": "L4_state/utils",
}


# ============================================================================
# SERVICE CLASS INDICATORS
# ============================================================================

SERVICE_CLASS_INDICATORS: Final[Sequence[str]] = [
    "Collector",
    "Monitor",
    "Tracker",
    "Reporter",
    "Emitter",
    "Publisher",
    "Subscriber",
    "Aggregator",
    "Accumulator",
    "Sampler",
    "Recorder",
]


# ============================================================================
# LAZY COMPILED PATTERN ACCESSORS
# ============================================================================


@lru_cache(maxsize=1)
def get_classification_suffix_patterns_compiled() -> dict[Pattern, str]:
    """Compile and cache classification suffix patterns."""
    return {re.compile(pattern): tag for pattern, tag in CLASSIFICATION_SUFFIX_PATTERNS.items()}


@lru_cache(maxsize=1)
def get_compound_suffix_patterns_compiled() -> list[tuple[Pattern, str, str, str]]:
    """Compile and cache compound suffix conflict patterns."""
    return [
        (re.compile(pattern), tag_a, tag_b, example)
        for pattern, tag_a, tag_b, example in COMPOUND_SUFFIX_CONFLICTS
    ]


@lru_cache(maxsize=1)
def get_folder_purity_patterns_compiled() -> dict[str, list[Pattern]]:
    """Compile and cache folder purity patterns."""
    return {folder: [re.compile(p) for p in patterns] for folder, patterns in FOLDER_PURITY_RULES.items()}


@lru_cache(maxsize=1)
def get_folder_purity_disallowed_compiled() -> dict[str, list[Pattern]]:
    """Compile and cache folder purity disallowed patterns."""
    return {
        folder: [re.compile(p) for p in patterns] for folder, patterns in FOLDER_PURITY_DISALLOWED.items()
    }


@lru_cache(maxsize=1)
def get_forbidden_compound_patterns_compiled() -> list[Pattern]:
    """Compile and cache forbidden compound patterns."""
    return [re.compile(p) for p in FORBIDDEN_COMPOUND_PATTERNS]


def get_folder_key_for_path(path: Path) -> str:
    """
    Get the folder purity key for a given path.

    Handles special cases:
    - config/agent_configs -> agent_configs
    - runtime/engine -> engines (via alias)
    - runtime/config -> config
    - prompt_governance -> prompt_governance
    - L*/subfolder -> subfolder
    """
    parts = path.relative_to("agentic_core").parts

    # Special case: config/agent_configs
    if len(parts) >= 3 and parts[0] == "config" and parts[1] == "agent_configs":
        return "agent_configs"

    # Special case: runtime subfolders
    if len(parts) >= 2 and parts[0] == "runtime":
        return parts[1]  # e.g., "config", "engine"

    # Special case: prompt_governance root
    if len(parts) >= 1 and parts[0] == "prompt_governance":
        return "prompt_governance"

    # L* subfolders
    if len(parts) >= 2 and parts[0].startswith("L") and parts[0][1].isdigit():
        return parts[1]

    # Root-level folders
    if len(parts) >= 1:
        return parts[0]

    return ""
