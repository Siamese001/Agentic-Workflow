from __future__ import annotations

# ruff: noqa: E501, E402
import os
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from re import Pattern
from typing import Any, Final, TypedDict

"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth-2 for Apps/Tests and Depth-3 for the Agentic Core.
[SSOT] This is the absolute source of truth for the entire repository structure.

CONSOLIDATED VERSION: Reduced redundancy while preserving all information.
[CRITICAL ANALYSIS] Upgraded from Any to strict typing with Final and Mapping for immutability.

CONSTITUTIONAL DESIGN PRINCIPLES (A+ HARDENED 2026-02-05):
=========================================================================

1. STRICT OBSOLESCENCE PROTOCOL:
   No file deletion based solely on naming. Requires AST-based zero-reference
   verification + fuzzy rename detection + manual approval.

2. TEST LAYERING PRINCIPLE:
   Guardian tests complement (never replace) unit/integration/E2E coverage.

3. STRUCTURAL INVARIANT (LEAF NODE RULE):
   Files permitted ONLY in leaf directories (no subfolders).
   Branch nodes: directories only.
   Exceptions: __init__.py, README.md, .gitignore, pyproject.toml, py.typed.

4. GUARDRAILS NAMING CONVENTION (CORRECTED 2026-02-07):
   All L5 safety guardrail agents in agentic_core/L5_safety/enforcement/
   MUST use PascalCase + "Agent.py" naming (e.g., PiiSanitizerAgent.py).
   This aligns with GOLDEN_BASELINE and standard agent naming conventions.
