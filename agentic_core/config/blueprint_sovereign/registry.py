"""
SSOT for Sovereign Registry Configuration.

This module contains the core registry data structures that define
the sovereign territory structure of the codebase.

SSOT Consolidation (Jan 20, 2026):
Moved from agentic_core/L5_safety/validators/structure_blueprint.py
"""
from typing import Any, Dict, FrozenSet, List, Set
import os

# ============================================================================
# SOVEREIGN REGISTRY - Core Territory Definitions
# ============================================================================
# This defines the allowed folder structure and depth constraints.

SOVEREIGN_REGISTRY: dict = {
    'agentic_core': {
        'depth': 3,
        'subfolders': [
            'L0_maintenance', 'L1_cognition', 'L2_execution', 'L3_orchestration',
            'L4_state', 'L5_safety', 'L6_observability', 'config', 'schemas',
            'prompt_governance', 'runtime', 'utils', 'patterns', 'semantic_memory',
            'knowledge', 'observability', 'common'
        ]
    },
    'apps_rg': {
        'depth': 2,
        'subfolders': ['logic_nodes', 'asset_library', 'system_flow', 'engines', 'templates', 'domain']
    },
    'apps_lic': {
        'depth': 2,
        'subfolders': ['logic_nodes', 'asset_library', 'system_flow', 'engines', 'templates', 'domain', 'core']
    },
    'apps_shared': {
        'depth': 3,
        'subfolders': [
            'base_definitions', 'common_utils', 'core_components', 'base_agents',
            'models', 'utils', 'mixins', 'P1_core', 'config', 'data', 'domain', 'templates'
        ],
        'description': 'Global utilities and shared logic accessible by all apps and core.'
    },
    'tests': {
        'depth': 2,
        'subfolders': [
            'unit', 'integration', 'e2e', 'functional', 'fixtures', 'automation',
            'core', 'data', 'performance', 'security', 'autogen', 'utils'
        ]
    },
    'scripts': {
        'depth': 1,
        'subfolders': [],
        'purpose': 'Standalone utility scripts'
    },
    '.sovereign_healing_backup': {
        'depth': 2,
        'subfolders': ['filesystem', 'location', 'naming', 'transactions', 'import_fixes'],
        'purpose': 'Backup directory for healing operations',
        'volatile': True
    }
}

# ============================================================================
# HEALING CONFIGURATION
# ============================================================================
HEALING_CONFIG: dict = {
    "max_rounds": int(os.getenv('MAX_HEALING_ROUNDS', '10')),
    "max_per_file": int(os.getenv('MAX_HEALING_PER_FILE', '8')),
    "global_budget": int(os.getenv('GLOBAL_HEALING_BUDGET', '500')),
    "max_moves_per_run": 250,
    "max_fissions_per_run": 50,
    "dust_threshold": 40  # Minimum lines for a module to exist (Span-of-Two)
}

# ============================================================================
# CORE SUBFOLDER MAPS
# ============================================================================
CORE_SUBFOLDER_MAP: dict = {
    'L0_maintenance': ['scripts', 'logs', 'benchmarks', 'mixins'],
    'L1_cognition': ['thought_engine', 'intent_analysis', 'planning'],
    'L2_execution': ['ToolRegistry', 'action_handlers', 'mcp', 'tool_registry'],
    'L3_orchestration': ['workflow_engines', 'fission_logic', 'S3_vitality', 'mcp', 'meta_learning', 'interfaces'],
    'L4_state': ['ValidationContext', 'ledger', 'filesystem', 'memory', 'validation_context'],
    'L5_safety': ['guardrails', 'red_teaming', 'gravity', 'validators', 'agents', 'bases', 'policies', 'utils', 'verifiability'],
    'L6_observability': ['dashboards', 'reports', 'metrics', 'telemetry', 'tracing', 'compliance', 'agents'],
    'schemas': ['models', 'messages', 'types', 'validators'],
    'config': ['blueprint_sovereign', 'environments', 'feature_flags', 'secrets_manager'],
    'prompt_governance': ['meta_prompts', 'version_registry', 'rendering', 'templates'],
    'runtime': ['shared_runtime', 'environment_setup', 'shared', 'resource_management'],
    'utils': ['core_extensions', 'wrappers', 'general_helpers', 'naming', 'deduplicated'],
    'patterns': ['agent_roles', 'communication_flow', 'interaction_patterns', 'reasoning_patterns'],
    'semantic_memory': ['store', 'embeddings', 'retrieval', 'index'],
    'knowledge': ['document_loaders', 'static_index', 'ResearchCache']
}

# ============================================================================
# VARIABLE DEPTH SUBFOLDERS
# ============================================================================
# These subfolders are exempt from strict depth enforcement.
VARIABLE_DEPTH_SUBFOLDERS: frozenset = frozenset({
    'utils', 'config', 'common', 'observability', 'L6_observability',
    'L3_orchestration', 'L0_maintenance', 'L1_cognition', 'L2_execution',
    'L4_state', 'L5_safety', 'schemas', 'prompt_governance', 'runtime',
    'patterns', 'semantic_memory', 'knowledge',
})

