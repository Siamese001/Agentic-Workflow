"""
Constants Module — LEAF NODE (Zero Internal Dependencies).

This module is the foundational leaf in the dependency graph for the
structure_blueprint package. It imports ONLY from the Python standard library
and agentic_core.L0_routing.config.path_constants (L0 is allowed for all layers).

All sibling modules (ssot.py, derived.py, etc.) import shared static data
from HERE, eliminating circular dependency patterns.

Contents:
  - SubfolderDefinition / TerritoryDefinition TypedDicts
  - LAYER_OVERRIDES (routing rules, suffix patterns, purpose strings per layer)
  - build_sovereign_territories() — DEPRECATED stub delegating to territories.py
  - Operational governance configs (HEALING_CONFIG, GRAVITY_CONFIG, etc.)

Directory existence is defined exclusively in territories.yaml via
territories.py — _constants.py carries only routing-relevant metadata.
"""

from __future__ import annotations

# Import canonical constants from L0 (L0 can be imported by any layer)
import os as _os
from collections.abc import Mapping, Sequence
from typing import Any, Final, TypedDict

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


APPS_TEST_SURFACE_DEFINITION: Final[Mapping[str, str]] = {
    "unit": "tests/unit/<app>",
    "integration": "tests/<app>",
    "contract": "tests/_apps_contract/test_<app>_*.py",
}


class SubfolderDefinition(TypedDict, total=False):
    purpose: str
    l4_specializations: Mapping[str, Sequence[str]]
    ast_signals: Mapping[str, Any]
    required_dirs: Sequence[str]
    forbidden_patterns: Sequence[str]
    allowed_suffixes: Sequence[str]
    forbidden_suffixes: Sequence[str]
    subfolders: Mapping[str, Any] | Sequence[str]
    notes: str
    naming_convention: str


class TerritoryDefinition(TypedDict, total=False):
    depth: int
    purpose: str
    subfolders: Mapping[str, Sequence[str] | Mapping[str, SubfolderDefinition]]
    ast_signals: Mapping[str, Mapping[str, Any]] | None
    volatile: bool | None
    required_dirs: Sequence[str] | None
    forbidden_patterns: Sequence[str] | None
    naming_convention: str | None
    allowed_suffixes: Mapping[str, Sequence[str]]
    forbidden_suffixes: Mapping[str, Sequence[str]]
    routing_rules: Mapping[str, str]
    notes: str
    forbidden_imports: Sequence[str]
    forbidden_capabilities: Sequence[str]


# ============================================================================
# LAYER-SPECIFIC OVERRIDES
# ============================================================================

