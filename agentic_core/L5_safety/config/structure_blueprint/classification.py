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
from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD
CLASSIFICATION_SUFFIX_PATTERNS: Final[Mapping[str, str]] = {'_agent\\.py$': 'AGENT', '_types\\.py$': 'TYPES', '_config\\.py$': 'CONFIG', '_validator\\.py$': 'VALIDATOR', '_util\\.py$': 'UTILITY', '_mixin\\.py$': 'MIXIN', '_strategy\\.py$': 'STRATEGY', '_adapter\\.py$': 'ADAPTER', '_protocol\\.py$': 'PROTOCOL', 'Agent\\.py$': 'AGENT', 'Strategy\\.py$': 'STRATEGY', 'Adapter\\.py$': 'ADAPTER', 'I[A-Z].*Protocol\\.py$': 'PROTOCOL', '_enforcer\\.py$': 'ENFORCER', '_guard\\.py$': 'ENFORCER', '_guardrail\\.py$': 'ENFORCER', '_seam\\.py$': 'SEAM', '_orchestrator\\.py$': 'ORCHESTRATOR', '_coordinator\\.py$': 'ORCHESTRATOR', '_router\\.py$': 'ENGINE'}
COMPOUND_SUFFIX_CONFLICTS: Final[Sequence[tuple[str, str, str, str]]] = [('_agent_types$', 'AGENT', 'TYPES', 'code_detector_agent_types.py'), ('_agent_config$', 'AGENT', 'CONFIG', 'security_level_agent_config.py'), ('_agent_validator$', 'AGENT', 'VALIDATOR', 'routing_decision_agent_validator.py'), ('_agent_util$', 'AGENT', 'UTILITY', 'extract_pattern_agent_util.py'), ('Agent_types$', 'AGENT', 'TYPES', 'CodeDetectorAgent_types.py'), ('Agent_config$', 'AGENT', 'CONFIG', 'SomeAgent_config.py'), ('_engine_types$', 'ENGINE', 'TYPES', 'safety_engine_types.py'), ('_engine_validator$', 'ENGINE', 'VALIDATOR', 'consensus_engine_validator.py'), ('_engine_config$', 'ENGINE', 'CONFIG', 'engine_config.py'), ('_guardrail_types$', 'GUARDRAIL', 'TYPES', 'mcp_security_guardrail_types.py'), ('_guardrail_mixin$', 'GUARDRAIL', 'MIXIN', 'cost_guardrail_mixin.py'), ('_guardrail_config$', 'GUARDRAIL', 'CONFIG', 'guardrail_config.py'), ('_manager_types$', 'MANAGER', 'TYPES', 'resource_manager_types.py'), ('_manager_config$', 'MANAGER', 'CONFIG', 'sovereign_manager_config.py'), ('_manager_validator$', 'MANAGER', 'VALIDATOR', 'context_manager_validator.py'), ('_strategy_types$', 'STRATEGY', 'TYPES', 'context_pruning_strategy_types.py'), ('_strategy_config$', 'STRATEGY', 'CONFIG', 'mcpservermode_strategy_config.py'), ('_strategy_mixin$', 'STRATEGY', 'MIXIN', 'healing_strategy_mixin.py'), ('_strategy_validator$', 'STRATEGY', 'VALIDATOR', 'reasoningnode_strategy_validator.py'), ('_validator_types$', 'VALIDATOR', 'TYPES', 'code_validator_types.py'), ('_validator_util$', 'VALIDATOR', 'UTILITY', 'check_sovereign_base_validator_util.py'), ('_scanner_types$', 'SCANNER', 'TYPES', 'credential_scanner_types.py'), ('_scanner_util$', 'SCANNER', 'UTILITY', 'sovereign_scanner_util.py'), ('_protocol_types$', 'PROTOCOL', 'TYPES', 'healer_protocol_types.py'), ('_protocol_config$', 'PROTOCOL', 'CONFIG', 'detection_protocol_config.py'), ('_protocol_guardrail$', 'PROTOCOL', 'GUARDRAIL', 'airlock_protocol_guardrail.py'), ('_suite_types$', 'SUITE', 'TYPES', 'security_validation_suite_types.py'), ('_factory_config$', 'FACTORY', 'CONFIG', 'gateway_factory_config.py'), ('_factory_util$', 'FACTORY', 'UTILITY', 'component_factory_util.py'), ('_orchestrator_types$', 'ORCHESTRATOR', 'TYPES', 'recursive_orchestrator_types.py'), ('_shield_validator$', 'SHIELD', 'VALIDATOR', 'governance_shield_validator.py'), ('_sanitizer_util$', 'SANITIZER', 'UTILITY', 'telemetry_sanitizer_util.py'), ('_guard_util$', 'GUARD', 'UTILITY', 'scan_guard_util.py'), ('_guard_mixin$', 'GUARD', 'MIXIN', 'cost_guard_mixin.py'), ('_detector_types$', 'DETECTOR', 'TYPES', 'code_detector_types.py'), ('_detector_config$', 'DETECTOR', 'CONFIG', 'gravity_leak_detector_config.py'), ('_enforcer_types$', 'ENFORCER', 'TYPES', 'code_enforcer_types.py'), ('_enforcer_util$', 'ENFORCER', 'UTILITY', 'root_hygiene_enforcer_util.py'), ('_config_types$', 'CONFIG', 'TYPES', 'blueprint_config_types.py'), ('_config_util$', 'CONFIG', 'UTILITY', 'sync_mcp_config_util.py'), ('_config_detector$', 'CONFIG', 'DETECTOR', 'magic_config_detector.py'), ('_adapter_types$', 'ADAPTER', 'TYPES', 'open_telemetry_tracing_adapter_types.py'), ('_adapter_config$', 'ADAPTER', 'CONFIG', 'storage_adapter_config.py'), ('_adapter_util$', 'ADAPTER', 'UTILITY', 'mcp_adapter_util.py'), ('Adapter_types$', 'ADAPTER', 'TYPES', 'SomeAdapter_types.py'), ('_mixin_agent_mixin$', 'MIXIN', 'AGENT', 'autonomy_mixin_agent_mixin.py'), ('_mixin_agent$', 'MIXIN', 'AGENT', 'some_mixin_agent.py'), ('_agent_mixin$', 'AGENT', 'MIXIN', 'feature_flagged_agent_mixin.py'), ('_mixin_types$', 'MIXIN', 'TYPES', 'healer_mixin_types.py'), ('_mixin_config$', 'MIXIN', 'CONFIG', 'autonomy_mixin_config.py'), ('_mixin_util$', 'MIXIN', 'UTILITY', 'healer_mixin_util.py'), ('_mixin_validator$', 'MIXIN', 'VALIDATOR', 'agent_mixin_validator.py')]
SUFFIX_TO_FOLDER: Final[Mapping[str, str]] = {'_config.py': 'config', '_types.py': 'types', '_protocol.py': 'types', '_validator.py': 'validators', '_util.py': 'utils', '_mixin.py': 'GLOBAL_MIXINS', 'Protocol.py': 'GLOBAL_INTERFACES', 'Agent.py': 'reasoning', 'Inspector.py': 'reasoning', 'Healer.py': 'reasoning', 'Guardian.py': 'reasoning', 'Orchestrator.py': 'reasoning', 'Monitor.py': 'enforcement', 'Strategy.py': 'enforcement', '_guardrail.py': 'enforcement', '_strategy.py': 'enforcement', '_enforcer.py': 'enforcement', '_guard.py': 'enforcement', '_seam.py': 'seams', 'Coordinator.py': 'engines', 'Router.py': 'engines'}
FILETYPE_TO_FOLDER: Final[Mapping[str, str]] = {'AGENT': 'reasoning', 'ORCHESTRATOR': 'reasoning', 'CONFIG': 'config', 'TYPES': 'types', 'PROTOCOL': 'types', 'VALIDATOR': 'validators', 'UTILITY': 'utils', 'MIXIN': 'GLOBAL_MIXINS', 'SCRIPT': 'scripts', 'FACTORY': 'enforcement', 'STRATEGY': 'enforcement', 'EXCEPTION': 'types', 'ENGINE': 'reasoning', 'GATEWAY': 'enforcement', 'SERVICE': 'utils', 'ENFORCER': 'enforcement', 'SEAM': 'seams'}
FOLDER_PURITY_RULES: Final[Mapping[str, Sequence[str]]] = {'reasoning': ['.*Agent\\.py$', '.*Executor\\.py$', '.*Orchestrator\\.py$', '.*Inspector\\.py$', '.*Healer\\.py$', '.*Guardian\\.py$'], 'validators': ['.*_validator\\.py$', '.*Validator\\.py$'], 'config': ['.*_config\\.py$', '.*_config\\.yaml$', '.*_config\\.json$'], 'types': ['.*_types\\.py$', '.*_protocol\\.py$', 'I[A-Z].*Protocol\\.py$', '.*Error\\.py$', '.*Exception\\.py$', '.*_spec\\.py$', '.*_schema\\.py$', '.*_model\\.py$'], 'utils': ['.*_util\\.py$', '.*_helper\\.py$'], 'scripts': ['^[a-z][a-z0-9_]*\\.py$'], 'enforcement': ['.*_guardrail\\.py$', '.*_enforcer\\.py$', '.*_gate\\.py$', '.*_strategy\\.py$', '.*Strategy\\.py$', '.*Adapter\\.py$', '.*Monitor\\.py$', '.*Factory\\.py$', '.*Gateway\\.py$'], 'dashboards': ['.*\\.html$', '.*\\.js$', '.*\\.css$', '.*\\.yaml$', '.*\\.json$', '.*\\.py$'], 'engines': ['.*_engine\\.py$', '.*_executor\\.py$', '.*_task\\.py$', '.*_impl\\.py$', '.*_router\\.py$', '.*_service\\.py$', '.*_client\\.py$', '.*_node\\.py$', '.*_cache\\.py$', '.*_planner\\.py$', '.*_analyzer\\.py$', '.*_mapper\\.py$', '.*_embedder\\.py$', '.*_scanner\\.py$', '.*_core\\.py$', '.*_system\\.py$', '.*_composer\\.py$', '.*_scorer\\.py$', '.*_detector\\.py$', '.*_builder\\.py$', '.*_normalizer\\.py$'], 'tools': ['.*_tool\\.py$', '.*_impl\\.py$', '.*_client\\.py$'], 'base_agents': ['^L[0-9][A-Za-z]+Base\\.py$', '^SovereignBaseAgent\\.py$', '^LightweightBase\\.py$'], 'mixins': ['^[a-z0-9_]+_mixin\\.py$'], 'interfaces': ['^I[A-Z][A-Za-z0-9]+\\.py$'], 'agent_configs': ['^[a-z0-9_]+_config\\.py$', '^[a-z0-9_]+\\.yaml$', '^[a-z0-9_]+\\.json$'], 'healers': ['.*_healer\\.py$', '.*Healer\\.py$'], 'caching': ['.*_cache\\.py$', '.*_cacher\\.py$', '.*Cache\\.py$'], 'memory': ['.*_memory\\.py$', '.*_store\\.py$', '.*Memory\\.py$'], 'security': ['.*_security\\.py$', '.*Security\\.py$', '.*_guard\\.py$'], 'golden_evaluation': ['.*_eval\\.py$', '.*_evaluation\\.py$', '.*Evaluator\\.py$'], 'exceptions': ['.*Error\\.py$', '.*Exception\\.py$', '.*_exceptions\\.py$'], 'core_kernel': ['.*_kernel\\.py$', '.*_core\\.py$']}
INFRASTRUCTURE_PROFILES: Final[Mapping[str, Sequence[str]]] = {'runtime': ['.*\\.py$'], 'meta_control': ['.*\\.py$'], 'policy': ['.*\\.py$']}
FOLDER_ALIASES: Final[Mapping[str, str]] = {'knowledge': 'reasoning', 'validation': 'validators', 'engine': 'engines'}
NO_ROOT_FILES_FOLDERS: Final[frozenset[str]] = frozenset({'security', 'prompt_governance'})
APPROVED_SUBFOLDERS: Final[Mapping[str, frozenset[str]]] = {'security': frozenset({'utils', 'detectors', 'schemas', 'validators', 'adversarial'}), 'prompt_governance': frozenset({'core', 'meta_prompts', 'optimization', 'registry', 'scripts', 'security', 'templates', 'utils', 'validation'})}
FOLDER_PURITY_DISALLOWED: Final[Mapping[str, Sequence[str]]] = {'engines': ['.*Agent\\.py$', '.*Orchestrator\\.py$', '.*Strategy\\.py$', '.*_strategy\\.py$', '.*Validator\\.py$', '.*_validator\\.py$', '.*_types\\.py$', '.*_util\\.py$', '.*_config\\.py$'], 'tools': ['.*Agent\\.py$', '.*Validator\\.py$', '.*_validator\\.py$', '.*_types\\.py$', '.*_util\\.py$', '.*_config\\.py$', '.*Strategy\\.py$', '.*_strategy\\.py$']}
KNOWN_ARCHITECTURAL_SUFFIXES: Final[Sequence[str]] = ['_types', '_config', '_validator', '_util', '_mixin', '_protocol', '_strategy', '_adapter', '_factory', '_orchestrator', '_engine', '_gateway', '_sensor', '_enforcer', '_guard', '_guardrail', '_seam', '_coordinator', '_router']
FORBIDDEN_COMPOUND_PATTERNS: Final[Sequence[str]] = ['.*_types_config\\.py$', '.*_validator_util\\.py$', '.*_types_validator\\.py$', '.*_config_util\\.py$']
L5_ENFORCEMENT_ALLOWED_SUFFIXES: Final[Sequence[str]] = ['_guardrail.py', '_enforcer.py', '_gate.py', '_manager.py', '_shield.py', '_firewall.py', '_sanitizer.py', '_governor.py', '_policy.py', '_guard.py']
LAYER_PREFIX_PATTERN: Final[str] = '(?i)(?:^|_)l([0-6])(?:_|[A-Z])'
INTERFACE_FILENAME_PATTERN: Final[str] = '^I[A-Z].*Protocol\\.py$'
GLOBAL_INTERFACES_FOLDER: Final[str] = 'agentic_core/interfaces'
CANONICAL_LOCATION_PRIORITY: Final[Sequence[str]] = ['runtime', 'interfaces', 'base_agents', 'mixins', 'config/core', 'config', 'utils', 'prompt_governance', 'L5_safety', 'L6_observability', 'L4_state', 'L3_orchestration', 'L2_execution', 'L1_cognition', 'L0_routing']
DUPLICATE_DETECTION_EXEMPT: Final[Sequence[str]] = ['__init__.py', 'conftest.py', '__main__.py']
NON_PYTHON_FOLDER_ROUTES: Final[Mapping[str, str]] = {'dashboard_ssot.yaml': 'dashboards', '.yaml': 'config', '.json': 'config', '.html': 'dashboards', '.js': 'dashboards', '.css': 'dashboards'}
DOMAIN_CONTENT_SIGNALS: Final[Mapping[str, str]] = {'dashboard': 'L6_observability/dashboards', 'playwright': 'L6_observability/dashboards', 'meta_learning_engine_util': 'system_learning/utils', 'meta_learning_storage_util': 'system_learning/utils', 'state_util': 'L4_state/utils'}
SERVICE_CLASS_INDICATORS: Final[Sequence[str]] = ['Collector', 'Monitor', 'Tracker', 'Reporter', 'Emitter', 'Publisher', 'Subscriber', 'Aggregator', 'Accumulator', 'Sampler', 'Recorder']