# ============================================================================
# L4 APPROVED FOLDERS (Depth-4 Structure)
# ============================================================================
L4_APPROVED_FOLDERS: set = {
    'agentic_core/L6_observability/dashboards',
    'agentic_core/L0_maintenance/scripts',
    'agentic_core/L3_orchestration/workflow_engines',
    'agentic_core/L1_cognition/thought_engine',
    'agentic_core/L5_safety/guardrails',
    'agentic_core/L5_safety/validators',
    'agentic_core/L5_safety/gravity',
    'agentic_core/L2_execution/ToolRegistry',
    'agentic_core/L2_execution/mcp',
    'agentic_core/L4_state/ValidationContext',
    'agentic_core/schemas/models',
    'agentic_core/utils/core_extensions',
    'agentic_core/config/blueprint_sovereign',
}

# ============================================================================
# GRAVITY CONFIGURATION
# ============================================================================
GRAVITY_CONFIG: dict = {
    'enabled': True,
    'UPSTREAM_SOVEREIGN_ROOTS': ['agentic_core'],
    'downstream_domains': ['apps_rg', 'apps_lic', 'apps_shared', 'tests'],
    'exemptions': []
}

# ============================================================================
# MISSION CONFIGURATION
# ============================================================================
MISSION_CONFIG: dict = {
    'GRAVITY_SURGERY_ENABLED': True,
    'hierarchy_healing_enabled': True,
    'span_surgery_enabled': True,
    'fission_enabled': True,
    'run_full_mission': True,
    'run_hierarchy_healing': True,
    'run_gravity_refactor': True,
    'run_sprawl_surgery': True,
    'structural_only_mode': False,
    'timeout_seconds': int(os.getenv('MISSION_TIMEOUT_SECONDS', '1800'))
}

# ============================================================================
# AGENT RESILIENCE CONFIGURATION
# ============================================================================
AGENT_RESILIENCE_CONFIG: dict = {
    'retry_count': int(os.getenv('AGENT_RETRY_COUNT', '3')),
    'backoff_base': float(os.getenv('AGENT_RETRY_BACKOFF_BASE', '0.5'))
}

# ============================================================================
# MCP CAPABILITIES
# ============================================================================
MCP_CAPABILITIES: dict = {
    'router': {'enabled': True, 'path': 'agentic_core.L3_orchestration.mcp'},
    'marketplace_filter': {'enabled': True, 'path': 'agentic_core.L3_orchestration.mcp'},
    'filesystem': {'enabled': True, 'path': 'agentic_core.L4_state.filesystem'},
    'figma': {'enabled': True, 'path': 'agentic_core.L2_execution.mcp'},
    'fetch': {'enabled': True, 'path': 'agentic_core.L2_execution.mcp'},
    'SemanticCache': {'enabled': True, 'path': 'agentic_core.L2_execution.mcp'}
}

# ============================================================================
# LAYER DIRECTORIES MAPPING
# ============================================================================
LAYER_DIRS: dict = {
    "L0": "L0_maintenance",
    "L1": "L1_cognition",
    "L2": "L2_execution",
    "L3": "L3_orchestration",
    "L4": "L4_state",
    "L5": "L5_safety",
    "L6": "L6_observability",
}

# ============================================================================
# L2 TO L1 REVERSE MAPPING
# ============================================================================
L2_TO_L1_MAP: dict = {
    "thought_engine": "L1_cognition",
    "intent_analysis": "L1_cognition",
    "planning": "L1_cognition",
    "ToolRegistry": "L2_execution",
    "action_handlers": "L2_execution",
    "mcp": "L2_execution",
    "workflow_engines": "L3_orchestration",
    "fission_logic": "L3_orchestration",
    "meta_learning": "L3_orchestration",
    "S3_vitality": "L3_orchestration",
    "ValidationContext": "L4_state",
    "ledger": "L4_state",
    "memory": "L4_state",
    "filesystem": "L4_state",
    "guardrails": "L5_safety",
    "validators": "L5_safety",
    "gravity": "L5_safety",
    "red_teaming": "L5_safety",
    "core_extensions": "utils",
    "naming": "utils",
    "wrappers": "utils",
    "general_helpers": "utils",
    "metrics": "observability",
    "tracing": "observability",
    "telemetry": "observability",
    "compliance": "observability",
    "models": "schemas",
    "messages": "schemas",
    "types": "schemas",
    "templates": "prompt_governance",
    "meta_prompts": "prompt_governance",
    "rendering": "prompt_governance",
    "version_registry": "prompt_governance",
    "blueprint_sovereign": "config",
    "environments": "config",
    "feature_flags": "config",
    "scripts": "L0_maintenance",
    "logs": "L0_maintenance",
    "benchmarks": "L0_maintenance",
}

__all__ = [
    "SOVEREIGN_REGISTRY",
    "HEALING_CONFIG",
    "CORE_SUBFOLDER_MAP",
    "VARIABLE_DEPTH_SUBFOLDERS",
    "L4_APPROVED_FOLDERS",
    "GRAVITY_CONFIG",
    "MISSION_CONFIG",
    "AGENT_RESILIENCE_CONFIG",
    "MCP_CAPABILITIES",
    "LAYER_DIRS",
    "L2_TO_L1_MAP",
]
