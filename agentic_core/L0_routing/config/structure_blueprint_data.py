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
# EXPORTS
# ============================================================================

__all__ = [
    "SCRIPTS_FORBIDDEN_PATTERNS",
    "L5_SUBPROCESS_ALLOWLIST",
    "L6_HYBRID_ALLOWLIST",
    "FOLDER_PURITY_RULES",
    "APP_DOMAIN_PREFIXES",
    "LAYER_KEYWORD_AFFINITY",
    "SUFFIX_TO_FOLDER",
    "INTERFACE_FILENAME_PATTERN",
    "GLOBAL_INTERFACES_FOLDER",
    "FORBIDDEN_EPHEMERAL_PATTERNS",
    "EPHEMERAL_PATTERN_EXEMPTIONS",
    "CANONICAL_LOCATION_PRIORITY",
    "DUPLICATE_DETECTION_EXEMPT",
    "LAYER_PREFIX_PATTERN",
]