@lru_cache(maxsize=1)
def get_classification_suffix_patterns_compiled() -> dict[Pattern, str]:
    """Compile and cache classification suffix patterns."""
    return {re.compile(pattern): tag for pattern, tag in CLASSIFICATION_SUFFIX_PATTERNS.items()}

@lru_cache(maxsize=1)
def get_compound_suffix_patterns_compiled() -> list[tuple[Pattern, str, str, str]]:
    """Compile and cache compound suffix conflict patterns."""
    return [(re.compile(pattern), tag_a, tag_b, example) for pattern, tag_a, tag_b, example in COMPOUND_SUFFIX_CONFLICTS]

@lru_cache(maxsize=1)
def get_folder_purity_patterns_compiled() -> dict[str, list[Pattern]]:
    """Compile and cache folder purity patterns."""
    return {folder: [re.compile(p) for p in patterns] for folder, patterns in FOLDER_PURITY_RULES.items()}

@lru_cache(maxsize=1)
def get_folder_purity_disallowed_compiled() -> dict[str, list[Pattern]]:
    """Compile and cache folder purity disallowed patterns."""
    return {folder: [re.compile(p) for p in patterns] for folder, patterns in FOLDER_PURITY_DISALLOWED.items()}

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
    parts = path.relative_to(AGENTIC_CORE_DIR).parts
    if len(parts) >= 3 and parts[0] == 'config' and (parts[1] == 'agent_configs'):
        return 'agent_configs'
    if len(parts) >= 2 and parts[0] == 'runtime':
        return parts[1]
    if len(parts) >= 1 and parts[0] == 'prompt_governance':
        return 'prompt_governance'
    if len(parts) >= 2 and parts[0].startswith('L') and parts[0][1].isdigit():
        return parts[1]
    if len(parts) >= 1:
        return parts[0]
    return ''
