"""
L0 Structure Blueprint Data - Literal-only constants extracted from L5.

This module contains ONLY literal assignments (str/int/bool/None, dict/list/set/tuple).
No functions, classes, or imports from L5+ layers.
"""

from __future__ import annotations

from typing import Final, Mapping, Sequence

# ============================================================================
# SCRIPTS PATTERNS
# ============================================================================

SCRIPTS_FORBIDDEN_PATTERNS: Final[Sequence[str]] = [
    r"^[A-Z]",
    r"^test_",
]

# ============================================================================
# ALLOWLISTS
# ============================================================================

L5_SUBPROCESS_ALLOWLIST: Final[Sequence[str]] = [
    "agentic_core/L5_safety/enforcement/safe_subprocess_handler.py",
    "agentic_core/L5_safety/utils/subprocess_security_util.py",
    "agentic_core/L5_safety/reasoning/PreCommitSovereignAgent.py",
    "agentic_core/L5_safety/reasoning/ArchitectureGovernorAgent.py",
    "agentic_core/L5_safety/reasoning/AutonomyGuardianAgent.py",
    "agentic_core/L5_safety/reasoning/SovereignActionPlaneAgent.py",
    "agentic_core/L5_safety/utils/pre_deploy_check_util.py",
]

L6_HYBRID_ALLOWLIST: Final[Sequence[str]] = [
    "agentic_core/L6_observability/dashboards/verify_dashboard_e2e_playwright_util.py",
]

# ============================================================================
# FOLDER CLASSIFICATION
# ============================================================================

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
    ],
}

# ============================================================================
# SEMANTIC CLASSIFICATION
# ============================================================================

APP_DOMAIN_PREFIXES: Final[Sequence[str]] = [
    "Lic",
    "Campaign",
    "Outreach",
]

LAYER_KEYWORD_AFFINITY: Final[Mapping[str, Sequence[str]]] = {
    "L0_routing": [
        "cleanup",
        "maintenance",
        "bootstrap",
        "heal",
        "repair",
        "reconcile",
        "ssot",
        "folder cleanup",
        "hygiene",
    ],
    "L1_cognition": [
        "reasoning",
        "cognition",
        "thinking",
        "analysis",
        "strategy",
        "planning",
        "inference",
    ],
    "L2_execution": [],
    "L3_orchestration": [],
    "L4_state": [],
    "L5_safety": [],
    "L6_observability": [],
}

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
    "Executor.py": "reasoning",
    "Orchestrator.py": "reasoning",
    "Strategy.py": "enforcement",
    "Adapter.py": "enforcement",
}

# ============================================================================
# INTERFACE PATTERNS
# ============================================================================

INTERFACE_FILENAME_PATTERN: Final[str] = r"^I[A-Z].*Protocol\.py$"
GLOBAL_INTERFACES_FOLDER: Final[str] = "agentic_core/interfaces"

# ============================================================================
# EPHEMERAL PATTERNS
# ============================================================================

FORBIDDEN_EPHEMERAL_PATTERNS: Final[Sequence[str]] = [
    r"(?i)phase\s*\d",
    r"(?i)wave\s*[\d_]",
    r"(?i)sprint\d",
]

EPHEMERAL_PATTERN_EXEMPTIONS: Final[Sequence[str]] = [
    r"(?i)two_?phase",
    r"(?i)execution_phase",
    r"(?i)mutation_phase",
    r"(?i)research_hop_phase",
]

# ============================================================================
# CANONICAL LOCATION
# ============================================================================

CANONICAL_LOCATION_PRIORITY: Final[Sequence[str]] = [
    "runtime",
    "interfaces",
    "reasoning",
    "validators",
    "utils",
    "config",
    "types",
]

DUPLICATE_DETECTION_EXEMPT: Final[Sequence[str]] = [
    "__init__.py",
    "_protocol.py",
]

# ============================================================================
# LAYER PREFIXES
# ============================================================================

LAYER_PREFIX_PATTERN: Final[str] = r"^(L[0-6]|apps_|ops_scripts|docs|archives)"

# ============================================================================
# AST PLACEMENT SIGNALS
# ============================================================================

AST_PLACEMENT_SIGNALS: Final[Sequence[str]] = [
    "Agent",
    "Strategy",
    "Adapter",
    "Protocol",
    "Healer",
    "Guardian",
    "Validator",
    "Enforcer",
    "Auditor",
    "Monitor",
    "Orchestrator",
    "Coordinator",
    "Manager",
    "Controller",
    "Service",
    "Handler",
    "Processor",
    "Executor",
    "Runner",
    "Worker",
]

# ============================================================================
# SOVEREIGN TERRITORIES
# ============================================================================

SOVEREIGN_TERRITORIES: Final[Mapping[str, Mapping[str, str]]] = {
    "agentic_core": {
        "description": "Core framework and shared utilities",
        "layer": "L0_routing",
    },
    "apps_rg": {
        "description": "Research and development applications",
        "layer": "L1_cognition",
    },
    "apps_lic": {
        "description": "Licensed commercial applications",
        "layer": "L2_execution",
    },
    "apps_shared": {
        "description": "Shared application components",
        "layer": "L3_orchestration",
    },
    "archives": {
        "description": "Archived code and documentation",
        "layer": "L4_state",
    },
    "docs": {
        "description": "Documentation and reports",
        "layer": "L5_safety",
    },
    "ops_scripts": {
        "description": "Operational scripts and tools",
        "layer": "L6_observability",
    },
}

# ============================================================================
# ============================================================================
# FORENSIC DISCOVERY CONSTANTS
# ============================================================================

FORENSIC_DISCOVERY_SCRIPT: Final[str] = "agentic_core/L0_routing/scripts/forensic_discovery_prep.py"
FORENSIC_DISCOVERY_INTEGRITY_HASH: Final[str] = (
    "e248d17f49620ba763ab161c8799bfd37cdfd71badf6adba3adb92e56504944b"
)


# ============================================================================
# COMPOUND SUFFIX CONFLICTS (Literal list of tuples)
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
# EXPORTS
# ============================================================================

__all__ = [
    "AST_PLACEMENT_SIGNALS",
    "APP_DOMAIN_PREFIXES",
    "CANONICAL_LOCATION_PRIORITY",
    "COMPOUND_SUFFIX_CONFLICTS",
    "DUPLICATE_DETECTION_EXEMPT",
    "EPHEMERAL_PATTERN_EXEMPTIONS",
    "FILETYPE_TO_FOLDER",
    "FOLDER_PURITY_RULES",
    "FORBIDDEN_EPHEMERAL_PATTERNS",
    "FORENSIC_DISCOVERY_INTEGRITY_HASH",
    "FORENSIC_DISCOVERY_SCRIPT",
    "GLOBAL_INTERFACES_FOLDER",
    "INTERFACE_FILENAME_PATTERN",
    "L5_SUBPROCESS_ALLOWLIST",
    "L6_HYBRID_ALLOWLIST",
    "LAYER_KEYWORD_AFFINITY",
    "LAYER_PREFIX_PATTERN",
    "SCRIPTS_FORBIDDEN_PATTERNS",
    "SOVEREIGN_TERRITORIES",
    "SUFFIX_TO_FOLDER",
]