"""

# Lock down core mappings to prevent runtime mutation during mission execution
# [CRITICAL ANALYSIS] Windsurf's initial attempt lacked static enforcement;
# this locks down the configuration to prevent 'Junior AI' drift during autonomous healing cycles.
# [HARDENING] 2026-01-26: Converted all mutable containers to immutable

# ============================================================================
# SOVEREIGN TERRITORY SCHEMA (The Master Constitution)
# ============================================================================
# [SSOT 2026-01-27] Consolidates all 5 legacy registries into a single
# hierarchical model. This eliminates 'Architectural Split-Brain'.


class SubfolderDefinition(TypedDict, total=False):
    purpose: str
    l4_specializations: Mapping[str, Sequence[str]]
    ast_signals: Mapping[str, Any]
    required_dirs: Sequence[str]
    forbidden_patterns: Sequence[str]


class TerritoryDefinition(TypedDict):
    depth: int
    purpose: str
    subfolders: Mapping[str, Sequence[str] | Mapping[str, SubfolderDefinition]]
    ast_signals: Mapping[str, Mapping[str, Any]] | None
    volatile: bool | None
    required_dirs: Sequence[str] | None
    forbidden_patterns: Sequence[str] | None
    naming_convention: str | None  # e.g., "snake_case_agent" or "PascalCase_Agent"


STANDARD_LAYER_STRUCTURE: Final[list[str]] = [
    "config",  # The Layer's Laws: settings, constants, feature flags
    "types",  # The Layer's Language: Pydantic Models, Enums, Protocols, Dataclasses
    "reasoning",  # Decision-making agents: planners, analyzers, strategists, engines
    "enforcement",  # Constraint execution: guardrails, governors, gravity, gates
    "validators",  # Passive auditing: compliance checks, structural validators
    "utils",  # Shared tooling: mixins, helpers, formatters
]

SOVEREIGN_TERRITORIES: Final[Mapping[str, TerritoryDefinition]] = {
    "agentic_core": {
        "depth": 3,
        "purpose": "Core agentic logic and safety layers.",
        "subfolders": {
            "base_agents": {
                "purpose": "STRICT IDENTITY ONLY. Sovereign base classes, layer bases, and decorators.",
                "notes": "No mixins, types, utils, or exceptions. Mixins are in agentic_core/mixins/.",
            },
            # DISSOLVED: "domain" removed — deported to runtime/exceptions, runtime/types, config/core
            "L0_maintenance": {
                "purpose": "Reflexive system health, boot integrity, and compliance checks.",
                "forbidden_capabilities": [
                    "debate",
                    "synthesis",
                    "complex_reasoning",
                    "multi_agent_coordination",
                ],
                "notes": "L0 agents must be low-level and deterministic. LCD+ canonical skeleton + scripts/ nuance.",
                "subfolders": {
                    "config": {
                        "purpose": "Maintenance configuration, boot settings, and log config.",
                        "allowed_suffixes": ["_config.py", "_settings.py"],
                    },
                    "types": {
                        "purpose": "Maintenance data models, enums, and protocols.",
                        "allowed_suffixes": ["_types.py", "_protocol.py", "_schema.py"],
                    },
                    "reasoning": {
                        "purpose": "Decision-making maintenance agents (healing strategies, planners).",
                    },
                    "enforcement": {
                        "purpose": "Integrity enforcement, sensors, and deterministic validators.",
                    },
                    "validators": {
                        "purpose": "Maintenance validation logic and compliance checks.",
                    },
                    "utils": {
                        "purpose": "Maintenance helper functions and bootstrap utilities.",
                    },
                    # NUANCE: scripts/ preserved — home for operational scripts
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
                "subfolders": {
                    "config": {
                        "purpose": "Cognitive configuration (RAG config, ReAct config, meta-learning config).",
                        "allowed_suffixes": ["_config.py", "_settings.py"],
                        "forbidden_suffixes": ["_types.py", "_class.py"],
                    },
                    "types": {
                        "purpose": "Passive data structures, enums, protocols, and abstract interfaces only.",
                        "allowed_suffixes": ["_types.py", "_protocol.py", "_schema.py", "_contract.py"],
                        "forbidden_suffixes": ["_config.py", "_engine.py", "_agent.py"],
                    },
                    "reasoning": {
                        "purpose": "Decision-making cognitive agents, engines, planners, and meta-learning logic.",
                        "allowed_suffixes": [
                            "_engine.py",
                            "_manager.py",
                            "_planner.py",
                            "_mapper.py",
                            "_strategy.py",
                            "_agent.py",
                        ],
                    },
                    "enforcement": {
                        "purpose": "Cognitive constraint enforcement and guardrails.",
                    },
                    "validators": {
                        "purpose": "Cognitive validation logic (consensus, reasoning checks, meta-learning guardrails).",
                    },
                    "utils": {"purpose": "Cognitive helper functions."},
                },
                "allowed_suffixes": {
                    "reasoning": [
                        "_engine.py",
                        "_manager.py",
                        "_planner.py",
                        "_mapper.py",
                        "_strategy.py",
                        "_agent.py",
                    ],
                    "config": ["_config.py", "_settings.py"],
                    "types": ["_types.py", "_protocol.py", "_schema.py", "_contract.py"],
                },
                "forbidden_suffixes": {
                    "reasoning": ["_config.py", "_types.py"],
                    "config": ["_types.py", "_class.py"],
                    "types": ["_config.py", "_engine.py", "_agent.py"],
                },
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
                "subfolders": {
                    "config": {
                        "purpose": "Execution configuration and settings.",
                        "allowed_suffixes": ["_config.py", "_settings.py"],
                        "forbidden_suffixes": ["_types.py"],
                    },
                    "types": {
                        "purpose": "Execution data models, schemas, protocols, and error types.",
                        "allowed_suffixes": ["_types.py", "_schema.py", "_model.py", "_protocol.py"],
                        "forbidden_suffixes": ["_config.py", "_engine.py", "_agent.py"],
                    },
                    "reasoning": {
                        "purpose": "Execution engines, registries, orchestrators, and client managers.",
                        "allowed_suffixes": [
                            "_executor.py",
                            "_runner.py",
                            "_client.py",
                            "_registry.py",
                            "_manager.py",
                            "_agent.py",
                        ],
                    },
                    "enforcement": {
                        "purpose": "MCP sovereign agents, sandbox enforcement, and execution gates.",
                        "allowed_suffixes": [
                            "_env.py",
                            "_jail.py",
                            "_container.py",
                            "_sandbox.py",
                            "_agent.py",
                        ],
                    },
                    "validators": {
                        "purpose": "Execution validation logic and tool compliance checks.",
                    },
                    "utils": {
                        "purpose": "Execution helper functions and shared utilities.",
                    },
                    # NUANCE: tools/ preserved — standardized tool implementations
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
                "allowed_suffixes": {
                    "reasoning": [
                        "_executor.py",
                        "_runner.py",
                        "_client.py",
                        "_registry.py",
                        "_manager.py",
                        "_agent.py",
                    ],
                    "enforcement": ["_env.py", "_jail.py", "_container.py", "_sandbox.py", "_agent.py"],
                    "config": ["_config.py", "_settings.py"],
                    "types": ["_types.py", "_schema.py", "_model.py", "_protocol.py"],
                    "tools": [
                        "_impl.py",
                        "_agent.py",
                        "_client.py",
                        "_util.py",
                        "_service.py",
                        "_executor.py",
                    ],
                },
                "forbidden_suffixes": {
                    "reasoning": ["_config.py", "_types.py"],
                    "config": ["_types.py", "_tool.py"],
                    "types": ["_config.py", "_engine.py", "_agent.py"],
                    "tools": ["_config.py", "_types.py", "_tool.py"],
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
                "subfolders": {
                    "config": {
                        "purpose": "Orchestration configuration and settings.",
                        "allowed_suffixes": ["_config.py", "_settings.py"],
                        "forbidden_suffixes": ["_types.py"],
                    },
                    "types": {
                        "purpose": "Orchestration data models, schemas, protocols, and state types.",
                        "allowed_suffixes": [
                            "_types.py",
                            "_state.py",
                            "_schema.py",
                            "_model.py",
                            "_protocol.py",
                        ],
                        "forbidden_suffixes": ["_config.py", "_engine.py"],
                    },
                    "reasoning": {
                        "purpose": "Decision-making: engines, orchestrators, routers, strategies, patterns, diagnostics.",
                        "allowed_suffixes": [
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
                    },
                    "enforcement": {
                        "purpose": "Orchestration constraint enforcement and coordination gates.",
                    },
                    "validators": {
                        "purpose": "Orchestration validation logic and workflow compliance checks.",
                    },
                    "utils": {
                        "purpose": "Orchestration helper functions and shared utilities.",
                    },
                },
                "allowed_suffixes": {
                    "reasoning": [
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
                        "_strategy.py",
                        "_pattern.py",
                        "_fsm.py",
                        "_flow.py",
                        "_metrics.py",
                    ],
                    "config": ["_config.py", "_settings.py"],
                    "types": ["_types.py", "_state.py", "_schema.py", "_model.py", "_protocol.py"],
                },
                "forbidden_suffixes": {
                    "reasoning": ["_config.py", "_types.py"],
                    "config": ["_types.py", "_router.py"],
                    "types": ["_config.py", "_engine.py"],
                },
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
                "subfolders": {
                    "config": {
                        "purpose": "State configuration and settings.",
                        "allowed_suffixes": ["_config.py", "_settings.py"],
                        "forbidden_suffixes": ["_types.py"],
                    },
                    "types": {
                        "purpose": "State data models, schemas, protocols, and error types.",
                        "allowed_suffixes": ["_types.py", "_schema.py", "_model.py", "_protocol.py"],
                        "forbidden_suffixes": ["_config.py", "_engine.py"],
                    },
                    "reasoning": {
                        "purpose": "State decision-making agents and planners.",
                    },
                    "enforcement": {
                        "purpose": "Ledger enforcement, graph integrity, change tracking, and audit trails.",
                        "allowed_suffixes": [
                            "_ledger.py",
                            "_log.py",
                            "_journal.py",
                            "_audit.py",
                            "_tracker.py",
                            "_graph.py",
                            "_node.py",
                            "_edge.py",
                        ],
                    },
                    "validators": {
                        "purpose": "State validation logic and compliance checks.",
                    },
                    "utils": {
                        "purpose": "State utility functions.",
                        "allowed_suffixes": ["_util.py", "_helper.py"],
                    },
                    # NUANCE: memory/ preserved — hot storage and semantic retrieval
                    "memory": {
                        "purpose": "Hot storage: vector stores, semantic caches, reasoning memory, experience buffers.",
                        "allowed_suffixes": [
                            "_store.py",
                            "_retriever.py",
                            "_cache.py",
                            "_memory.py",
                            "_db.py",
                        ],
                        "subfolders": {
                            "semantic": {"purpose": "Semantic search stores (BM25, embeddings)."},
                        },
                    },
                },
                "allowed_suffixes": {
                    "memory": ["_store.py", "_retriever.py", "_cache.py", "_memory.py", "_db.py"],
                    "enforcement": [
                        "_ledger.py",
                        "_log.py",
                        "_journal.py",
                        "_audit.py",
                        "_tracker.py",
                        "_graph.py",
                        "_node.py",
                        "_edge.py",
                    ],
                    "config": ["_config.py", "_settings.py"],
                    "types": ["_types.py", "_schema.py", "_model.py", "_protocol.py"],
                    "utils": ["_util.py", "_helper.py"],
                },
                "forbidden_suffixes": {
                    "memory": ["_config.py", "_types.py"],
                    "config": ["_types.py", "_store.py"],
                    "types": ["_config.py", "_store.py"],
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
                "subfolders": {
                    "config": {
                        "purpose": "The Law: blueprint config, safety settings, and constitutional definitions.",
                        "allowed_suffixes": ["_config.py", "_blueprint.py", "_settings.py"],
                    },
                    "types": {
                        "purpose": "Safety data models, schemas, protocols, and error types.",
                        "allowed_suffixes": ["_types.py", "_schema.py", "_model.py", "_protocol.py"],
                    },
                    "reasoning": {
                        "purpose": "Decision-making safety agents: analyzers, strategists, policy engines, red teaming, cognition.",
                        "allowed_suffixes": [
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
                    },
                    "enforcement": {
                        "purpose": "Constraint execution: guardrails, governors, gravity, gates, shields, security, runtime guards.",
                        "naming_convention": "PascalCaseAgent",
                        "allowed_suffixes": [
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
                    },
                    "validators": {
                        "purpose": "Passive auditing: structural validators, compliance checks, classification agents.",
                        "allowed_suffixes": [
                            "_validator.py",
                            "_check.py",
                            "_inspector.py",
                            "_agent.py",
                            "_categorizer.py",
                            "_generator.py",
                            "_canonicalizer.py",
                        ],
                    },
                    "utils": {
                        "purpose": "Safety utility functions, mixins, and helpers.",
                        "allowed_suffixes": [
                            "_util.py",
                            "_mixin.py",
                            "_helper.py",
                            "_visitor.py",
                            "_extractor.py",
                        ],
                    },
                },
                "allowed_suffixes": {
                    "config": ["_config.py", "_blueprint.py", "_settings.py"],
                    "types": ["_types.py", "_schema.py", "_model.py", "_protocol.py"],
                    "reasoning": [
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
                    "enforcement": [
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
                    ],
                    "validators": [
                        "_validator.py",
                        "_check.py",
                        "_inspector.py",
                        "_agent.py",
                        "_categorizer.py",
                        "_generator.py",
                        "_canonicalizer.py",
                    ],
                    "utils": ["_util.py", "_mixin.py", "_helper.py", "_visitor.py", "_extractor.py"],
                },
                "forbidden_suffixes": {
                    "config": ["_types.py", "_validator.py"],
                    "types": ["_config.py", "_validator.py"],
                    "validators": ["_config.py", "_types.py"],
                    "reasoning": ["_config.py", "_types.py"],
                    "enforcement": ["_config.py", "_types.py"],
                },
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
                "subfolders": {
                    "config": {
                        "purpose": "Observability configuration and settings.",
                        "allowed_suffixes": ["_config.py", "_settings.py"],
                    },
                    "types": {
                        "purpose": "Observability data models (ExecutionMetrics, AggregatedMetrics).",
                        "allowed_suffixes": ["_types.py", "_schema.py", "_model.py"],
                    },
                    "reasoning": {
                        "purpose": "Active observability agents, monitoring engines, analysis, and synthesis.",
                        "allowed_suffixes": [
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
                    },
                    "enforcement": {
                        "purpose": "Compliance enforcement, audit reporting, and observability gates.",
                    },
                    "validators": {
                        "purpose": "Observability validation logic and compliance checks.",
                    },
                    "utils": {"purpose": "Observability utility functions."},
                    # NUANCE: dashboards/ preserved — operational dashboards
                    "dashboards": {
                        "purpose": "Operational dashboards, visualizations, and renderers.",
                        "allowed_suffixes": ["_dashboard.py", "_view.py", "_panel.py", "_renderer.py"],
                    },
                },
                "allowed_suffixes": {
                    "reasoning": [
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
                    "dashboards": ["_dashboard.py", "_view.py", "_panel.py", "_renderer.py"],
                    "config": ["_config.py", "_settings.py"],
                    "types": ["_types.py", "_schema.py", "_model.py"],
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
            "config": {
                "purpose": "Static configuration, feature flags, and default constants.",
                "subfolders": {
                    "core": {"purpose": "Core configuration files, settings, constants, and registries."},
                },
                "allowed_extensions": [".py", ".json"],
                "naming_convention": r"^[a-z][a-z0-9_]*_(config|defaults|settings|flags|loader)\.py$",
                "forbidden_patterns": [
                    r"^constants\.py$",  # Must be constants_config.py
                    r"^registry\.py$",  # Must be registry_config.py
                    r"^json_loader\.py$",  # Must be config_loader.py (domain-aligned)
                ],
            },
            # DISSOLVED: "schemas" removed — contents deported to runtime/types, L4/contracts, L6/engine+types
            "prompt_governance": {
                "purpose": "Template lifecycle and persona management.",
                "l4_specializations": {
                    "meta_prompts": ["orchestration", "reasoning", "personas"],
                    "templates": ["instructional", "specialized", "fragments"],
                    "scripts": ["audit", "migration", "maintenance"],
                    "version_registry": ["manifests", "locks", "lineage"],
                },
                # VIOLATION PREVENTION: Explicitly block legacy L3_ prefixing
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
                "purpose": "ALL shared mixins and behavioral contracts. Canonical home for *_mixin.py files.",
                "notes": "36 mixins migrated from base_agents/. configuration_mixin.py migrated from config/core/.",
                "subfolders": {
                    "contracts": {"purpose": "Abstract interfaces and behavioral contracts."},
                },
                "naming_convention": r"^[a-z][a-z0-9_]*_(mixin|contract)\.py$",
            },
            "utils": {
                "purpose": "Shared, passive helper functions. NO executable scripts (if __name__ == '__main__'). NO tests.",
                "forbidden_patterns": ["test_", "utilities_"],
                "notes": "Scripts go to L0_maintenance/scripts. Tests go to tests/.",
            },
            # DEPRECATED: "patterns" territory removed - evacuate to base_agents
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
                "naming_convention": "I*Protocol.py",  # Must start with I, end with Protocol.py
                "content_types": ["protocols", "abstract_interfaces", "type_contracts"],
            },
        },
        "ast_signals": {
            # --- CONSTITUTIONAL FOUNDATION (Weight 100) ---
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
                # GRAVITY REDIRECTED: Keywords from deprecated patterns/agent_roles
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
            # --- L5 SAFETY: MAXIMUM DEFENSIVE PRIORITY (Weight 22-25) ---
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
            # --- L1 COGNITION: REASONING SUPERIORITY (Weight 18) ---
            "agentic_core/L1_cognition/reasoning": {
                "class_patterns": [".*Node$", ".*Thought.*", ".*Reason.*"],
                "base_classes": ["ThoughtNode", "ReActNode"],
                "keyword_signals": ["chain_of_thought", "self_reflection", "deliberation"],
                "weight": 18,
            },
            # --- L3 ORCHESTRATION: STRATEGIC COORDINATION (Weight 16) ---
            "agentic_core/L3_orchestration/reasoning": {
                "class_patterns": [".*Orchestrator$", ".*Workflow.*"],
                "base_classes": ["BaseOrchestrator", "WorkflowEngine"],
                "keyword_signals": ["mission_control", "fission_logic", "dag_executor"],
                "weight": 16,
            },
            # --- DOMAIN SPECIALIZATION: PROMPT GOVERNANCE (Weight 12-15) ---
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
            # --- L4 STATE: PERSISTENCE INTEGRITY (Weight 11-14) ---
            "agentic_core/L4_state/memory": {
                "class_patterns": [".*Context.*", ".*State.*"],
                "base_classes": ["ValidationContext", "StateManager"],
                "weight": 14,
            },
            "agentic_core/prompt_governance/version_registry": {
                "json_keys": ["registry_version", "checksum_manifest"],
                "weight": 11,
            },
            # --- L0/L2 BASELINE: GENERIC UTILITIES (Weight 9) ---
            "agentic_core/L2_execution/reasoning": {
                "class_patterns": [".*Agent$"],
                "weight": 9,
            },
        },
        "required_dirs": ["agentic_core/base_agents", "agentic_core/L5_safety"],
        "forbidden_patterns": [
            "agentic_core/common",
            "agentic_core/utils/core_extensions",
        ],
    },
    # ============================================================================
    # === APPS_* LCD STRUCTURE (Mirrored between apps_rg and apps_lic) ===
    # ============================================================================
    # Both apps_rg and apps_lic follow the same LCD-inspired structure:
    # - config/: Application-specific configuration
    # - types/: Type definitions and data models
    # - reasoning/: Agent classes and business logic
    # - engines/: Processing engines and pipelines
    # - utils/: Utility functions
    # - scripts/: CLI entrypoints and one-off scripts
    # - domain/: Domain models and entities
    # - shared/: Shared components within the app
    # - system_flow/: Workflow and pipeline definitions
    # - asset_library/: Templates, wording, and static assets
    "apps_rg": {
        "depth": 3,
        "purpose": "Resume Generation Application domain.",
        "subfolders": {
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
        },
        "ast_signals": {"apps_rg/engines": {"keyword_signals": ["resume", "cv", "formatting"], "weight": 90}},
    },
    "apps_lic": {
        "depth": 3,
        "purpose": "LinkedIn Canonical application domain.",
        "subfolders": {
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
            "reports": {"purpose": "Report generation and output", "subfolders": []},
            "tools": {"purpose": "Tool implementations", "subfolders": []},
        },
        "ast_signals": {
            "apps_lic/engines": {"keyword_signals": ["linkedin", "connection", "messaging"], "weight": 90},
        },
    },
    "apps_shared": {
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
        # [HARDENING] 2026-01-27: Strict Shared-Layer Independence
        "forbidden_imports": ["apps_rg", "apps_lic"],
        "ast_signals": {
            "apps_shared/utils": {
                "class_patterns": [".*Utility$", ".*Helper$", ".*Detector$"],
                "keyword_signals": ["global", "shared", "generic", "cross_app"],
                "weight": 95,  # Constitutional priority for shared code
            },
            "apps_shared/core_components": {
                "base_classes": ["BaseNode", "BaseEngine", "BaseFlow"],
                "weight": 92,
            },
        },
    },
    "tests": {
        "depth": 3,
        "purpose": "Universal test suites organized by Type then Domain.",
        "subfolders": {
            # TYPE 1: Unit Tests (Mocked, Fast, Isolated)
            # Mirror-Image Principle: Tests MUST mirror source structure exactly
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
                                "scripts",  # NUANCE
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
                                "tools",  # NUANCE
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
                                "memory",  # NUANCE
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
                                "dashboards",  # NUANCE
                            ],
                            "base_agents": [],
                            "utils": [],
                        },
                    },
                    "apps_lic": {
                        "purpose": "Unit tests for apps_lic modules",
                        "subfolders": {
                            "asset_library": ["scripts", "templates", "hooks"],
                            "domain": ["config", "utils", "models"],
                            "engines": ["navigation", "interaction", "scraping", "drivers"],
                            "logic_nodes": ["analysis", "connection", "messaging"],
                            "reports": ["daily", "campaign", "performance"],
                            "scripts": ["maintenance", "setup"],
                            "shared": ["tools", "utils", "components"],
                            "system_flow": ["campaigns", "cadence", "sequences"],
                            "tools": ["browser", "network"],
                        },
                    },
                    "apps_rg": {
                        "purpose": "Unit tests for apps_rg modules",
                        "subfolders": {
                            "asset_library": ["templates", "wording", "taxonomy"],
                            "core": ["config", "exceptions"],
                            "domain": ["entities", "models", "value_objects"],
                            "engines": [
                                "base",
                                "generation",
                                "hops",
                                "orchestration",
                                "quality",
                                "retrieval",
                                "safety",
                                "utils",
                            ],
                            "logic_nodes": ["extraction", "formatting", "parsing"],
                            "shared": ["tools", "utils", "components"],
                            "system_flow": ["pipelines", "lifecycle"],
                            "validation": ["checkers", "rules"],
                        },
                    },
                    "apps_shared": {
                        "purpose": "Unit tests for apps_shared modules",
                        "subfolders": {
                            "common_utils": [],
                            "config": [],
                            "core_components": [],
                            "llm": [],
                            "mixins": [],
                            "scripts": [],
                            "utils": [],
                            "agents": [],
                            "validators": [],
                        },
                    },
                    "utils": {"purpose": "Utility tests", "subfolders": []},
                },
                "forbidden_zones": ["misc", "temp", "old", "deprecated", "archive", "scratch"],
            },
            # TYPE 2: Integration Tests (DB, API, Component Interaction)
            # Mirror-Image Principle: Tests MUST mirror source structure exactly
            "integration": {
                "purpose": "Component interaction tests mirroring source structure",
                "mirror_source": True,
                "subfolders": {
                    "agentic_core": {
                        "purpose": "Integration tests for agentic_core",
                        "subfolders": [
                            "L0_maintenance",
                            "L1_cognition",
                            "L3_orchestration",
                            "L5_safety",
                            "L6_observability",
                            "core",
                            "agents",
                        ],
                    },
                    "apps_lic": {
                        "purpose": "Integration tests for apps_lic",
                        "subfolders": [
                            "config",
                            "types",
                            "reasoning",
                            "engines",
                            "utils",
                            "scripts",
                            "domain",
                            "shared",
                            "system_flow",
                            "asset_library",
                            "validation",
                            "logic_nodes",
                            "reports",
                            "tools",
                        ],
                    },
                    "apps_rg": {
                        "purpose": "Integration tests for apps_rg",
                        "subfolders": [
                            "config",
                            "types",
                            "reasoning",
                            "engines",
                            "utils",
                            "scripts",
                            "domain",
                            "shared",
                            "system_flow",
                            "asset_library",
                            "validation",
                            "logic_nodes",
                        ],
                    },
                    "apps_shared": {
                        "purpose": "Integration tests for apps_shared",
                        "subfolders": ["common_utils", "core"],
                    },
                    "core": {"purpose": "Cross-cutting integration tests", "subfolders": []},
                },
                "forbidden_zones": ["misc", "temp", "old", "deprecated", "archive", "scratch"],
            },
            # TYPE 3: E2E (Full System)
            "e2e": {
                "purpose": "Full system user-flow simulations",
                "subfolders": ["scenarios", "flows", "snapshots"],
            },
            # TYPE 4: Guardian (Architectural Compliance Validation)
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
            "fixtures": {
                "purpose": "Shared Pytest fixtures",
                "subfolders": ["data", "mocks", "factories"],
            },
            "snapshots": {
                "purpose": "Test snapshot data for comparison and regression testing",
            },
            "behavioral": {
                "purpose": "Behavioral and acceptance testing",
            },
            "stress": {
                "purpose": "Stress and load testing",
            },
            "performance": {
                "purpose": "Performance benchmarking and profiling tests",
            },
        },
        "volatile": False,
    },
    "ops_scripts": {
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
    },
    "archives": {
        "depth": 3,
        "purpose": "Canonical repository for deprecated agents and transaction artifacts. Allows flexible recursive subfolders.",
        "subfolders": {},
        "volatile": False,
    },
    "data": {
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
    },
    "docs": {
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
    },
    ".github": {
        "depth": 2,
        "purpose": "GitHub Actions workflows and repository configuration.",
        "subfolders": [],
        "volatile": True,
    },
    ".gravity_state": {
        "depth": 2,
        "purpose": "Gravity system state tracking and metadata.",
        "subfolders": [],
        "volatile": True,
    },
    ".backup": {
        "depth": 2,
        "purpose": "Backup and recovery artifacts.",
        "subfolders": [],
        "volatile": True,
    },
    "config": {
        "depth": 2,
        "purpose": "Root-level configuration files and agent configs.",
        "subfolders": ["agent_configs"],
    },
}

# === VARIABLE DEPTH SUBFOLDERS (Flexible Depth - Option A) ===
# These subfolders are exempt from strict depth enforcement.
# Files at depth 2 are allowed in these folders to support:
# - Base agents at layer root (e.g., SovereignBaseAgent.py)
# Orchestrator at layer root
# - Core utilities (e.g., sovereign_index.py)
VARIABLE_DEPTH_SUBFOLDERS: frozenset[str] = frozenset(
    {
        "base_agents",  # Flat folder - foundational classes at depth 2
        "utils",  # utils/sovereign_index.py at depth 2
        "config",  # config/core/* variable depth
        "reasoning",  # LCD+ reasoning folder at variable depth
        "enforcement",  # LCD+ enforcement folder at variable depth
        "validators",  # LCD+ validators at variable depth
        "L6_observability",  # L6ObservabilityBase.py at depth 2
        "L3_orchestration",  # Orchestrator at layer root
        "L0_maintenance",  # scripts at variable depth
        "L1_cognition",  # reasoning at variable depth
        "L2_execution",  # tools at variable depth
        "L4_state",  # memory at variable depth
        "L5_safety",  # validators/enforcement at variable depth
        "prompt_governance",  # meta_prompts at variable depth
        "runtime",  # shared_runtime at variable depth
        "semantic_memory",  # store/embeddings at variable depth
        # Top-level territories that allow files in root
        "agentic_core",  # __init__.py and core files at territory root
        "apps_rg",  # Application files at territory root
        "apps_lic",  # Application files at territory root
        "apps_shared",  # Shared files at territory root
        "ops_scripts",  # Standalone scripts at territory root
        "tests",  # Test files at territory root (conftest.py, etc.)
        "docs",  # Documentation files at territory root
        "reports",  # Report files at territory root
        "logs",  # Log files at territory root
        "archives",  # Archive files at territory root
        ".gravity_state",  # State files at territory root
        ".backup",  # Backup files at territory root
        "knowledge",  # document_loaders at variable depth
    },
)
# ============================================================================
# === SSOT: CRITICAL FILE AND DIRECTORY PATHS ===
# ============================================================================
# Single source of truth for all commonly referenced paths in the codebase.
# NO HARDCODING OF THESE PATHS IN DOWNSTREAM FILES - ALWAYS IMPORT FROM HERE.
#
# Usage Pattern:
#       AGENT_DISCOVERY_JSON, DASHBOARD_DIR, get_validated_project_root
#   )
#   discovery_path = get_validated_project_root() / AGENT_DISCOVERY_JSON

# ============================================================================
# === HARDENED ROOT DIRECTORY CONSTANTS FOR PATH RESOLUTION ===
# ============================================================================
# [CRITICAL ANALYSIS] Final constants prevent runtime mutation during mission execution
# This locks down the core directory structure to prevent 'Junior AI' drift
# ALL DOWNSTREAM AGENTS MUST IMPORT FROM THIS SSOT

# Hardened Root Directory Constants
# ALL DOWNSTREAM AGENTS MUST IMPORT FROM THIS SSOT
AGENTIC_CORE_DIR: Final[str] = "agentic_core"
APPS_RG_DIR: Final[str] = "apps_rg"
APPS_LIC_DIR: Final[str] = "apps_lic"
APPS_SHARED_DIR: Final[str] = "apps_shared"

# === Agent Discovery Files ===
AGENT_DISCOVERY_JSON: str = "agent_discovery_full.json"
AGENT_DISCOVERY_MANIFEST_JSON: str = "agent_discovery_full.manifest.json"
RUNTIME_STATE_JSON: str = "runtime_state.json"

# === Core Directory Paths ===
OPS_SCRIPTS_DIR: str = "ops_scripts"
TESTS_DIR: str = "tests"

# === Layer Directories (L0-L6) ===
L0_MAINTENANCE_DIR: str = "agentic_core/L0_maintenance"
L1_COGNITION_DIR: str = "agentic_core/L1_cognition"
L2_EXECUTION_DIR: str = "agentic_core/L2_execution"
L3_ORCHESTRATION_DIR: str = "agentic_core/L3_orchestration"
L4_STATE_DIR: str = "agentic_core/L4_state"
L5_SAFETY_DIR: str = "agentic_core/L5_safety"
L6_OBSERVABILITY_DIR: str = "agentic_core/L6_observability"

# === Critical Subdirectories ===
DASHBOARD_DIR: str = "agentic_core/L6_observability/dashboards"
BLUEPRINT_SOVEREIGN_DIR: str = "agentic_core/config/core"  # DISSOLVED: was blueprint_sovereign
SCHEMAS_DIR: str = "agentic_core/runtime/types"  # DISSOLVED: was agentic_core/schemas
PROMPT_GOVERNANCE_DIR: str = "agentic_core/prompt_governance"
UTILS_DIR: str = "agentic_core/utils"
RUNTIME_DIR: str = "agentic_core/runtime"

# === Test Subdirectories ===
TESTS_UNIT_DIR: str = "tests/unit"
TESTS_INTEGRATION_DIR: str = "tests/integration"
TESTS_E2E_DIR: str = "tests/e2e"
TESTS_AUTOGEN_DIR: str = "tests/autogen"

# === Reporting and Output Directories ===
REPORTS_DIR: str = "reports"
ARCHIVES_DIR: str = "archives"
COVERAGE_HTML_DIR: str = "reports/coverage_html"
DOCS_REPORTS_PLANS: str = "docs/reports/plans"

# === Trust-But-Verify: Known Good Hashes (Watcher of the Watchers) ===
# SHA-256 hashes of critical audit infrastructure scripts
# If these scripts are modified, the audit is compromised
KNOWN_GOOD_HASHES: Final[Mapping[str, str]] = {
    "forensic_discovery_prep.py": "3fadb7164353e0d7072d985da0ba06187a4f3a003588dd3341a43dd94eaa86d0",
}

# ============================================================================
# === DERIVED REGISTRIES (Compiled from SOVEREIGN_TERRITORIES) ===
# ============================================================================
# These registries are derived from SOVEREIGN_TERRITORIES to eliminate duplication.
# The derivation functions extract subfolder lists, metadata, and L4 structures
# from the single SSOT above.


def _derive_core_subfolder_map() -> dict[str, list[str]]:
    """Derive CORE_SUBFOLDER_MAP from SOVEREIGN_TERRITORIES."""
    result: dict[str, list[str]] = {}
    agentic_core = SOVEREIGN_TERRITORIES.get("agentic_core", {})
    subfolders = agentic_core.get("subfolders", {})

    for domain_name, domain_def in subfolders.items():
        if isinstance(domain_def, dict):
            nested = domain_def.get("subfolders", {})
            if isinstance(nested, dict):
                result[domain_name] = list(nested.keys())
            else:
                result[domain_name] = []
        else:
            result[domain_name] = []

    return result


def _derive_subfolder_metadata() -> dict[str, dict[str, Any]]:
    """Derive SUBFOLDER_METADATA from SOVEREIGN_TERRITORIES."""
    result: dict[str, dict[str, Any]] = {}
    agentic_core = SOVEREIGN_TERRITORIES.get("agentic_core", {})
    subfolders = agentic_core.get("subfolders", {})

    for domain_name, domain_def in subfolders.items():
        if isinstance(domain_def, dict):
            result[domain_name] = {
                "purpose": domain_def.get("purpose", f"{domain_name} domain"),
                "content_types": list(domain_def.get("subfolders", {}).keys()) or [domain_name],
                "execution_allowed": domain_def.get("execution_allowed", False),
                "notes": domain_def.get("notes", ""),
            }

    return result


def _derive_apps_subfolder_map(territory_name: str) -> dict[str, list[str]]:
    """Derive APPS_*_SUBFOLDER_MAP from SOVEREIGN_TERRITORIES."""
    result: dict[str, list[str]] = {}
    territory = SOVEREIGN_TERRITORIES.get(territory_name, {})
    if not isinstance(territory, dict):
        return result

    subfolders = territory.get("subfolders", {})

    # Handle case where subfolders is a list (e.g., apps_rg has list of subfolder names)
    if isinstance(subfolders, (list, tuple)):
        for sf_name in subfolders:
            result[sf_name] = []
        return result

    if not isinstance(subfolders, dict):
        return result

    for sf_name, sf_def in subfolders.items():
        if isinstance(sf_def, dict):
            nested = sf_def.get("subfolders", {})
            if isinstance(nested, dict):
                result[sf_name] = list(nested.keys())
            elif isinstance(nested, (list, tuple)):
                result[sf_name] = list(nested)
            else:
                result[sf_name] = []
        elif isinstance(sf_def, (list, tuple)):
            result[sf_name] = list(sf_def)
        else:
            result[sf_name] = []

    return result


# === DERIVED: CORE_SUBFOLDER_MAP ===
# Extracted from SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"]
CORE_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_core_subfolder_map()

# === DERIVED: SUBFOLDER_METADATA ===
# Extracted from SOVEREIGN_TERRITORIES["agentic_core"]["subfolders"] purpose/notes
SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = _derive_subfolder_metadata()

# === DERIVED: APPS_*_SUBFOLDER_MAP ===
APPS_RG_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map("apps_rg")
APPS_LIC_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map("apps_lic")
APPS_SHARED_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = _derive_apps_subfolder_map("apps_shared")

# Type-safe aliases
agentic_core_registry: Final[Mapping[str, Sequence[str]]] = CORE_SUBFOLDER_MAP


def verify_derived_registries() -> list[str]:
    """
    Invariant self-check: verify derived registries are consistent with SOVEREIGN_TERRITORIES.

    Returns list of discrepancies (empty if all consistent).
    Call this during tests or startup to catch SSOT drift.
    """
    discrepancies: list[str] = []

    # Check that all L0-L6 layers have the standard LCD subfolders
    standard_lcd = {"config", "types", "reasoning", "enforcement", "validators", "utils"}
    for layer in [
        "L0_maintenance",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    ]:
        derived = set(CORE_SUBFOLDER_MAP.get(layer, []))
        if not standard_lcd.issubset(derived):
            missing = standard_lcd - derived
            discrepancies.append(f"{layer} missing LCD subfolders: {missing}")

    # Check that SUBFOLDER_METADATA has entries for all CORE_SUBFOLDER_MAP keys
    for key in CORE_SUBFOLDER_MAP:
        if key not in SUBFOLDER_METADATA:
            discrepancies.append(f"SUBFOLDER_METADATA missing key: {key}")

    # Check that APPS_RG has expected structure
    if not APPS_RG_SUBFOLDER_MAP:
        discrepancies.append("APPS_RG_SUBFOLDER_MAP is empty")

    return discrepancies


# ============================================================================
# === L4 SUBFOLDER MAP (Depth-4 Structure for Complex L3 Folders) ===
# ============================================================================
# Some L3 folders have grown beyond manageable size and warrant L4 subfolders.
# This map defines the approved L4 structure for these folders.
# Criteria for L4: >50 files, >5 subdirs, or high functional diversity.

L4_SUBFOLDER_MAP: Final[Mapping[str, Mapping[str, Sequence[str]]]] = {
    # L6_observability/dashboards/ - 13 .py files, 7 subdirs, mixed concerns
    "dashboards": {
        "generators": ["dashboard_generators", "data_generators"],
        "templates": ["html_templates", "component_templates"],
        "components": ["ui_components", "chart_components"],
        "data": ["json_data", "runtime_data"],
        "tests": ["unit_tests", "e2e_tests"],
        "js": ["components", "controllers", "renderers", "utils", "constants"],
        "css": ["themes", "layouts"],
        "config": ["dashboard_config"],
    },
    # L0_maintenance/reasoning/ - Healing strategy implementations (was strategies/)
    "reasoning": {
        "healing": ["audit_healing_strategy"],
    },
    # L0_maintenance/scripts/ - 181 .py files, flat structure (simplified)
    "scripts": {
        "healing": ["healing_strategies", "healing_engines"],
        "validation": ["validators", "checkers"],
        "utilities": ["file_utilities", "code_utilities"],
        "workflows": ["workflow_scripts", "pipeline_scripts"],
        "installation": ["install_scripts"],
        "maintenance": ["maintenance_scripts"],
        "test_utilities": ["test_helpers"],
    },
    # L3_orchestration/reasoning/ - 130 .py files (was engine/ + orchestrators/)
    # NOTE: "reasoning" key already defined above for L0, so use full path as key
    "L3_reasoning": {
        "core": ["base_orchestrators", "orchestration_types"],
        "dag": ["dag_executors", "dag_managers"],
        "rl": ["rl_orchestrators", "rl_coordinators"],
        "mission": ["mission_controllers", "mission_runners"],
        "mcp": ["mcp_routers", "mcp_managers"],
        "safety": ["safety_orchestrators"],
        "state": ["state_managers"],
        "rag": ["rag_orchestrators"],
        "telemetry": ["telemetry_agents", "metrics_agents"],
    },
    # L1_cognition/reasoning/ - 160 .py files (was thought_engine/)
    "L1_reasoning": {
        "engines": ["reasoning_engines", "logic_processors"],
        "planning": ["planners", "schedulers"],
        "memory": ["memory_managers", "context_handlers"],
        "analysis": ["analyzers", "evaluators"],
        "synthesis": ["synthesizers", "generators"],
        "evaluation": ["evaluators", "scorers"],
    },
    # L5_safety/enforcement/ - 79+ .py files (was guardrails/ + gravity/)
    "enforcement": {
        "security": ["pii_guards", "injection_guards", "auth_guards"],
        "quality": ["code_quality", "format_guards"],
        "structural": ["hierarchy_healers", "structure_guards"],
        "constitutional": ["constitutional_ai", "governance_guards"],
        "resource": ["resource_guards", "budget_guards"],
        "mcp": ["mcp_security", "mcp_guards"],
        "detection": ["duplicate_detectors", "threat_detectors"],
    },
    # L2_execution/reasoning/ - 145 .py files (was engine/)
    "L2_reasoning": {
        "core": ["registry_core", "registry_types"],
        "tools": ["tool_implementations"],
        "handlers": ["tool_handlers"],
        "validators": ["tool_validators"],
        "adapters": ["tool_adapters"],
    },
    # prompt_governance/ - [RECONCILED] Functional L3 Structure
    "prompt_governance": {
        "meta_prompts": {
            "orchestration": ["agents", "flows"],
            "reasoning": ["cot", "tot", "react"],
            "security": ["guards", "pii"],
            "personas": ["roles", "behavioral"],
        },
        "templates": {
            "instructional": ["cognition", "execution", "safety"],
            "specialized": ["domain", "format"],
            "fragments": ["partials", "blocks"],
            "rendering": ["engines", "filters"],
        },
        "scripts": {
            "audit": ["syntax_checks", "compliance_scans"],
            "migration": ["version_porters", "legacy_converters"],
            "maintenance": ["registry_cleaners", "cache_managers"],
        },
        "version_registry": {
            "manifests": ["active", "history"],
            "locks": ["commit_locks"],
            "lineage": ["parents", "forks"],
        },
    },
}

# Folders that are approved for L4 depth (depth=4 instead of depth=3)
L4_APPROVED_FOLDERS: Final[frozenset[str]] = frozenset(
    {
        "agentic_core/L6_observability/dashboards",
        "agentic_core/L0_maintenance/scripts",
        "agentic_core/L0_maintenance/reasoning",
        "agentic_core/L3_orchestration/reasoning",
        "agentic_core/L1_cognition/reasoning",
        "agentic_core/L5_safety/enforcement",
        "agentic_core/L5_safety/validators",
        "agentic_core/L5_safety/reasoning",
        "agentic_core/L2_execution/reasoning",
        "agentic_core/L2_execution/tools",
        "agentic_core/L4_state/memory",
        "agentic_core/config/core",
        "agentic_core/prompt_governance/meta_prompts",
        "agentic_core/prompt_governance/templates",
        "agentic_core/prompt_governance/scripts",
        "agentic_core/prompt_governance/version_registry",
    },
)

# ============================================================================
# SCRIPTS PLACEMENT RULES - Semantic Boundary Enforcement
# ============================================================================
# Distinguishes root ops_scripts/ (standalone utilities) from L0_maintenance/scripts/
# (sovereign system scripts). Uses AST import analysis, NOT line counts.
SCRIPTS_PLACEMENT_RULES: Final[Mapping[str, Mapping[str, Any]]] = {
    "root_ops_scripts": {
        "description": "Standalone utilities (setup, pip, env) with NO core dependencies.",
        "forbidden_imports": ["agentic_core"],
        "allowed_depth": 1,
        "violation_destination": "agentic_core/L0_maintenance/scripts",
    },
    "l0_maintenance_scripts": {
        "description": "System maintenance, healing, and sovereign agents.",
        "required_capabilities": ["core_access"],
        "preferred_location": "agentic_core/L0_maintenance/scripts",
    },
}

# [REMOVED] Old CORE_SUBFOLDER_MAP - now derived from SOVEREIGN_TERRITORIES above
# See _derive_core_subfolder_map() for the derivation logic

# [REMOVED] Old SUBFOLDER_METADATA - now derived from SOVEREIGN_TERRITORIES above
# See _derive_subfolder_metadata() for the derivation logic

# [REMOVED] Old APPS_*_SUBFOLDER_MAP - now derived from SOVEREIGN_TERRITORIES above
# See _derive_apps_subfolder_map() for the derivation logic

# Tests subfolder map (kept as explicit since tests/ has unique structure)
TESTS_L2_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = {
    "unit": [],  # Has 229 items (flat structure) - LARGE FOLDER
    "integration": [],  # Has 23 items (flat structure)
    "e2e": [],  # Has 8 items (flat structure)
    "functional": [],  # Has 19 items (flat structure)
    "fixtures": [],  # Has 12 items (flat structure)
    "core": [],  # Has 4 items (flat structure)
    "apps_rg": [],  # Has 19 items (flat structure)
    "apps_lic": [],  # RECONCILED: Added parity with apps_rg
}
TESTS_SUBFOLDER_MAP: Final[Mapping[str, Sequence[str]]] = TESTS_L2_SUBFOLDER_MAP

# === APP-SPECIFIC FILE PLACEMENT RULES ===
# Files with these prefixes MUST be placed in their respective app folders, NOT agentic_core
# Enforced by FCA.validate_app_prefix_placement() (prefix-based)
# and FCA.validate_territory_alignment() (import/content-based).
# LocationAgent and HierarchyAgent also consume these during validation.

APP_SPECIFIC_PREFIXES: Final[Mapping[str, str]] = {
    "rg_": "apps_rg",  # Resume Gen executors/tools
    "lic_": "apps_lic",  # LinkedIn Canonical executors/tools
    "resume_": "apps_rg",  # Resume-related files
    "outreach_": "apps_rg",  # Outreach-related files
    "dispatch_resume": "apps_rg",  # Resume dispatch tools
    "dispatch_outreach": "apps_rg",  # Outreach dispatch tools
    "contact_research": "apps_rg",  # Contact research executors
    "company_research": "apps_rg",  # Company research executors
}

# === STUTTERING PREFIX DETECTION ===
# Detects malformed app prefixes where letters are split by underscores.
# Root cause: healing passes that tokenize abbreviations letter-by-letter.
# Used by FCA.validate_app_prefix_placement() to flag and auto-correct.
STUTTERING_PREFIX_MAP: Final[Mapping[str, str]] = {
    "r_g_": "rg_",  # r_g_sovereign_auditor → rg_sovereign_auditor
    "l_i_c_": "lic_",  # l_i_c_scraper → lic_scraper
}

# Central SSOT — all agents should use get_correct_app_path() for precise suggestions
APP_SPECIFIC_TARGET_SUBFOLDER: str = "reasoning"

# Pre-compiled APP_SPECIFIC_PATTERNS for performance - eliminates hot-path re-compilation
APP_SPECIFIC_PATTERNS: Final[list[Pattern]] = [
    re.compile(r"^rg_.*\.py$"),
    re.compile(r"^lic_.*\.py$"),
    re.compile(r"^resume_.*\.py$"),
    re.compile(r"^outreach_.*\.py$"),
    re.compile(r"^dispatch_(resume|outreach).*\.py$"),
]

# Optimized FORBIDDEN_LAYER_PREFIXES as tuple for C-level startswith() performance
FORBIDDEN_LAYER_PREFIXES: Final[tuple[str, ...]] = (
    "l0_",
    "l1_",
    "l2_",
    "l3_",
    "l4_",
    "l5_",
    "l6_",
    "L0_",
    "L1_",
    "L2_",
    "L3_",
    "L4_",
    "L5_",
    "L6_",
    "p0_",
    "p1_",
    "p2_",
    "p3_",
    "P0_",
    "P1_",
    "P2_",
    "P3_",
)

# Pre-compiled FORBIDDEN_BACKUP_PATTERNS for O(1) compilation overhead
FORBIDDEN_BACKUP_PATTERNS: Final[list[Pattern]] = [
    re.compile(r".*\.bak\.\d+$"),
    re.compile(r".*\.backup\.\d+$"),
    re.compile(r".*\.old\.\d+$"),
    re.compile(r".*\.tmp\.\d+$"),
]


def has_forbidden_layer_prefix(filename: str) -> str | None:
    """
    Check if filename starts with a forbidden layer/priority prefix.
    Optimized: Uses C-implemented tuple-startswith for O(1) performance in Python space.
    """
    if filename.startswith(FORBIDDEN_LAYER_PREFIXES):
        for prefix in FORBIDDEN_LAYER_PREFIXES:
            if filename.startswith(prefix):
                return prefix
    return None


def is_broken_backup_file(filename: str) -> bool:
    """
    Check if filename matches broken backup pattern (.bak.NNNNNN, etc.)
    [SSOT] Optimized to use pre-compiled module-level Patterns.
    """
    return any(pattern.match(filename) for pattern in FORBIDDEN_BACKUP_PATTERNS)


# === AST-BASED DOMAIN SIGNALS (2026-01-02 hardening) ===
# High-confidence identifier terms for structural detection of leaked app logic
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
VARIABLE_HIT_WEIGHT: Final[float] = 0.5
STRING_HIT_WEIGHT: Final[float] = 0.25
AST_DOMAIN_HIT_THRESHOLD: Final[float] = 2.0
FORBIDDEN_APP_MODULES: Final[frozenset[str]] = frozenset({"apps_rg", "apps_lic"})

# String literal signals (docstrings, comments, etc.)
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
# POLYGLOT DOMAIN DETECTION (Non-Code Asset Routing)
# ============================================================================
# Enables structural scanning of non-Python files (YAML, JSON, MD, TXT).
# Agents scan raw text content against domain dictionaries to route artifacts.

# 3. ADD POLYGLOT DOMAIN SIGNALS (For YAML/JSON Analysis)
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

# === CORE LAYER GRAVITY RULES (Internal dependency direction) ===
# === APP-LAYER GRAVITY RULES (Cross-App Isolation) ===
# [SSOT] Prevents apps_shared from importing from specific apps to avoid circularity.
LAYER_FORBIDDEN_IMPORTS: Final[Mapping[str, frozenset[str]]] = {
    "L1_cognition": frozenset({"L2_execution", "L3_orchestration", "L4_state", "L5_safety"}),
    "L2_execution": frozenset({"L1_cognition", "L3_orchestration", "L5_safety"}),
    "L3_orchestration": frozenset({"L5_safety"}),
    "apps_shared": frozenset({"apps_rg", "apps_lic"}),  # Shared must be independent
    "apps_rg": frozenset({"apps_lic"}),  # Apps are horizontally isolated
    "apps_lic": frozenset({"apps_rg"}),  # Apps are horizontally isolated
}

# === STRUCTURED TERRITORY KEYWORDS FOR ALIGNMENT SCORING ===
CORE_TERRITORY_KEYWORDS: Final[Mapping[str, Mapping[str, frozenset[str]]]] = {
    "L1_cognition/thought_engine": {
        "primary": frozenset({"think", "reason", "plan", "decompose", "critique", "reflect"}),
    },
    # DISSOLVED: "L1_cognition/intent_analysis" removed
    "L2_execution/engine": {"primary": frozenset({"tool", "execute", "call", "registry", "runner"})},
    "L2_execution/mcp": {"primary": frozenset({"mcp", "client", "fetch", "protocol"})},
    "L3_orchestration/engine": {
        "primary": frozenset({"orchestrate", "workflow", "route", "dispatch", "coordinate", "flow"}),
    },
    "L3_orchestration/engine": {"primary": frozenset({"fission", "split", "decompose", "atomic"})},
    "L4_state/memory": {"primary": frozenset({"state", "context", "checkpoint", "persist"})},
    "L4_state/ledger": {"primary": frozenset({"ledger", "history", "record", "transaction"})},
    "L5_safety/validators": {
        "primary": frozenset({"validate", "enforce", "check", "guard", "policy", "heal"}),
    },
    "L5_safety/guardrails": {"primary": frozenset({"guardrail", "safety", "membrane", "airlock", "pii"})},
    "L5_safety/gravity": {"primary": frozenset({"gravity", "import", "dependency", "layer"})},
    "config/core": {
        "primary": frozenset({"blueprint", "registry", "sovereign", "canon", "config", "settings"}),
    },
    "schemas/models": {"primary": frozenset({"schema", "model", "type", "message"})},
    "prompt_governance/L3_core": {"primary": frozenset({"render", "registry", "assemble", "govern"})},
    "prompt_governance/L3_templates": {
        "primary": frozenset({"template", "prompt", "persona", "instructional"}),
    },
    "prompt_governance/L3_security": {"primary": frozenset({"security", "injection", "pii", "compliance"})},
    "prompt_governance/L3_integrity": {"primary": frozenset({"validate", "optimize", "test", "quality"})},
    "prompt_governance/L3_utilities": {"primary": frozenset({"script", "middleware", "monitor", "audit"})},
    "observability": {"primary": frozenset({"metric", "trace", "telemetry", "log", "compliance"})},
    "utils": {"primary": frozenset({"util", "helper", "extension", "wrapper"})},
}

# Territory alignment thresholds
TERRITORY_MISMATCH_THRESHOLD: Final[float] = 2.5
MIN_ALIGNMENT_SCORE: Final[float] = 1.5

# === ULTRA HEALING DEFAULTS (2026-01-02 Reliability Hardening) ===
# Fallback targets when AST scoring is inconclusive
DEFAULT_APP_HEALING_TARGET: Final[str] = "apps_rg/engines"  # Most common leak destination
DEFAULT_CORE_HEALING_TERRITORY: Final[str] = "L2_execution/engine"  # Safe neutral territory

# Violation severity levels for prioritized healing
VIOLATION_SEVERITY: Final[Mapping[str, int]] = {
    "GRAVITY VIOLATION": 10,
    "AST DOMAIN VIOLATION": 9,
    "TERRITORY MISMATCH VIOLATION": 8,
    "APP-SPECIFIC IN CORE VIOLATION": 7,
    "TERRITORY ALIGNMENT WEAK": 5,
}


def get_correct_app_folder(filename: str) -> str | None:
    """
    Return the correct root app folder (e.g., 'apps_rg') for a file based on prefix.
    Legacy — kept for backward compatibility with existing agent code.
    Prefer get_correct_app_path() for new healing/validation logic.
    """
    for prefix, folder in APP_SPECIFIC_PREFIXES.items():
        if filename.startswith(prefix):
            return folder
    return None


def get_correct_app_path(filename: str) -> str | None:
    """
    Return the full recommended path (e.g., 'apps_rg/engines') for app-specific files.
    Uses centralized target subfolder — all migrated files went here.
    Returns None if not app-specific.
    """
    root = get_correct_app_folder(filename)
    if root:
        return f"{root}/{APP_SPECIFIC_TARGET_SUBFOLDER}"
    return None


def is_app_specific_file(filename: str) -> bool:
    """
    Check if a file should be in an app folder, not agentic_core.
    Uses pre-compiled regex for O(1) matching during large-scale hierarchy scans.
    """
    return any(pattern.match(filename) for pattern in APP_SPECIFIC_PATTERNS)


# === PROJECT ROOT SAFETY ===
# Prevent agents from creating folders/files outside the active project root
# RCA: Folders were created at C:\Git\ instead of C:\Git\Agentic-Workflow\

PROJECT_ROOT_MARKERS: frozenset[str] = frozenset(
    {
        "pyproject.toml",
        "canon_validator_agentic_v2_thin.py",
        "agentic_core",
        ".git",
    },
)


def get_validated_project_root():
    """
    Get the validated project root by searching upward from this file.
    Raises ValueError if no valid project root is found.
    """
    from pathlib import Path

    current = Path(__file__).resolve()

    for parent in [current] + list(current.parents):
        markers_found = sum(1 for marker in PROJECT_ROOT_MARKERS if (parent / marker).exists())
        if markers_found >= 2:
            return parent

    raise ValueError(f"Could not find valid project root from {__file__}")


def validate_path_within_project(path, project_root=None) -> bool:
    """
    Validate that a path is within the project root.
    Returns True if path is within project root, False otherwise.
    """
    from pathlib import Path

    if project_root is None:
        project_root = get_validated_project_root()

    try:
        path = Path(path).resolve()
        project_root = Path(project_root).resolve()
        path.relative_to(project_root)
        return True
    except ValueError:
        return False


def safe_path_join(project_root, *parts):
    """
    Safely join path parts and validate result is within project root.
    Raises ValueError if resulting path would be outside project root.
    """
    from pathlib import Path

    project_root = Path(project_root).resolve()
    result = project_root.joinpath(*parts).resolve()

    if not validate_path_within_project(result, project_root):
        raise ValueError(f"SAFETY VIOLATION: Path '{result}' is outside project root '{project_root}'")

    return result


# === GLOBAL NAMING RESTRICTIONS (Root Cause Prevention) ===
# These patterns are FORBIDDEN in all filenames across the repository.
# They target the root causes of naming violations discovered during the Great Sanitization.
FORBIDDEN_FILENAME_PATTERNS: Final[Sequence[Mapping[str, str]]] = [
    {
        # Detects stuttering acronyms caused by naive CamelCase splitting
        # e.g., "s_s_o_t" (from SSOT), "h_t_t_p" (from HTTP)
        "pattern": r"(?<![a-z])[a-z]_[a-z]_[a-z]_[a-z]",
        "reason": "Stuttering Acronym Violation (naive CamelCase split). "
        "Fix: collapse single-char segments (e.g., s_s_o_t → ssot).",
    },
    {
        # Detects double/triple underscores caused by unsanitized concatenation
        # Excludes __init__.py and __pycache__ which are Python conventions
        "pattern": r"(?<!^)_{2,}(?!init__|pycache__)",
        "reason": "Multiple Underscore Violation (unsanitized concatenation). "
        "Fix: collapse to single underscore (e.g., setup___init___ → setup_init).",
    },
    {
        # Detects filenames starting with underscore (except __init__.py)
        # Root cause: legacy convention leaking into sovereign territory
        "pattern": r"^_[a-z]",
        "reason": "Leading Underscore Violation (non-__init__ file). "
        "Fix: remove leading underscore or rename to descriptive name.",
    },
]

# === KNOWN ARCHITECTURAL SUFFIXES (LCD+ Compound Suffix Prevention) ===
# Single-suffix rule: every .py file must have AT MOST ONE of these suffixes.
# Files with multiple suffixes (e.g., *_types_config.py) are compound violations.
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

# Explicit forbidden compound suffix patterns (regex).
# These are the most common compound violations discovered during LCD+ migration.
FORBIDDEN_COMPOUND_PATTERNS: Final[Sequence[str]] = [
    r".*_types_config\.py$",
    r".*_validator_util\.py$",
    r".*_types_validator\.py$",
    r".*_config_util\.py$",
]

# === CANONICAL SUFFIX-TO-FOLDER MAPPING (LCD+ Routing SSOT) ===
# Maps architectural suffixes to their canonical LCD folder.
# Used by FileClassificationAgent for territory enforcement.
# "GLOBAL_MIXINS" is a sentinel meaning agentic_core/mixins/ (not layer-local).
SUFFIX_TO_FOLDER: Final[Mapping[str, str]] = {
    "_config.py": "config",
    "_types.py": "types",
    "_protocol.py": "types",
    "_validator.py": "validators",
    "_util.py": "utils",
    "_mixin.py": "GLOBAL_MIXINS",
    "Protocol.py": "GLOBAL_INTERFACES",  # I*Protocol.py -> agentic_core/interfaces/
    "Agent.py": "reasoning",
    "Inspector.py": "reasoning",
    "Healer.py": "reasoning",
    "Guardian.py": "reasoning",
    "Orchestrator.py": "reasoning",
    "Monitor.py": "enforcement",
    "Strategy.py": "enforcement",
    # "Adapter.py": removed — adapters inherit subfolder from wrapped component (RCA_Adapter_Classification)
    "_guardrail.py": "enforcement",
    "_strategy.py": "enforcement",
}

# === GLOBAL INTERFACE ROUTING ===
# Files matching this pattern are global interface contracts and MUST live in
# agentic_core/interfaces/, NOT in layer-level types/ folders.
# The "I" prefix + "Protocol" suffix is the canonical interface naming convention.
# "GLOBAL_INTERFACES" is a sentinel in SUFFIX_TO_FOLDER (like GLOBAL_MIXINS for mixins).
INTERFACE_FILENAME_PATTERN: Final[str] = r"^I[A-Z].*Protocol\.py$"

# Files matching INTERFACE_FILENAME_PATTERN are routed to this global folder:
GLOBAL_INTERFACES_FOLDER: Final[str] = "agentic_core/interfaces"

# === FORBIDDEN EPHEMERAL SCRIPT PATTERNS ===
# Files matching these patterns are one-off migration/maintenance scripts that should
# never be committed. They accumulate as tech debt and clutter the codebase.
# Used by FileClassificationAgent._detect_ephemeral_scripts() to flag for deletion.
# Exemptions: "two_phase" (algorithm name), "execution_phase" (domain concept),
#             "mutation_phase" (pipeline concept) — these use "phase" semantically.
FORBIDDEN_EPHEMERAL_PATTERNS: Final[Sequence[str]] = [
    r"(?i)phase\s*\d",  # phase1, phase_2, phase 3, Phase10
    r"(?i)wave\s*[\d_]",  # wave_9, wave1, Wave 2
    r"(?i)sprint\d",  # sprint4, Sprint1
]
EPHEMERAL_PATTERN_EXEMPTIONS: Final[Sequence[str]] = [
    r"(?i)two_?phase",  # TwoPhaseDeduplication (algorithm name)
    r"(?i)execution_phase",  # execution_phase_types (domain concept)
    r"(?i)mutation_phase",  # mutation_phase (pipeline concept)
    r"(?i)research_hop_phase",  # research_hop_phase (domain concept)
]

# === AST-BASED FILETYPE-TO-FOLDER ROUTING (replaces suffix matching) ===
# Maps the FileType returned by classify_file() (AST analysis) to the correct LCD folder.
# This is the ONLY routing table for folder assignment. Suffix matching is FORBIDDEN.
# Used by FileClassificationAgent._get_correct_folder_for_type_ast().
FILETYPE_TO_FOLDER: Final[Mapping[str, str]] = {
    "AGENT": "reasoning",
    "ORCHESTRATOR": "reasoning",
    "CONFIG": "config",
    "TYPES": "types",
    "PROTOCOL": "types",
    "VALIDATOR": "validators",
    "UTILITY": "utils",
    "MIXIN": "GLOBAL_MIXINS",  # Sentinel: routed to agentic_core/mixins/
    "SCRIPT": "scripts",
    "FACTORY": "enforcement",
    # "ADAPTER": removed — adapters inherit subfolder from wrapped component (RCA_Adapter_Classification)
    "STRATEGY": "enforcement",
    "EXCEPTION": "types",
    "ENGINE": "reasoning",
    "GATEWAY": "enforcement",
    "SERVICE": "utils",  # Singleton services, monitors, collectors → utils/
    # CLASS, STUB, TEST, IGNORE → no routing (stay where they are)
}

# === DUPLICATE FILE DETECTION ===
# When the same filename exists in multiple locations, the canonical copy is determined
# by this priority order. Higher priority locations win.
# Used by FileClassificationAgent._detect_duplicate_files().
CANONICAL_LOCATION_PRIORITY: Final[Sequence[str]] = [
    "runtime",  # Runtime types/config are most canonical
    "interfaces",  # Global interfaces
    "base_agents",  # Base agents
    "mixins",  # Global mixins
    "config/core",  # Core config
    "config",  # Global config
    "utils",  # Global utils
    "prompt_governance",  # Domain-specific governance
    "L5_safety",  # Safety layer
    "L6_observability",  # Observability layer
    "L4_state",  # State layer
    "L3_orchestration",  # Orchestration layer
    "L2_execution",  # Execution layer
    "L1_cognition",  # Cognition layer
    "L0_maintenance",  # Maintenance layer
]

# Files exempt from duplicate detection (legitimately exist in multiple locations)
DUPLICATE_DETECTION_EXEMPT: Final[Sequence[str]] = [
    "__init__.py",
    "conftest.py",
    "__main__.py",
]

# === CROSS-LAYER FILENAME DETECTION ===
# Files with layer indicators (l0-l6, L0-L6) in their filenames MUST live in the
# matching layer. A file named "l5_streamer.py" in L6_observability/ is a violation.
# Used by FileClassificationAgent._detect_cross_layer_naming_violation().
# The regex captures the layer number from the filename for comparison.
LAYER_PREFIX_PATTERN: Final[str] = r"(?i)(?:^|_)l([0-6])(?:_|[A-Z])"

# === L5 ENFORCEMENT DOMAIN-SPECIALIZED SUFFIXES ===
# L5_safety/enforcement/ uses domain-specific semantic suffixes.
# The _script.py suffix is NOT used in enforcement/ — scripts belong in scripts/.
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

# === FILENAME SINGLE-TAG RULE (RCA: dual-tag prevention) ===
# Each filename must carry at most ONE classification tag. Filenames with multiple
# tags (e.g., "code_detection_types.py" has both AGENT and TYPES) create
# ambiguous classification and must be renamed.
#
# RCA: 13 files were found with both "agent" and "types" in the filename.
# 10 of those were full agent implementations dumped into types/ folders with
# "_types" appended. The classifier saw SovereignBaseAgent → AGENT, but the
# "_types" suffix and types/ folder said TYPES. No validation prevented this.
#
# Rule: A filename may contain AT MOST ONE classification suffix.
# Violation = the file needs renaming before it can be correctly classified.
#
# IMPORTANT: This detects COMPOUND SUFFIXES (two tags concatenated), NOT domain
# words. "find_misnamed_agents_util.py" is fine ("agents" is a domain word,
# "_util" is the only classification suffix). But "code_detector_agent_types.py"
# is forbidden ("_agent" + "_types" = two classification suffixes).
#
# The detection uses regex on the filename stem, not simple substring matching.

# Classification suffix patterns that are matched precisely using regex.
# Used by FileClassificationAgent._classify_filename_by_suffix() to determine
# the file's classification tag.
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
    r"Agent\.py$": "AGENT",  # PascalCase class-style (e.g., CodeDetectorAgent.py)
    r"Strategy\.py$": "STRATEGY",  # PascalCase class-style (e.g., RecoveryStrategy.py)
    r"Adapter\.py$": "ADAPTER",  # PascalCase class-style (e.g., LocalDiskAdapter.py)
    r"I[A-Z].*Protocol\.py$": "PROTOCOL",  # PascalCase interface-style (e.g., IHealerProtocol.py)
}

# Compound suffix patterns that are FORBIDDEN in filenames.
# Each pattern matches a stem that has two classification suffixes back-to-back.
# Format: (regex_pattern, tag_A, tag_B, example)
COMPOUND_SUFFIX_CONFLICTS: Final[Sequence[tuple[str, str, str, str]]] = [
    # AGENT compounds
    (r"_agent_types$", "AGENT", "TYPES", "code_detector_agent_types.py"),
    (r"_agent_config$", "AGENT", "CONFIG", "security_level_agent_config.py"),
    (r"_agent_validator$", "AGENT", "VALIDATOR", "routing_decision_agent_validator.py"),
    (r"_agent_util$", "AGENT", "UTILITY", "extract_pattern_agent_util.py"),
    (r"Agent_types$", "AGENT", "TYPES", "CodeDetectorAgent_types.py"),
    (r"Agent_config$", "AGENT", "CONFIG", "SomeAgent_config.py"),
    # ENGINE compounds
    (r"_engine_types$", "ENGINE", "TYPES", "safety_engine_types.py"),
    (r"_engine_validator$", "ENGINE", "VALIDATOR", "consensus_engine_validator.py"),
    (r"_engine_config$", "ENGINE", "CONFIG", "engine_config.py"),
    # GUARDRAIL compounds
    (r"_guardrail_types$", "GUARDRAIL", "TYPES", "mcp_security_guardrail_types.py"),
    (r"_guardrail_mixin$", "GUARDRAIL", "MIXIN", "cost_guardrail_mixin.py"),
    (r"_guardrail_config$", "GUARDRAIL", "CONFIG", "guardrail_config.py"),
    # MANAGER compounds
    (r"_manager_types$", "MANAGER", "TYPES", "resource_manager_types.py"),
    (r"_manager_config$", "MANAGER", "CONFIG", "sovereign_manager_config.py"),
    (r"_manager_validator$", "MANAGER", "VALIDATOR", "context_manager_validator.py"),
    # STRATEGY compounds
    (r"_strategy_types$", "STRATEGY", "TYPES", "context_pruning_strategy_types.py"),
    (r"_strategy_config$", "STRATEGY", "CONFIG", "mcpservermode_strategy_config.py"),
    (r"_strategy_mixin$", "STRATEGY", "MIXIN", "healing_strategy_mixin.py"),
    (r"_strategy_validator$", "STRATEGY", "VALIDATOR", "reasoningnode_strategy_validator.py"),
    # VALIDATOR compounds
    (r"_validator_types$", "VALIDATOR", "TYPES", "code_validator_types.py"),
    (r"_validator_util$", "VALIDATOR", "UTILITY", "check_sovereign_base_validator_util.py"),
    # SCANNER compounds
    (r"_scanner_types$", "SCANNER", "TYPES", "credential_scanner_types.py"),
    (r"_scanner_util$", "SCANNER", "UTILITY", "sovereign_scanner_util.py"),
    # PROTOCOL compounds
    (r"_protocol_types$", "PROTOCOL", "TYPES", "healer_protocol_types.py"),
    (r"_protocol_config$", "PROTOCOL", "CONFIG", "detection_protocol_config.py"),
    (r"_protocol_guardrail$", "PROTOCOL", "GUARDRAIL", "airlock_protocol_guardrail.py"),
    # SUITE compounds
    (r"_suite_types$", "SUITE", "TYPES", "security_validation_suite_types.py"),
    # FACTORY compounds
    (r"_factory_config$", "FACTORY", "CONFIG", "gateway_factory_config.py"),
    (r"_factory_util$", "FACTORY", "UTILITY", "component_factory_util.py"),
    # ORCHESTRATOR compounds
    (r"_orchestrator_types$", "ORCHESTRATOR", "TYPES", "recursive_orchestrator_types.py"),
    # SHIELD compounds
    (r"_shield_validator$", "SHIELD", "VALIDATOR", "governance_shield_validator.py"),
    # SANITIZER compounds
    (r"_sanitizer_util$", "SANITIZER", "UTILITY", "telemetry_sanitizer_util.py"),
    # GUARD compounds
    (r"_guard_util$", "GUARD", "UTILITY", "scan_guard_util.py"),
    (r"_guard_mixin$", "GUARD", "MIXIN", "cost_guard_mixin.py"),
    # DETECTOR compounds
    (r"_detector_types$", "DETECTOR", "TYPES", "code_detector_types.py"),
    (r"_detector_config$", "DETECTOR", "CONFIG", "gravity_leak_detector_config.py"),
    # ENFORCER compounds
    (r"_enforcer_types$", "ENFORCER", "TYPES", "code_enforcer_types.py"),
    (r"_enforcer_util$", "ENFORCER", "UTILITY", "root_hygiene_enforcer_util.py"),
    # CONFIG compounds
    (r"_config_types$", "CONFIG", "TYPES", "blueprint_config_types.py"),
    (r"_config_util$", "CONFIG", "UTILITY", "sync_mcp_config_util.py"),
    (r"_config_detector$", "CONFIG", "DETECTOR", "magic_config_detector.py"),
    # ADAPTER compounds
    (r"_adapter_types$", "ADAPTER", "TYPES", "open_telemetry_tracing_adapter_types.py"),
    (r"_adapter_config$", "ADAPTER", "CONFIG", "storage_adapter_config.py"),
    (r"_adapter_util$", "ADAPTER", "UTILITY", "mcp_adapter_util.py"),
    (r"Adapter_types$", "ADAPTER", "TYPES", "SomeAdapter_types.py"),
    # MIXIN compounds (RCA: healing-pass suffix accumulation)
    (r"_mixin_agent_mixin$", "MIXIN", "AGENT", "autonomy_mixin_agent_mixin.py"),
    (r"_mixin_agent$", "MIXIN", "AGENT", "some_mixin_agent.py"),
    (r"_agent_mixin$", "AGENT", "MIXIN", "feature_flagged_agent_mixin.py"),
    (r"_mixin_types$", "MIXIN", "TYPES", "healer_mixin_types.py"),
    (r"_mixin_config$", "MIXIN", "CONFIG", "autonomy_mixin_config.py"),
    (r"_mixin_util$", "MIXIN", "UTILITY", "healer_mixin_util.py"),
    (r"_mixin_validator$", "MIXIN", "VALIDATOR", "agent_mixin_validator.py"),
]

# === FOLDER PURITY RULES (BIDIRECTIONAL ENFORCEMENT) ===
# Defines which file suffixes are ALLOWED in each LCD folder.
# Used by FileClassificationAgent._enforce_folder_purity() to EVICT misplaced files.
# Key = folder name, Value = list of allowed filename patterns (suffix or regex).
FOLDER_PURITY_RULES: Final[Mapping[str, Sequence[str]]] = {
    "reasoning": [
        r".*Agent\.py$",
    ],  # ONLY *Agent.py files allowed (snake_case services/monitors → enforcement/)
    "validators": [r".*_validator\.py$", r".*Validator.*\.py$"],
    "config": [r".*_config\.py$", r".*_config\.yaml$", r".*_config\.json$"],
    "types": [
        r".*_types\.py$",
        r".*_protocol\.py$",
        r"I[A-Z].*Protocol\.py$",
        r".*Error\.py$",
        r".*Exception\.py$",
    ],  # Exception classes live in types/
    "utils": [
        r".*_util\.py$",
        r".*_mixin\.py$",
        r".*_helper\.py$",
        r".*_collector\.py$",
        r".*_monitor\.py$",
    ],  # Service singletons route here
    "scripts": [
        r"^[a-z][a-z0-9_]*\.py$",
        r".*_util\.py$",
    ],  # snake_case .py files (no _script suffix needed — folder is the signal)
    "enforcement": [
        r".*_guardrail\.py$",
        r".*_enforcer\.py$",
        r".*_gate\.py$",
        r".*_manager\.py$",
        r".*_shield\.py$",
        r".*_firewall\.py$",
        r".*_sanitizer\.py$",
        r".*_governor\.py$",
        r".*_policy\.py$",
        r".*_guard\.py$",
        r".*_strategy\.py$",
        r".*Strategy\.py$",
        r".*Adapter\.py$",
        r".*Monitor\.py$",
        r".*Factory\.py$",
        r".*Gateway\.py$",
        r".*_adapter\.py$",
        r"^[a-z][a-z0-9_]*\.py$",
    ],  # Plain snake_case .py (no suffix) allowed
    "dashboards": [
        r".*\.html$",
        r".*\.js$",
        r".*\.css$",
        r".*\.yaml$",
        r".*\.json$",
        r".*\.py$",
    ],  # Dashboard assets: HTML/JS/CSS/YAML/JSON/PY
}

# === NON-PYTHON FILE ROUTING ===
# Maps non-Python file extensions to their canonical subfolder within a layer.
# Used by FCA._enforce_folder_purity() and _classify_non_python_file().
# Files that don't match any layer's expected non-Python patterns are flagged.
NON_PYTHON_FOLDER_ROUTES: Final[Mapping[str, str]] = {
    "dashboard_ssot.yaml": "dashboards",  # Dashboard config belongs with dashboards
    ".yaml": "config",  # Default: YAML files → config/
    ".json": "config",  # Default: JSON files → config/
    ".html": "dashboards",  # HTML → dashboards/
    ".js": "dashboards",  # JS → dashboards/
    ".css": "dashboards",  # CSS → dashboards/
}

# === DOMAIN-SPECIFIC PYTHON FILE ROUTING ===
# Python files whose CONTENT is tightly bound to a specific domain should be
# routed there instead of relying purely on suffix. The _util.py suffix sends
# files to utils/, but dashboard-specific utils belong in dashboards/.
# Used by FCA to flag misplaced domain-specific files.
DOMAIN_CONTENT_SIGNALS: Final[Mapping[str, str]] = {
    "dashboard": "L6_observability/dashboards",  # dashboard-specific utils/scripts
    "playwright": "L6_observability/dashboards",  # E2E dashboard testing
}

# === SERVICE CLASS DETECTION PATTERNS ===
# Patterns that identify service/infrastructure classes (NOT agents).
# These classes are singletons, collectors, monitors that belong in utils/, not reasoning/.
# Used by FileClassificationAgent._is_service_singleton() for SERVICE classification.
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

# === APP DOMAIN PREFIXES ===
# Filename prefixes that indicate an agent belongs to an app domain, NOT agentic_core.
# If a file in agentic_core/ matches these, it's a cross-domain violation.
APP_DOMAIN_PREFIXES: Final[Sequence[str]] = [
    "Lic",  # apps_lic (Letter of Intent/Correspondence)
    "Campaign",  # apps_lic campaign logic
    "Outreach",  # apps_lic outreach logic
]

# === LAYER KEYWORD AFFINITY ===
# Keywords in docstrings/class names that indicate layer affinity.
# Used by FileClassificationAgent._compute_layer_affinity() for semantic scoring.
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
    "L2_execution": ["tool", "mcp", "action", "execute", "invoke", "run", "embed", "search", "index"],
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
    "L4_state": ["state", "memory", "ledger", "cache", "redis", "pinecone", "persist", "store", "context"],
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

# === COMPREHENSIVE NAMING CONVENTIONS (SSOT) ===
# All naming rules for all file types in the repository

NAMING_CONVENTIONS: Final[Mapping[str, Mapping[str, Any]]] = {
    # Python Agent files - PascalCase, must end with Agent
    "agent": {
        "pattern": r"^[A-Z][a-zA-Z0-9]*Agent\.py$",
        "description": "PascalCase ending with 'Agent'",
        "examples": ["HealerAgent.py", "NamingAgent.py", "CodeDeduplicationAgent.py"],
        "anti_examples": ["HealerAgent.py", "NamingAgent.py", "Healer.py"],
        "extensions": [".py"],
        "min_words": 2,  # At least 2 words (e.g., HealerAgent = Healer + Agent)
        "max_words": 4,  # Max 4 words (e.g., CodeDeduplicationAgent)
    },
    # Python scripts - snake_case, MUST end with _script.py (Zero-Ambiguity Standard)
    "script": {
        "pattern": r"^[a-z][a-z0-9_]*_script\.py$",
        "description": "snake_case ending with '_script.py'",
        "examples": ["db_migration_script.py", "daily_cleanup_script.py", "audit_status_script.py"],
        "anti_examples": ["main.py", "utils.py", "script.py", "run.py"],
        "extensions": [".py"],
    },
    # Python utilities - snake_case, MUST end with _util.py (Zero-Ambiguity Standard)
    "utility": {
        "pattern": r"^[a-z][a-z0-9_]*_util\.py$",
        "description": "snake_case ending with '_util.py'",
        "examples": ["string_formatter_util.py", "date_parser_util.py", "decorators_util.py"],
        "anti_examples": ["utils.py", "helpers.py", "util.py"],
        "extensions": [".py"],
    },
    # Python types/schemas - snake_case, MUST end with _types.py (Zero-Ambiguity Standard)
    "types": {
        "pattern": r"^[a-z][a-z0-9_]*_types\.py$",
        "description": "snake_case ending with '_types.py' for type definitions/schemas",
        "examples": ["user_profile_types.py", "api_response_types.py", "action_request_types.py"],
        "anti_examples": ["types.py", "models.py", "schemas.py"],
        "extensions": [".py"],
    },
    # Python exceptions - snake_case, MUST end with _exceptions.py (Zero-Ambiguity Standard)
    "exception": {
        "pattern": r"^[a-z][a-z0-9_]*_exceptions\.py$",
        "description": "snake_case ending with '_exceptions.py'",
        "examples": ["runtime_exceptions.py", "healer_exceptions.py", "core_exceptions.py"],
        "anti_examples": ["AgentRuntimeError.py", "HealerError.py", "Errors.py", "exceptions.py"],
        "extensions": [".py"],
    },
    # Strategy pattern - PascalCase ending with Strategy (Zero-Ambiguity Standard)
    "strategy": {
        "pattern": r"^[A-Z][a-zA-Z0-9]*Strategy\.py$",
        "description": "PascalCase ending with 'Strategy'",
        "examples": ["RecoveryStrategy.py", "BackoffStrategy.py", "ExpansionStrategy.py"],
        "anti_examples": ["strategy.py", "Strategies.py"],
        "extensions": [".py"],
    },
    # Adapter pattern - PascalCase ending with Adapter (Zero-Ambiguity Standard)
    "adapter": {
        "pattern": r"^[A-Z][a-zA-Z0-9]*Adapter\.py$",
        "description": "PascalCase ending with 'Adapter'",
        "examples": ["LocalDiskAdapter.py", "S3Adapter.py", "MCPAdapter.py"],
        "anti_examples": ["adapter.py", "Adapters.py"],
        "extensions": [".py"],
    },
    # Protocol/Interface - PascalCase starting with I, ending with Protocol (Zero-Ambiguity Standard)
    "protocol": {
        "pattern": r"^I[A-Z][a-zA-Z0-9]*Protocol\.py$",
        "description": "PascalCase starting with 'I', ending with 'Protocol'",
        "examples": ["IHealerProtocol.py", "IValidatorProtocol.py", "IExecutorProtocol.py"],
        "anti_examples": ["Protocol.py", "protocol.py", "HealerProtocol.py"],
        "extensions": [".py"],
    },
    # Mixin - snake_case ending with _mixin.py (Zero-Ambiguity Standard)
    "mixin": {
        "pattern": r"^[a-z][a-z0-9_]*_mixin\.py$",
        "description": "snake_case ending with '_mixin.py'",
        "examples": ["caching_mixin.py", "audit_trail_mixin.py", "rate_limit_mixin.py"],
        "anti_examples": ["Mixin.py", "mixins.py", "CachingMixin.py"],
        "extensions": [".py"],
    },
    # Sensor - snake_case ending with _sensor.py (Zero-Ambiguity Standard)
    "sensor": {
        "pattern": r"^[a-z][a-z0-9_]*_sensor\.py$",
        "description": "snake_case ending with '_sensor.py' for deterministic binary sensors",
        "examples": ["git_health_sensor.py", "import_violation_sensor.py", "file_integrity_sensor.py"],
        "anti_examples": ["Sensor.py", "sensors.py", "GitHealthSensor.py"],
        "extensions": [".py"],
    },
    # Validator - snake_case ending with _validator.py (Zero-Ambiguity Standard)
    "validator": {
        "pattern": r"^[a-z][a-z0-9_]*_validator\.py$",
        "description": "snake_case ending with '_validator.py' for deterministic validators",
        "examples": [
            "input_validator.py",
            "schema_validator.py",
            "ats_validator.py",
            "lead_quality_validator.py",
        ],
        "anti_examples": ["Validator.py", "validators.py", "InputValidator.py"],
        "extensions": [".py"],
    },
    # Python core modules - snake_case, high-signal, 2-3 words
    "core_module": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){1,2}\.py$",
        "description": "snake_case with 2-3 words containing high-signal keyword",
        "examples": ["InferenceEngine.py", "HybridRetriever.py", "semantic_cache.py"],
        "anti_examples": ["utils.py", "base.py", "core.py", "a_very_long_module_name_here.py"],
        "extensions": [".py"],
        "min_words": 2,
        "max_words": 3,
        # "require_signal": True,  # DEPRECATED: CANON_SIGNALS removed
    },
    # Python base classes - snake_case ending with _base
    "base_class": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+)*_base\.py$",
        "description": "snake_case ending with '_base'",
        "examples": ["outreach_base.py", "resume_base.py", "canon_base.py"],
        "anti_examples": ["base_agent.py", "BaseAgent.py", "base.py", "L1CognitionBaseAgent.py"],
        "extensions": [".py"],
        "min_words": 2,
        "max_words": 3,
    },
    # Jinja templates - snake_case, descriptive, 2-3 words
    "jinja_template": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){1,2}\.(jinja|jinja2|j2)$",
        "description": "snake_case with 2-3 words",
        "examples": ["resume_template.jinja", "email_outreach.jinja2", "prompt_system.j2"],
        "anti_examples": ["template.jinja", "t.jinja", "my_super_long_template_name.jinja"],
        "extensions": [".jinja", ".jinja2", ".j2"],
        "min_words": 2,
        "max_words": 3,
    },
    # JSON config files - snake_case, descriptive, 2-3 words
    "json_config": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){0,2}\.json$",
        "description": "snake_case with 1-3 words",
        "examples": ["registry.json", "agent_config.json", "prompt_templates.json"],
        "anti_examples": ["data.json", "config.json", "a_very_long_config_name_here.json"],
        "extensions": [".json"],
        "min_words": 1,
        "max_words": 3,
    },
    # YAML config files - snake_case, descriptive, 2-3 words
    "yaml_config": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){0,2}\.(yaml|yml)$",
        "description": "snake_case with 1-3 words",
        "examples": ["config.yaml", "AGENT_REGISTRY.yml", "prompt_config.yaml"],
        "anti_examples": ["c.yaml", "a_very_long_config_name_here.yml"],
        "extensions": [".yaml", ".yml"],
        "min_words": 1,
        "max_words": 3,
    },
    # Markdown documentation - snake_case or SCREAMING_SNAKE for special files
    "markdown_doc": {
        "pattern": r"^([a-z][a-z0-9]*(_[a-z0-9]+){0,3}|[A-Z][A-Z0-9]*(_[A-Z0-9]+)*)\.md$",
        "description": "snake_case or SCREAMING_SNAKE_CASE",
        "examples": ["README.md", "CHANGELOG.md", "api_reference.md", "getting_started.md"],
        "anti_examples": ["doc.md", "a.md"],
        "extensions": [".md"],
        "min_words": 1,
        "max_words": 4,
    },
    # Text files - snake_case, descriptive
    "text_file": {
        "pattern": r"^[a-z][a-z0-9]*(_[a-z0-9]+){0,2}\.txt$",
        "description": "snake_case with 1-3 words",
        "examples": ["requirements.txt", "test_results.txt", "mission_audit.txt"],
        "anti_examples": ["t.txt", "a_very_long_text_file_name.txt"],
        "extensions": [".txt"],
        "min_words": 1,
        "max_words": 3,
    },
}

# File extensions that NamingAgent should validate
VALIDATED_FILE_EXTENSIONS: frozenset[str] = frozenset(
    {
        # Python
        ".py",
        # Templates
        ".jinja",
        ".jinja2",
        ".j2",
        # Config
        ".json",
        ".yaml",
        ".yml",
        ".toml",
        # Documentation
        ".md",
        ".txt",
        ".rst",
        # Web
        ".html",
        ".css",
        ".js",
        ".ts",
    },
)

# Files exempt from naming validation (infrastructure files)
NAMING_EXEMPT_FILES: frozenset[str] = frozenset(
    {
        # Python infrastructure
        "__init__.py",
        "__main__.py",
        "conftest.py",
        "setup.py",
        # Config files
        "pyproject.toml",
        ".env",
        ".gitignore",
        ".dockerignore",
        "Dockerfile",
        "Makefile",
        "requirements.txt",
        # Documentation
        "README.md",
        "CHANGELOG.md",
        "LICENSE",
        "LICENSE.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        # IDE/Editor
        ".editorconfig",
        ".prettierrc",
        ".eslintrc",
        # Git
        ".gitattributes",
    },
)

# Directories exempt from naming validation
NAMING_EXEMPT_DIRS: frozenset[str] = frozenset(
    {
        "archives",
        "data",
        "docs",  # [ADDED] Valid root
        "legacy_code",
        "legacy_engines",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        ".pytest_cache",
        ".mypy_cache",
        "dist",
        "build",
        ".tox",
        "logs",
    },
)
FORBIDDEN_PATTERNS: Final[Sequence[Pattern]] = [
    re.compile("^utils\\.py$"),
    re.compile("^helper\\.py$"),
    re.compile("^temp\\.py$"),
    re.compile(".*_v\\d+\\.py$"),
    re.compile("^main\\.py$"),
    re.compile("^test\\.py$"),
    re.compile(".*_final\\.py$"),
    re.compile(".*_new\\.py$"),
    re.compile(".*_old\\.py$"),
    re.compile(".*_copy\\.py$"),
    re.compile(".*_backup\\.py$"),
    re.compile("^legacy_.*\\.py$"),
    re.compile("^.+_\\d+\\.py$"),
    re.compile("^draft_.*\\.py$"),
    # Schema Dissolution + Utils Sanitization
    re.compile(r"^utilities_.*"),  # Redundant prefix. Use simple snake_case.
    re.compile(r".*_util_util\.py$"),  # Stuttering suffix violation.
]
# Static protected files (hard-coded core infrastructure)
_STATIC_ROOT_PROTECTED_FILES: frozenset[str] = frozenset(
    {
        "canon_validator_agentic_v2.py",
        "canon_validator_agentic_v2_thin.py",
        "pyproject.toml",
        "README.md",
        "langgraph.json",
        ".env",
        "windsurfrules.md",
        ".gitignore",
        ".pre-commit-config.yaml",
        ".coverage",
        "pytest.ini",
        "tox.ini",
        ".python-version",
        ".schema_violations_tracking.yaml",
        ".secrets.baseline",
        "archives_restoration_manifest.json",
        "audit_residual_rglob_results.json",
        "git.code-workspace",
        "current_test_status.txt",
        "mission_audit.csv",
    },
)

# Dynamic protected files derived from SSOT constants
_DYNAMIC_ROOT_PROTECTED_FILES: frozenset[str] = frozenset(
    {
        AGENT_DISCOVERY_JSON,
        AGENT_DISCOVERY_MANIFEST_JSON,
        RUNTIME_STATE_JSON,
    },
)

# Final combined immutable set - Single Source of Truth for all root-level protection
ROOT_PROTECTED_FILES: frozenset[str] = _STATIC_ROOT_PROTECTED_FILES | _DYNAMIC_ROOT_PROTECTED_FILES

# 2. ENFORCE ROOT PURITY
# Only these folders are allowed at the project root level
PROJECT_ROOT_WHITELIST: Final[frozenset[str]] = frozenset(
    {
        "agentic_core",
        "apps_rg",
        "apps_lic",
        "apps_shared",
        "ops_scripts",
        "tests",
        "docs",
        "data",
        "archives",
        ".git",
        ".github",
        ".gravity_state",
        ".backup",
        ".vscode",
    },
)

# [SSOT] STRICT ROOT POLICY: Any file NOT in this list or matching these patterns
# is considered "Drift" and must be routed via ARTIFACT_ROUTING_MAP.
ROOT_ALLOWED_PATTERNS: Final[Sequence[Pattern]] = [
    re.compile(r"^trace_.*\.jsonl$"),  # Allowed: Mission Traces
    re.compile(r"^mission_.*\.log$"),  # Allowed: Mission Logs
    re.compile(r"^.*\.bat$"),  # Allowed: Windows Batch scripts
    re.compile(r"^.*\.sh$"),  # Allowed: Shell scripts
    re.compile(r"^root_drift_.*\.py$"),  # Allowed: Remediation scripts (Temp)
]

SOVEREIGN_EXCLUDED_FOLDERS: frozenset[str] = frozenset(
    {
        ".git",
        ".venv",
        "venv",
        "venv_stable",
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        ".mypy_cache",
        ".tox",
        "archives",
        "legacy_code",
        "legacy_engines",
        "legacy_resume_gen",
        "data",
        "docs",
        "env",
        "build",
        "dist",
        "_build",
        "Lib",
        "site-packages",
        "google",
        "gapic",
        "logging",
        "licenses",
        "src",
        "pip",
        "dist-info",
        "raw",
        "golden_state",
        "logs",
        "processed",
        "shared",
        "refs",
        "remotes",
        "v",
        "stubs",
        ".sovereign_healing_backup",
        ".idea",
        ".vscode",
        ".DS_Store",
        "Thumbs.db",
    },
)
FORBIDDEN_FOLDER_PATTERN: Pattern = re.compile(r"^\d+_")
FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset(
    {"legacy_code", "legacy_engines", "legacy_resume_gen", "old_core"},
)
TESTS_ROOT_FILE_WHITELIST: frozenset[str] = frozenset(
    {"conftest.py", "pytest.ini", "sovereign_smoke_test.py", "test_autonomous_improvements.py"},
)
AUTONOMOUS_AGENT_WHITELIST: frozenset[str] = frozenset(
    {
        "autonomous_checkpoint_manager.py",
        "autonomous_state_guardian.py",
        "self_updating_safety_engine.py",
        "neural_auto_immune_agent.py",
    },
)
protected_folders: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS
ignore_dirs: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS
sovereign_ignored_folders: Final[frozenset[str]] = SOVEREIGN_EXCLUDED_FOLDERS
HEALING_CONFIG: Final[Mapping[str, int]] = {
    "max_rounds": int(os.getenv("MAX_HEALING_ROUNDS", "10")),
    "max_per_file": int(os.getenv("MAX_HEALING_PER_FILE", "8")),
    "global_budget": int(
        os.getenv("GLOBAL_HEALING_BUDGET", "500"),
    ),  # [TEMP BOOST] Unblock 10k Violation backlog
    "max_moves_per_run": 250,
    "max_shared_upgrades_per_run": 10,  # [CIRCUIT BREAKER] Prevent mass-migration to apps_shared
    "max_fissions_per_run": 50,
    "dust_threshold": 40,  # Minimum lines for a module to exist (Span-of-Two)
}
AGENT_RESILIENCE_CONFIG: Final[Mapping[str, int | float]] = {
    "retry_count": int(os.getenv("AGENT_RETRY_COUNT", "3")),
    "backoff_base": float(os.getenv("AGENT_RETRY_BACKOFF_BASE", "0.5")),
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
    "timeout_seconds": int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800")),
}
MCP_CAPABILITIES: Final[Mapping[str, Mapping[str, bool | str]]] = {
    "router": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "marketplace_filter": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "filesystem": {"enabled": True, "path": "agentic_core.L4_state.filesystem"},
    "figma": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "fetch": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
    "semantic_cache": {"enabled": True, "path": "agentic_core.L2_execution.enforcement"},
}
SCOPE_SUMMARY_EXCLUSIONS: frozenset[str] = frozenset({"stubs", ".sovereign_healing_backup", "__pycache__"})

# === ALLOWED DUPLICATE FILENAMES ===
# These files are permitted to exist with the same name across multiple directories.
# This is the SSOT for filename uniqueness exceptions - all agents must respect this list.
ALLOWED_DUPLICATE_FILENAMES: frozenset[str] = frozenset(
    {
        # Python package infrastructure (MUST exist in every package)
        "__init__.py",
        "__main__.py",
        # Testing infrastructure (pytest requires these in test directories)
        "conftest.py",
        # Common module patterns (legitimate per-package definitions)
        "context.py",
        "config.py",
        "constants.py",
        "exceptions.py",
        "types.py",
        "models.py",
        "base.py",
        "utils.py",
        "helpers.py",
        "common.py",
        # observability patterns (per-engine instrumentation)
        "observability.py",
        "metrics.py",
        "logging.py",
        "tracing.py",
        # Autonomous agent patterns (per-engine autonomy)
        "proactive.py",
        "autonomous.py",
        "self_healing.py",
        # Prompt patterns (per-domain prompts)
        "prompts.py",
        "templates.py",
    },
)


def safe_prefixed_filename(prefix: str, filename: str) -> str:
    """
    SSOT safeguard: Generate a prefixed filename WITHOUT duplicate prefixes.

    Prevents name sprawl like:
        healing_strategies.py -> healing_healing_strategies.py (BAD)

    Instead produces:
        healing_strategies.py -> healing_strategies.py (already has prefix)
        strategies.py -> healing_strategies.py (prefix added)

    Args:
        prefix: The prefix to add (e.g., 'healing', 'auditors')
        filename: The original filename

    Returns:
        Filename with prefix added only if not already present
    """
    if not prefix:
        return filename

    # Normalize prefix (remove trailing underscore if present)
    prefix = prefix.rstrip("_")

    # Check if filename already starts with the prefix
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    "." + filename.rsplit(".", 1)[1] if "." in filename else ""

    # If already has prefix, return unchanged
    if stem.startswith(prefix + "_") or stem == prefix:
        return filename

    # Add prefix
    return f"{prefix}_{filename}"


def validate_no_duplicate_prefix(filename: str) -> tuple[bool, str]:
    """
    SSOT safeguard: Detect if a filename has duplicate prefixes.

    Examples of violations:
        healing_healing_strategies.py -> True, "Duplicate prefix: healing_"
        auditors_auditors_report.py -> True, "Duplicate prefix: auditors_"

    Returns:
        (has_violation, message)
    """
    stem = filename.rsplit(".", 1)[0] if "." in filename else filename
    parts = stem.split("_")

    # Check for consecutive duplicate parts
    for i in range(len(parts) - 1):
        if parts[i] == parts[i + 1] and parts[i]:  # Non-empty consecutive duplicates
            return True, f"Duplicate prefix detected: '{parts[i]}_' repeated in '{filename}'"

    return False, ""


DISCOVERY_EXCLUDED_TERRITORIES: frozenset[str] = frozenset(
    {"runtime_shared", "legacy_code", "legacy_engines", "archives", "stubs", "examples"},
)
PYTHON_STDLIB_MODULES: frozenset[str] = frozenset(
    {
        "os",
        "sys",
        "pathlib",
        "logging",
        "asyncio",
        "typing",
        "dataclasses",
        "collections",
        "json",
        "re",
        "datetime",
        "functools",
        "itertools",
        "abc",
        "enum",
        "contextlib",
        "threading",
        "time",
        "random",
        "math",
        "urllib",
        "http",
        "socket",
        "subprocess",
        "shutil",
        "hashlib",
        "uuid",
        "copy",
        "io",
        "traceback",
        "inspect",
        "importlib",
        "warnings",
        "pickle",
    },
)
ROOT_WHITELIST: set[str] = set(SOVEREIGN_TERRITORIES.keys())

# ============================================================================
# GLOBAL EXCLUDED DIRECTORIES - Production Lens SSOT
# ============================================================================
GLOBAL_EXCLUDED_DIRS: frozenset[str] = frozenset(
    {
        # Build/cache directories
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        "build",
        "dist",
        ".eggs",
        # Version control
        ".git",
        ".svn",
        ".hg",
        # Virtual environments
        ".venv",
        "venv",
        "env",
        ".env",
        "node_modules",
        # Coverage/reports
        "coverage_html",
        "htmlcov",
        ".coverage",
        "reports",
        # Archives and backups
        "archives",
        ".sovereign_healing_backup",
        # Test directories (Production Lens)
        "tests",
    },
)


def is_path_allowed(rel_path: str | Path) -> bool:
    """
    [ULTRA-HARDENED] Determines if a path conforms to SOVEREIGN_TERRITORIES.
    Enforces path normalization, cross-domain deportation, and depth precision.
    """
    # 1. Path Normalization: Neutralize traversal (../) and redundant slashes (//)
    original_path = str(rel_path).replace("\\", "/")

    # [CRITICAL] Block paths with redundant slashes for security
    if "//" in original_path:
        return False

    normalized_path = os.path.normpath(original_path).replace("\\", "/")

    # Reject paths that normalize to parent directories or empty
    if not normalized_path or normalized_path.startswith("..") or normalized_path == ".":
        return False

    # Filter out empty parts from normalized path
    parts = [p for p in normalized_path.split("/") if p]
    if not parts:
        return False

    if len(parts) == 1:
        # Allow sovereign territory directories at root level
        if parts[0] in SOVEREIGN_TERRITORIES:
            return True
        return parts[0] in ROOT_PROTECTED_FILES or parts[0] in ALLOWED_DUPLICATE_FILENAMES

    root = parts[0]
    if root not in SOVEREIGN_TERRITORIES:
        return False

    config = SOVEREIGN_TERRITORIES[root]

    # 2. Cross-Sovereign Deportation: Prevent App/Test leakage into Core
    filename = parts[-1]
    if root == "agentic_core":
        # Critical Analysis: Blocks 'rg_', 'lic_', and 'test_' prefixes to prevent
        # semantic drift while allowing __init__.py and L0 scripts.
        if filename.startswith(("rg_", "lic_", "test_")):
            if not (filename == "__init__.py" or "L0_maintenance/scripts" in normalized_path):
                return False

    # 3. Depth Enforcement: L4 applies to folder structure, not the filename
    path_depth = len(parts)
    # If the last part is a file, the 'folder depth' is path_depth - 1
    folder_depth = path_depth - 1 if "." in filename else path_depth

    # [CRITICAL] For L4 specializations, ensure we don't exceed depth 5 (L4 + 1 for file)
    if folder_depth > config["depth"] + 1 and not is_l4_approved(normalized_path):
        return False

    # [CRITICAL] Even for L4-approved paths, don't allow depth 6+ (L4 + L5 + file)
    if folder_depth > config["depth"] + 2:
        return False

    # Check subfolder existence and nested forbidden patterns
    if len(parts) > 1:
        sub_name = parts[1]
        allowed_subs = config["subfolders"]

        # [HARDENING] Check for forbidden patterns at the subfolder level (e.g., L3_ prefixes)
        if isinstance(allowed_subs, dict) and sub_name in allowed_subs:
            sub_cfg = allowed_subs[sub_name]
            if isinstance(sub_cfg, dict):
                patterns = sub_cfg.get("forbidden_patterns", [])
                if any(re.search(p, normalized_path) for p in patterns):
                    return False  # BLOCK: Legacy structure detected

        if isinstance(allowed_subs, dict):
            if sub_name not in allowed_subs:
                return sub_name.endswith(".py")  # Root files like __init__.py
        elif isinstance(allowed_subs, list):
            if sub_name not in allowed_subs:
                # Allow files at the correct depth (not subdirectories)
                if "." in sub_name and len(parts) <= config["depth"] + 1:
                    return True
                return False

    return True


def is_l4_approved(path: str) -> bool:
    """
    [HARDENED] Helper to verify L4 specializations.
    Safely navigates both List-based (Apps) and Dict-based (Core) subfolders.
    ONLY approves exactly depth 4 folder structures (excluding filename).
    """
    parts = [p for p in path.split("/") if p]
    if len(parts) < 4:
        return False

    root, l2, l3, l4 = parts[0], parts[1], parts[2], parts[3]

    # Remove filename to check folder structure (depth should be exactly 4 folders)
    folder_parts = parts[:-1] if parts and "." in parts[-1] else parts

    # Must be exactly depth 4 folders for L4 approval
    if len(folder_parts) != 4:
        return False

    try:
        # Check if this is an L4-approved folder path first
        full_folder_path = f"{root}/{l2}/{l3}"
        if full_folder_path in L4_APPROVED_FOLDERS:
            # For approved folders, check if l4 is a valid L4 subfolder in L4_SUBFOLDER_MAP
            # Need to find the right key in L4_SUBFOLDER_MAP and navigate the nested structure
            l4_structure = L4_SUBFOLDER_MAP.get(l2, {})
            if isinstance(l4_structure, dict) and l3 in l4_structure:
                l3_structure = l4_structure[l3]
                if isinstance(l3_structure, dict):
                    # Check if l4 is directly a key in the L3 structure
                    if l4 in l3_structure:
                        return True
                    # Check if l4 is in any of the subfolder lists within the L3 structure
                    for subfolder_list in l3_structure.values():
                        if isinstance(subfolder_list, list) and l4 in subfolder_list:
                            return True

        # Fallback: Check l3-specific configuration for l4_specializations
        root_cfg = SOVEREIGN_TERRITORIES.get(root, {})
        subs = root_cfg.get("subfolders", {})

        # Critical Analysis: Prevent TypeError by ensuring 'subs' is a Dict
        # before attempting L2/L3 key lookups (fixes apps_rg crash).
        if not isinstance(subs, dict):
            return False

        # Check both L2 and L3 for the specialization map (Fallback lookup)
        l2_cfg = subs.get(l2, {})
        if isinstance(l2_cfg, dict):
            l3_cfg = l2_cfg.get(l3, {})
            if isinstance(l3_cfg, dict):
                specs = l3_cfg.get("l4_specializations", [])
                if l4 in specs:
                    return True

        return False
    except (KeyError, TypeError, AttributeError):
        return False


GRAVITY_CONFIG: Any = {
    "enabled": True,
    "UPSTREAM_SOVEREIGN_ROOTS": ["agentic_core"],
    "downstream_domains": ["apps_rg", "apps_lic", "apps_shared", "tests"],
    "exemptions": [],
}
GRAVITY_SURGERY_ENABLED: Any = GRAVITY_CONFIG["enabled"]
UPSTREAM_SOVEREIGN_ROOTS: Any = frozenset(GRAVITY_CONFIG["UPSTREAM_SOVEREIGN_ROOTS"])
DOWNSTREAM_ROOTS: Any = frozenset(GRAVITY_CONFIG["downstream_domains"])
_semantic_templates = {
    "node_pattern": {
        "entity_types": ["Class"],
        "examples_suffix": ["Node", "ExtractNode", "DraftNode"],
    },
    "flow_pattern": {
        "entity_types": ["Class"],
        "bases": ["BaseFlow"],
        "examples_suffix": ["Flow", "Pipeline", "Campaign"],
    },
    "engine_pattern": {
        "entity_types": ["Class"],
        "bases": ["BaseEngine"],
        "examples_suffix": ["Engine", "Builder", "Driver"],
    },
    "template_pattern": {
        "entity_types": ["Class", "Dict"],
        "bases": ["BaseTemplate"],
        "examples_suffix": ["Template", "Layout", "Format"],
    },
}
# ============================================================================
# ARTIFACT ROUTING MAP (The "Customs" Agent Logic)
# ============================================================================
# Routes non-code artifacts and standalone scripts based on INTELLIGENT CONTENT SIGNATURES.
# [SSOT 2026-01-27] Ultra-Hardened: Includes strict 'forbidden_signals' to prevent gravity leakage.
ARTIFACT_ROUTING_MAP: Final[Mapping[str, Mapping[str, Any]]] = {
    # === DOCS & REPORTS ===
    "docs/reports/assessments": {
        "description": "Gap analyses, architectural assessments, and strategic reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "keywords": ["assessment", "analysis", "gap", "architecture", "strategic"],
        },
        "naming_patterns": [
            re.compile(r".*assessment.*"),
            re.compile(r".*analysis.*"),
            re.compile(r".*gap.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/audit": {
        "description": "Structural audits, drift analysis, and compliance reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "headers": ["# Audit Report", "## Violations", "## Drift"],
            "json_keys": ["critical_violations", "compliance_score", "drift_metrics"],
            "keywords": ["audit", "drift", "variance", "compliance", "SSOT"],
        },
        "naming_patterns": [
            re.compile(r".*audit.*"),
            re.compile(r".*drift.*"),
            re.compile(r".*variance.*"),
            re.compile(r".*compliance.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/coverage": {
        "description": "Test coverage reports and code quality metrics.",
        "file_extensions": [".md", ".json", ".html", ".xml", ".txt"],
        "content_signals": {
            "keywords": ["coverage", "test", "quality", "percentage", "htmlcov"],
        },
        "naming_patterns": [
            re.compile(r".*coverage.*"),
            re.compile(r".*test.*"),
            re.compile(r".*quality.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/security": {
        "description": "Security assessments, vulnerability scans, and safety reports.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "keywords": ["security", "vulnerability", "safety", "hardened", "guardrails"],
        },
        "naming_patterns": [
            re.compile(r".*security.*"),
            re.compile(r".*vulnerability.*"),
            re.compile(r".*hardened.*"),
            re.compile(r".*hardening.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/telemetry": {
        "description": "System telemetry, performance metrics, and observability data.",
        "file_extensions": [".md", ".json", ".csv", ".txt"],
        "content_signals": {
            "keywords": ["telemetry", "metrics", "performance", "observability"],
        },
        "naming_patterns": [
            re.compile(r".*telemetry.*"),
            re.compile(r".*metrics.*"),
            re.compile(r".*performance.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    "docs/reports/missions": {
        "description": "High-level mission execution traces and runtime logs (Deported from Root).",
        "file_extensions": [".jsonl", ".trace", ".log", ".json"],
        "content_signals": {
            "json_keys": ["mission_id", "trace_id", "execution_log"],
            "keywords": ["mission", "trace", "execution"],
        },
        "naming_patterns": [
            re.compile(r".*mission.*"),
            re.compile(r".*trace.*"),
            re.compile(r".*execution.*"),
        ],
        "forbidden_extensions": [".py", ".js", ".sh", ".bat", ".ts"],
        "forbidden_keywords": ["def ", "class ", "import ", "function ", "var ", "const "],
    },
    # === DATA & LOGS (Runtime Debugging) ===
    "agentic_core/L0_maintenance/utils": {
        "description": "Runtime debug logs, error dumps, and stack traces.",
        "file_extensions": [".log", ".err", ".out", ".txt"],
        "content_signals": {
            "keywords": [
                "DEBUG",
                "ERROR",
                "Traceback (most recent call)",
                "Exception",
                "Stack trace",
            ],
        },
        "naming_patterns": [
            re.compile(r".*debug.*"),
            re.compile(r".*error.*"),
            re.compile(r".*crash.*"),
        ],
        # HARDENING: Explicitly forbid Python scripts even if they contain the word "error"
        "forbidden_extensions": [".py", ".pyc", ".pyo"],
        "forbidden_keywords": ["def main", "if __name__", "import sys", "class "],
    },
    # === PYTHON UTILITY SCRIPTS (Standalone) ===
    "agentic_core/L0_maintenance/scripts": {
        "description": "Python utility scripts, maintenance tools, and standalone executables.",
        "file_extensions": [".py"],
        "content_signals": {
            "keywords": [
                "def main(",
                "if __name__",
                "#!/usr/bin/env python",
                "import sys",
                "argparse",
                "click",
                "typer",
            ],
            "imports": ["os", "sys", "shutil", "pathlib", "logging"],
        },
        "naming_patterns": [
            re.compile(r".*script.*"),
            re.compile(r".*fixer.*"),
            re.compile(r".*tool.*"),
            re.compile(r".*util.*"),
            re.compile(r".*cleaner.*"),
            re.compile(r".*migrat.*"),
        ],
        # HARDENING: Prevent Tests and Core Modules from being misclassified as scripts
        "forbidden_keywords": [
            "class Test",
            "def test_",
            "import unittest",
            "import pytest",  # Not a Test
            "class BaseAgent",
            "class Sovereign",  # Not a Core Agent
        ],
    },
    # === MISSION TRACES (Root Approved) ===
    "logs": {
        "description": "High-level Mission Execution Traces (Approved for Root).",
        "file_extensions": [".jsonl", ".trace"],
        "content_signals": {
            "json_keys": ["mission_id", "step_count", "agent_action", "thought_process"],
        },
        "naming_patterns": [re.compile(r"^trace_.*"), re.compile(r"^mission_.*")],
        # HARDENING: Prevent generic JSON data or debug logs
        "forbidden_keywords": ["Traceback", "Exception", "dataset_version"],
    },
    # === DATASETS ===
    "data/processed": {
        "description": "Structured data outputs and intermediate processing states.",
        "file_extensions": [".json", ".csv", ".parquet"],
        "content_signals": {
            "json_keys": ["dataset_version", "record_count", "processed_at", "schema_version"],
        },
        "naming_patterns": [
            re.compile(r".*dataset.*"),
            re.compile(r".*processed.*"),
            re.compile(r"agent_discovery.*\.json$"),
            re.compile(r".*manifest.*\.json$"),
        ],
        # HARDENING: Prevent config files or code
        "forbidden_keywords": ["def ", "class ", "api_key", "secret"],
    },
}

# ============================================================================
# ARTIFACT ROUTING VALIDATION UTILITIES
# ============================================================================


def validate_artifact_routing(
    filename: str,
    content: str | None = None,
) -> tuple[bool, str | None, str | None]:
    """
    Validate file against ARTIFACT_ROUTING_MAP negative logic.

    Implements HARD REJECT for files that match forbidden_extensions or forbidden_keywords
    ONLY when they would otherwise match the positive signals for that destination.
    This prevents gravity leakage where code files get misclassified as reports/logs/data.

    Args:
        filename: Name of the file to validate
        content: Optional file content for keyword checking

    Returns:
        Tuple of (is_valid, matched_destination, rejection_reason)
        - is_valid: False if file matches forbidden signals (HARD REJECT)
        - matched_destination: Destination path if positive match found
        - rejection_reason: Reason for rejection if is_valid is False

    Example:
        >>> validate_artifact_routing("test_report.py", "def main():")
        (False, None, "Forbidden extension .py for destination docs/reports")

        >>> validate_artifact_routing("audit_results.md", "# Assessment Report")
        (True, "docs/reports", None)
    """
    file_ext = Path(filename).suffix.lower()

    for dest, rules in ARTIFACT_ROUTING_MAP.items():
        # First check if file would match positive signals for this destination
        allowed_exts = rules.get("file_extensions", [])
        matches_positive = False

        # Check extension match
        if allowed_exts and file_ext in allowed_exts:
            matches_positive = True

        # Check naming patterns
        naming_patterns = rules.get("naming_patterns", [])
        if naming_patterns:
            for pattern in naming_patterns:
                if pattern.match(filename):
                    matches_positive = True
                    break

        # Check content signals if provided
        if content and matches_positive:
            content_signals = rules.get("content_signals", {})

            # Check headers
            headers = content_signals.get("headers", [])
            if headers and any(header in content for header in headers):
                matches_positive = True

            # Check keywords
            keywords = content_signals.get("keywords", [])
            if keywords and any(keyword in content for keyword in keywords):
                matches_positive = True

        # ONLY apply negative checks if file matches positive signals
        if matches_positive:
            # 1. NEGATIVE EXTENSION CHECK (HARD REJECT)
            forbidden_exts = rules.get("forbidden_extensions", [])
            if forbidden_exts and file_ext in forbidden_exts:
                return (False, None, f"Forbidden extension {file_ext} for destination {dest}")

            # 2. NEGATIVE CONTENT CHECK (HARD REJECT)
            if content:
                forbidden_keywords = rules.get("forbidden_keywords", [])
                if forbidden_keywords:
                    for keyword in forbidden_keywords:
                        if keyword in content:
                            return (
                                False,
                                None,
                                f"Forbidden keyword '{keyword}' for destination {dest}",
                            )

            # Passed all checks - return positive match
            return (True, dest, None)

    # No match found (neither positive nor negative)
    return (True, None, None)


def check_forbidden_signals(filename: str, content: str | None = None) -> str | None:
    """
    Quick check for forbidden signals across all routing rules.

    Returns rejection reason if file matches any forbidden_extensions or forbidden_keywords,
    None otherwise.

    This is a fast-path check for agents that only need to know if a file is forbidden,
    without needing the full routing destination.

    Args:
        filename: Name of the file to check
        content: Optional file content for keyword checking

    Returns:
        Rejection reason string if forbidden, None if allowed
    """
    is_valid, _, rejection_reason = validate_artifact_routing(filename, content)
    return rejection_reason if not is_valid else None


# ============================================================================
# TEST TAXONOMY SIGNALS (The "Test Sorter" Logic)
# ============================================================================
# Strictly enforces the separation of Unit, Integration, and E2E tests based on
# their import dependencies and decorators.
TEST_TYPE_SIGNALS: Final[Mapping[str, Mapping[str, Any]]] = {
    "tests/unit": {
        "description": "Isolated logic tests using mocks and no external I/O.",
        "imports": ["unittest.mock", "MagicMock", "patch", "pytest_mock"],
        "forbidden_imports": ["playwright", "selenium", "requests", "httpx", "psycopg2"],
        "decorators": ["@pytest.mark.unit"],
        "class_patterns": [".*Unit.*", ".*TestBase$"],
        "priority": 1,
    },
    "tests/integration": {
        "description": "Component interaction tests involving DB, API, or Filesystem.",
        "imports": ["fastapi.testclient", "httpx", "requests", "sqlalchemy", "redis"],
        "decorators": ["@pytest.mark.integration", "@pytest.mark.asyncio"],
        "class_patterns": [".*Integration.*", ".*ApiTest.*"],
        "priority": 2,
    },
    "tests/e2e": {
        "description": "Full system simulation using browser automation or real environments.",
        "imports": ["playwright", "selenium", "puppeteer", "subprocess"],
        "decorators": ["@pytest.mark.e2e"],
        "class_patterns": [".*E2E.*", ".*Browser.*", ".*Flow.*"],
        "priority": 3,
    },
}

# ============================================================================
# LEGACY/ZOMBIE SIGNALS (The "Archivist" Logic)
# ============================================================================
# Detects deprecated or superseded code and routes it to archives.
LEGACY_AST_SIGNALS: Final[Mapping[str, Mapping[str, Any]]] = {
    "archives/legacy_code": {
        "description": "Code explicitly marked as deprecated, legacy, or v1.",
        "decorators": ["@deprecated", "@obsolete"],
        "docstring_markers": ["DEPRECATED", "LEGACY", "DO NOT USE", "MOVED TO"],
        "class_patterns": [".*Legacy.*", ".*Old$", ".*V1$"],
        "function_calls": ["warnings.warn"],
        "variable_markers": ["DEPRECATION_WARNING"],
    },
}

# === AST PLACEMENT SIGNAL REGISTRY ===
# Maps AST patterns to exact L1/L2 paths for file placement
# This is the SSOT for AST-based file placement decisions
AST_PLACEMENT_SIGNALS: Final[Mapping[str, Mapping[str, Any]]] = {
    # [NEW] Interfaces - Sovereign Protocols (Constitutional Priority)
    "agentic_core/interfaces": {
        "class_patterns": ["^I[A-Z].*Protocol$", "^I[A-Z].*$"],
        "base_classes": ["Protocol", "ABC", "typing.Protocol", "abc.ABC"],
        "function_patterns": [],
        "import_signals": ["typing.Protocol", "abc.ABC", "abc.abstractmethod"],
        "keyword_signals": ["protocol", "interface", "contract", "abstract"],
        "filename_patterns": ["^I[A-Z].*Protocol\\.py$"],
        "decorator_signals": ["@abstractmethod", "@runtime_checkable"],
        "weight": 100,  # Constitutional Priority - same as base_agents
    },
    # Base agents - Constitutional Priority (V10 Zero-Ambiguity: Base-Only suffix)
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
        "function_patterns": [],
        "import_signals": [],
        "keyword_signals": ["sovereign", "base", "inheritance", "abstract", "foundation"],
        "decorator_signals": [],
        "weight": 100,  # Constitutional Priority
    },
    # [NEW] Pydantic Domain Modeling (Schema Separation)
    # Zero-Ambiguity: Also routes *_types.py files here
    "agentic_core/runtime/types": {
        "class_patterns": [".*Model$", ".*Schema$", ".*DTO$", ".*Types$"],
        "base_classes": ["BaseModel", "pydantic.BaseModel"],
        "import_signals": ["pydantic", "typing", "typing_extensions"],
        "keyword_signals": [
            "field",
            "validator",
            "root_validator",
            "config",
            "TypeAlias",
            "TypedDict",
            "Literal",
            "Union",
            "Optional",
        ],
        "filename_patterns": [".*_types\\.py$"],  # Route *_types.py files here
        "weight": 10,
    },
    # [NEW] Configuration Modeling
    "agentic_core/config": {
        "class_patterns": [".*Config$", ".*Settings$"],
        "base_classes": ["BaseSettings"],
        "import_signals": ["pydantic_settings"],
        "keyword_signals": ["env_file", "secrets", "api_key"],
        "weight": 10,
    },
    # [NEW] Knowledge Management (RAG, Document Loaders, Orchestrators)
    "agentic_core/knowledge": {
        "class_patterns": [".*Orchestrator$", ".*Manager$", ".*Loader$", ".*Cache$"],
        "base_classes": ["BaseDocumentLoader"],
        "function_patterns": ["retrieve_.*", "ingest_.*", "index_.*"],
        "import_signals": ["knowledge", "rag", "document_loaders"],
        "keyword_signals": ["rag", "retrieval", "knowledge", "document", "ingest", "orchestrator"],
        "weight": 12,
    },
    # L1_cognition placements
    "agentic_core/L1_cognition/thought_engine": {
        "class_patterns": [".*Node$", ".*Thought.*", ".*Reason.*", ".*Chain.*", ".*Strategy$"],
        "base_classes": ["BaseNode", "ThoughtNode", "ReActNode", "ReActStrategy"],
        "function_patterns": ["think_.*", "reason_.*", "decompose_.*"],
        "import_signals": ["langchain", "langgraph", "thought_engine"],
        "keyword_signals": ["thought", "reasoning", "decomposition", "chain_of_thought", "react", "strategy"],
        "decorator_signals": ["@thought_node", "@reasoning_step"],
        "weight": 15,  # Domain Logic tier
    },
    # DISSOLVED: "agentic_core/L1_cognition/intent_analysis" removed
    "agentic_core/L1_cognition/planning": {
        "class_patterns": [".*Planner.*", ".*Strategy.*", ".*Plan.*"],
        "base_classes": ["BasePlanner", "StrategyPlanner"],
        "function_patterns": ["plan_.*", "strategize_.*", "decompose_task.*"],
        "import_signals": ["planning", "strategy"],
        "keyword_signals": ["planner", "strategy", "plan", "goal", "objective"],
        "weight": 15,
    },
    # L2_execution placements
    "agentic_core/L2_execution/reasoning": {
        "class_patterns": [".*Agent$", ".*Tool$", ".*Handler$"],
        "base_classes": ["SubAtomicAgent", "BaseTool", "ToolHandler"],
        "function_patterns": ["execute_.*", "run_tool.*", "invoke_.*"],
        "import_signals": ["tool_registry", "SubAtomicAgent"],
        "keyword_signals": ["tool", "execute", "invoke", "action", "handler"],
        "decorator_signals": ["@tool", "@action"],
        "weight": 9,
    },
    "agentic_core/L2_execution/action_handlers": {
        "class_patterns": [".*ActionHandler$", ".*Executor$"],
        "base_classes": ["ActionHandler", "BaseExecutor"],
        "function_patterns": ["handle_action.*", "execute_action.*"],
        "import_signals": ["action_handlers"],
        "keyword_signals": ["action", "handler", "execute", "perform"],
        "weight": 7,
    },
    "agentic_core/L2_execution/enforcement": {
        "class_patterns": [".*MCP.*", ".*Client$", ".*Server$"],
        "base_classes": ["MCPClient", "MCPServer"],
        "function_patterns": ["mcp_.*", "fetch_.*", "connect_.*"],
        "import_signals": ["mcp", "model_context_protocol"],
        "keyword_signals": ["mcp", "model_context_protocol", "fetch", "client", "server"],
        "weight": 9,
    },
    # L3_orchestration placements
    "agentic_core/L3_orchestration/reasoning": {
        "class_patterns": [".*Engine$", ".*Orchestrator$", ".*Controller$", ".*Coordinator$"],
        "base_classes": ["BaseEngine", "WorkflowEngine", "Orchestrator"],
        "function_patterns": ["orchestrate_.*", "coordinate_.*", "run_workflow.*"],
        "import_signals": ["workflow_engines", "orchestration"],
        "keyword_signals": [
            "orchestrator",
            "workflow",
            "engine",
            "coordinate",
            "mission",
            "controller",
        ],
        "decorator_signals": ["@workflow", "@orchestrate"],
        "weight": 16,
    },
    "agentic_core/L3_orchestration/reasoning": {
        "class_patterns": [".*Fission.*", ".*Split.*", ".*Decompose.*"],
        "base_classes": ["FissionEngine", "TaskSplitter"],
        "function_patterns": ["fission_.*", "split_.*", "decompose_.*"],
        "import_signals": ["fission_logic"],
        "keyword_signals": ["fission", "split", "decompose", "parallel", "distribute"],
        "weight": 16,
    },
    "agentic_core/L3_orchestration/meta_learning": {
        "class_patterns": [".*MetaLearn.*", ".*Adaptive.*", ".*SelfImprove.*"],
        "base_classes": ["MetaLearner", "AdaptiveAgent"],
        "function_patterns": ["meta_learn.*", "adapt_.*", "self_improve.*"],
        "import_signals": ["meta_learning"],
        "keyword_signals": ["meta", "learning", "adaptive", "self_improve", "evolve"],
        "weight": 16,
    },
    # L4_state placements
    "agentic_core/L4_state/memory": {
        "class_patterns": [".*Context.*", ".*State.*", ".*Session.*"],
        "base_classes": ["ValidationContext", "StateManager"],
        "function_patterns": ["get_context.*", "set_state.*", "validate_context.*"],
        "import_signals": ["validation_context"],
        "keyword_signals": ["context", "state", "session", "validation"],
        "weight": 14,
    },
    "agentic_core/L4_state/enforcement": {
        "class_patterns": [".*Ledger.*", ".*Audit.*", ".*Log.*", ".*Historian.*"],
        "base_classes": ["BaseLedger", "AuditLog"],
        "function_patterns": ["log_.*", "record_.*", "audit_.*"],
        "import_signals": ["ledger"],
        "keyword_signals": ["ledger", "audit", "log", "record", "Historian", "trail"],
        "weight": 14,
    },
    "agentic_core/L4_state/memory": {
        "class_patterns": [".*Memory.*", ".*cache.*", ".*Store.*", ".*Adapter$"],
        "base_classes": ["MemoryStore", "CacheManager"],
        "function_patterns": ["store_.*", "retrieve_.*", "cache_.*"],
        "import_signals": ["pinecone", "redis", "memory"],
        "keyword_signals": ["memory", "cache", "store", "retrieve", "embedding", "vector", "adapter"],
        "weight": 14,
    },
    # L5_safety placements
    "agentic_core/L5_safety/enforcement": {
        "class_patterns": [".*Guardrail.*", ".*Limit.*", ".*Throttle.*", ".*Healer.*"],
        "base_classes": ["BaseGuardrail", "RateLimiter", "CircuitBreaker"],
        "function_patterns": ["guard_.*", "limit_.*", "throttle_.*", "heal_.*"],
        "import_signals": ["guardrails", "safety"],
        "keyword_signals": [
            "guardrail",
            "safety",
            "limit",
            "throttle",
            "heal",
            "circuit",
            "breaker",
        ],
        "decorator_signals": ["@guardrail", "@rate_limit"],
        "weight": 25,
    },
    "agentic_core/L5_safety/validators": {
        "purpose": "Deterministic safety checks and domain validation",
        "class_patterns": [".*Validator.*", ".*Enforcer.*", ".*Checker.*", ".*Agent$", ".*Deterministic$"],
        "base_classes": ["BaseValidator", "Enforcer"],
        "function_patterns": ["validate_.*", "enforce_.*", "check_.*"],
        "import_signals": ["validators", "compliance"],
        "keyword_signals": [
            "validator",
            "enforce",
            "compliance",
            "check",
            "verify",
            "audit",
            "deterministic",
            "sanitizer",
        ],
        "filename_patterns": [".*_validator\\.py$"],
        "weight": 50,  # Increased to attract deterministic validators from L0
    },
    "agentic_core/L5_safety/enforcement": {
        "class_patterns": [".*Gravity.*", ".*Import.*", ".*Waterfall.*"],
        "base_classes": ["GravityEnforcer", "ImportValidator"],
        "function_patterns": ["check_gravity.*", "validate_import.*"],
        "import_signals": ["gravity"],
        "keyword_signals": ["gravity", "import", "waterfall", "upstream", "downstream"],
        "weight": 22,
    },
    "agentic_core/L5_safety/reasoning": {
        "class_patterns": [".*RedTeam.*", ".*Adversarial.*", ".*Attack.*"],
        "base_classes": ["RedTeamAgent", "AdversarialTester"],
        "function_patterns": ["attack_.*", "probe_.*", "fuzz_.*"],
        "import_signals": ["red_teaming"],
        "keyword_signals": ["redteam", "adversarial", "attack", "probe", "jailbreak", "exploit"],
        "weight": 20,
    },
    # [NEW] L5_safety/utils - Security utilities (higher weight than config to win gravity)
    "agentic_core/L5_safety/utils": {
        "class_patterns": [".*Security.*", ".*Control.*", ".*Subprocess.*"],
        "base_classes": [],
        "function_patterns": ["validate_.*", "safe_.*", "security_.*", "create_instance.*"],
        "import_signals": ["L5_safety", "security"],
        "keyword_signals": ["security", "controls", "safe_execute", "subprocess", "injection", "whitelist"],
        "filename_patterns": [".*security.*_util\\.py$", ".*controls.*_util\\.py$"],
        "weight": 26,  # Higher than config (10) to win gravity battles
    },
    # Utils placements
    # core_extensions EVICTED - merged into utils root or specialized helpers
    "agentic_core/utils/naming": {
        "class_patterns": [".*Naming.*", ".*Case.*"],
        "base_classes": [],
        "function_patterns": ["to_snake_case.*", "to_pascal_case.*", "validate_name.*"],
        "import_signals": ["naming"],
        "keyword_signals": ["naming", "snake_case", "pascal_case", "case", "convention"],
        "weight": 7,
    },
    # observability placements
    "agentic_core/observability/metrics": {
        "class_patterns": [".*Metric.*", ".*Counter.*", ".*Gauge.*"],
        "base_classes": ["MetricCollector"],
        "function_patterns": ["collect_metric.*", "record_.*", "measure_.*"],
        "import_signals": ["prometheus", "metrics"],
        "keyword_signals": ["Metric", "counter", "gauge", "measure", "telemetry"],
        "weight": 7,
    },
    "agentic_core/observability/tracing": {
        "class_patterns": [".*Tracer.*", ".*Span.*"],
        "base_classes": ["Tracer", "SpanContext"],
        "function_patterns": ["trace_.*", "start_span.*"],
        "import_signals": ["opentelemetry", "tracing"],
        "keyword_signals": ["trace", "Span", "opentelemetry", "jaeger"],
        "weight": 7,
    },
    "agentic_core/observability/compliance": {
        "class_patterns": [".*Compliance.*", ".*Report.*"],
        "base_classes": ["ComplianceReporter"],
        "function_patterns": ["report_.*", "generate_compliance.*"],
        "import_signals": ["compliance"],
        "keyword_signals": ["compliance", "report", "audit", "coverage"],
        "weight": 7,
    },
    # Prompt governance placements
    "agentic_core/prompt_governance/templates": {
        "class_patterns": [".*Template.*", ".*Prompt.*"],
        "base_classes": ["PromptTemplate"],
        "function_patterns": ["render_prompt.*", "format_template.*"],
        "import_signals": ["jinja2", "prompt_governance"],
        "keyword_signals": ["prompt", "template", "jinja", "render"],
        "decorator_signals": ["@registers_prompt"],
        "weight": 15,
    },
    "agentic_core/prompt_governance/meta_prompts": {
        "class_patterns": [".*MetaPrompt.*", ".*SystemPrompt.*"],
        "base_classes": ["MetaPrompt"],
        "function_patterns": ["generate_meta_prompt.*"],
        "import_signals": ["meta_prompts"],
        "keyword_signals": ["meta_prompt", "system_prompt", "persona"],
        "weight": 15,
    },
}

# === PLACEMENT CONFIDENCE THRESHOLDS ===
PLACEMENT_CONFIDENCE = {
    "HIGH": 0.8,  # Auto-move without confirmation
    "MEDIUM": 0.5,  # Suggest move, require confirmation
    "LOW": 0.3,  # Log suggestion only
    "REJECT": 0.0,  # Cannot determine placement
}

# === REVERSE LOOKUP: L2 -> L1 MAPPING ===
# For quick parent resolution
L2_TO_L1_MAP: Final[Mapping[str, str]] = {
    # LCD+ canonical folders → parent layer
    "reasoning": "CONTEXT_DEPENDENT",  # Present in all layers — resolved by parent path
    "enforcement": "CONTEXT_DEPENDENT",
    "validators": "CONTEXT_DEPENDENT",
    "utils": "CONTEXT_DEPENDENT",
    "config": "CONTEXT_DEPENDENT",
    "types": "CONTEXT_DEPENDENT",
    # Nuance folders → specific layer
    "scripts": "L0_maintenance",
    "tools": "L2_execution",
    "memory": "L4_state",
    "dashboards": "L6_observability",
    # Non-layer domains
    "templates": "prompt_governance",
    "meta_prompts": "prompt_governance",
    "rendering": "prompt_governance",
    "version_registry": "prompt_governance",
    "environments": "config",
    "feature_flags": "config",
    "models": "runtime",
    "messages": "runtime",
}

# === GENERALIZED EXERCISER REGISTRY (Phase 7 SSOT) ===
# Map layer → exerciser class (or "GeneralExerciserAgent" for fallback)
EXERCISER_REGISTRY: Final[Mapping[str, str]] = {
    "L5_safety": "L5SafetyExerciserAgent",  # Existing specialized
    "L4_state": "L4StateExerciserAgent",
    "L1_cognition": "L1CognitionExerciserAgent",
    "L2_execution": "GeneralExerciserAgent",  # Fallback generic
    "L3_orchestration": "GeneralExerciserAgent",
    "L0_maintenance": "GeneralExerciserAgent",
    "observability": "GeneralExerciserAgent",
    "utils": "GeneralExerciserAgent",
    "config": "GeneralExerciserAgent",
    # DISSOLVED: "schemas" removed
    "prompt_governance": "GeneralExerciserAgent",
    "patterns": "GeneralExerciserAgent",
    "semantic_memory": "GeneralExerciserAgent",
    "knowledge": "GeneralExerciserAgent",
}

# === UPPERCASE ALIASES FOR BACKWARD COMPATIBILITY ===

# [PHASE 17] AGENT REGISTRY - Complete PascalCase Agent Discovery Map
# Generated from AST analysis - 64 total agents across all layers
AGENT_REGISTRY: Final[Mapping[str, Sequence[Mapping[str, str | int]]]] = {
    "L0": [
        {
            "name": "BootstrapAgent",
            "file": "agentic_core/L0_maintenance/reasoning/BootstrapAgent.py",
            "methods": 6,
            "fingerprint": "fcfd5e27416abb4c",
        },
    ],
    "L1": [
        {
            "name": "CanonBaseAgent",
            "file": "agentic_core/L1_cognition/thought_engine/CognitionCanonBaseAgent.py",
            "methods": 8,
            "fingerprint": "ea8e7e56381918dc",
        },
        {
            "name": "DependencySentinelAgent",
            "file": "agentic_core/L1_cognition/thought_engine/DependencySentinelAgent.py",
            "methods": 9,
            "fingerprint": "3773a3e6e7e65f7d",
        },
        {
            "name": "GovernanceAgent",
            "file": "agentic_core/L1_cognition/thought_engine/GovernanceAgent.py",
            "methods": 12,
            "fingerprint": "3bab1afa3cbc06ee",
        },
        {
            "name": "MetaLearningAgent",
            "file": "agentic_core/L1_cognition/thought_engine/MetaLearningAgent.py",
            "methods": 6,
            "fingerprint": "da27f331da4c5e37",
        },
        {
            "name": "ReflectionAgent",
            "file": "agentic_core/L1_cognition/thought_engine/ReflectionAgent.py",
            "methods": 9,
            "fingerprint": "c58961965bf91d5c",
        },
    ],
    "L2": [
        {
            "name": "CanonBaseAgent",
            "file": "agentic_core/L2_execution/reasoning/ExecutionCanonBaseAgent.py",
            "methods": 13,
            "fingerprint": "00b4b4376214468b",
        },
        {
            "name": "CodeDeduplicationAgent",
            "file": "agentic_core/L2_execution/reasoning/CodeDeduplicationAgent.py",
            "methods": 11,
            "fingerprint": "1c26bf7b92ef3fb8",
        },
        {
            "name": "CodeJanitorAgent",
            "file": "agentic_core/L2_execution/reasoning/CodeJanitorAgent.py",
            "methods": 12,
            "fingerprint": "ae825674e1abeb55",
        },
        {
            "name": "ContextCuratorAgent",
            "file": "agentic_core/L2_execution/reasoning/ContextCuratorAgent.py",
            "methods": 13,
            "fingerprint": "b55bbeb3cc150054",
        },
        {
            "name": "DependencyDiplomatAgent",
            "file": "agentic_core/L2_execution/reasoning/DependencyDiplomatAgent.py",
            "methods": 11,
            "fingerprint": "15bc567d77279e31",
        },
        {
            "name": "DynamicModelRouterAgent",
            "file": "agentic_core/L2_execution/reasoning/DynamicModelRouterAgent.py",
            "methods": 11,
            "fingerprint": "e6532e4040366631",
        },
        {
            "name": "GitAgent",
            "file": "agentic_core/L2_execution/reasoning/GitAgent.py",
            "methods": 12,
            "fingerprint": "82c9b049e6fd5597",
        },
        {
            "name": "IntegrityGateExecutorAgent",
            "file": "agentic_core/L2_execution/reasoning/IntegrityGateExecutorAgent.py",
            "methods": 8,
            "fingerprint": "cc6465bde4266c9f",
        },
        {
            "name": "MemoryArchitectAgent",
            "file": "agentic_core/L2_execution/reasoning/MemoryArchitectAgent.py",
            "methods": 13,
            "fingerprint": "b07bc5ecfbb20791",
        },
        {
            "name": "SovereignActionPlaneAgent",
            "file": "agentic_core/L2_execution/reasoning/SovereignActionPlaneAgent.py",
            "methods": 11,
            "fingerprint": "91faa15364d0a1a5",
        },
        {
            "name": "StructuralEngineerAgent",
            "file": "agentic_core/L2_execution/reasoning/StructuralEngineerAgent.py",
            "methods": 8,
            "fingerprint": "37d55e1531ee303e",
        },
        {
            "name": "SystemArchitectAgent",
            "file": "agentic_core/L2_execution/reasoning/SystemArchitectAgent.py",
            "methods": 8,
            "fingerprint": "e340d23c73eb4451",
        },
        {
            "name": "ToolsmithAgent",
            "file": "agentic_core/L2_execution/reasoning/ToolsmithAgent.py",
            "methods": 17,
            "fingerprint": "920d8dc7ea2d38d4",
        },
    ],
    "L3": [
        {
            "name": "DagEngineAgent",
            "file": "agentic_core/L3_orchestration/reasoning/DagEngineAgent.py",
            "methods": 14,
            "fingerprint": "e58f4699d9aa84e5",
        },
        {
            "name": "MockAgent",
            "file": "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
            "methods": 2,
            "fingerprint": "b644392cf05e5442",
        },
        {
            "name": "NervousSystemAgent",
            "file": "agentic_core/L3_orchestration/reasoning/NervousSystemAgent.py",
            "methods": 12,
            "fingerprint": "c3a187f4f4fd9eeb",
        },
        {
            "name": "SemanticGatekeeperAgent",
            "file": "agentic_core/L3_orchestration/reasoning/SemanticGatekeeperAgent.py",
            "methods": 6,
            "fingerprint": "40da7e8727c03cdc",
        },
        {
            "name": "SubatomicHopAgent",
            "file": "agentic_core/L3_orchestration/reasoning/SubatomicHopAgent.py",
            "methods": 14,
            "fingerprint": "7c2a442208c79cd7",
        },
        {
            "name": "TestPilotAgent",
            "file": "agentic_core/L3_orchestration/reasoning/TestPilotAgent.py",
            "methods": 15,
            "fingerprint": "5948ee871695c65f",
        },
    ],
    "L4": [
        {
            "name": "AutonomousCheckpointManagerAgent",
            "file": "agentic_core/L4_state/memory/AutonomousCheckpointManagerAgent.py",
            "methods": 13,
            "fingerprint": "41e505612b995ed9",
        },
        {
            "name": "AutonomousStateGuardianAgent",
            "file": "agentic_core/L4_state/memory/AutonomousStateGuardianAgent.py",
            "methods": 10,
            "fingerprint": "5ebb94cbbdf1aa58",
        },
        {
            "name": "PineconeSovereignAgent",
            "file": "agentic_core/L4_state/memory/PineconeSovereignAgent.py",
            "methods": 12,
            "fingerprint": "4dd0d1e4b0e3e220",
        },
        {
            "name": "RedisSovereignAgent",
            "file": "agentic_core/L4_state/memory/RedisSovereignAgent.py",
            "methods": 6,
            "fingerprint": "b040e351f725cddb",
        },
        {
            "name": "SchemaEvolverAgent",
            "file": "agentic_core/L4_state/memory/SchemaEvolverAgent.py",
            "methods": 14,
            "fingerprint": "895c1f48e33df32e",
        },
        {
            "name": "SovereignPineconeStoreAgent",
            "file": "agentic_core/L4_state/memory/SovereignPineconeStoreAgent.py",
            "methods": 10,
            "fingerprint": "f441583d3a2a4cd2",
        },
        {
            "name": "SubAtomicRegistryAgent",
            "file": "agentic_core/L4_state/memory/SubAtomicRegistryAgent.py",
            "methods": 7,
            "fingerprint": "78801bbc67f74db4",
        },
    ],
    "L5": [
        {
            "name": "AdversarialRedTeamerAgent",
            "file": "agentic_core/L5_safety/enforcement/AdversarialRedTeamerAgent.py",
            "methods": 24,
            "fingerprint": "f7b28e4a681e38f8",
        },
        {
            "name": "AutonomousThreatEvolutionAgent",
            "file": "agentic_core/L5_safety/enforcement/AutonomousThreatEvolutionAgent.py",
            "methods": 11,
            "fingerprint": "c181817ddf232911",
        },
        {
            "name": "DocstringComplianceAgent",
            "file": "agentic_core/L5_safety/validators/DocstringComplianceAgent.py",
            "methods": 3,
            "fingerprint": "667c2361a762cd69",
        },
        {
            "name": "FilenameUniquenessGuardianAgent",
            "file": "agentic_core/L5_safety/validators/FilenameUniquenessGuardianAgent.py",
            "methods": 5,
            "fingerprint": "823711cf0f58b0ff",
        },
        {
            "name": "FilesystemAgent",
            "file": "agentic_core/L5_safety/validators/FilesystemAgent.py",
            "methods": 6,
            "fingerprint": "404bc60482eb1646",
        },
        {
            "name": "GravityLeakRepairAgent",
            "file": "agentic_core/L5_safety/enforcement/GravityLeakRepairAgent.py",
            "methods": 3,
            "fingerprint": "51dbad0a31ea9c72",
        },
        {
            "name": "HallucinationHunterAgent",
            "file": "agentic_core/L5_safety/enforcement/HallucinationHunterAgent.py",
            "methods": 9,
            "fingerprint": "88a8355c3b923aa1",
        },
        {
            "name": "HealerAgent",
            "file": "agentic_core/L5_safety/enforcement/HealerAgent.py",
            "methods": 14,
            "fingerprint": "f7be54e968a04313",
        },
        {
            "name": "HierarchyAgent",
            "file": "agentic_core/L5_safety/validators/HierarchyAgent.py",
            "methods": 14,
            "fingerprint": "c4ba74a74c6e27d2",
        },
        {
            "name": "HygieneGuardianAgent",
            "file": "agentic_core/L5_safety/validators/HygieneGuardianAgent.py",
            "methods": 4,
            "fingerprint": "3aa2327dde094b31",
        },
        {
            "name": "ImportAgent",
            "file": "agentic_core/L5_safety/enforcement/ImportAgent.py",
            "methods": 7,
            "fingerprint": "f1dad62889a51085",
        },
        {
            "name": "InferenceTypeHintAgent",
            "file": "agentic_core/L5_safety/validators/InferenceTypeHintAgent.py",
            "methods": 3,
            "fingerprint": "0fd4fbfb4402be61",
        },
        {
            "name": "L5IntegrityGateExecutorAgent",
            "file": "agentic_core/L5_safety/enforcement/L5IntegrityGateExecutorAgent.py",
            "methods": 17,
            "fingerprint": "790a1b648be58757",
        },
        {
            "name": "LocationAgent",
            "file": "agentic_core/L5_safety/validators/LocationAgent.py",
            "methods": 9,
            "fingerprint": "5e49cfc8aebe839e",
        },
        {
            "name": "NeuralAutoImmuneAgent",
            "file": "agentic_core/L5_safety/enforcement/NeuralAutoImmuneAgent.py",
            "methods": 3,
            "fingerprint": "78dc1bb327996dcf",
        },
        {
            "name": "RedTeamAgent",
            "file": "agentic_core/L5_safety/reasoning/RedTeamAgent.py",
            "methods": 3,
            "fingerprint": "d76f6932c53b7a77",
        },
        {
            "name": "RegressionOracleAgent",
            "file": "agentic_core/L5_safety/validators/RegressionOracleAgent.py",
            "methods": 4,
            "fingerprint": "65c42eea1de011b7",
        },
        {
            "name": "SSOTRefactorAgent",
            "file": "agentic_core/L5_safety/validators/SSOTRefactorAgent.py",
            "methods": 4,
            "fingerprint": "29f31ace7a8982fb",
        },
        {
            "name": "SelfUpdatingSafetyEngineAgent",
            "file": "agentic_core/L5_safety/enforcement/SelfUpdatingSafetyEngineAgent.py",
            "methods": 14,
            "fingerprint": "ce122c5e1c1fe306",
        },
        {
            "name": "TerritoryHealerAgent",
            "file": "agentic_core/L5_safety/enforcement/TerritoryHealerAgent.py",
            "methods": 7,
            "fingerprint": "6fdffa7306e70169",
        },
        {
            "name": "TypeHintEnforcementAgent",
            "file": "agentic_core/L5_safety/validators/TypeHintEnforcementAgent.py",
            "methods": 3,
            "fingerprint": "9bf27471e887b95c",
        },
    ],
    "L6-OBS": [
        {
            "name": "BenchmarkingAgent",
            "file": "agentic_core/observability/metrics/BenchmarkingAgent.py",
            "methods": 14,
            "fingerprint": "aaccf245087d7b9a",
        },
        {
            "name": "CoordinateObservabilityOperationsAgent",
            "file": "agentic_core/observability/metrics/CoordinateObservabilityOperationsAgent.py",
            "methods": 3,
            "fingerprint": "b79b37e264d36fb5",
        },
        {
            "name": "MetricsAgent",
            "file": "agentic_core/observability/metrics/MetricsAgent.py",
            "methods": 14,
            "fingerprint": "c857ceb2e36799b9",
        },
        {
            "name": "PredictiveCostAuditorAgent",
            "file": "agentic_core/observability/metrics/PredictiveCostAuditorAgent.py",
            "methods": 12,
            "fingerprint": "8ef66dd746dd7e50",
        },
        {
            "name": "ReportingAgent",
            "file": "agentic_core/observability/compliance/ReportingAgent.py",
            "methods": 5,
            "fingerprint": "2c9e248f2f70804b",
        },
        {
            "name": "SignatureVerifierAgent",
            "file": "agentic_core/observability/metrics/SignatureVerifierAgent.py",
            "methods": 3,
            "fingerprint": "60824e83630f2650",
        },
        {
            "name": "TelemetryAgent",
            "file": "agentic_core/observability/telemetry/TelemetryAgent.py",
            "methods": 11,
            "fingerprint": "d026b54bad957126",
        },
        {
            "name": "TracingAgent",
            "file": "agentic_core/observability/tracing/TracingAgent.py",
            "methods": 15,
            "fingerprint": "8c951c49ffa5b5ed",
        },
        {
            "name": "TrackObservabilityCostAgent",
            "file": "agentic_core/observability/metrics/TrackObservabilityCostAgent.py",
            "methods": 3,
            "fingerprint": "15b577bc8c1d7075",
        },
    ],
    "UTILS": [
        {
            "name": "NamingAgent",
            "file": "agentic_core/utils/naming/NamingAgent.py",
            "methods": 13,
            "fingerprint": "27645aed97c3aa01",
        },
        {
            "name": "NamingNormalizationAgent",
            "file": "agentic_core/utils/naming/NamingNormalizationAgent.py",
            "methods": 4,
            "fingerprint": "e09b6daa7f5988eb",
        },
    ],
}

# [HARDENING] Convert nested structures to Mapping for immutability
semantic_l2_registry: Final[Mapping[str, Any]] = {
    "L5_safety": {
        "base_agents": {
            "purpose": "Constitutional foundation for all agents. Home of SovereignBaseAgent and LayerBaseAgents.",
            "entity_types": ["Class"],
            "keywords": [
                "base",
                "sovereign",
                "foundation",
                "inheritance",
                "abstract",
            ],
            "imports": [],
            "bases": ["ABC"],
            "examples": ["SovereignBaseAgent", "L1CognitionBase"],
        },
        "enforcement": {
            "purpose": "Hard safety limits, mutation controls, deletion guards, circuit breakers, rate limits, throttling, and emergency stop mechanisms",
            "entity_types": ["Class"],
            "keywords": [
                "guardrail",
                "safety",
                "limit",
                "constraint",
                "circuit",
                "breaker",
                "throttle",
                "rate",
                "quota",
                "mutate",
                "delete",
                "emergency",
                "stop",
                "block",
                "prevent",
            ],
            "imports": ["agentic_core.L5_safety.enforcement"],
            "bases": ["BaseGuardrail", "SafetyGuardrail", "CircuitBreaker", "RateLimiter"],
            "examples": [
                "MutationGuardrail",
                "DeletionGuardrail",
                "RateLimitGuardrail",
                "EmergencyStopGuardrail",
                "ContentFilterGuardrail",
            ],
        },
        "reasoning": {
            "purpose": "Adversarial testing agents, automated threat simulation, exploit probing, jailbreak attempts, prompt injection testing, and attack vector generation",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "redteam",
                "red_team",
                "adversary",
                "adversarial",
                "attack",
                "exploit",
                "probe",
                "jailbreak",
                "threat",
                "simulate",
                "fuzz",
                "injection",
                "poison",
            ],
            "imports": ["agentic_core.L5_safety.reasoning"],
            "bases": ["RedTeamAgent", "AdversarialAgent", "ThreatSimulator"],
            "examples": [
                "JailbreakProber",
                "PromptInjectionAttacker",
                "ThreatSimulator",
                "AdversarialFuzzer",
                "ExploitGenerator",
            ],
        },
        # DISSOLVED: "gravity" merged into "enforcement" per LCD+
        # Gravity keywords: gravity, waterfall, import, dependency, direction, layer, authority
        "validators": {
            "purpose": "Canon constitution validators, structural policy enforcement, naming law validation, runtime compliance auditing, and architectural drift detection",
            "entity_types": ["Class"],
            "keywords": [
                "validator",
                "canon",
                "constitution",
                "rule",
                "policy",
                "enforce",
                "compliance",
                "audit",
                "drift",
                "naming",
                "law",
                "check",
                "verify",
            ],
            "imports": ["agentic_core.L5_safety.validators", "structure_blueprint"],
            "bases": [
                "CanonBaseAgent",
                "StructureValidator",
                "ComplianceAuditor",
                "DriftDetector",
            ],
            "examples": [
                "NamingLawValidator",
                "DepthValidator",
                "GravityComplianceValidatorAgent",
                "StructuralPolicyValidator",
                "RuntimeComplianceAuditor",
            ],
        },
    },
    "L0_maintenance": {
        "scripts": {
            "purpose": "Autonomous healing scripts, Checkpoint management, self-updating systems, neural immune agents, and sovereign improvement missions",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "autonomous",
                "heal",
                "repair",
                "Checkpoint",
                "guardian",
                "self_update",
                "immune",
                "mission",
                "surgery",
                "refactor",
                "evolution",
            ],
            "imports": ["agentic_core.L0_maintenance.scripts", "structure_blueprint"],
            "bases": ["CanonBaseAgent", "AutonomousAgent", "HealingEngine"],
            "examples": [
                "AutonomousCheckpointManager",
                "AutonomousStateGuardian",
                "SelfUpdatingSafetyEngine",
                "NeuralAutoImmuneAgent",
                "SovereignHealingMission",
            ],
        },
        "logs": {
            "purpose": "Structured diagnostic logs, healing operation records, mission transcripts, and maintenance audit trails",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "log",
                "diagnostic",
                "record",
                "transcript",
                "audit",
                "maintenance_log",
                "healing_trace",
                "mission_log",
            ],
            "imports": ["agentic_core.L0_maintenance.utils", "logging", "json"],
            "bases": ["DiagnosticLogger", "MissionTranscript", "MaintenanceAudit"],
            "examples": [
                "HealingOperationLogger",
                "AutonomousMissionLog",
                "SovereignDiagnosticWriter",
                "MaintenanceTrace",
            ],
        },
        "benchmarks": {
            "purpose": "Performance benchmarking suites, timing profiles, resource usage metrics, and autonomous optimization baselines",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "benchmark",
                "perf",
                "timing",
                "profile",
                "Metric",
                "baseline",
                "optimize",
                "resource",
                "efficiency",
            ],
            "imports": ["agentic_core.L0_maintenance.benchmarks", "time", "asyncio", "psutil"],
            "bases": ["BenchmarkSuite", "PerformanceProfiler", "ResourceMonitor"],
            "examples": [
                "SovereignBenchmarkRunner",
                "ReasoningSpeedTest",
                "MemoryEfficiencyBenchmark",
                "HealingCycleProfiler",
            ],
        },
    },
    "L1_cognition": {
        "reasoning": {
            "purpose": "Core reasoning primitives, thought nodes, chain-of-thought execution, internal monologue structures, and advanced deliberation patterns",
            "entity_types": ["Class", "Protocol"],
            "keywords": [
                "thought",
                "reason",
                "node",
                "chain",
                "cot",
                "tot",
                "react",
                "monologue",
                "step",
                "decompose",
                "analyze",
                "reflect",
                "critique",
                "socratic",
                "deliberate",
                "ponder",
                "contemplate",
                "self_reflect",
            ],
            "imports": ["agentic_core.L1_cognition.reasoning", "pydantic", "typing"],
            "bases": [
                "ThoughtNode",
                "ReasoningStep",
                "BaseThought",
                "ChainOfThought",
                "TreeOfThoughts",
                "ReActStep",
                "BaseReasoningEngine",
            ],
            "examples": [
                "ReasoningNode",
                "CritiqueStep",
                "ReflectionThought",
                "ChainOfThoughtExecutor",
                "SocraticReasoner",
                "TreeOfThoughtsNode",
                "ReActAgentStep",
            ],
        },
        # DISSOLVED: "intent_analysis" removed — distributed to engine/, types/, L2/config/, L0/scripts/
        "planning": {
            "purpose": "Mission decomposition, strategy formulation, step sequencing, dependency mapping, plan validation, and execution roadmap generation",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "plan",
                "strategy",
                "decompose",
                "sequence",
                "step",
                "Task",
                "subtask",
                "dependency",
                "order",
                "validate",
                "breakdown",
                "hierarchy",
                "outline",
                "roadmap",
                "execute_order",
                "priority",
                "milestone",
            ],
            "imports": ["agentic_core.L1_cognition.planning", "networkx", "pydantic", "typing"],
            "bases": [
                "Planner",
                "DecompositionEngine",
                "PlanValidator",
                "StrategyBuilder",
                "BasePlanner",
                "TaskGraph",
            ],
            "examples": [
                "MissionDecomposer",
                "TaskSequencer",
                "DependencyResolver",
                "PlanValidator",
                "StrategicPlannerAgent",
                "StepHierarchyBuilder",
                "PriorityScheduler",
            ],
        },
    },
    "L2_execution": {
        "reasoning": {
            "purpose": "Registration and discovery of external tools, base tool definitions, and tool metadata management",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "tool",
                "registry",
                "register",
                "discover",
                "metadata",
                "available_tools",
                "toolset",
            ],
            "imports": ["agentic_core.L2_execution.reasoning", "pydantic", "typing"],
            "bases": ["BaseTool"],
            "examples": ["register_tool", "AvailableToolsList", "ToolMetadata"],
        },
        "action_handlers": {
            "purpose": "Action dispatch logic, handler mapping, execution routing, and fallback strategies for tool calls",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "action",
                "handler",
                "execute",
                "dispatch",
                "Route",
                "fallback",
                "perform",
                "invoke",
                "call_action",
            ],
            "imports": ["agentic_core.L2_execution.action_handlers"],
            "bases": ["ActionHandler", "BaseActionDispatcher"],
            "examples": [
                "ActionDispatcher",
                "HandlerMap",
                "DefaultActionExecutor",
                "ToolCallRouter",
                "FallbackHandler",
            ],
        },
        "mcp": {
            "purpose": "Multi-Component Protocol clients and tool implementations (figma, fetch, filesystem, semantic_cache, router, marketplace_filter)",
            "entity_types": ["Class"],
            "keywords": [
                "mcp",
                "client",
                "figma",
                "fetch",
                "filesystem",
                "semantic_cache",
                "router",
                "marketplace",
                "filter",
                "protocol",
            ],
            "imports": [
                "agentic_core.L2_execution.enforcement",
                "requests",
                "playwright",
                "selenium",
                "pinecone",
            ],
            "bases": ["BaseTool", "MCPClientBase"],
            "examples": [
                "FigmaClient",
                "FetchClientSovereign",
                "FilesystemMCPClient",
                "SemanticCacheClient",
                "MCPRouter",
                "MarketplaceFilter",
            ],
        },
    },
    "L3_orchestration": {
        "reasoning": {
            "purpose": "High-level agent orchestration, multi-agent workflow engines, Task routing, mission lifecycle management, and coordination primitives",
            "entity_types": ["Class"],
            "keywords": [
                "orchestrator",
                "coordinator",
                "workflow",
                "engine",
                "manager",
                "supervisor",
                "crew",
                "team",
                "mission",
                "lifecycle",
                "Route",
                "dispatch",
                "schedule",
            ],
            "imports": ["agentic_core.L3_orchestration.reasoning", "langgraph", "pydantic"],
            "bases": ["CanonBaseAgent", "WorkflowEngine", "OrchestratorBase", "MissionManager"],
            "examples": [
                "SovereignOrchestrator",
                "MultiAgentWorkflow",
                "TaskRouter",
                "MissionLifecycleManager",
                "AgentSupervisor",
            ],
        },
        "fission_logic": {
            "purpose": "Agent fission mechanics, dynamic sub-agent spawning, division of labor, and recursive self-delegation systems",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "fission",
                "spawn",
                "subagent",
                "divide",
                "delegate",
                "recursive",
                "split",
                "branch",
                "fork",
                "proliferate",
            ],
            "imports": ["agentic_core.L3_orchestration.reasoning"],
            "bases": ["FissionEngine", "SubAgentSpawner", "CanonBaseAgent"],
            "examples": [
                "FissionManagerAgent",
                "DynamicSubAgentCreator",
                "RecursiveDelegator",
                "TaskFissionLogic",
            ],
        },
        "S3_vitality": {
            "purpose": "System vitality monitoring, health checks, self-preservation protocols, anomaly detection, and resilience mechanisms",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "vitality",
                "health",
                "monitor",
                "heartbeat",
                "anomaly",
                "resilience",
                "self_preserve",
                "watchdog",
                "liveness",
                "readiness",
            ],
            "imports": ["agentic_core.L3_orchestration.S3_vitality"],
            "bases": ["VitalityMonitor", "HealthChecker", "CanonBaseAgent"],
            "examples": [
                "VitalityGuardian",
                "SystemHealthMonitor",
                "AnomalyDetector",
                "ResilienceEngine",
                "WatchdogAgent",
            ],
        },
        "mcp": {
            "purpose": "Orchestration-level Multi-Component Protocol components (router, marketplace_filter, coordination logic)",
            "entity_types": ["Class"],
            "keywords": [
                "mcp",
                "router",
                "marketplace",
                "filter",
                "orchestrate",
                "coordinate",
                "gateway",
                "proxy",
            ],
            "imports": ["agentic_core.L3_orchestration.mcp"],
            "bases": ["MCPRouterBase", "MarketplaceFilter", "CanonBaseAgent"],
            "examples": [
                "MCPRouter",
                "MarketplaceToolFilter",
                "OrchestrationGateway",
                "MCPCoordinator",
            ],
        },
    },
    "L4_state": {
        "reasoning": {
            "purpose": "Runtime validation contexts, state integrity containers, and scoped validation environments",
            "entity_types": ["Class"],
            "keywords": [
                "validation",
                "context",
                "scope",
                "integrity",
                "state_check",
                "validate_in_context",
            ],
            "imports": ["agentic_core.L4_state.memory", "pydantic", "typing"],
            "bases": ["ValidationContext", "BaseStateContext"],
            "examples": [
                "SovereignValidationContext",
                "MissionValidationScope",
                "StateIntegrityContainer",
            ],
        },
        "ledger": {
            "purpose": "Immutable audit ledgers, historical state records, event sourcing, and tamper-evident logs",
            "entity_types": ["Class"],
            "keywords": [
                "ledger",
                "immutable",
                "audit",
                "trail",
                "history",
                "event_source",
                "append_only",
                "commit_log",
            ],
            "imports": ["agentic_core.L4_state.enforcement"],
            "bases": ["ImmutableLedger", "AuditTrail", "EventLedger"],
            "examples": [
                "SovereignLedger",
                "MissionHistoryLedger",
                "StateCommitLog",
                "TamperEvidentRecord",
            ],
        },
        "filesystem": {
            "purpose": "Sovereign filesystem abstractions, MCP filesystem operations, and persistent file state management",
            "entity_types": ["Class"],
            "keywords": [
                "filesystem",
                "mcp",
                "file",
                "directory",
                "path",
                "persistent",
                "storage",
                "disk",
            ],
            "imports": ["agentic_core.L4_state.filesystem", "pathlib"],
            "bases": ["FilesystemMCP", "BaseFilesystemClient", "BaseTool"],
            "examples": ["SovereignFilesystemClient", "PersistentStateStore", "FileLedgerAdapter"],
        },
        "memory": {
            "purpose": "In-memory state stores, session management, ephemeral caches, and short-term memory systems",
            "entity_types": ["Class"],
            "keywords": [
                "memory",
                "session",
                "cache",
                "ephemeral",
                "short_term",
                "in_memory",
                "working_memory",
            ],
            "imports": ["agentic_core.L4_state.memory", "redis", "typing"],
            "bases": ["MemoryStore", "SessionManager", "EphemeralCache"],
            "examples": [
                "SovereignWorkingMemory",
                "SessionState",
                "ShortTermCache",
                "InMemoryLedger",
            ],
        },
    },
    "config": {
        "core": {
            "purpose": "Core configuration, constants, registries, and settings",
            "entity_types": ["Dict", "Class"],
            "keywords": [
                "blueprint",
                "sovereign",
                "constitution",
                "registry",
                "structure",
                "map",
                "ssot",
            ],
            "imports": ["agentic_core.config.core"],
            "bases": ["BaseConfiguration", "Constitution"],
            "examples": ["StructureBlueprint", "CanonRegistry", "SovereignConstitution"],
        },
        "environments": {
            "purpose": "Environment-specific configuration loaders, .env parsers, and context switching",
            "entity_types": ["Class", "Function"],
            "keywords": ["env", "config", "loader", "dotenv", "dev", "prod", "staging", "variable"],
            "imports": ["os", "dotenv"],
            "bases": ["ConfigLoader", "EnvironmentContext"],
            "examples": ["EnvLoader", "ProductionConfig", "DevContext", "DotenvParser"],
        },
        "feature_flags": {
            "purpose": "Feature toggle management, rollout controls, and A/B testing switches",
            "entity_types": ["Class"],
            "keywords": [
                "flag",
                "feature",
                "toggle",
                "rollout",
                "switch",
                "beta",
                "enable",
                "disable",
            ],
            "imports": ["agentic_core.config.feature_flags"],
            "bases": ["FeatureToggle", "FlagManager"],
            "examples": ["LaunchDarklyAdapter", "FeatureFlagStore", "BetaRolloutSwitch"],
        },
        "secrets_manager": {
            "purpose": "Secure secret retrieval, vault integration, and credential rotation",
            "entity_types": ["Class"],
            "keywords": [
                "secret",
                "vault",
                "key",
                "credential",
                "token",
                "password",
                "encrypt",
                "decrypt",
            ],
            "imports": ["agentic_core.config.secrets_manager"],
            "bases": ["SecretsVault", "CredentialProvider"],
            "examples": ["VaultClient", "AWSSystemManager", "SecureTokenStore"],
        },
    },
    "runtime": {
        "shared_runtime": {
            "purpose": "Shared runtime environment setup, void compliance, and global initialization",
            "entity_types": ["Class", "Function"],
            "keywords": [
                "runtime",
                "shared",
                "void",
                "compliance",
                "init",
                "bootstrap",
                "setup",
                "global",
            ],
            "imports": ["agentic_core.runtime.shared_runtime"],
            "bases": ["RuntimeContext"],
            "examples": ["VoidComplianceCheck", "runtime_bootstrapper", "GlobalInit"],
        },
        "resource_management": {
            "purpose": "Resource allocation, throttling quotas, thread pool management, and cleanup",
            "entity_types": ["Class"],
            "keywords": [
                "resource",
                "throttle",
                "quota",
                "cleanup",
                "pool",
                "thread",
                "limit",
                "allocate",
            ],
            "imports": ["concurrent.futures"],
            "bases": ["ResourceManager", "QuotaEnforcer"],
            "examples": ["ThreadPoolManager", "MemoryQuotaGuard", "ResourceCleaner"],
        },
    },
    "observability": {
        "metrics": {
            "purpose": "Metric collection, counters, gauges, and prometheus exports",
            "entity_types": ["Class"],
            "keywords": ["Metric", "counter", "gauge", "histogram", "prometheus", "stat"],
            "imports": ["prometheus_client"],
            "bases": ["MetricCollector"],
            "examples": ["PerformanceMetrics", "RequestCounter", "SystemGauge"],
        },
        "telemetry": {
            "purpose": "Distributed telemetry, event emission, and structured observability events",
            "entity_types": ["Class"],
            "keywords": ["telemetry", "event", "emit", "signal", "observe"],
            "imports": ["opentelemetry"],
            "bases": ["TelemetryProvider"],
            "examples": ["EventEmitter", "TelemetrySignal", "StructuredObserver"],
        },
        "tracing": {
            "purpose": "Span tracing, context propagation, and distributed trace ids",
            "entity_types": ["Class"],
            "keywords": ["trace", "Span", "context", "propagate", "id", "parent"],
            "imports": ["opentelemetry.trace"],
            "bases": ["TracerBase"],
            "examples": ["SpanContext", "DistributedTracer", "ContextPropagator"],
        },
        "compliance": {
            "purpose": "Compliance reporting, canon drift detection logs, and policy Violation records",
            "entity_types": ["Class", "Function"],
            "keywords": ["compliance", "drift", "report", "canon", "Violation", "audit"],
            "imports": [],
            "bases": ["ComplianceReporter"],
            "examples": ["DriftReportGenerator", "CanonComplianceLog", "ViolationTracker"],
        },
    },
    "utils": {
        "core_extensions": {
            "purpose": "Core Python extensions, polyfills, and monkey-patches",
            "entity_types": ["Function", "Class"],
            "keywords": ["extension", "polyfill", "monkey", "patch", "enhance"],
            "imports": [],
            "bases": [],
            "examples": ["StringExtensions", "DictMergePolyfill", "CoreMonkeyPatch"],
        },
        "wrappers": {
            "purpose": "Decorators, generic wrappers, and function proxies",
            "entity_types": ["Function"],
            "keywords": ["wrapper", "decorator", "retry", "cache", "proxy", "intercept"],
            "imports": ["functools"],
            "bases": [],
            "examples": ["retry_with_backoff", "cached_property_wrapper", "LogExecutionDecorator"],
        },
        "general_helpers": {
            "purpose": "Domain-agnostic helper functions and miscellaneous core utilities",
            "entity_types": ["Function"],
            "keywords": ["helper", "util", "misc", "common", "format"],
            "imports": [],
            "bases": [],
            "examples": ["date_helper", "string_formatter", "generic_util"],
        },
        "naming": {
            "purpose": "Naming law enforcement logic, casing validators, and canon signal checks",
            "entity_types": ["Class", "Function"],
            "keywords": ["naming", "canon", "signal", "law", "case", "snake", "camel"],
            "imports": ["agentic_core.utils.naming", "re"],
            "bases": ["NamingValidator"],
            "examples": ["SnakeCaseValidator", "CanonSignalChecker", "NamingLawEnforcer"],
        },
    },
    "patterns": {
        "agent_roles": {
            "purpose": "Pre-defined agent personas, role templates, and behavioral archetypes",
            "entity_types": ["Class", "Dict"],
            "keywords": ["role", "persona", "agent_type", "Archetype", "behavior"],
            "imports": [],
            "bases": ["CanonBaseAgent"],
            "examples": ["SocraticPersona", "CriticRole", "ArchitectArchetype"],
        },
        "communication_flow": {
            "purpose": "Inter-agent message passing patterns and handoff protocols",
            "entity_types": ["Class"],
            "keywords": ["communication", "message", "flow", "protocol", "handoff", "channel"],
            "imports": [],
            "bases": ["CommunicationProtocol"],
            "examples": ["MessageBusPattern", "HandoffProtocol", "ChannelPattern"],
        },
        "interaction_patterns": {
            "purpose": "Common human-agent and agent-tool interaction patterns (CLI, Chat, etc)",
            "entity_types": ["Class"],
            "keywords": ["interaction", "pattern", "ui", "cli", "chat", "ux"],
            "imports": [],
            "bases": [],
            "examples": ["CliInteractionPattern", "ChatLoopPattern", "ToolUsePattern"],
        },
        "reasoning_patterns": {
            "purpose": "Reusable reasoning strategies (CoT, ToT, ReAct) as abstract patterns",
            "entity_types": ["Class"],
            "keywords": ["reasoning", "strategy", "cot", "tot", "react", "chain", "tree"],
            "imports": ["agentic_core.patterns.reasoning_patterns"],
            "bases": ["BaseReasoningEngine"],
            "examples": ["ChainOfThoughtPattern", "TreeOfThoughtsStrategy", "ReActLoopPattern"],
        },
    },
    "knowledge": {
        "document_loaders": {
            "purpose": "Document ingestion, parsing, and unstructured data loading utilities",
            "entity_types": ["Class"],
            "keywords": ["loader", "ingest", "parse", "document", "pdf", "txt", "html"],
            "imports": ["unstructured", "langchain"],
            "bases": ["BaseLoader"],
            "examples": ["PDFLoader", "TextIngestor", "HTMLParser"],
        },
        "static_index": {
            "purpose": "Hard-coded knowledge bases, static facts, and lookup tables",
            "entity_types": ["Dict", "Class"],
            "keywords": ["static", "index", "facts", "knowledge", "lookup", "table", "constants"],
            "imports": [],
            "bases": [],
            "examples": ["WorldFactsIndex", "ConstantLookup", "StaticKnowledgeBase"],
        },
        "ResearchCache": {
            "purpose": "Cached research results, external knowledge snapshots, and query history",
            "entity_types": ["Class"],
            "keywords": ["research", "cache", "snapshot", "history", "query", "stored"],
            "imports": [],
            "bases": ["CacheStore"],
            "examples": ["ResearchResultCache", "KnowledgeSnapshot", "QueryHistoryLog"],
        },
    },
    # DISSOLVED: "schemas" removed — deported to runtime/types, L4/contracts, L6/engine+types
    "prompt_governance": {
        "templates": {
            "description": "Atomic instructional fragments and Jinja2 partials.",
            "purpose": "Reusable prompt fragments, system instructions, and jinja templates",
            "entity_types": ["Class", "str constant"],
            "keywords": ["prompt", "template", "system", "instruction", "jinja", "partial"],
            "imports": ["jinja2"],
            "bases": [],
            "allowed_extensions": [".jinja", ".txt"],
            "required_content": ["SCHEMA_HEADER"],
            "category": "PARTIAL",
        },
        "meta_prompts": {
            "description": "High-level strategic directives and persona definitions.",
            "purpose": "Strategic prompt orchestration, persona definitions, and meta-level directives",
            "entity_types": ["Class", "str constant"],
            "keywords": ["meta", "persona", "strategy", "directive", "orchestration"],
            "imports": ["jinja2", "yaml"],
            "bases": [],
            "allowed_extensions": [".jinja", ".yaml"],
            "required_content": ["VERSIONED_ENTRY"],
            "category": "STRATEGY",
        },
        "rendering": {
            "purpose": "Dynamic prompt assembly, variable substitution, and rendering logic",
            "entity_types": ["Class", "Function"],
            "keywords": ["render", "assemble", "build", "format", "interpolate"],
            "imports": ["jinja2"],
            "bases": [],
        },
    },
    "semantic_memory": {
        "embeddings": {
            "purpose": "Embedding generation, caching, and dimension management",
            "entity_types": ["Class", "Function"],
            "keywords": ["embedding", "embed", "vectorize", "dimension", "latent"],
            "imports": ["google.genai"],
            "bases": [],
        },
        "retrieval": {
            "purpose": "Semantic search, similarity scoring, and RAG retrieval",
            "entity_types": ["Class", "Function"],
            "keywords": ["retriev", "search", "similarity", "rag", "query", "lookup"],
            "imports": ["pinecone"],
            "bases": [],
        },
    },
    "apps_rg": {
        "core": {
            "purpose": "App-specific base classes, configuration, and exception definitions",
            "entity_types": ["Class"],
            "keywords": ["base", "config", "exception", "settings", "setup"],
            "imports": ["apps_rg.core"],
            "bases": ["BaseConfig", "BaseException"],
        },
        "domain": {
            "purpose": "Pure domain models, type definitions, and business entities",
            "entity_types": ["Class"],
            "keywords": ["model", "type", "entity", "struct", "dataclass"],
            "imports": ["pydantic"],
            "bases": ["BaseModel"],
        },
        "logic_nodes": {
            "purpose": "Business logic nodes for resume extraction, parsing, and section formatting",
            "entity_types": ["Class"],
            "keywords": [
                "resume",
                "cv",
                "node",
                "section",
                "experience",
                "education",
                "skill",
                "extract",
                "format",
                "parse",
            ],
            "imports": ["apps_rg.logic_nodes", "pydantic"],
            "bases": ["BaseNode", "ResumeNode", "ExtractionNode"],
            "examples": [
                "ExperienceNode",
                "SkillExtractNode",
                "EducationFormatter",
                "HeaderLogicNode",
            ],
        },
        "asset_library": {
            "purpose": "Static assets, hardcoded strings, action verbs, and skill taxonomies for resumes",
            "entity_types": ["Class", "Dict"],
            "keywords": [
                "asset",
                "string",
                "text",
                "resource",
                "copy",
                "wording",
                "verbs",
                "skills",
                "taxonomy",
            ],
            "imports": [],
            "bases": ["BaseAsset"],
            "examples": ["ResumeAssets", "ActionVerbs", "SkillTaxonomy", "ResumeTemplateStrings"],
        },
        "system_flow": {
            "purpose": "Linear and branching pipelines for the resume generation lifecycle",
            "entity_types": ["Class"],
            "keywords": [
                "flow",
                "pipeline",
                "sequence",
                "generate",
                "create",
                "process",
                "workflow",
                "lifecycle",
            ],
            "imports": ["apps_rg.system_flow"],
            "bases": ["BaseFlow", "ResumeGenerationFlow"],
            "examples": [
                "GenerationFlow",
                "ReviewPipeline",
                "PdfGenerationWorkflow",
                "ContentRefinementFlow",
            ],
        },
        "engines": {
            "purpose": "Core rendering engines for document export (PDF, Docx, HTML)",
            "entity_types": ["Class"],
            "keywords": ["engine", "render", "export", "pdf", "docx", "builder", "latex", "jinja"],
            "imports": ["apps_rg.engines", "jinja2"],
            "bases": ["BaseEngine", "DocumentBuilder"],
            "examples": ["PdfEngine", "DocxBuilder", "HtmlRenderer", "LatexCompiler"],
        },
        "templates": {
            "purpose": "Visual layouts, CSS/Style definitions, and structural blueprints for documents",
            "entity_types": ["Class", "Dict"],
            "keywords": [
                "template",
                "layout",
                "style",
                "theme",
                "design",
                "format",
                "css",
                "blueprint",
            ],
            "imports": [],
            "bases": ["BaseTemplate", "ResumeLayout"],
            "examples": [
                "ModernTemplate",
                "ClassicLayout",
                "ExecutiveBlueprint",
                "MinimalistStyle",
            ],
        },
    },
    "apps_lic": {
        "core": {
            "purpose": "App-specific base classes, configuration, and exception definitions",
            "entity_types": ["Class"],
            "keywords": ["base", "config", "exception", "settings", "setup"],
            "imports": ["apps_lic.core"],
            "bases": ["BaseConfig", "BaseException"],
        },
        "domain": {
            "purpose": "Pure domain models, type definitions, and business entities",
            "entity_types": ["Class"],
            "keywords": ["model", "type", "entity", "struct", "dataclass"],
            "imports": ["pydantic"],
            "bases": ["BaseModel"],
        },
        "logic_nodes": {
            "purpose": "Business logic nodes for profile analysis, connection requests, and message generation",
            "entity_types": ["Class"],
            "keywords": [
                "linkedin",
                "lic",
                "node",
                "message",
                "connect",
                "invite",
                "profile",
                "scrutinize",
                "analyze",
            ],
            "imports": ["apps_lic.logic_nodes"],
            "bases": ["BaseNode", "LicNode", "MessagingNode"],
            "examples": [
                "ConnectNode",
                "MessageDraftNode",
                "ProfileScrutinyNode",
                "LeadValidationNode",
            ],
        },
        "asset_library": {
            "purpose": "Outreach scripts, message templates, connection notes, and sequence assets",
            "entity_types": ["Class", "Dict"],
            "keywords": [
                "asset",
                "note",
                "message",
                "template",
                "script",
                "outreach",
                "sequence",
                "hook",
            ],
            "imports": [],
            "bases": ["BaseAsset"],
            "examples": ["ConnectionNotes", "FollowUpScripts", "OutreachTemplates", "MessageHooks"],
        },
        "system_flow": {
            "purpose": "Outreach campaign management, multi-step drip sequences, and cadence logic",
            "entity_types": ["Class"],
            "keywords": [
                "flow",
                "campaign",
                "sequence",
                "cadence",
                "outreach",
                "drip",
                "funnel",
                "pipeline",
            ],
            "imports": ["apps_lic.system_flow"],
            "bases": ["BaseFlow", "OutreachCampaign"],
            "examples": ["OutreachCampaign", "DailyFlow", "DripSequenceFlow", "FollowUpCadence"],
        },
        "engines": {
            "purpose": "Automated browser drivers for LinkedIn navigation and interaction",
            "entity_types": ["Class"],
            "keywords": [
                "engine",
                "driver",
                "navigate",
                "automate",
                "browser",
                "playwright",
                "selenium",
                "scrape",
            ],
            "imports": ["apps_lic.engines", "playwright", "selenium"],
            "bases": ["BaseEngine", "BrowserDriver"],
            "examples": [
                "NavigationEngine",
                "BrowserDriver",
                "ScrapingEngine",
                "InteractionDriver",
            ],
        },
        "templates": {
            "purpose": "Message formatting schemas and campaign structural blueprints",
            "entity_types": ["Class"],
            "keywords": ["template", "structure", "format", "blueprint", "schema"],
            "imports": [],
            "bases": ["BaseTemplate", "LicTemplate"],
            "examples": ["CampaignTemplate", "MessageFormat", "OutreachBlueprint"],
        },
    },
    "apps_shared": {
        "core": {
            "purpose": "Abstract base classes, core interfaces, and type contracts shared across all application domains",
            "entity_types": ["Class", "Protocol", "TypeAlias"],
            "keywords": [
                "base",
                "definition",
                "type",
                "shared",
                "interface",
                "abstract",
                "contract",
                "blueprint",
                "abc",
            ],
            "imports": ["abc", "typing"],
            "bases": ["ABC", "Protocol"],
            "examples": ["BaseNode", "BaseFlow", "BaseEngine", "BaseTemplate", "BaseAsset"],
        },
        "utils": {
            "purpose": "Shared application-level utility functions for data manipulation, formatting, and common logic",
            "entity_types": ["Function", "Class"],
            "keywords": [
                "util",
                "common",
                "shared",
                "helper",
                "date",
                "string",
                "collection",
                "formatter",
                "converter",
            ],
            "imports": ["datetime", "re", "json"],
            "bases": [],
            "examples": [
                "date_utils",
                "string_helpers",
                "collection_transformers",
                "CurrencyFormatter",
            ],
        },
        "components": {
            "purpose": "Reusable architectural widgets and modular components used across multiple app flows",
            "entity_types": ["Class"],
            "keywords": ["component", "module", "widget", "part", "element", "plugin", "extension"],
            "imports": [],
            "bases": ["BaseComponent"],
            "examples": ["LoggerComponent", "ConfigLoader", "NotificationWidget", "AppPluginBase"],
        },
        "agents": {
            "purpose": "Shared application-level agent templates and worker base classes - home for AppBase.py",
            "entity_types": ["Class"],
            "keywords": ["agent", "base_agent", "worker", "bot", "task_executor", "app_worker"],
            "imports": ["agentic_core.L3_orchestration.reasoning", "apps_shared.agents.AppBase"],
            "bases": ["CanonBaseAgent", "AppBase"],
            "examples": ["AppBase", "TaskWorker", "AsyncAppWorker", "StatefulAppAgent"],
            "canonical_files": ["AppBase.py"],  # Zero-Ambiguity: Renamed from AppBaseAgent.py
        },
        "models": {
            "purpose": "Shared Pydantic data models, Data Transfer Objects (DTOs), and domain-agnostic schemas",
            "entity_types": ["Class"],
            "keywords": [
                "model",
                "dto",
                "data",
                "struct",
                "object",
                "payload",
                "contract",
                "pydantic",
            ],
            "imports": ["pydantic"],
            "bases": ["BaseModel"],
            "examples": ["UserProfile", "TaskResult", "CommonMetadata", "SharedDataPacket"],
        },
        "templates": {
            "purpose": "Shared UI/Text patterns, format schemas, and presentation layers",
            "entity_types": ["Class", "Dict"],
            "keywords": ["template", "format", "schema", "presentation", "layout", "pattern"],
            "imports": [],
            "bases": ["BaseTemplate"],
            "examples": ["CommonLayout", "StandardEmailFormat", "ReportTemplate"],
        },
        "config": {
            "purpose": "Shared configuration files, settings, and environment management",
            "entity_types": ["Class", "Dict", "Function"],
            "keywords": ["config", "settings", "environment", "configuration", "setup", "params"],
            "imports": ["os", "pathlib", "pydantic"],
            "bases": ["BaseSettings", "BaseConfig"],
            "examples": ["AppConfig", "EnvironmentSettings", "SharedParams"],
        },
        "core_components": {
            "purpose": "Core architectural components and foundational building blocks",
            "entity_types": ["Class"],
            "keywords": ["core", "component", "foundation", "building_block", "infrastructure"],
            "imports": [],
            "bases": ["BaseComponent"],
            "examples": ["EmbedJobDescription", "EmbedMessageTemplate", "EmbedRecipientProfile"],
        },
        "data": {
            "purpose": "Shared data structures, data access objects, and data management utilities",
            "entity_types": ["Class", "Function"],
            "keywords": ["data", "dao", "repository", "storage", "persistence", "cache"],
            "imports": ["typing", "pathlib"],
            "bases": ["BaseRepository", "BaseDAO"],
            "examples": ["DataCache", "SharedRepository", "DataAccessLayer"],
        },
        "tools": {
            "purpose": "Shared tooling, utilities, and helper functions for common operations",
            "entity_types": ["Class", "Function"],
            "keywords": ["tool", "utility", "helper", "function", "operation", "service"],
            "imports": [],
            "bases": [],
            "examples": ["FileTools", "StringTools", "DateTools", "ValidationTools"],
        },
    },
}
SEMANTIC_L2_REGISTRY: Final[Mapping[str, Any]] = semantic_l2_registry


# =============================================================================
# PROJECT ROOT STRUCTURE
# =============================================================================

# Project root subfolders that are not part of agentic_core or apps_*
PROJECT_ROOT_SUBFOLDERS: Final[Mapping[str, Sequence[str]]] = {
    "logs": [],  # Mission execution logs and trace files
    "ops_scripts": [  # [ADDED] The new legal location for standalone scripts
        "ci",
        "maintenance",
        "security",
        "setup",
    ],
    "data": [
        "raw",  # Raw input data and sources
        "processed",  # Processed and transformed data
        "datasets",  # Structured datasets and test data
        "configurations",  # Configuration files and settings
        "governance",  # Governance and security data
        "cache",  # Temporary cache files
        "archives",  # Archived historical data
        "logs",  # Data processing logs
    ],
    "docs": [
        "technical",  # Technical documentation
        "project",  # Project management docs
        "analysis",  # Analysis and research
        "guides",  # User and developer guides
        "archive",  # Archived documentation
    ],
    "tests": [],  # Test files (separate from scripts)
    "archives": [],  # Archived files and historical data
}

# Project root metadata for clarity
PROJECT_ROOT_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "logs": {
        "purpose": "Mission execution logs and trace files",
        "content_types": ["mission_logs", "trace_files", "execution_logs"],
        "execution_allowed": False,
        "notes": "Contains trace.jsonl files for various mission executions",
        "file_patterns": ["*.log", "*.jsonl", "*.trace"],
        "keywords": ["transcript", "log", "trace", "execution"],
    },
    "scripts": {
        "purpose": "Project-level utility scripts (standalone, no core dependencies)",
        "content_types": ["setup_scripts", "deployment_tools", "ci_scripts", "migration_tools"],
        "execution_allowed": True,
        "notes": "Standalone utilities only - NO agentic_core imports allowed",
        "file_patterns": ["*.py", "*.sh", "*.bat", "*.cmd"],
        "keywords": ["setup", "install", "ci", "build", "deploy", "migration", "run"],
    },
    "data": {
        "purpose": "Data files and datasets used by the project",
        "content_types": [
            "raw_data",
            "processed_data",
            "datasets",
            "configurations",
            "governance_data",
        ],
        "execution_allowed": False,
        "notes": "Organized by data lifecycle: raw → processed → datasets → configurations",
        "file_patterns": [
            "*.csv",
            "*.json",
            "*.yaml",
            "*.yml",
            "*.xml",
            "*.parquet",
            "*.db",
            "*.sqlite",
        ],
        "keywords": ["data", "dataset", "config", "settings", "parameters"],
    },
    "docs": {
        "purpose": "Project documentation and reports organized by purpose",
        "content_types": ["technical_docs", "project_docs", "analysis_reports", "user_guides"],
        "execution_allowed": False,
        "notes": "Categorized documentation: technical, project, analysis, and guides",
        "file_patterns": ["*.md", "*.rst", "*.txt", "*.pdf", "*.docx", "*.html"],
        "keywords": ["doc", "guide", "manual", "readme", "tutorial", "specification"],
    },
    "reports": {
        "purpose": "Generated reports, analysis outputs, and implementation plans",
        "content_types": [
            "coverage_reports",
            "telemetry_data",
            "audit_reports",
            "implementation_plans",
        ],
        "execution_allowed": False,
        "notes": "SSOT location for all implementation plans and generated reports",
        "file_patterns": ["*.html", "*.json", "*.md", "*.xml", "*.csv"],
        "keywords": ["report", "coverage", "telemetry", "audit", "plan", "implementation"],
    },
    "tests": {
        "purpose": "Test files and test data",
        "content_types": ["test_files", "test_data", "fixtures"],
        "execution_allowed": True,
        "notes": "Test files separate from execution scripts",
        "file_patterns": ["test_*.py", "*_test.py", "conftest.py", "*.fixture"],
        "keywords": ["test", "spec", "fixture", "mock"],
        "naming_convention": "snake_case_test",  # Enforce consistent test naming
    },
    "enforcement": {  # LCD+ CONTENT TYPE FOR L5 SAFETY (was guardrails)
        "purpose": "L5 safety enforcement agents and components (guardrails, gravity, gates)",
        "content_types": ["safety_agent", "membrane", "sanitizer", "hygiene_agent", "guardrail", "gate"],
        "execution_allowed": True,  # Operational agents
        "notes": "Sovereign operational safety components - snake_case_agent naming mandatory",
        "file_patterns": ["*_agent.py"],
        "keywords": ["guardrail", "membrane", "sanitizer", "hygiene", "redact", "scrub", "pii", "threat"],
        "naming_convention": "snake_case_agent",
    },
    "archives": {
        "purpose": "Archived files and historical data",
        "content_types": ["archived_code", "historical_data", "backups"],
        "execution_allowed": False,
        "notes": "Legacy files and historical archives",
        "file_patterns": ["*.bak", "*.old", "*.backup", "*.archive", "*.zip", "*.tar.gz"],
        "keywords": ["archive", "backup", "old", "legacy", "retired"],
    },
}

# Detailed subfolder metadata for data and docs directories
DATA_SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "raw": {
        "purpose": "Raw input data and external sources",
        "content_types": ["external_references", "input_files", "source_data"],
        "execution_allowed": False,
        "notes": "Contains external/ reference materials and raw inputs",
    },
    "processed": {
        "purpose": "Processed and transformed data artifacts",
        "content_types": ["audit_results", "evaluations", "manifests", "outputs"],
        "execution_allowed": False,
        "notes": "Data that has been processed or transformed",
    },
    "datasets": {
        "purpose": "Structured datasets for testing and reference",
        "content_types": ["golden_datasets", "test_data", "reference_data"],
        "execution_allowed": False,
        "notes": "Curated datasets for testing and validation",
    },
    "configurations": {
        "purpose": "Configuration files and settings",
        "content_types": ["sdk_configs", "mcp_configs", "prompt_configs", "task_definitions"],
        "execution_allowed": False,
        "notes": "Configuration files for various components",
    },
    "governance": {
        "purpose": "Governance and security-related data",
        "content_types": ["prompt_governance", "injection_data", "safety_data", "registry_data"],
        "execution_allowed": False,
        "notes": "Security, governance, and compliance data",
    },
    "cache": {
        "purpose": "Temporary cache files",
        "content_types": ["temp_files", "cache_data"],
        "execution_allowed": False,
        "notes": "Temporary storage that can be cleared",
    },
    "archives": {
        "purpose": "Archived historical data",
        "content_types": ["historical_data", "backups", "legacy_files"],
        "execution_allowed": False,
        "notes": "Long-term storage of historical data",
    },
    "logs": {
        "purpose": "Data processing logs and traces",
        "content_types": ["processing_logs", "error_logs", "trace_files"],
        "execution_allowed": False,
        "notes": "Logs from data processing operations",
    },
}

DOCS_SUBFOLDER_METADATA: Final[Mapping[str, Mapping[str, Any]]] = {
    "technical": {
        "purpose": "Technical documentation and specifications",
        "content_types": [
            "architecture_docs",
            "integration_guides",
            "api_docs",
            "configuration_guides",
        ],
        "execution_allowed": False,
        "notes": "Technical documentation for developers and architects",
    },
    "project": {
        "purpose": "Project management and governance documentation",
        "content_types": ["phase_docs", "planning_docs", "governance_docs", "milestone_tracking"],
        "execution_allowed": False,
        "notes": "Project management and planning documentation",
    },
    "analysis": {
        "purpose": "Analysis reports and research documentation",
        "content_types": ["analysis_reports", "metrics_docs", "investigation_reports", "rca_docs"],
        "execution_allowed": False,
        "notes": "Analysis, research, and investigation reports",
    },
    "guides": {
        "purpose": "User and developer guides",
        "content_types": ["user_guides", "developer_guides", "deployment_guides", "tutorials"],
        "execution_allowed": False,
        "notes": "Instructional documentation for users and developers",
    },
    "archive": {
        "purpose": "Archived and outdated documentation",
        "content_types": ["legacy_docs", "outdated_specs", "historical_docs"],
        "execution_allowed": False,
        "notes": "Documentation kept for historical reference",
    },
}

# ============================================================================
# LAYER VALIDATION API (Phase 1 Hardening — 2026-02-07)
# ============================================================================
# Programmatic API consumed by FCA.validate_layer_alignment() and healing agents.
# Enforces: layer roots, required subfolders, nested-LCD prevention, scripts purity,
# subprocess allowlists, and "Purpose Over Mechanism" policy.

LAYER_ROOTS: Final[frozenset[str]] = frozenset(
    {
        "L0_maintenance",
        "L1_cognition",
        "L2_execution",
        "L3_orchestration",
        "L4_state",
        "L5_safety",
        "L6_observability",
    },
)

REQUIRED_LCD_SUBFOLDERS: Final[frozenset[str]] = frozenset(
    {
        "reasoning",
        "enforcement",
        "config",
        "types",
        "validators",
        "utils",
    },
)

# Only layer roots may contain LCD subfolders. Leaf domains listed here
# are forbidden from sprouting reasoning/enforcement/config/types/validators/utils.
LEAF_DOMAINS_NO_LCD: Final[frozenset[str]] = frozenset(
    {
        "prompt_governance",
        "knowledge",
        "mixins",
        "runtime",
        "interfaces",
        "base_agents",
        "config",
    },
)


def is_layer_root(name: str) -> bool:
    """Return True if *name* is a canonical L0–L6 layer root."""
    return name in LAYER_ROOTS


def is_allowed_subfolder(layer: str, subfolder: str) -> bool:
    """Return True if *subfolder* is a required LCD subfolder under *layer*."""
    if layer not in LAYER_ROOTS:
        return False
    return subfolder in REQUIRED_LCD_SUBFOLDERS


def validate_no_nested_lcd(path_parts: Sequence[str]) -> dict[str, Any] | None:
    """Detect leaf domains that illegally sprout LCD subtrees.

    Args:
        path_parts: tuple/list of path components (e.g. Path.parts).

    Returns:
        None if compliant, or a violation dict with:
        - domain: the leaf domain that is sprouting
        - illegal_subfolder: the LCD subfolder it created
        - message: human-readable explanation
    """
    for i, part in enumerate(path_parts):
        if part in LEAF_DOMAINS_NO_LCD:
            # Check remaining parts for LCD subfolder names
            for j in range(i + 1, len(path_parts)):
                child = path_parts[j]
                if child in REQUIRED_LCD_SUBFOLDERS:
                    # Allow if the child is ALSO inside a layer root higher up
                    has_layer_root_ancestor = any(path_parts[k] in LAYER_ROOTS for k in range(i))
                    if has_layer_root_ancestor:
                        break  # e.g. L0_maintenance/scripts/prompt_governance — OK
                    return {
                        "domain": part,
                        "illegal_subfolder": child,
                        "message": (
                            f"Leaf domain '{part}' must not sprout LCD subfolder "
                            f"'{child}/'. Only L0–L6 layer roots may have LCD subtrees."
                        ),
                    }
    return None


# === L5 SUBPROCESS ALLOWLIST (Purpose Over Mechanism) ===
# These L5 files are PERMITTED to import subprocess because their PRIMARY PURPOSE
# is safety enforcement — subprocess is merely the mechanism.
# Any L5 file importing subprocess NOT on this list is a TERRITORY_MISALIGNMENT.
L5_SUBPROCESS_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        "safe_subprocess_handler.py",
        "subprocess_security_util.py",
        "PreCommitSovereignAgent.py",
        "ArchitectureGovernorAgent.py",
        "AutonomyGuardianAgent.py",
        "SovereignActionPlaneAgent.py",
        "pre_deploy_check_util.py",
    },
)

# === L6 HYBRID ALLOWLIST ===
# L6 files permitted to use subprocess/playwright for dashboard E2E.
L6_HYBRID_ALLOWLIST: Final[frozenset[str]] = frozenset(
    {
        "verify_dashboard_e2e_playwright_util.py",
    },
)

# === SCRIPTS PURITY POLICY ===
# scripts/ folders may contain ONLY:
#   - snake_case .py files with __main__ guard or CLI entrypoint
#   - _util.py helper scripts
# FORBIDDEN in scripts/:
SCRIPTS_FORBIDDEN_PATTERNS: Final[Sequence[str]] = [
    r"^[A-Z]",  # PascalCase module filenames (classes belong elsewhere)
    r"^test_",  # Test files belong in tests/
]
