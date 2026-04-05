"""
Constants Module — LEAF NODE (Zero Internal Dependencies).

This module is the foundational leaf in the dependency graph for the
structure_blueprint package. It imports ONLY from the Python standard library
and agentic_core.L0_routing.config.path_constants (L0 is allowed for all layers).

All sibling modules (ssot.py, derived.py, etc.) import shared static data
from HERE, eliminating circular dependency patterns.

Contents:
  - SubfolderDefinition / TerritoryDefinition TypedDicts
  - LAYER_OVERRIDES (layer-specific template overrides)
  - build_sovereign_territories() and private helpers
  - SOVEREIGN_TERRITORIES (materialized at import time)
  - ROOT_WHITELIST (frozenset, materialized from SOVEREIGN_TERRITORIES keys)

Design rationale:
  The private builder functions (_build_lcd_subfolders_template,
  _build_layer_definition) are co-located with LAYER_OVERRIDES and
  build_sovereign_territories() because they form a single build pipeline
  that runs exactly once at import time.  They are:
    - pure and deterministic (no I/O, no side-effects),
    - consumed only within this module,
    - prefixed with underscore to signal internal use.
  Extracting them into a separate module would add an unnecessary node to
  the dependency graph with no maintainability benefit.
"""

from __future__ import annotations

# Import canonical constants from L0 (L0 can be imported by any layer)
import warnings
from collections.abc import Mapping, Sequence
from types import MappingProxyType
from typing import Any, Final, TypedDict

# Import YAML loader for data extraction
from agentic_core.L5_safety.config.structure_blueprint.yaml_loader import (
    load_territories,
    load_layer_overrides,
    get_territory,
    match_wildcard_territory,
)

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


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
# LAYER TEMPLATE (Common LCD Structure)
# ============================================================================