LAYER_OVERRIDES: Final[Mapping[str, Mapping[str, Any]]] = {
    "L0_routing": {
        "purpose": (
            "Core Logic & Routing + Control-Plane Core — "
            "ingestion, route election, capability arbitration, policy-aware dispatch; "
            "plus boot integrity, SSOT discovery, and guardian runner health checks."
        ),
        "forbidden_capabilities": [
            "debate",
            "synthesis",
            "complex_reasoning",
            "multi_agent_coordination",
        ],
        "notes": (
            "L0 is the routing and minimal system-integrity control-plane. "
            "Agents must be low-level and deterministic. "
            "LCD+ canonical skeleton + scripts/ nuance."
        ),
        "routing_rules": {
            "*_guardian.py": "enforcement",
            "*_boot*.py": "enforcement",
            "*_routing*.py": "enforcement",
            "*_dispatch*.py": "enforcement",
            "*_config.py": "config",
            "*_types.py": "types",
            "*Agent.py": "reasoning",
        },
    },
    "L1_cognition": {
        "purpose": "Cognitive processing, reasoning, and thought patterns.",
        "notes": "LCD+ canonical skeleton. thought_engine/ and meta_learning/ DISSOLVED into 6 folders.",
        "reasoning_suffixes": [
            "_engine.py",
            "_manager.py",
            "_planner.py",
            "_mapper.py",
            "_strategy.py",
            "_agent.py",
        ],
        "config_suffixes": ["_config.py", "_settings.py"],
        "types_suffixes": ["_types.py", "_protocol.py", "_schema.py", "_contract.py"],
        "routing_rules": {
            "*_config.py": "config",
            "*_types.py": "types",
            "I*.py": "types",
            "*_engine.py": "reasoning",
            "*_planner.py": "reasoning",
            "*_strategy.py": "reasoning",
            "*Agent.py": "reasoning",
        },
    },
    "L2_execution": {
        "purpose": "The Hands: Tool execution, MCP clients, and sandboxed environments.",
        "notes": "LCD+ canonical skeleton + tools/ nuance. engine/mcp/sandbox DISSOLVED into 6 folders.",
        "reasoning_suffixes": [
            "_executor.py",
            "_runner.py",
            "_client.py",
            "_registry.py",
            "_manager.py",
            "_agent.py",
        ],
        "enforcement_suffixes": ["_env.py", "_jail.py", "_container.py", "_sandbox.py", "_agent.py"],
        "routing_rules": {
            "*_impl.py": "tools",
            "*_config.py": "config",
            "*_types.py": "types",
            "*_protocol.py": "types",
            "*_client.py": "reasoning",
            "*_executor.py": "reasoning",
            "*_registry.py": "reasoning",
            "*_sandbox.py": "enforcement",
            "*Agent.py": "reasoning",
        },
    },
    "L3_orchestration": {
        "purpose": "The Conductor: Workflow Management, DAGs, and Coordination.",
        "notes": "LCD+ canonical skeleton. engine/orchestrators/routers/strategies/patterns/diagnostics DISSOLVED.",
        "reasoning_suffixes": [
            "_engine.py",
            "_manager.py",
            "_inspector.py",
            "_policy.py",
            "_scanner.py",
            "_impl.py",
            "_agent.py",
            "_adapter.py",
            "_orchestrator.py",
            "_coordinator.py",
            "_handshake.py",
            "_system.py",
            "_marketplace.py",
            "_router.py",
            "_dispatcher.py",
            "_switch.py",
            "_delegator.py",
            "_strategy.py",
            "_pattern.py",
            "_fsm.py",
            "_flow.py",
            "_metrics.py",
            "_telemetry.py",
            "_report.py",
        ],
        "types_suffixes": ["_types.py", "_state.py", "_schema.py", "_model.py", "_protocol.py"],
        "routing_rules": {
            "*_orchestrator.py": "reasoning",
            "*_coordinator.py": "reasoning",
            "*_router.py": "reasoning",
            "*_dispatcher.py": "reasoning",
            "*_strategy.py": "reasoning",
            "*_pattern.py": "reasoning",
            "*_config.py": "config",
            "*_types.py": "types",
            "*_engine.py": "reasoning",
            "*_manager.py": "reasoning",
            "*_metrics.py": "reasoning",
            "*Agent.py": "reasoning",
        },
    },
    "L4_state": {
        "purpose": "The Memory: Databases, Knowledge Graphs, Ledgers, and State.",
        "notes": "LCD+ canonical skeleton + memory/ nuance. graph/ledger/schemas/contracts/session_manager DISSOLVED.",
        "enforcement_suffixes": [
            "_ledger.py",
            "_log.py",
            "_journal.py",
            "_audit.py",
            "_tracker.py",
            "_graph.py",
            "_node.py",
            "_edge.py",
        ],
        "utils_suffixes": ["_util.py", "_helper.py"],
        "routing_rules": {
            "*_store.py": "memory",
            "*_retriever.py": "memory",
            "*_cache.py": "memory",
            "*_graph.py": "enforcement",
            "*_ledger.py": "enforcement",
            "*_tracker.py": "enforcement",
            "*_config.py": "config",
            "*_types.py": "types",
            "*_util.py": "utils",
            "*Agent.py": "reasoning",
        },
    },
    "L5_safety": {
        "purpose": "The Guardian: Safety, Security, and Governance.",
        "notes": "LCD+ canonical skeleton. guardrails/gravity/cognition/governance/security/policy_engine/red_teaming/runtime/human_review DISSOLVED into reasoning/enforcement.",
        "config_suffixes": ["_config.py", "_blueprint.py", "_settings.py"],
        "reasoning_suffixes": [
            "_agent.py",
            "_strategy.py",
            "_processor.py",
            "_disposition.py",
            "_analyzer.py",
            "_healer.py",
            "_detector.py",
            "_executor.py",
            "_probe.py",
            "_adapter.py",
        ],
        "enforcement_suffixes": [
            "_guardrail.py",
            "_shield.py",
            "_firewall.py",
            "_sanitizer.py",
            "_agent.py",
            "_vault.py",
            "_gate.py",
            "_governor.py",
            "_policy.py",
            "_compliance.py",
            "_fixer.py",
            "_enforcer.py",
            "_refactorer.py",
            "_medic.py",
            "_surgeon.py",
            "_scanner.py",
            "_gatekeeper.py",
            "_breaker.py",
            "_guard.py",
            "_handler.py",
            "_queue.py",
            "_portal.py",
            "_workflow.py",
        ],
        "validators_suffixes": [
            "_validator.py",
            "_check.py",
            "_inspector.py",
            "_agent.py",
            "_categorizer.py",
            "_generator.py",
            "_canonicalizer.py",
        ],
        "utils_suffixes": ["_util.py", "_mixin.py", "_helper.py", "_visitor.py", "_extractor.py"],
        "routing_rules": {
            "*_fixer.py": "enforcement",
            "*_enforcer.py": "enforcement",
            "*_refactorer.py": "enforcement",
            "*_medic.py": "enforcement",
            "*_surgeon.py": "enforcement",
            "*_scanner.py": "enforcement",
            "*_gatekeeper.py": "enforcement",
            "*_breaker.py": "enforcement",
            "*_guardrail.py": "enforcement",
            "*_shield.py": "enforcement",
            "*_gate.py": "enforcement",
            "*_governor.py": "enforcement",
            "*_policy.py": "enforcement",
            "*_guard.py": "enforcement",
            "*_processor.py": "reasoning",
            "*_disposition.py": "reasoning",
            "*_strategy.py": "reasoning",
            "*_analyzer.py": "reasoning",
            "*_probe.py": "reasoning",
            "*_validator.py": "validators",
            "*_categorizer.py": "validators",
            "*_inspector.py": "validators",
            "*_config.py": "config",
            "*_types.py": "types",
            "*_protocol.py": "types",
            "*_util.py": "utils",
            "*_mixin.py": "utils",
            "*Agent.py": "reasoning",
        },
    },
    "L6_observability": {
        "purpose": "The Sensory Layer: Metrics, Logs, Tracing, and Dashboards.",
        "notes": "LCD+ canonical skeleton + dashboards/ nuance. metrics/logs/tracing/telemetry/reports/agents/engine DISSOLVED.",
        # Subfolder trees removed — territories.yaml is SSOT for directory existence.
        "reasoning_suffixes": [
            "_agent.py",
            "_metrics.py",
            "_gauge.py",
            "_counter.py",
            "_collector.py",
            "_logger.py",
            "_handler.py",
            "_formatter.py",
            "_sink.py",
            "_spy.py",
            "_tracer.py",
            "_span.py",
            "_context.py",
            "_propagator.py",
        ],
        "routing_rules": {
            "*_metrics.py": "reasoning",
            "*_collector.py": "reasoning",
            "*_logger.py": "reasoning",
            "*_handler.py": "reasoning",
            "*_tracer.py": "reasoning",
            "*_span.py": "reasoning",
            "*_dashboard.py": "dashboards",
            "*_config.py": "config",
            "*_types.py": "types",
            "*Agent.py": "reasoning",
        },
    },
}


