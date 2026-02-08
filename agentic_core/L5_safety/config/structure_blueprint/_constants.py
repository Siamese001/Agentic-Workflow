"""
Constants Module — LEAF NODE (Zero Internal Dependencies).

This module is the foundational leaf in the dependency graph for the
structure_blueprint package. It imports ONLY from the Python standard library.

All sibling modules (ssot.py, derived.py, etc.) import shared static data
from HERE, eliminating circular dependency patterns.

Contents:
  - SubfolderDefinition / TerritoryDefinition TypedDicts
  - LAYER_OVERRIDES (layer-specific template overrides)
  - build_sovereign_territories() and helpers
  - SOVEREIGN_TERRITORIES (materialized at import time)
  - ROOT_WHITELIST (materialized from SOVEREIGN_TERRITORIES keys)
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Final, TypedDict

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
            "allowed_suffixes": ["_types.py", "_protocol.py", "_schema.py", "_model.py"],
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
    "L0_maintenance": {
        "purpose": "Reflexive system health, boot integrity, and compliance checks.",
        "forbidden_capabilities": ["debate", "synthesis", "complex_reasoning", "multi_agent_coordination"],
        "notes": "L0 agents must be low-level and deterministic. LCD+ canonical skeleton + scripts/ nuance.",
        "extra_subfolders": {
            "scripts": {
                "purpose": "Maintenance and operational scripts (Zero-Ambiguity Standard)",
                "subfolders": {
                    ".github": {"purpose": "GitHub workflow scripts"},
                    "ci": {"purpose": "CI/CD pipeline scripts"},
                    "config": {"purpose": "Configuration scripts"},
                    "installation": {"purpose": "Installation and setup scripts"},
                    "general_scripts": {"purpose": "General maintenance scripts"},
                },
            },
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
        "extra_subfolders": {
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
            "memory": {
                "purpose": "Hot storage: vector stores, semantic caches, reasoning memory, experience buffers.",
                "allowed_suffixes": ["_store.py", "_retriever.py", "_cache.py", "_memory.py", "_db.py"],
                "subfolders": {
                    "semantic": {"purpose": "Semantic search stores (BM25, embeddings)."},
                },
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
    """Build the complete SOVEREIGN_TERRITORIES from templates + overrides."""
    territories: dict[str, Any] = {}

    # Build agentic_core with all layers
    agentic_core_subfolders: dict[str, Any] = {
        "base_agents": {
            "purpose": "STRICT IDENTITY ONLY. Sovereign base classes, layer bases, and decorators.",
            "notes": "No mixins, types, utils, or exceptions. Mixins are in agentic_core/mixins/.",
        },
    }

    # Add L0-L6 layers
    for layer in [
        "L0_maintenance",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    ]:
        agentic_core_subfolders[layer] = _build_layer_definition(layer)

    # Add non-layer subfolders
    agentic_core_subfolders.update(
        {
            "config": {
                "purpose": "Static configuration, feature flags, and default constants.",
                "subfolders": {
                    "core": {"purpose": "Core configuration files, settings, constants, and registries."},
                },
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
                    "version_registry": ["manifests", "locks", "lineage"],
                },
                "forbidden_patterns": ["L3_", "l3_"],
                "required_dirs": [
                    "agentic_core/prompt_governance/meta_prompts",
                    "agentic_core/prompt_governance/version_registry",
                ],
            },
            "runtime": {
                "purpose": "Active execution engine and primitives.",
                "subfolders": {
                    "engine": {"purpose": "Core execution engine and agent runtime."},
                    "types": {"purpose": "Shared type definitions, enums, and data models."},
                    "exceptions": {"purpose": "Exception hierarchies for runtime errors."},
                    "utils": {"purpose": "Shared runtime utilities and discovery logic."},
                    "config": {"purpose": "Runtime configuration and environment settings."},
                },
                "naming_convention": r"^[a-z][a-z0-9_]*_(util|types|exceptions|engine|config)\.py$",
            },
            "mixins": {
                "purpose": "ALL shared mixins and behavioral contracts. Canonical home for *_mixin.py and *_contract.py files.",
                "notes": "36 mixins migrated from base_agents/. FLAT: no subfolders allowed (contracts/ dissolved 2026-02-08).",
                "subfolders": {},
                "flat": True,
                "naming_convention": r"^[a-z][a-z0-9_]*_(mixin|contract|engine|storage|client_mixin)\.py$",
            },
            "utils": {
                "purpose": "Shared, passive helper functions. NO executable scripts (if __name__ == '__main__'). NO tests.",
                "forbidden_patterns": ["test_", "utilities_"],
                "notes": "Scripts go to L0_maintenance/scripts. Tests go to tests/.",
            },
            "semantic_memory": {"purpose": "Vector storage and semantic retrieval systems"},
            "knowledge": {
                "purpose": "Knowledge management and RAG systems.",
                "notes": "Domain root must NOT contain logic files. Only sub-directories (Leaf Node Rule).",
                "subfolders": {
                    "document_loaders": {"purpose": "Document ingestion and loader implementations."},
                    "research_cache": {"purpose": "Cached research results and retrieval data."},
                    "static_index": {"purpose": "Static knowledge indices and pre-built lookups."},
                    "engine": {"purpose": "RAG orchestration and retrieval logic."},
                    "healing": {"purpose": "Knowledge-domain healing strategies (wiki, docs)."},
                },
                "naming_convention": r"^[a-z][a-z0-9_]*_(loader|cache|index|orchestrator|engine|healer)\.py$",
            },
            "interfaces": {
                "purpose": "Standardized internal API contracts and protocols",
                "weight": 100,
                "naming_convention": "I*Protocol.py",
                "content_types": ["protocols", "abstract_interfaces", "type_contracts"],
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
                "L0MaintenanceBase",
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
            "purpose": "Processing engines and pipelines",
            "subfolders": [
                "base",
                "generation",
                "hops",
                "orchestration",
                "quality",
                "refinement",
                "retrieval",
                "safety",
                "utils",
            ],
        },
        "utils": {"purpose": "Utility functions", "subfolders": []},
        "scripts": {"purpose": "CLI entrypoints and one-off scripts", "subfolders": []},
        "domain": {"purpose": "Domain models and entities", "subfolders": ["config", "utils"]},
        "shared": {
            "purpose": "Shared components within the app",
            "subfolders": ["core", "reasoning", "tools", "utils"],
        },
        "system_flow": {"purpose": "Workflow and pipeline definitions", "subfolders": []},
        "asset_library": {"purpose": "Templates, wording, and static assets", "subfolders": []},
        "validation": {"purpose": "Validation rules and checkers", "subfolders": []},
        "logic_nodes": {"purpose": "Logic node implementations", "subfolders": []},
    }

    territories["apps_rg"] = {
        "depth": 3,
        "purpose": "Resume Generation Application domain.",
        "subfolders": apps_lcd_subfolders.copy(),
        "ast_signals": {"apps_rg/engines": {"keyword_signals": ["resume", "cv", "formatting"], "weight": 90}},
    }

    apps_lic_subfolders = apps_lcd_subfolders.copy()
    apps_lic_subfolders["reports"] = {"purpose": "Report generation and output", "subfolders": []}
    apps_lic_subfolders["tools"] = {"purpose": "Tool implementations", "subfolders": []}

    territories["apps_lic"] = {
        "depth": 3,
        "purpose": "LinkedIn Canonical application domain.",
        "subfolders": apps_lic_subfolders,
        "ast_signals": {
            "apps_lic/engines": {"keyword_signals": ["linkedin", "connection", "messaging"], "weight": 90},
        },
    }

    territories["apps_shared"] = {
        "depth": 2,
        "purpose": "Global utilities and shared logic accessible by all apps and core.",
        "subfolders": [
            "agents",
            "config",
            "core_components",
            "data",
            "tools",
            "utils",
            "common_utils",
            "mixins",
            "scripts",
            "integration",
            "llm",
        ],
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

    # Tests territory
    territories["tests"] = {
        "depth": 3,
        "purpose": "Universal test suites organized by Type then Domain.",
        "subfolders": {
            "unit": {
                "purpose": "Isolated logic tests mirroring source structure",
                "mirror_source": True,
                "subfolders": {
                    "agentic_core": {
                        "purpose": "Unit tests for agentic_core modules",
                        "subfolders": {
                            "L0_maintenance": [
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
                            "base_agents": [],
                            "utils": [],
                        },
                    },
                    "apps_lic": {"purpose": "Unit tests for apps_lic modules", "subfolders": {}},
                    "apps_rg": {"purpose": "Unit tests for apps_rg modules", "subfolders": {}},
                    "apps_shared": {"purpose": "Unit tests for apps_shared modules", "subfolders": {}},
                    "utils": {"purpose": "Utility tests", "subfolders": []},
                },
                "forbidden_zones": ["misc", "temp", "old", "deprecated", "archive", "scratch"],
            },
            "integration": {
                "purpose": "Component interaction tests mirroring source structure",
                "mirror_source": True,
                "subfolders": {},
                "forbidden_zones": ["misc", "temp", "old", "deprecated", "archive", "scratch"],
            },
            "e2e": {
                "purpose": "Full system user-flow simulations",
                "subfolders": ["scenarios", "flows", "snapshots"],
            },
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
            "fixtures": {"purpose": "Shared Pytest fixtures", "subfolders": ["data", "mocks", "factories"]},
            "snapshots": {"purpose": "Test snapshot data for comparison and regression testing"},
            "behavioral": {"purpose": "Behavioral and acceptance testing"},
            "stress": {"purpose": "Stress and load testing"},
            "performance": {"purpose": "Performance benchmarking and profiling tests"},
        },
        "volatile": False,
    }

    # Other territories
    territories["ops_scripts"] = {
        "depth": 2,
        "purpose": "Standalone utility scripts (formerly root scripts/).",
        "subfolders": [
            "ci",
            "maintenance",
            "security",
            "setup",
            "governance",
            "hooks",
            "simulations",
            "general",
        ],
    }

    territories["archives"] = {
        "depth": 3,
        "purpose": "Canonical repository for deprecated agents and transaction artifacts. Allows flexible recursive subfolders.",
        "subfolders": {},
        "volatile": False,
    }

    territories["data"] = {
        "depth": 2,
        "purpose": "Data storage and processing artifacts.",
        "subfolders": [
            "archives",
            "cache",
            "external",
            "freeze_reports",
            "golden",
            "golden_state",
            "logs",
            "manifests",
            "output",
            "processed",
            "prompt_governance",
            "prompt_libraries",
            "prompts",
            "raw",
            "sdks_mcps",
            "snapshots",
            "tasks",
        ],
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
                },
            },
            "architecture": {},
            "plans": {},
            "technical": {},
        },
    }

    territories[".github"] = {
        "depth": 2,
        "purpose": "GitHub Actions workflows and repository configuration.",
        "subfolders": [],
        "volatile": True,
    }
    territories[".gravity_state"] = {
        "depth": 2,
        "purpose": "Gravity system state tracking and metadata.",
        "subfolders": [],
        "volatile": True,
    }
    territories[".backup"] = {
        "depth": 2,
        "purpose": "Backup and recovery artifacts.",
        "subfolders": [],
        "volatile": True,
    }
    territories["config"] = {
        "depth": 2,
        "purpose": "Root-level configuration files and agent configs.",
        "subfolders": ["agent_configs"],
    }

    return territories


# Build and export at import time
SOVEREIGN_TERRITORIES: Final[Mapping[str, TerritoryDefinition]] = build_sovereign_territories()

# Materialized at import time — consumers get a real set, not a lazy proxy.
# This is the canonical set of top-level territory names.
ROOT_WHITELIST: set[str] = set(SOVEREIGN_TERRITORIES.keys())