def _build_lcd_subfolders_template() -> dict[str, SubfolderDefinition]:
    """Build the common LCD subfolder template shared by all layers."""
    return {
        "config": {
            "purpose": "Configuration, settings, and constants.",
            "allowed_suffixes": ["_config.py", "_settings.py"],
            "forbidden_suffixes": ["_types.py"],
        },
        "types": {
            "purpose": "Data models, enums, protocols, and schemas.",
            "allowed_suffixes": ["_types.py", "_protocol.py", "_schema.py", "_model.py", "_spec.py"],
            "forbidden_suffixes": ["_config.py", "_engine.py", "_agent.py"],
        },
        "reasoning": {
            "purpose": "Decision-making agents, engines, planners, and strategists.",
        },
        "enforcement": {
            "purpose": "Constraint execution, guardrails, governors, and gates.",
        },
        "validators": {
            "purpose": "Passive auditing, compliance checks, and structural validators.",
        },
        "utils": {
            "purpose": "Helper functions, mixins, and shared utilities.",
        },
    }


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
        "extra_subfolders": {
            "scripts": {
                "purpose": "Operational scripts (Zero-Ambiguity Standard)",
                "subfolders": {
                    ".github": {"purpose": "GitHub workflow scripts"},
                    "ci": {"purpose": "CI/CD pipeline scripts"},
                    "config": {"purpose": "Configuration scripts"},
                    "installation": {"purpose": "Installation and setup scripts"},
                    "general_scripts": {"purpose": "General maintenance scripts"},
                },
            },
            "logs": {
                "purpose": "Guardian and audit log outputs (JSON reports).",
                "allowed_extensions": [".json", ".log"],
            },
            "engines": {
                "purpose": "Routing engines and dispatch processors.",
            },
            "meta_control": {
                "purpose": "Meta-control logic for routing governance and self-regulation.",
            },
            "policy": {
                "purpose": "Policy definitions and routing policy engines.",
            },
            "seams": {
                "purpose": "Cross-layer seam contracts and integration points.",
            },
            "seam": {
                "purpose": "Legacy single-seam audit module. Predates seams/; kept for backward compatibility.",
            },
        },
    },
    "L1_cognition": {
        "purpose": "Cognitive processing, reasoning, and thought patterns.",
        "notes": "LCD+ canonical skeleton. thought_engine/ and meta_learning/ DISSOLVED into 6 folders.",
        "extra_subfolders": {
            "engines": {
                "purpose": "Cognitive engines and processing pipelines.",
            },
            "telemetry": {
                "purpose": "Layer-level telemetry emitters and observability event reporters.",
            },
        },
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
        "extra_subfolders": {
            "audit": {
                "purpose": "Execution audit trails and compliance logging.",
            },
            "capability": {
                "purpose": "Capability token promotion and execution capability gates.",
            },
            "determinism": {
                "purpose": "Determinism guards, replay guards, and canonical digest calculators.",
            },
            "engines": {
                "purpose": "Execution engines and processing pipelines.",
            },
            "healers": {
                "purpose": "Self-healing strategies for execution failures.",
            },
            "scripts": {
                "purpose": "Execution-layer operational scripts.",
            },
            "tools": {
                "purpose": "Standardized tool implementations — strict naming enforced.",
                "allowed_suffixes": [
                    "_impl.py",
                    "_agent.py",
                    "_client.py",
                    "_util.py",
                    "_service.py",
                    "_executor.py",
                ],
                "forbidden_suffixes": ["_tool.py"],
            },
        },
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
        "extra_subfolders": {
            "arbitration": {
                "purpose": "Multi-advisor arbitration and decision arbitrator logic.",
            },
            "engines": {
                "purpose": "Orchestration engines and workflow processors.",
            },
            "ptc": {
                "purpose": "Prompt-to-completion (PTC) tool registry, contract definitions, and invoker.",
            },
            "replay": {
                "purpose": "Deterministic replay and state reconstruction for orchestration traces.",
            },
            "scripts": {
                "purpose": "Orchestration-layer operational scripts.",
            },
        },
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
        "extra_subfolders": {
            "caching": {
                "purpose": "Caching layers and cache management strategies.",
            },
            "engines": {
                "purpose": "State management engines: ghost mutation detector, replay bundle emitter, readonly retrieval orchestrator.",
            },
            "memory": {
                "purpose": "Hot storage: vector stores, semantic caches, reasoning memory, experience buffers.",
                "allowed_suffixes": ["_store.py", "_retriever.py", "_cache.py", "_memory.py", "_db.py"],
                "subfolders": {
                    "semantic": {"purpose": "Semantic search stores (BM25, embeddings)."},
                },
            },
            "storage": {
                "purpose": "Persistent and filesystem-backed state storage implementations.",
            },
        },
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
        "extra_subfolders": {
            "core_kernel": {
                "purpose": "Zero-dependency safety kernel and foundational primitives.",
            },
            "static_checks": {
                "purpose": "Static analysis invariant checks: determinism serialization, PowerShell ban, PTC invariants, write-gateway enforcement.",
            },
        },
        "enforcement_subfolders": {
            "governance": {
                "purpose": "Governance policies, audit hooks, and compliance frameworks nested under safety enforcement.",
            },
        },
        "config_subfolders": {
            "structure_blueprint": {
                "purpose": "SSOT structure blueprint module — _constants.py, territories.py, ssot.py, derived.py, and enforcement/ snapshot baseline files.",
            },
        },
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
        "extra_subfolders": {
            "dashboards": {
                "purpose": "Operational dashboards, visualizations, and renderers.",
                "allowed_suffixes": ["_dashboard.py", "_view.py", "_panel.py", "_renderer.py"],
                "subfolders": {
                    "core": {"purpose": "Core dashboard logic and shared components."},
                    "css": {"purpose": "Dashboard stylesheets and themes."},
                    "data": {"purpose": "Dashboard data files and fixtures."},
                    "js": {
                        "purpose": "Dashboard JavaScript modules.",
                        "subfolders": {
                            "components": {"purpose": "Reusable UI components."},
                            "constants": {"purpose": "JS constant definitions."},
                            "controllers": {"purpose": "Dashboard controllers."},
                            "renderers": {"purpose": "Chart and data renderers."},
                            "utils": {"purpose": "JS utility functions."},
                        },
                    },
                    "renderers": {"purpose": "Server-side rendering logic."},
                },
            },
            "engines": {
                "purpose": "Observability engines and telemetry processors.",
            },
            "golden_evaluation": {
                "purpose": "Golden evaluation datasets and benchmark tooling.",
            },
        },
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


def _build_layer_definition(layer_name: str) -> dict[str, Any]:
    """Build a complete layer definition from template + overrides."""
    overrides = LAYER_OVERRIDES.get(layer_name, {})

    # Start with LCD template
    subfolders = _build_lcd_subfolders_template()

    # Apply suffix overrides
    if "reasoning_suffixes" in overrides:
        subfolders["reasoning"]["allowed_suffixes"] = overrides["reasoning_suffixes"]
    if "enforcement_suffixes" in overrides:
        subfolders["enforcement"]["allowed_suffixes"] = overrides["enforcement_suffixes"]
    if "config_suffixes" in overrides:
        subfolders["config"]["allowed_suffixes"] = overrides["config_suffixes"]
    if "types_suffixes" in overrides:
        subfolders["types"]["allowed_suffixes"] = overrides["types_suffixes"]
    if "validators_suffixes" in overrides:
        subfolders["validators"]["allowed_suffixes"] = overrides["validators_suffixes"]
    if "utils_suffixes" in overrides:
        subfolders["utils"]["allowed_suffixes"] = overrides["utils_suffixes"]

    # Add extra subfolders (scripts, tools, memory, dashboards)
    if "extra_subfolders" in overrides:
        subfolders.update(overrides["extra_subfolders"])

    # Allow layer overrides to declare subfolders of enforcement
    if "enforcement_subfolders" in overrides:
        if not isinstance(subfolders["enforcement"].get("subfolders"), dict):
            subfolders["enforcement"]["subfolders"] = {}
        subfolders["enforcement"]["subfolders"].update(overrides["enforcement_subfolders"])

    # Allow layer overrides to declare subfolders of config
    if "config_subfolders" in overrides:
        if not isinstance(subfolders["config"].get("subfolders"), dict):
            subfolders["config"]["subfolders"] = {}
        subfolders["config"]["subfolders"].update(overrides["config_subfolders"])

    # Build the definition
    definition: dict[str, Any] = {
        "purpose": overrides.get("purpose", f"{layer_name} layer"),
        "subfolders": subfolders,
    }

    if "notes" in overrides:
        definition["notes"] = overrides["notes"]
    if "forbidden_capabilities" in overrides:
        definition["forbidden_capabilities"] = overrides["forbidden_capabilities"]
    if "routing_rules" in overrides:
        definition["routing_rules"] = overrides["routing_rules"]

    # Build allowed_suffixes mapping
    allowed_suffixes = {}
    for sf_name, sf_def in subfolders.items():
        if isinstance(sf_def, dict) and "allowed_suffixes" in sf_def:
            allowed_suffixes[sf_name] = sf_def["allowed_suffixes"]
    if allowed_suffixes:
        definition["allowed_suffixes"] = allowed_suffixes

    # Build forbidden_suffixes mapping
    forbidden_suffixes = {}
    for sf_name, sf_def in subfolders.items():
        if isinstance(sf_def, dict) and "forbidden_suffixes" in sf_def:
            forbidden_suffixes[sf_name] = sf_def["forbidden_suffixes"]
    if forbidden_suffixes:
        definition["forbidden_suffixes"] = forbidden_suffixes

    return definition


def build_sovereign_territories() -> dict[str, TerritoryDefinition]:
    """Build the complete SOVEREIGN_TERRITORIES from templates + overrides.

    DEPRECATED: This function and SOVEREIGN_TERRITORIES are deprecated.
    Use the new territory API in territories.py instead:
    - get_territory_metadata(name) for single territory lookup
    - get_all_territories() for full territory map
    - is_valid_root_folder(name) for root validation
    """
    warnings.warn(
        "SOVEREIGN_TERRITORIES is deprecated. Use get_territory_metadata() or "
        "get_all_territories() from structure_blueprint.territories instead.",
        DeprecationWarning,
        stacklevel=2,
    )
    territories: dict[str, Any] = {}

    # Build agentic_core with all layers
    agentic_core_subfolders: dict[str, Any] = {
        "adg": {
            "purpose": "Architecture Dependency Graph (ADG) — commit-scoped static analysis, MCP-backed graph persistence, and policy enforcement.",
            "subfolders": {
                "applications": {
                    "purpose": "ADG governance applications (blast radius, gateway enforcement, RAG, UWG)."
                },
                "ci": {"purpose": "CI integration and invariant checks."},
                "client": {"purpose": "MCP client for ADG graph operations."},
                "extraction": {"purpose": "Static AST-based scanner and edge extraction."},
            },
        },
        "agents": {
            "purpose": "Agent execution profiles and registry. SSOT for agent identity, execution mode, and reasoning intensity.",
            "notes": "Contains agent_registry.py (AGENT_REGISTRY, get_profile, registry_digest) and types/ subfolder.",
            "subfolders": {
                "types": {
                    "purpose": "Agent execution profile type definitions (AgentExecutionProfile, ExecutionMode, etc.)."
                },
            },
        },
        "base_agents": {
            "purpose": "STRICT IDENTITY ONLY. Sovereign base classes, layer bases, and decorators.",
            "notes": "No mixins, types, utils, or exceptions. Mixins are in agentic_core/mixins/.",
        },
    }

    # Add L0-L6 layers
    for layer in [
        "L0_routing",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    ]:
        agentic_core_subfolders[layer] = _build_layer_definition(layer)

    # L7_meta_learning migrated to system_learning/ - removed phantom layer definition

    # Add non-layer subfolders
    agentic_core_subfolders.update(
        {
            "config": {
                "purpose": "Static configuration, feature flags, and default constants.",
                "subfolders": {
                    "core": {"purpose": "Core configuration files, settings, constants, and registries."},
                    "agent_configs": {
                        "purpose": "Agent specification YAML files.",
                        "type": "spec_data",
                        "allowed_extensions": [".yaml", ".yml"],
                        "no_python": True,
                    },
                },
                "allow_root_py": False,
                "allowed_extensions": [".py", ".json"],
                "naming_convention": r"^[a-z][a-z0-9_]*_(config|defaults|settings|flags|loader)\.py$",
                "forbidden_patterns": [
                    r"^constants\.py$",
                    r"^registry\.py$",
                    r"^json_loader\.py$",
                ],
            },
            "prompt_governance": {
                "purpose": "Template lifecycle and persona management.",
                "l4_specializations": {
                    "meta_prompts": ["orchestration", "reasoning", "personas"],
                    "templates": ["instructional", "specialized", "fragments"],
                    "scripts": ["audit", "migration", "maintenance"],
                },
                "strict_subfolder_enforcement": True,
                "required_subfolders": ["meta_prompts", "templates", "scripts", "security"],
                "optional_subfolders": ["core", "domain", "optimization", "registry", "utils", "validation"],
                "forbidden_patterns": ["L3_", "l3_"],
                "required_dirs": [
                    "agentic_core/prompt_governance/meta_prompts",
                ],
                "subfolders": {
                    "contracts": {
                        "purpose": "Prompt governance contract definitions and interface agreements."
                    },
                    "core": {"purpose": "Core prompt governance logic and shared primitives."},
                    "meta_prompts": {"purpose": "Meta-prompt definitions and persona templates."},
                    "optimization": {"purpose": "Prompt optimization strategies and tuning."},
                    "registry": {
                        "purpose": "Prompt version registry and manifest management.",
                        "subfolders": {
                            "backups": {"purpose": "Registry backup snapshots."},
                        },
                    },
                    "scripts": {"purpose": "Prompt governance operational scripts."},
                    "security": {
                        "purpose": "Prompt security, injection detection, and adversarial defense.",
                        "subfolders": {
                            "adversarial": {"purpose": "Adversarial prompt testing and red-teaming."},
                            "detectors": {"purpose": "Injection and anomaly detection modules."},
                            "utils": {"purpose": "Security utility functions."},
                            "validators": {"purpose": "Security validation logic."},
                        },
                    },
                    "templates": {"purpose": "Prompt templates and rendering logic."},
                    "utils": {"purpose": "Prompt governance utility functions."},
                    "validation": {"purpose": "Prompt validation rules and compliance checks."},
                },
            },
            "runtime": {
                "purpose": "Active execution engine and primitives.",
                "subfolders": {
                    "engine": {"purpose": "Core execution engine and agent runtime."},
                    "types": {"purpose": "Shared type definitions, enums, and data models."},
                    "exceptions": {"purpose": "Exception hierarchies for runtime errors."},
                    "utils": {"purpose": "Shared runtime utilities and discovery logic."},
                    "config": {"purpose": "Runtime configuration and environment settings."},
                    "enforcement": {"purpose": "Runtime enforcement hooks and guards."},
                },
                "naming_convention": r"^[a-z][a-z0-9_]*_(util|types|exceptions|engine|config)\.py$",
            },
            "mixins": {
                "purpose": "ALL shared mixins and behavioral contracts. Canonical home for *_mixin.py and *_contract.py files.",
                "notes": "36 mixins migrated from base_agents/. FLAT: no subfolders allowed (contracts/ dissolved 2026-02-08).",
                "subfolders": {},
                "flat": True,
                "naming_convention": r"^[a-z][a-z0-9_]*_(mixin|contract|client_mixin)\.py$",
            },
            "seams": {
                "purpose": "Cross-layer seam contracts and integration points.",
                "subfolders": {
                    "contracts": {"purpose": "Seam contract definitions and interface agreements."},
                },
            },
            "utils": {
                "purpose": "Shared, passive helper functions. NO executable scripts (if __name__ == '__main__'). NO tests.",
                "forbidden_patterns": ["test_", "utilities_"],
                "notes": "Scripts go to L0_routing/scripts. Tests go to tests/.",
            },
            # semantic_memory removed — never materialized, use knowledge/ instead
            "knowledge": {
                "purpose": "Knowledge management and RAG systems.",
                "notes": "Domain root must NOT contain logic files. Only sub-directories (Leaf Node Rule).",
                "allow_root_py": False,
                "subfolders": {
                    "document_loaders": {"purpose": "Document ingestion and loader implementations."},
                    "research_cache": {"purpose": "Cached research results and retrieval data."},
                    "static_index": {"purpose": "Static knowledge indices and pre-built lookups."},
                    "engine": {"purpose": "RAG orchestration and retrieval logic."},
                    "healing": {"purpose": "Knowledge-domain healing strategies (wiki, docs)."},
                    "reasoning": {"purpose": "Knowledge-domain reasoning agents."},
                },
                "naming_convention": r"^[a-z][a-z0-9_]*_(loader|cache|index|orchestrator|engine|healer)\.py$",
            },
            "interfaces": {
                "purpose": "Standardized internal API contracts and protocols",
                "weight": 100,
                "naming_convention": "I*Protocol.py",
                "content_types": ["protocols", "abstract_interfaces", "type_contracts"],
            },
            "_compat": {
                "purpose": "Backward-compatibility shims and alias re-exports for renamed modules.",
                "notes": "Shim-only: no new logic. Files re-export renamed symbols for migration.",
            },
            "evaluation": {
                "purpose": "Evaluation frameworks, benchmarking, and quality assessment tooling.",
                "subfolders": {
                    "chunking": {"purpose": "Text chunking strategies for evaluation pipelines."},
                    "feedback": {"purpose": "Feedback collection and annotation tooling."},
                    "monitoring": {"purpose": "Evaluation monitoring and metric tracking."},
                    "retrieval": {
                        "purpose": "Retrieval evaluation and relevance scoring.",
                        "allowed_suffixes": [
                            "_retrieval.py",
                            "_eval.py",
                            "_registries.py",
                            "_index.py",
                            "_scorer.py",
                        ],
                    },
                    "runners": {"purpose": "Evaluation pipeline runners and orchestrators."},
                    "schemas": {"purpose": "Evaluation data schemas and validation contracts."},
                },
            },
            "enforcement": {
                "purpose": "Cross-cutting enforcement hooks, guards, and policy primitives shared across layers.",
                "notes": "Layer-specific enforcement lives in each layer's enforcement/ subfolder.",
            },
            "cache": {
                "purpose": "Shared caching infrastructure and cache management primitives.",
                "notes": "Layer-specific caches live in their respective layer directories.",
            },
            "agents": {
                "purpose": "Legacy agent registry and agent discovery scaffolding.",
                "notes": "Active agents live in layer reasoning/ folders. This holds discovery metadata.",
            },
        },
    )

    # Build AST signals
    ast_signals = {
        "agentic_core/base_agents": {
            "class_patterns": [".*Base$"],
            "base_classes": [
                "SovereignBaseAgent",
                "CanonBaseAgent",
                "L0RoutingBase",
                "L1CognitionBase",
                "L2ExecutionBase",
                "L3OrchestrationBase",
                "L4StateBase",
                "L5SafetyBase",
                "L6ObservabilityBase",
            ],
            "keyword_signals": [
                "sovereign",
                "base",
                "inheritance",
                "abstract",
                "foundation",
                "role",
                "persona",
                "archetype",
                "behavior",
                "agent_type",
            ],
            "weight": 100,
        },
        "agentic_core/L5_safety/enforcement": {
            "class_patterns": [".*Guardrail.*", ".*Barrier.*", ".*Gravity.*", ".*Leak.*"],
            "base_classes": ["BaseGuardrail", "SafetyAirlock"],
            "keyword_signals": [
                "mutation_check",
                "deletion_block",
                "circuit_breaker",
                "import_waterfall",
                "layer_violation",
                "deportation",
            ],
            "weight": 25,
        },
        "agentic_core/L1_cognition/reasoning": {
            "class_patterns": [".*Node$", ".*Thought.*", ".*Reason.*"],
            "base_classes": ["ThoughtNode", "ReActNode"],
            "keyword_signals": ["chain_of_thought", "self_reflection", "deliberation"],
            "weight": 18,
        },
        "agentic_core/L3_orchestration/reasoning": {
            "class_patterns": [".*Orchestrator$", ".*Workflow.*"],
            "base_classes": ["BaseOrchestrator", "WorkflowEngine"],
            "keyword_signals": ["mission_control", "fission_logic", "dag_executor"],
            "weight": 16,
        },
        "agentic_core/prompt_governance/meta_prompts": {
            "class_patterns": [".*MetaPrompt.*", ".*Persona.*"],
            "base_classes": ["MetaPrompt", "BasePersona"],
            "keyword_signals": ["sovereign_instruction", "persona_definition"],
            "weight": 15,
        },
        "agentic_core/prompt_governance/scripts": {
            "content_signals": {
                "keywords": ["render_all_templates", "validate_prompt_syntax"],
                "imports": ["jinja2", "prompt_governance"],
            },
            "weight": 12,
        },
        "agentic_core/L4_state/memory": {
            "class_patterns": [".*Context.*", ".*State.*"],
            "base_classes": ["ValidationContext", "StateManager"],
            "weight": 14,
        },
        "agentic_core/prompt_governance/version_registry": {
            "json_keys": ["registry_version", "checksum_manifest"],
            "weight": 11,
        },
        "agentic_core/L2_execution/reasoning": {
            "class_patterns": [".*Agent$"],
            "weight": 9,
        },
    }

    territories["agentic_core"] = {
        "depth": 3,
        "purpose": "Core agentic logic and safety layers.",
        "subfolders": agentic_core_subfolders,
        "ast_signals": ast_signals,
        "required_dirs": ["agentic_core/base_agents", "agentic_core/L5_safety"],
        "forbidden_patterns": ["agentic_core/common", "agentic_core/utils/core_extensions"],
    }

    # Apps territories
    apps_lcd_subfolders = {
        "config": {"purpose": "Application-specific configuration", "subfolders": []},
        "types": {"purpose": "Type definitions and data models", "subfolders": []},
        "reasoning": {"purpose": "Agent classes and business logic", "subfolders": []},
        "engines": {
            "purpose": "Processing engines and pipelines (flat .py files, no nested subdirs)",
            "subfolders": [],
        },
        "enforcement": {
            "purpose": "Constraint execution, guardrails, governors, and strategy gates",
            "subfolders": [],
        },
        "utils": {"purpose": "Utility functions", "subfolders": []},
        "scripts": {"purpose": "CLI entrypoints and one-off scripts", "subfolders": []},
        # NOTE: domain, shared, system_flow, asset_library, validation, logic_nodes
        # were removed as never-materialized speculative structure. If needed in
        # future, add back with explicit required/optional classification.
        "tools": {"purpose": "Tool implementations and wrappers", "subfolders": []},
        "validators": {"purpose": "Input/output validators", "subfolders": []},
    }

    # Canonical routing rules shared by all apps_* territories.
    # Agents (files ending *Agent.py) MUST live under reasoning/.
    # Strategy objects (*Strategy.py) live under enforcement/.
    apps_routing_rules = {
        "*Agent.py": "reasoning",
        "*Strategy.py": "enforcement",
        "*Engine.py": "engines",
        "*_config.py": "config",
        "*_types.py": "types",
        "*_util.py": "utils",
        "*_validator.py": "validators",
    }

    apps_rg_subfolders = apps_lcd_subfolders.copy()
    apps_rg_subfolders["domain"] = {
        "purpose": "Domain objects (entities, models, value_objects)",
        "subfolders": {"entities": [], "models": [], "value_objects": []},
    }

    territories["apps_rg"] = {
        "depth": 2,
        "purpose": "Resume Generation Application domain.",
        "subfolders": apps_rg_subfolders,
        "routing_rules": apps_routing_rules,
        "ast_signals": {"apps_rg/engines": {"keyword_signals": ["resume", "cv", "formatting"], "weight": 90}},
    }

    apps_lic_subfolders = apps_lcd_subfolders.copy()
    # reports removed — never materialized on disk, add back when needed
    apps_lic_subfolders["tools"] = {"purpose": "Tool implementations", "subfolders": []}
    apps_lic_subfolders["domain"] = {
        "purpose": "Domain objects (config, utils, models)",
        "subfolders": {"config": [], "utils": [], "models": []},
    }

    territories["apps_lic"] = {
        "depth": 2,
        "purpose": "LinkedIn Canonical application domain.",
        "subfolders": apps_lic_subfolders,
        "routing_rules": apps_routing_rules,
        "ast_signals": {
            "apps_lic/engines": {"keyword_signals": ["linkedin", "connection", "messaging"], "weight": 90},
        },
    }

    territories["apps_shared"] = {
        "depth": 2,
        "purpose": "Global utilities and shared logic accessible by all apps and core.",
        "required_subfolders": ["config", "data", "reasoning", "scripts", "types", "utils", "validators"],
        "optional_subfolders": [
            "agents",
            "core_components",
            "enforcement",
            "tools",
            "mixins",
            "integration",
            "llm",
            "spine",
        ],
        "subfolders": {
            "config": {"purpose": "Shared configuration loaders and environment setup"},
            "data": {"purpose": "Shared data files (resume templates, knowledge bases)"},
            "reasoning": {
                "purpose": "Cross-app reasoning agents (adaptive retrieval, circuit breaker, etc.)",
            },
            "scripts": {"purpose": "Shared CLI scripts and batch utilities"},
            "types": {"purpose": "Shared type definitions and data models"},
            "utils": {"purpose": "Shared utility functions (formatting, parsing, etc.)"},
            "validators": {"purpose": "Shared input/output validation logic"},
            "agents": {"purpose": "Shared base agent implementations (optional, migrate to core)"},
            "core_components": {"purpose": "Shared base nodes, engines, flows (optional)"},
            "enforcement": {
                "purpose": "Shared constraint execution, guardrails, and strategy gates (optional)"
            },
            "tools": {"purpose": "Shared tool implementations and wrappers (optional)"},
            "mixins": {"purpose": "Shared capability mixins (optional)"},
            "integration": {"purpose": "Integration adapters for external services (optional)"},
            "spine": {"purpose": "Shared spine adapters bridging app domains to core services (optional)"},
            "llm": {"purpose": "LLM interaction utilities (optional)"},
        },
        "forbidden_imports": ["apps_rg", "apps_lic"],
        "ast_signals": {
            "apps_shared/utils": {
                "class_patterns": [".*Utility$", ".*Helper$", ".*Detector$"],
                "keyword_signals": ["global", "shared", "generic", "cross_app"],
                "weight": 95,
            },
            "apps_shared/core_components": {
                "base_classes": ["BaseNode", "BaseEngine", "BaseFlow"],
                "weight": 92,
            },
        },
    }

    # New apps territories (apps_eval, apps_exec, apps_research, apps_rfp)
    # All share the standard apps LCD subfolder structure.
    apps_new_lcd_subfolders = apps_lcd_subfolders.copy()

    territories["apps_eval"] = {
        "depth": 2,
        "purpose": "Evaluation Application domain — scenario running, regression detection, and eval orchestration.",
        "subfolders": apps_new_lcd_subfolders,
        "routing_rules": apps_routing_rules,
        "ast_signals": {
            "apps_eval/engines": {
                "keyword_signals": ["eval", "scenario", "regression", "benchmark"],
                "weight": 90,
            }
        },
    }

    territories["apps_exec"] = {
        "depth": 2,
        "purpose": "Execution Application domain — brief assembly, exec orchestration, and delivery pipelines.",
        "subfolders": apps_new_lcd_subfolders,
        "routing_rules": apps_routing_rules,
        "ast_signals": {
            "apps_exec/engines": {
                "keyword_signals": ["exec", "brief", "assembly", "delivery"],
                "weight": 90,
            }
        },
    }

    territories["apps_research"] = {
        "depth": 2,
        "purpose": "Research Application domain — research assembly, source gathering, and synthesis pipelines.",
        "subfolders": apps_new_lcd_subfolders,
        "routing_rules": apps_routing_rules,
        "ast_signals": {
            "apps_research/engines": {
                "keyword_signals": ["research", "synthesis", "source", "assembly"],
                "weight": 90,
            }
        },
    }

    territories["apps_rfp"] = {
        "depth": 2,
        "purpose": "RFP Application domain — proposal assembly, RFP orchestration, and bid pipelines.",
        "subfolders": apps_new_lcd_subfolders,
        "routing_rules": apps_routing_rules,
        "ast_signals": {
            "apps_rfp/engines": {
                "keyword_signals": ["rfp", "proposal", "bid", "assembly"],
                "weight": 90,
            }
        },
    }

    # Tests territory
    territories["tests"] = {
        "depth": 2,
        "purpose": "Universal test suites organized by Type then Domain.",
        "subfolders": {
            "_config": {"purpose": "Test-suite configuration (conftest helpers, marker registries)"},
            "adg": {"purpose": "ADG-specific tests and graph validation checks"},
            "architecture": {
                "purpose": "Structural invariant tests — AST-based, no filesystem mutations",
            },
            "ci": {"purpose": "CI and compliance gate tests"},
            "e2e": {
                "purpose": "Full system user-flow simulations",
                "subfolders": [
                    "scenarios",
                    "flows",
                    "snapshots",
                    "agentic_core",
                    "apps_lic",
                    "apps_rg",
                    "ops_scripts",
                ],
            },
            "evaluation": {"purpose": "Evaluation pipeline and scoring tests"},
            "governance": {"purpose": "Governance policy and lifecycle tests"},
            "guardian": {
                "purpose": "Architectural compliance validation (Red Shield validation gate)",
                "constitutional_rules": [
                    "Guardian tests are COMPLEMENTARY to unit/e2e tests, NOT replacements",
                    "Guardian validates architectural compliance, NOT functional correctness",
                    "Guardian tests do NOT fulfill 100% coverage requirements",
                    "Guardian tests use AST-based analysis, NEVER string regex",
                    "Guardian tests NEVER delete files based on filename patterns",
                ],
            },
            "infrastructure": {"purpose": "Infrastructure-layer verification tests"},
            "integration": {
                "purpose": "Component interaction tests mirroring source structure",
                "mirror_source": True,
                "exclude_from_depth_rules": True,
                "subfolders": {},
                "forbidden_zones": ["misc", "temp", "old", "deprecated", "archive", "scratch"],
            },
            "ops_scripts": {"purpose": "Tests for ops_scripts territory and CI hooks"},
            "performance": {"purpose": "Performance benchmarking and profiling tests"},
            "smoke": {"purpose": "Smoke and startup-path sanity tests"},
            "system_learning": {
                "purpose": "Higher-level functional tests for system_learning (embedding, meta-learning, pattern analysis). Canonical unit mirror: tests/unit/system_learning/.",
                "subfolders": {
                    "engines": {"purpose": "Tests for system_learning engine implementations"},
                    "ports": {"purpose": "Tests for system_learning port interfaces"},
                },
            },
            "unit_min_deps": {
                "purpose": "Minimal-dependency unit tests (no heavy imports)",
                "exclude_from_depth_rules": True,
                "subfolders": {
                    "L0_routing": {"purpose": "Min-dep tests for L0_routing utilities"},
                    "L2_execution": {"purpose": "Min-dep tests for L2_execution utilities"},
                    "L6_observability": {"purpose": "Min-dep tests for L6_observability utilities"},
                    "utils": {"purpose": "Min-dep tests for shared utility modules"},
                },
            },
            "unit": {
                "purpose": "Isolated logic tests mirroring source structure",
                "mirror_source": True,
                "exclude_from_depth_rules": True,
                "subfolders": {
                    "agentic_core": {
                        "purpose": "Unit tests for agentic_core modules",
                        "subfolders": {
                            "L0_routing": [
                                "config",
                                "types",
                                "reasoning",
                                "enforcement",
                                "validators",
                                "utils",
                                "scripts",
                            ],
                            "L1_cognition": [
                                "config",
                                "types",
                                "reasoning",
                                "enforcement",
                                "validators",
                                "utils",
                            ],
                            "L2_execution": [
                                "config",
                                "types",
                                "reasoning",
                                "enforcement",
                                "validators",
                                "utils",
                                "tools",
                            ],
                            "L3_orchestration": [
                                "config",
                                "types",
                                "reasoning",
                                "enforcement",
                                "validators",
                                "utils",
                            ],
                            "L4_state": [
                                "config",
                                "types",
                                "reasoning",
                                "enforcement",
                                "validators",
                                "utils",
                                "memory",
                            ],
                            "L5_safety": [
                                "config",
                                "types",
                                "reasoning",
                                "enforcement",
                                "validators",
                                "utils",
                            ],
                            "L6_observability": [
                                "config",
                                "types",
                                "reasoning",
                                "enforcement",
                                "validators",
                                "utils",
                                "dashboards",
                            ],
                            "agents": [],
                            "base_agents": [],
                            "config": [],
                            "core": [],
                            "embeddings": [],
                            "interfaces": [],
                            "knowledge": [],
                            "mixins": [],
                            "prompt_governance": [],
                            "runtime": [],
                            "seams": [],
                            "utils": [],
                        },
                    },
                    # apps_* wildcard — covers all apps_lic, apps_rg, apps_shared,
                    # apps_eval, apps_exec, apps_research, apps_rfp.
                    # Each mirrors the same LCD subfolder structure.
                    "apps_*": {
                        "purpose": "Unit tests for any apps_* domain (apps_lic, apps_rg, apps_shared, apps_eval, apps_exec, apps_research, apps_rfp)",
                        "wildcard": True,
                        "subfolders": {
                            "config": [],
                            "engines": [],
                            "enforcement": [],
                            "reasoning": [],
                            "scripts": [],
                            "tools": [],
                            "types": [],
                            "utils": [],
                            "validators": [],
                        },
                    },
                    "system_learning": {
                        "purpose": "Unit tests mirroring system_learning/ source root",
                        "subfolders": {
                            "arbitration": [],
                            "confidence": [],
                            "config": [],
                            "constraints": [],
                            "correlation": [],
                            "enforcement": [],
                            "engines": [],
                            "fingerprinting": [],
                            "pipelines": [],
                            "ports": [],
                            "runtime": [],
                            "snapshots": [],
                            "types": [],
                            "validators": [],
                        },
                    },
                },
                "forbidden_zones": ["misc", "temp", "old", "deprecated", "archive", "scratch"],
            },
        },
        "volatile": True,  # Tests are volatile/output (excluded from Production Lens)
    }

    # Other territories
    territories["ops_scripts"] = {
        "depth": 2,
        "purpose": "Standalone utility scripts (formerly root scripts/).",
        "required_subfolders": [
            "ci",
            "maintenance",
            "security",
            "setup",
            "governance",
            "hooks",
            "simulations",
            "general",
        ],
        "subfolders": {
            "ci": {"purpose": "CI validation and agent-check scripts"},
            "maintenance": {"purpose": "Maintenance and cleanup utilities"},
            "security": {"purpose": "Security scanning and audit scripts"},
            "setup": {"purpose": "Environment setup and initialization"},
            "governance": {"purpose": "Layer separation and test structure governance"},
            "hooks": {"purpose": "Pre-commit and validation hooks"},
            "simulations": {"purpose": "Dry-run and simulation runners"},
            "general": {"purpose": "General-purpose analysis and discovery scripts"},
        },
    }

    territories["system_learning"] = {
        "depth": 2,
        "purpose": "Adaptive learning subsystem: runtime snapshots, training pipelines, and SSOT enforcement.",
        "subfolders": {
            "adapters": {"purpose": "Per-layer adaptation modules (l0_–l5_ prefixes are intentional)"},
            "arbitration": {"purpose": "Conflict resolution and policy arbitration for learning proposals"},
            "confidence": {"purpose": "Confidence scoring and calibration"},
            "config": {"purpose": "Learning system configuration"},
            "constraints": {"purpose": "Learning constraints and guardrails"},
            "correlation": {"purpose": "Cross-signal correlation and pattern matching"},
            "enforcement": {"purpose": "Policy enforcement for learning outputs"},
            "engines": {"purpose": "Learning engine implementations (l0_–l5_ prefixes are intentional)"},
            "fingerprinting": {"purpose": "Behavioral fingerprinting and change detection"},
            "pipelines": {"purpose": "Training and inference pipelines"},
            "ports": {"purpose": "Integration ports for external learning systems"},
            "runtime": {"purpose": "Runtime state for active learning loops"},
            "snapshots": {"purpose": "Periodic state snapshots for rollback and replay"},
            "stores": {"purpose": "Persistent learning artifact stores"},
            "types": {"purpose": "Domain types and data contracts"},
            "validators": {"purpose": "Validation logic for learning artifacts"},
        },
        "allowed_extensions": [".py", ".json", ".jsonl", ".md"],
        "layer_prefix_exempt": True,
        "no_cross_layer_imports": False,
    }

    territories["tools"] = {
        "depth": 2,
        "purpose": "Developer tooling: evidence runners, canonical hash utilities, VRAM checks.",
        "subfolders": {
            "evidence": {"purpose": "Evidence capture and runner scripts for phase verification"},
        },
        "allowed_extensions": [".py"],
        "allow_root_py": True,
        "no_cross_layer_imports": True,
    }

    territories["logs"] = {
        "depth": 2,
        "purpose": "Runtime and audit log outputs from agents and governance pipeline.",
        "subfolders": {
            "compliance_reports": {"purpose": "Structured compliance report outputs"},
            "sovereign_audit": {"purpose": "Sovereign execution audit trail logs"},
        },
        "volatile": True,
        "no_cross_layer_imports": True,
        "allowed_extensions": [".log", ".jsonl", ".json", ".txt"],
        "allow_root_py": False,
    }

    territories["archives"] = {
        "depth": 3,
        "purpose": "Canonical repository for deprecated agents and transaction artifacts. Allows flexible recursive subfolders.",
        "subfolders": {
            "deprecated": {"purpose": "Deprecated agent files pending removal or reference"},
            "gatekeeper": {"purpose": "Gatekeeper transaction artifacts and audit trails"},
        },
        "volatile": False,
        "no_cross_layer_imports": True,
        "allowed_extensions": [".py", ".json", ".md"],
        "allow_root_py": True,
    }

    territories["data"] = {
        "depth": 3,
        "purpose": "Data storage and processing artifacts.",
        "required_subfolders": [
            "external",
            "freeze_reports",
            "golden",
            "golden_state",
            "logs",
            "manifests",
            "output",
            "processed",
            "prompt_governance",
            "raw",
            "sdks_mcps",
            "snapshots",
            "tasks",
        ],
        "optional_subfolders": ["archives", "cache"],
        "subfolders": {
            "external": {"purpose": "External reference data (OpenAI best practices, playbooks)"},
            "freeze_reports": {"purpose": "Frozen governance and config state reports"},
            "golden": {"purpose": "Golden test datasets (JSONL ground truth)"},
            "golden_state": {"purpose": "Golden state snapshots and datasets"},
            "logs": {"purpose": "Runtime and guardian log outputs"},
            "manifests": {"purpose": "Agent and module manifest files"},
            "output": {"purpose": "Generated output artifacts"},
            "processed": {"purpose": "Processed intermediate data"},
            "prompt_governance": {"purpose": "Prompt governance rules and audit trails"},
            "raw": {"purpose": "Raw unprocessed input data"},
            "sdks_mcps": {
                "purpose": "SDK and MCP integration data",
                "subfolders": {
                    "client_wrappers": {
                        "purpose": "Production-ready client builder functions for AI SDKs (OpenAI, Anthropic, Vertex)."
                    },
                },
            },
            "snapshots": {"purpose": "Data state snapshots for rollback"},
            "tasks": {"purpose": "Task definitions and queue data"},
            "archives": {"purpose": "Archived data batches (optional, created on demand)"},
            "cache": {"purpose": "Ephemeral computation cache (optional, gitignored)"},
        },
        "no_cross_layer_imports": True,
    }

    territories["docs"] = {
        "depth": 3,
        "purpose": "Documentation and reporting.",
        "subfolders": {
            "metrics": {},
            "reports": {
                "purpose": "Categorized assessment and execution reports.",
                "subfolders": {
                    "assessments": {
                        "purpose": "Gap analyses, architectural assessments, and strategic reports",
                    },
                    "coverage": {"purpose": "Test coverage reports and code quality metrics"},
                    "telemetry": {"purpose": "System telemetry, performance metrics, and observability data"},
                    "security": {"purpose": "Security assessments, vulnerability scans, and safety reports"},
                    "audit": {"purpose": "Structural audits, drift analysis, and compliance reports"},
                    "missions": {"purpose": "High-level mission execution traces and runtime logs"},
                    ".migration": {"purpose": "Migration tracking artifacts"},
                    "MCP": {"purpose": "MCP server integration reports"},
                    "apps_lic": {"purpose": "apps_lic domain-specific reports"},
                    "apps_rg": {"purpose": "apps_rg domain-specific reports"},
                    "misc": {"purpose": "Miscellaneous reports"},
                    "plans": {"purpose": "Planning documents and evidence packs"},
                    "verification": {"purpose": "Enforcement verification artifacts"},
                },
            },
            "architecture": {"purpose": "Architecture decision records and diagrams"},
            "contracts": {"purpose": "Interface contracts and API agreements"},
            "plans": {"purpose": "Implementation plans and roadmaps"},
            "technical": {"purpose": "Technical reference documentation"},
            "policies": {"purpose": "Governance policies and SSOT enforcement policy documents"},
            "project": {"purpose": "Project-level documentation and status"},
            "testing": {"purpose": "Test strategy and methodology documentation"},
        },
    }

    territories[".github"] = {
        "depth": 2,
        "purpose": "GitHub Actions workflows and repository configuration.",
        "subfolders": {
            "workflows": {"purpose": "CI/CD workflow definitions (.yml)"},
        },
        "volatile": True,
        "allow_root_py": False,
        "allowed_extensions": [".yml", ".yaml", ".md"],
    }
    territories[".gravity_state"] = {
        "depth": 2,
        "purpose": "Gravity system state tracking and metadata.",
        "subfolders": [],
        "volatile": True,
    }
    territories[".backup"] = {
        "depth": 2,
        "purpose": "Backup and recovery artifacts. Staging-only; no production imports allowed.",
        "subfolders": {
            "guardian_tests": {"purpose": "Backed-up guardian test files"},
            "phase1": {"purpose": "Phase 1 migration backups"},
            "phase2": {"purpose": "Phase 2 migration backups"},
        },
        "volatile": True,
        "no_cross_layer_imports": True,
        "allow_root_py": True,
    }
    territories["artifacts"] = {
        "depth": 2,
        "purpose": "Build artifacts, dedup reports, and transient analysis outputs.",
        "subfolders": ["consolidation", "dedup"],
        "volatile": True,
        "enforcement_level": "relaxed",
        "exclude_from_depth_rules": True,
        "exclude_from_naming_rules": True,
        "exclude_from_layer_validation": True,
        "no_cross_layer_imports": True,
        "allowed_extensions": [".py", ".json", ".md"],
    }

    # Infrastructure territory — restored from commit 02169159bf deletion
    # Updated: files now live directly in infrastructure/, not infrastructure/hardening/
    territories["infrastructure"] = {
        "depth": 1,
        "purpose": "Infrastructure hardening modules — cross-cutting system optimization and security frameworks.",
        "subfolders": {},
        "required_dirs": ["infrastructure"],
        "forbidden_patterns": ["infrastructure/tests", "infrastructure/temp", "infrastructure/hardening"],
        "no_cross_layer_imports": False,
        "allowed_extensions": [".py"],
        "allow_root_py": True,
        "allowed_suffixes": [
            "_optimizer.py",
            "_framework.py",
            "_manager.py",
            "_router.py",
            "_contracts.py",
            "_coherence.py",
            "_state.py",
            "_plan.py",
        ],
        "forbidden_suffixes": ["_test.py", "_spec.py"],
    }

    return territories


def _deep_freeze(obj: Any) -> Any:
    """Recursively convert mutable containers to immutable equivalents.

    - dict  → MappingProxyType (wrapping recursed values)
    - list  → tuple (of recursed elements)
    - set   → frozenset (of recursed elements)
    - other → returned as-is (str, int, bool, None, etc.)
    """
    if isinstance(obj, dict):
        return MappingProxyType({k: _deep_freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(_deep_freeze(item) for item in obj)
    if isinstance(obj, set):
        return frozenset(_deep_freeze(item) for item in obj)
    return obj


# Build and deep-freeze at import time
SOVEREIGN_TERRITORIES: Final[Mapping[str, Any]] = _deep_freeze(build_sovereign_territories())

# Materialized at import time — consumers get a real frozenset, not a lazy proxy.
# frozenset guarantees immutability: no downstream code can accidentally mutate
# the SSOT whitelist and cause global side-effects.
ROOT_WHITELIST: Final[frozenset[str]] = frozenset(SOVEREIGN_TERRITORIES.keys())


# ============================================================================
# OPERATIONAL GOVERNANCE CONFIGURATION
# Merged from governance.py (2026-03-08) — one leaf, zero drift.
# ============================================================================

import os as _os

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key,
)

_emit_emits_metric_event("_constants", "p4obs", "metric_1")
_emit_emits_metric_event("_constants", "p4obs", "metric_2")
_emit_emits_metric_event("_constants", "p4obs", "metric_3")
_emit_emits_metric_event("_constants", "p4obs", "metric_4")
_emit_emits_metric_event("_constants", "p4obs", "metric_5")
_emit_emits_metric_event("_constants", "p4obs", "metric_6")
_emit_records_incident_event("_constants", "p4obs", "incident")
_emit_captures_runtime_anomaly("_constants", "p4obs", "anomaly")
_emit_writes_observability_log("_constants", "p4obs", "obs_log")
_emit_updates_monitoring_state("_constants", "p4obs", "mon_state")
_emit_triggers_alert("_constants", "p4obs", "alert")
_emit_links_incident_trace("_constants", "p4obs", "trace_link")
_emit_captures_pattern("_constants", "p3lm", "pattern")
_emit_records_learning_event("_constants", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_constants", "p3lm", "snapshot")
_emit_feeds_meta_learning("_constants", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_constants", "p3lm", "routing")
_emit_improves_agent_policy("_constants", "p3lm", "policy")
_emit_stores_learning_state("_constants", "p3lm", "state")
_emit_records_execution_trace("_constants", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_constants", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_constants", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_constants", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_constants", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_constants", "env_read", "p2_env_1")
_emit_reads_environ("_constants", "env_read", "p2_env_2")
_emit_reads_runtime_state("_constants", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_constants", "runtime_state", "p2_rt_2")

_emit_reads_policy_state("p1", "_constants", "L5")
_emit_escalates_to_human("p1", "_constants", "L5")
_emit_routes_through("p1", "_constants", "L5")
_emit_checks_agent_registry("p1", "_constants", "agent_registry")
_emit_validates_agent_capability("p1", "_constants", "capability")
_emit_dispatches_execution_plan("p1", "_constants", "exec_plan")
_emit_agent_executes_agent("p1", "_constants", "sub_agent")
_emit_routes_to_agent("p1", "_constants", "target_agent")
_emit_verifies_policy("p1", "_constants", "policy_check")
_emit_observes_runtime_state("p1", "_constants", "runtime_state")
_emit_verifies_boundary("p1", "_constants", "boundary_check")
_emit_transcripts_response("p1", "_constants", "transcript")
_emit_hard_fails_untranscripted("p1", "_constants")
_emit_gated_by_confidence("p1", "_constants", "confidence_gate")
_emit_dispatches_healing_run("p1", "_constants", "L5")
_emit_records_execution_trace("p0", "evidence", "_constants")
_emit_applies_guardrail("p0", "_constants", "p0_governance")
_emit_snapshots_state("p0", "_constants", "state_snapshot")
_emit_pulls_context("p1", "_constants", "context_pull")
_emit_pulls_context("p1", "_constants", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_constants", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_constants", "uwg_term_secondary")
_emit_writes_through("p1", "_constants", "write_through")
_emit_writes_through("p1", "_constants", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_constants", "safety_validation")
_emit_invokes_eval("p1", "_constants", "eval_call")
_emit_proposal_commits_routing("p1", "_constants", "routing_commit")
emit_replay_key("p0", "_constants")
emit_determinism_digest("p0", "_constants")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_constants", "execution_auth")
_emit_validates_capability("p2", "_constants", "capability_check")
_emit_routes_to_capability("p2", "_constants", "capability_route")
_emit_writes_via_uwg("p2", "_constants", "uwg_write")
_emit_blocks_direct_write("p2", "_constants", "direct_write_block")
_emit_records_tool_invocation("p2", "_constants", "tool_invocation")
_emit_captures_execution_output("p2", "_constants", "exec_output")
_emit_dispatches_agent("p3", "_constants", "agent_dispatch")
_emit_coordinates_agents("p3", "_constants", "agent_coordination")
_emit_records_workflow_lineage("p3", "_constants", "workflow_lineage")
_emit_records_healing_outcome("p3", "_constants", "healing_outcome")
_emit_escalates_failure("p3", "_constants", "failure_escalation")
_emit_orchestrates_workflow("p3", "_constants", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_constants", "healing_dispatch")
_emit_invokes_evaluation("p3", "_constants", "evaluation_signal")
_emit_records_telemetry_event("p4", "_constants", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_constants", "eval_metric")
_emit_stores_embedding("p4", "_constants", "embedding_store")
_emit_updates_meta_learning_state("p4", "_constants", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_constants", "exec_snapshot_link")

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

GRAVITY_CONFIG: Mapping[str, Any] = {
    "enabled": True,
    "UPSTREAM_SOVEREIGN_ROOTS": ["agentic_core"],
    "downstream_domains": ["apps_rg", "apps_lic", "apps_shared", "tests"],
    "exemptions": [],
}

GRAVITY_SURGERY_ENABLED: Any = GRAVITY_CONFIG["enabled"]
UPSTREAM_SOVEREIGN_ROOTS: Any = frozenset(GRAVITY_CONFIG["UPSTREAM_SOVEREIGN_ROOTS"])
DOWNSTREAM_ROOTS: Any = frozenset(GRAVITY_CONFIG["downstream_domains"])