# ============================================================================
# OPERATIONAL GOVERNANCE CONFIGURATION
# Merged from governance.py (2026-03-08) — one leaf, zero drift.
# ============================================================================

# (Removed 2026-05-02: build_sovereign_territories() deprecated stub +
#  171 lines of import-time lifecycle_trace_contract _emit_* side effects.
#  Plan: ssot-consolidation-cleanup-b7f3a1 Phases 1.1 + 1.2.
#  ADG verified: build_sovereign_territories had 0 consumers; emit calls
#  were import-time side effects only. Constants modules carry data, not
#  side effects.)

HEALING_CONFIG: Final[Mapping[str, int]] = {
    "max_rounds": int(_os.getenv("MAX_HEALING_ROUNDS", "10")),
    "max_per_file": int(_os.getenv("MAX_HEALING_PER_FILE", "8")),
    "global_budget": int(_os.getenv("GLOBAL_HEALING_BUDGET", "500")),
    "max_moves_per_run": 250,
    "max_shared_upgrades_per_run": 10,
    "max_fissions_per_run": 50,
    "dust_threshold": 40,
}

AGENT_RESILIENCE_CONFIG: Final[Mapping[str, int | float]] = {
    "retry_count": int(_os.getenv("AGENT_RETRY_COUNT", "3")),
    "backoff_base": float(_os.getenv("AGENT_RETRY_BACKOFF_BASE", "0.5")),
}

MISSION_CONFIG: Final[Mapping[str, bool | int]] = {
    "GRAVITY_SURGERY_ENABLED": True,
    "hierarchy_healing_enabled": True,
    "span_surgery_enabled": True,
    "fission_enabled": True,
    "run_full_mission": True,
    "run_hierarchy_healing": True,
    "run_gravity_refactor": True,
    "run_sprawl_surgery": True,
    "structural_only_mode": False,
    "timeout_seconds": int(_os.getenv("MISSION_TIMEOUT_SECONDS", "1800")),
}

MCP_CAPABILITIES: Final[Mapping[str, Mapping[str, bool | str]]] = {
    "router": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "marketplace_filter": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "filesystem": {"enabled": True, "path": "agentic_core.L4_state.filesystem"},
    "figma": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "fetch": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "semantic_cache": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
}

# GRAVITY_CONFIG: downstream_domains uses apps_* wildcard.
# Resolved at runtime by GRAVITY helpers that call _discover_apps_wildcard_folders().
GRAVITY_CONFIG: Mapping[str, Any] = {
    "enabled": True,
    "UPSTREAM_SOVEREIGN_ROOTS": ["agentic_core"],
    "downstream_domains": ["apps_*", "tests"],
    "exemptions": [],
}

GRAVITY_SURGERY_ENABLED: Any = GRAVITY_CONFIG["enabled"]
UPSTREAM_SOVEREIGN_ROOTS: Any = frozenset(GRAVITY_CONFIG["UPSTREAM_SOVEREIGN_ROOTS"])
DOWNSTREAM_ROOTS: Any = frozenset(GRAVITY_CONFIG["downstream_domains"])
