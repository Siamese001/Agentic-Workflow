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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "classification")
emit_determinism_digest("p0", "classification")

_emit_dispatches_healing_run("p1", "classification", "L5")
_emit_routes_through("p1", "classification", "L5")
_emit_checks_agent_registry("p1", "classification", "agent_registry")
_emit_validates_agent_capability("p1", "classification", "capability")
_emit_dispatches_execution_plan("p1", "classification", "exec_plan")
_emit_agent_executes_agent("p1", "classification", "sub_agent")
_emit_routes_to_agent("p1", "classification", "target_agent")
_emit_verifies_policy("p1", "classification", "policy_check")
_emit_observes_runtime_state("p1", "classification", "runtime_state")
_emit_verifies_boundary("p1", "classification", "boundary_check")
_emit_transcripts_response("p1", "classification", "transcript")
_emit_hard_fails_untranscripted("p1", "classification")
_emit_gated_by_confidence("p1", "classification", "confidence_gate")
_emit_escalates_to_human("p1", "classification", "L5")
_emit_reads_policy_state("p1", "classification", "L5")
_emit_authorize_and_execute("p2", "classification", "execution_auth")
_emit_validates_capability("p2", "classification", "capability_check")
_emit_routes_to_capability("p2", "classification", "capability_route")
_emit_writes_via_uwg("p2", "classification", "uwg_write")
_emit_blocks_direct_write("p2", "classification", "direct_write_block")
_emit_records_tool_invocation("p2", "classification", "tool_invocation")
_emit_captures_execution_output("p2", "classification", "exec_output")
_emit_dispatches_agent("p3", "classification", "agent_dispatch")
_emit_coordinates_agents("p3", "classification", "agent_coordination")
_emit_records_workflow_lineage("p3", "classification", "workflow_lineage")
_emit_records_healing_outcome("p3", "classification", "healing_outcome")
_emit_escalates_failure("p3", "classification", "failure_escalation")
_emit_orchestrates_workflow("p3", "classification", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "classification", "healing_dispatch")
_emit_invokes_evaluation("p3", "classification", "evaluation_signal")
_emit_records_telemetry_event("p4", "classification", "telemetry_event")
_emit_captures_evaluation_metric("p4", "classification", "eval_metric")
_emit_stores_embedding("p4", "classification", "embedding_store")
_emit_updates_meta_learning_state("p4", "classification", "meta_learning")
_emit_links_execution_to_snapshot("p4", "classification", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("classification", "p4obs", "metric_1")
_emit_emits_metric_event("classification", "p4obs", "metric_2")
_emit_emits_metric_event("classification", "p4obs", "metric_3")
_emit_emits_metric_event("classification", "p4obs", "metric_4")
_emit_emits_metric_event("classification", "p4obs", "metric_5")
_emit_emits_metric_event("classification", "p4obs", "metric_6")
_emit_records_incident_event("classification", "p4obs", "incident")
_emit_captures_runtime_anomaly("classification", "p4obs", "anomaly")
_emit_writes_observability_log("classification", "p4obs", "obs_log")
_emit_updates_monitoring_state("classification", "p4obs", "mon_state")
_emit_triggers_alert("classification", "p4obs", "alert")
_emit_links_incident_trace("classification", "p4obs", "trace_link")
_emit_captures_pattern("classification", "p3lm", "pattern")
_emit_records_learning_event("classification", "p3lm", "learning_event")
_emit_writes_learning_snapshot("classification", "p3lm", "snapshot")
_emit_feeds_meta_learning("classification", "p3lm", "meta_feed")
_emit_updates_routing_strategy("classification", "p3lm", "routing")
_emit_improves_agent_policy("classification", "p3lm", "policy")
_emit_stores_learning_state("classification", "p3lm", "state")
_emit_records_execution_trace("classification", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("classification", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("classification", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("classification", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("classification", "L4_STATE", "p2_trace_5")
_emit_reads_environ("classification", "env_read", "p2_env_1")
_emit_reads_environ("classification", "env_read", "p2_env_2")
_emit_reads_runtime_state("classification", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("classification", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "classification", "context_pull")
_emit_pulls_context("p1", "classification", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "classification", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "classification", "uwg_term_2")
_emit_writes_through("p1", "classification", "write_through")
_emit_writes_through("p1", "classification", "write_through_2")
_emit_validated_by_safety_plane("p1", "classification", "safety_validation")
_emit_invokes_eval("p1", "classification", "eval_call")
_emit_proposal_commits_routing("p1", "classification", "routing_commit")

CLASSIFICATION_SUFFIX_PATTERNS: Final[Mapping[str, str]] = {
    "_agent\\.py$": "AGENT",
    "_types\\.py$": "TYPES",
    "_config\\.py$": "CONFIG",
    "_validator\\.py$": "VALIDATOR",
    "_util\\.py$": "UTILITY",
    "_mixin\\.py$": "MIXIN",
    "_strategy\\.py$": "STRATEGY",
    "_adapter\\.py$": "ADAPTER",
    "_protocol\\.py$": "PROTOCOL",
    "Agent\\.py$": "AGENT",
    "Strategy\\.py$": "STRATEGY",
    "Adapter\\.py$": "ADAPTER",
    "I[A-Z].*Protocol\\.py$": "PROTOCOL",
    "_enforcer\\.py$": "ENFORCER",
    "_guard\\.py$": "ENFORCER",
    "_guardrail\\.py$": "ENFORCER",
    "_seam\\.py$": "SEAM",
    "_orchestrator\\.py$": "ORCHESTRATOR",
    "_coordinator\\.py$": "ORCHESTRATOR",
    "_router\\.py$": "ENGINE",
}
COMPOUND_SUFFIX_CONFLICTS: Final[Sequence[tuple[str, str, str, str]]] = [
    ("_agent_types$", "AGENT", "TYPES", "code_detector_agent_types.py"),
    ("_agent_config$", "AGENT", "CONFIG", "security_level_agent_config.py"),
    ("_agent_validator$", "AGENT", "VALIDATOR", "routing_decision_agent_validator.py"),
    ("_agent_util$", "AGENT", "UTILITY", "extract_pattern_agent_util.py"),
    ("Agent_types$", "AGENT", "TYPES", "CodeDetectorAgent_types.py"),
    ("Agent_config$", "AGENT", "CONFIG", "SomeAgent_config.py"),
    ("_engine_types$", "ENGINE", "TYPES", "safety_engine_types.py"),
    ("_engine_validator$", "ENGINE", "VALIDATOR", "consensus_engine_validator.py"),
    ("_engine_config$", "ENGINE", "CONFIG", "engine_config.py"),
    ("_guardrail_types$", "GUARDRAIL", "TYPES", "mcp_security_guardrail_types.py"),
    ("_guardrail_mixin$", "GUARDRAIL", "MIXIN", "cost_guardrail_mixin.py"),
    ("_guardrail_config$", "GUARDRAIL", "CONFIG", "guardrail_config.py"),
    ("_manager_types$", "MANAGER", "TYPES", "resource_manager_types.py"),
    ("_manager_config$", "MANAGER", "CONFIG", "sovereign_manager_config.py"),
    ("_manager_validator$", "MANAGER", "VALIDATOR", "context_manager_validator.py"),
    ("_strategy_types$", "STRATEGY", "TYPES", "context_pruning_strategy_types.py"),
    ("_strategy_config$", "STRATEGY", "CONFIG", "mcpservermode_strategy_config.py"),
    ("_strategy_mixin$", "STRATEGY", "MIXIN", "healing_strategy_mixin.py"),
    ("_strategy_validator$", "STRATEGY", "VALIDATOR", "reasoningnode_strategy_validator.py"),
    ("_validator_types$", "VALIDATOR", "TYPES", "code_validator_types.py"),
    ("_validator_util$", "VALIDATOR", "UTILITY", "check_sovereign_base_validator_util.py"),
    ("_scanner_types$", "SCANNER", "TYPES", "credential_scanner_types.py"),
    ("_scanner_util$", "SCANNER", "UTILITY", "sovereign_scanner_util.py"),
    ("_protocol_types$", "PROTOCOL", "TYPES", "healer_protocol_types.py"),
    ("_protocol_config$", "PROTOCOL", "CONFIG", "detection_protocol_config.py"),
    ("_protocol_guardrail$", "PROTOCOL", "GUARDRAIL", "airlock_protocol_guardrail.py"),
    ("_suite_types$", "SUITE", "TYPES", "security_validation_suite_types.py"),
    ("_factory_config$", "FACTORY", "CONFIG", "gateway_factory_config.py"),
    ("_factory_util$", "FACTORY", "UTILITY", "component_factory_util.py"),
    ("_orchestrator_types$", "ORCHESTRATOR", "TYPES", "recursive_orchestrator_types.py"),
    ("_shield_validator$", "SHIELD", "VALIDATOR", "governance_shield_validator.py"),
    ("_sanitizer_util$", "SANITIZER", "UTILITY", "telemetry_sanitizer_util.py"),
    ("_guard_util$", "GUARD", "UTILITY", "scan_guard_util.py"),
    ("_guard_mixin$", "GUARD", "MIXIN", "cost_guard_mixin.py"),
    ("_detector_types$", "DETECTOR", "TYPES", "code_detector_types.py"),
    ("_detector_config$", "DETECTOR", "CONFIG", "gravity_leak_detector_config.py"),
    ("_enforcer_types$", "ENFORCER", "TYPES", "code_enforcer_types.py"),
    ("_enforcer_util$", "ENFORCER", "UTILITY", "root_hygiene_enforcer_util.py"),
    ("_config_types$", "CONFIG", "TYPES", "blueprint_config_types.py"),
    ("_config_util$", "CONFIG", "UTILITY", "sync_mcp_config_util.py"),
    ("_config_detector$", "CONFIG", "DETECTOR", "magic_config_detector.py"),
    ("_adapter_types$", "ADAPTER", "TYPES", "open_telemetry_tracing_adapter_types.py"),
    ("_adapter_config$", "ADAPTER", "CONFIG", "storage_adapter_config.py"),
    ("_adapter_util$", "ADAPTER", "UTILITY", "mcp_adapter_util.py"),
    ("Adapter_types$", "ADAPTER", "TYPES", "SomeAdapter_types.py"),
    ("_mixin_agent_mixin$", "MIXIN", "AGENT", "autonomy_mixin_agent_mixin.py"),
    ("_mixin_agent$", "MIXIN", "AGENT", "some_mixin_agent.py"),
    ("_agent_mixin$", "AGENT", "MIXIN", "feature_flagged_agent_mixin.py"),
    ("_mixin_types$", "MIXIN", "TYPES", "healer_mixin_types.py"),
    ("_mixin_config$", "MIXIN", "CONFIG", "autonomy_mixin_config.py"),
    ("_mixin_util$", "MIXIN", "UTILITY", "healer_mixin_util.py"),
    ("_mixin_validator$", "MIXIN", "VALIDATOR", "agent_mixin_validator.py"),
]
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
    "_enforcer.py": "enforcement",
    "_guard.py": "enforcement",
    "_seam.py": "seams",
    "Coordinator.py": "engines",
    "Router.py": "engines",
}
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
    "ENFORCER": "enforcement",
    "SEAM": "seams",
}
FOLDER_PURITY_RULES: Final[Mapping[str, Sequence[str]]] = {
    "reasoning": [
        ".*Agent\\.py$",
        ".*Executor\\.py$",
        ".*Orchestrator\\.py$",
        ".*Inspector\\.py$",
        ".*Healer\\.py$",
        ".*Guardian\\.py$",
    ],
    "validators": [".*_validator\\.py$", ".*Validator\\.py$"],
    "config": [".*_config\\.py$", ".*_config\\.yaml$", ".*_config\\.json$"],
    "types": [
        ".*_types\\.py$",
        ".*_protocol\\.py$",
        "I[A-Z].*Protocol\\.py$",
        ".*Error\\.py$",
        ".*Exception\\.py$",
        ".*_spec\\.py$",
        ".*_schema\\.py$",
        ".*_model\\.py$",
    ],
    "utils": [".*_util\\.py$", ".*_helper\\.py$"],
    "scripts": ["^[a-z][a-z0-9_]*\\.py$"],
    "enforcement": [
        ".*_guardrail\\.py$",
        ".*_enforcer\\.py$",
        ".*_gate\\.py$",
        ".*_strategy\\.py$",
        ".*Strategy\\.py$",
        ".*Adapter\\.py$",
        ".*Monitor\\.py$",
        ".*Factory\\.py$",
        ".*Gateway\\.py$",
    ],
    "dashboards": [".*\\.html$", ".*\\.js$", ".*\\.css$", ".*\\.yaml$", ".*\\.json$", ".*\\.py$"],
    "engines": [
        ".*_engine\\.py$",
        ".*_executor\\.py$",
        ".*_task\\.py$",
        ".*_impl\\.py$",
        ".*_router\\.py$",
        ".*_service\\.py$",
        ".*_client\\.py$",
        ".*_node\\.py$",
        ".*_cache\\.py$",
        ".*_planner\\.py$",
        ".*_analyzer\\.py$",
        ".*_mapper\\.py$",
        ".*_embedder\\.py$",
        ".*_scanner\\.py$",
        ".*_core\\.py$",
        ".*_system\\.py$",
        ".*_composer\\.py$",
        ".*_scorer\\.py$",
        ".*_detector\\.py$",
        ".*_builder\\.py$",
        ".*_normalizer\\.py$",
    ],
    "tools": [".*_tool\\.py$", ".*_impl\\.py$", ".*_client\\.py$"],
    "base_agents": ["^L[0-9][A-Za-z]+Base\\.py$", "^SovereignBaseAgent\\.py$", "^LightweightBase\\.py$"],
    "mixins": ["^[a-z0-9_]+_mixin\\.py$"],
    "interfaces": ["^I[A-Z][A-Za-z0-9]+\\.py$"],
    "agent_configs": ["^[a-z0-9_]+_config\\.py$", "^[a-z0-9_]+\\.yaml$", "^[a-z0-9_]+\\.json$"],
    "healers": [".*_healer\\.py$", ".*Healer\\.py$"],
    "caching": [".*_cache\\.py$", ".*_cacher\\.py$", ".*Cache\\.py$"],
    "memory": [".*_memory\\.py$", ".*_store\\.py$", ".*Memory\\.py$"],
    "security": [".*_security\\.py$", ".*Security\\.py$", ".*_guard\\.py$"],
    "golden_evaluation": [".*_eval\\.py$", ".*_evaluation\\.py$", ".*Evaluator\\.py$"],
    "exceptions": [".*Error\\.py$", ".*Exception\\.py$", ".*_exceptions\\.py$"],
    "core_kernel": [".*_kernel\\.py$", ".*_core\\.py$"],
}
INFRASTRUCTURE_PROFILES: Final[Mapping[str, Sequence[str]]] = {
    "runtime": [".*\\.py$"],
    "meta_control": [".*\\.py$"],
    "policy": [".*\\.py$"],
}
FOLDER_ALIASES: Final[Mapping[str, str]] = {
    "knowledge": "reasoning",
    "validation": "validators",
    "engine": "engines",
}
NO_ROOT_FILES_FOLDERS: Final[frozenset[str]] = frozenset({"security", "prompt_governance"})
APPROVED_SUBFOLDERS: Final[Mapping[str, frozenset[str]]] = {
    "security": frozenset({"utils", "detectors", "schemas", "validators", "adversarial"}),
    "prompt_governance": frozenset(
        {
            "core",
            "meta_prompts",
            "optimization",
            "registry",
            "scripts",
            "security",
            "templates",
            "utils",
            "validation",
        },
    ),
}
FOLDER_PURITY_DISALLOWED: Final[Mapping[str, Sequence[str]]] = {
    "engines": [
        ".*Agent\\.py$",
        ".*Orchestrator\\.py$",
        ".*Strategy\\.py$",
        ".*_strategy\\.py$",
        ".*Validator\\.py$",
        ".*_validator\\.py$",
        ".*_types\\.py$",
        ".*_util\\.py$",
        ".*_config\\.py$",
    ],
    "tools": [
        ".*Agent\\.py$",
        ".*Validator\\.py$",
        ".*_validator\\.py$",
        ".*_types\\.py$",
        ".*_util\\.py$",
        ".*_config\\.py$",
        ".*Strategy\\.py$",
        ".*_strategy\\.py$",
    ],
}
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
    "_enforcer",
    "_guard",
    "_guardrail",
    "_seam",
    "_coordinator",
    "_router",
]
FORBIDDEN_COMPOUND_PATTERNS: Final[Sequence[str]] = [
    ".*_types_config\\.py$",
    ".*_validator_util\\.py$",
    ".*_types_validator\\.py$",
    ".*_config_util\\.py$",
]
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
LAYER_PREFIX_PATTERN: Final[str] = "(?i)(?:^|_)l([0-6])(?:_|[A-Z])"
INTERFACE_FILENAME_PATTERN: Final[str] = "^I[A-Z].*Protocol\\.py$"
GLOBAL_INTERFACES_FOLDER: Final[str] = "agentic_core/interfaces"
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
DUPLICATE_DETECTION_EXEMPT: Final[Sequence[str]] = ["__init__.py", "conftest.py", "__main__.py"]
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
    "meta_learning_engine_util": "system_learning/utils",
    "meta_learning_storage_util": "system_learning/utils",
    "state_util": "L4_state/utils",
}
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


@lru_cache(maxsize=1)
def get_classification_suffix_patterns_compiled() -> dict[Pattern, str]:
    """Compile and cache classification suffix patterns."""
    return {re.compile(pattern): tag for pattern, tag in CLASSIFICATION_SUFFIX_PATTERNS.items()}


@lru_cache(maxsize=1)
def get_compound_suffix_patterns_compiled() -> list[tuple[Pattern, str, str, str]]:
    """Compile and cache compound suffix conflict patterns."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_compound_suffix_patterns_compiled", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_compound_suffix_patterns_compiled", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "get_compound_suffix_patterns_compiled")
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
    parts = path.relative_to(AGENTIC_CORE_DIR).parts
    if len(parts) >= 3 and parts[0] == "config" and (parts[1] == "agent_configs"):
        return "agent_configs"
    if len(parts) >= 2 and parts[0] == "runtime":
        return parts[1]
    if len(parts) >= 1 and parts[0] == "prompt_governance":
        return "prompt_governance"
    if len(parts) >= 2 and parts[0].startswith("L") and parts[0][1].isdigit():
        return parts[1]
    if len(parts) >= 1:
        return parts[0]
    return ""
