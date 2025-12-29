"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth-2 for Apps/Tests and Depth-3 for the Agentic Core.
[SSOT] This is the absolute source of truth for the entire repository structure.

CONSOLIDATED VERSION: Reduced redundancy while preserving all information.
"""
import os
import re
from typing import Any, Dict, List, Optional, Protocol, Set

# ==============================================================================
# SECTION 1: EXCEPTION LEDGERS & KEY MAPPINGS
# ==============================================================================

# [KEY EXCEPTION LEDGER] Central SSOT for False Positive Suppression
CANON_KEY_EXCEPTIONS: Dict[int, Dict[str, Any]] = {
    23: {"files": {"agentic_core/L2_execution/mcp/fetch_client_sovereign.py"}, "patterns": [r"if TYPE_CHECKING:", r"\"\"\".*requests.*\"\"\""]},
    20: {"files": {"canon_validator_agentic_v2.py", "pyproject.toml"}, "patterns": []}
}

# [CANON KEY CONSTITUTION] Active keys and their folder mappings
ACTIVE_CANON_KEYS = list(range(0, 22))
CANON_KEY_TO_FOLDER_MAP: Dict[int, List[str]] = {
    0: ["."], 1: ["agentic_core/prompt_governance"], 7: ["agentic_core/schemas"],
    11: ["agentic_core/L1_cognition"], 12: ["agentic_core/L3_orchestration"], 13: ["agentic_core/L4_state"],
    19: ["agentic_core/L5_safety"], 20: ["agentic_core/L0_maintenance", "agentic_core/utils/naming", "agentic_core/observability/compliance"],
    21: ["agentic_core/L2_execution", "agentic_core/patterns", "agentic_core/semantic_memory", "agentic_core/knowledge"],
    14: ["apps_shared", "apps_rg", "apps_lic"], 15: ["apps_rg/agents", "apps_lic/agents"], 16: ["apps_shared/utils"], 17: ["tests"]
}

# ==============================================================================
# SECTION 2: SOVEREIGN REGISTRY (Root Structure)
# ==============================================================================

SOVEREIGN_REGISTRY = {
    "agentic_core": {
        "depth": 3,
        "subfolders": ["L0_maintenance", "L1_cognition", "L2_execution", "L3_orchestration", "L4_state", "L5_safety",
                      "config", "schemas", "prompt_governance", "runtime", "observability", "utils", "patterns", "semantic_memory", "knowledge"]
    },
    "apps_rg": {"depth": 2, "subfolders": ["logic_nodes", "asset_library", "system_flow", "engines", "templates"]},
    "apps_lic": {"depth": 2, "subfolders": ["logic_nodes", "asset_library", "system_flow", "engines", "templates"]},
    "apps_shared": {"depth": 2, "subfolders": ["base_definitions", "common_utils", "core_components", "base_agents", "models", "utils"]},
    "tests": {"depth": 2, "subfolders": ["unit", "integration", "e2e", "functional", "fixtures", "automation", "core", "data", "performance", "security"]}
}

# ==============================================================================
# SECTION 3: L2 SUBFOLDER MAPS (Depth-3 Structure for agentic_core)
# ==============================================================================

CORE_SUBFOLDER_MAP = {
    "L0_maintenance": ["scripts", "logs", "benchmarks"],
    "L1_cognition": ["thought_engine", "intent_analysis", "planning"],
    "L2_execution": ["tool_registry", "action_handlers", "mcp"],
    "L3_orchestration": ["workflow_engines", "fission_logic", "S3_vitality", "mcp"],
    "L4_state": ["validation_context", "ledger", "filesystem", "memory"],
    "L5_safety": ["guardrails", "red_teaming", "gravity", "validators"],
    "schemas": ["models", "messages", "types", "validators"],
    "config": ["blueprint_sovereign", "environments", "feature_flags", "secrets_manager"],
    "prompt_governance": ["meta_prompts", "version_registry", "rendering", "templates"],
    "runtime": ["shared_runtime", "environment_setup", "shared", "resource_management"],
    "observability": ["metrics", "telemetry", "tracing", "compliance"],
    "utils": ["core_extensions", "wrappers", "helpers", "naming"],
    "patterns": ["agent_roles", "communication_flow", "interaction_patterns", "reasoning_patterns"],
    "semantic_memory": ["store", "embeddings", "retrieval", "index"],
    "knowledge": ["document_loaders", "static_index", "research_cache"]
}

# [DOMAIN L2 MAPS] Consolidated structure - apps use consistent pattern
# All apps_rg and apps_lic L2 folders follow: {type}_definitions + {type}_helpers
APPS_RG_SUBFOLDER_MAP = {
    "logic_nodes": ["node_definitions", "node_helpers"],
    "asset_library": ["asset_definitions", "asset_helpers"],
    "system_flow": ["flow_definitions", "flow_helpers"],
    "engines": ["engine_definitions", "engine_helpers"],
    "templates": ["template_definitions", "template_helpers"]
}
APPS_LIC_SUBFOLDER_MAP = APPS_RG_SUBFOLDER_MAP  # Identical structure
APPS_SHARED_SUBFOLDER_MAP = {
    "base_definitions": ["definition_helpers", "definition_types"],
    "common_utils": ["utility_helpers", "utility_types"],
    "core_components": ["component_definitions", "component_helpers"],
    "base_agents": ["agent_definitions", "agent_helpers"],
    "models": ["model_definitions", "model_helpers"],
    "utils": ["utility_helpers", "utility_types"]
}
TESTS_L2_SUBFOLDER_MAP = {
    "unit": ["test_definitions", "test_helpers"],
    "integration": ["test_definitions", "test_helpers"],
    "e2e": ["test_definitions", "test_helpers"],
    "functional": ["test_definitions", "test_helpers"],
    "fixtures": ["fixture_definitions", "fixture_helpers"],
    "automation": ["automation_definitions", "automation_helpers"],
    "core": ["core_definitions", "core_helpers"],
    "data": ["data_definitions", "data_helpers"],
    "performance": ["performance_definitions", "performance_helpers"],
    "security": ["security_definitions", "security_helpers"]
}

# Backward compatibility
AGENTIC_CORE_REGISTRY = CORE_SUBFOLDER_MAP
TESTS_SUBFOLDER_MAP = TESTS_L2_SUBFOLDER_MAP

# ==============================================================================
# SECTION 4: NAMING LAW & FORBIDDEN PATTERNS
# ==============================================================================

CANON_SIGNALS: set[str] = {
    "agent", "manager", "engine", "validator", "healer", "auditor", "enforcer", "detector",
    "orchestrator", "coordinator", "pruner", "mapper", "handler", "guardian", "governor", "sentinel",
    "strategy", "reasoning", "fission", "workflow", "state", "memory", "cache",
    "safety", "guardrail", "prompt", "persona", "schema", "blueprint", "template",
    "context", "ledger", "historian", "audit", "coverage",
    "vector", "embedding", "pinecone", "redis", "compliance", "drift", "hierarchy",
    "span", "depth", "naming", "rescue", "integrity", "gravity", "subatomic", "gemini"
}

FORBIDDEN_PATTERNS = [
    re.compile(r"^utils\.py$"), re.compile(r"^helper\.py$"), re.compile(r"^temp\.py$"),
    re.compile(r".*_v\d+\.py$"), re.compile(r"^main\.py$"), re.compile(r"^test\.py$"),
    re.compile(r".*_final\.py$"), re.compile(r".*_new\.py$"), re.compile(r".*_old\.py$"),
    re.compile(r".*_copy\.py$"), re.compile(r".*_backup\.py$"), re.compile(r"^legacy_.*\.py$"),
    re.compile(r"^.+_\d+\.py$"), re.compile(r"^draft_.*\.py$")
]

# ==============================================================================
# SECTION 5: SYSTEM CONFIGURATION & WHITELISTS
# ==============================================================================

ROOT_PROTECTED_FILES = {"canon_validator_agentic_v2.py", "pyproject.toml", "README.md", "langgraph.json", ".env", "windsurfrules.md", ".gitignore"}

SOVEREIGN_EXCLUDED_FOLDERS: frozenset[str] = frozenset({
    ".git", ".venv", "venv", "venv_stable", "__pycache__", ".pytest_cache", ".ruff_cache", "node_modules", ".mypy_cache", ".tox",
    "archives", "legacy_code", "legacy_engines", "legacy_resume_gen", "data", "docs", "env", "build", "dist", "_build",
    "Lib", "site-packages", "google", "gapic", "logging", "licenses", "src", "pip", "dist-info", "raw", "golden_state", "logs", "processed",
    "shared", "refs", "remotes", "v", "stubs", ".sovereign_healing_backup", ".idea", ".vscode", ".DS_Store", "Thumbs.db"
})

FORBIDDEN_FOLDER_PATTERN = re.compile(r"^\d+_")
FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset({"legacy_code", "legacy_engines", "legacy_resume_gen", "old_core"})
TESTS_ROOT_FILE_WHITELIST: frozenset[str] = frozenset({"conftest.py", "sovereign_smoke_test.py", "test_autonomous_improvements.py"})
AUTONOMOUS_AGENT_WHITELIST: frozenset[str] = frozenset({"autonomous_checkpoint_manager.py", "autonomous_state_guardian.py", "self_updating_safety_engine.py", "neural_auto_immune_agent.py"})

# Backward compatibility aliases
PROTECTED_FOLDERS = SOVEREIGN_EXCLUDED_FOLDERS
IGNORE_DIRS = SOVEREIGN_EXCLUDED_FOLDERS
SOVEREIGN_IGNORED_FOLDERS = SOVEREIGN_EXCLUDED_FOLDERS

# ==============================================================================
# SECTION 6: RUNTIME CONFIGURATION
# ==============================================================================

HEALING_CONFIG = {
    "max_rounds": int(os.getenv('MAX_HEALING_ROUNDS', '10')),
    "max_per_file": int(os.getenv('MAX_HEALING_PER_FILE', '8')),
    "global_budget": int(os.getenv('GLOBAL_HEALING_BUDGET', '50'))
}

AGENT_RESILIENCE_CONFIG = {
    "retry_count": int(os.getenv("AGENT_RETRY_COUNT", "3")),
    "backoff_base": float(os.getenv("AGENT_RETRY_BACKOFF_BASE", "0.5"))
}

MISSION_CONFIG = {
    "gravity_surgery_enabled": True, "hierarchy_healing_enabled": True, "span_surgery_enabled": True, "fission_enabled": True, "run_full_mission": True,
    "run_hierarchy_healing": False, "run_gravity_refactor": False, "run_sprawl_surgery": False, "structural_only_mode": False,
    "timeout_seconds": int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800"))
}

MCP_CAPABILITIES = {
    "router": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "marketplace_filter": {"enabled": True, "path": "agentic_core.L3_orchestration.mcp"},
    "filesystem": {"enabled": True, "path": "agentic_core.L4_state.filesystem"},
    "figma": {"enabled": True, "path": "agentic_core.L2_execution.mcp"},
    "fetch": {"enabled": True, "path": "agentic_core.L2_execution.mcp"},
    "semantic_cache": {"enabled": True, "path": "agentic_core.L2_execution.mcp"}
}

SCOPE_SUMMARY_EXCLUSIONS: frozenset[str] = frozenset({"stubs", ".sovereign_healing_backup", "__pycache__"})
DISCOVERY_EXCLUDED_TERRITORIES: frozenset[str] = frozenset({"runtime_shared", "legacy_code", "legacy_engines", "archives", "stubs", "examples"})

PYTHON_STDLIB_MODULES: frozenset[str] = frozenset({
    "os", "sys", "pathlib", "logging", "asyncio", "typing", "dataclasses", "collections", "json", "re", "datetime", "functools", "itertools",
    "abc", "enum", "contextlib", "threading", "time", "random", "math", "urllib", "http", "socket", "subprocess", "shutil", "hashlib", "uuid",
    "copy", "io", "traceback", "inspect", "importlib", "warnings", "pickle"
})

# ==============================================================================
# SECTION 7: GRAVITY CONFIGURATION (Waterfall Enforcement)
# ==============================================================================

ROOT_WHITELIST: set[str] = set(SOVEREIGN_REGISTRY.keys())

GRAVITY_CONFIG = {
    "enabled": True,
    "upstream_sovereign_roots": ["agentic_core"],
    "downstream_domains": ["apps_rg", "apps_lic", "apps_shared", "tests"],
    "exemptions": []
}

GRAVITY_SURGERY_ENABLED = GRAVITY_CONFIG["enabled"]
UPSTREAM_SOVEREIGN_ROOTS = frozenset(GRAVITY_CONFIG["upstream_sovereign_roots"])
DOWNSTREAM_ROOTS = frozenset(GRAVITY_CONFIG["downstream_domains"])

# ==============================================================================
# SECTION 8: SEMANTIC L2 REGISTRY (AST Relocation Intelligence)
# ==============================================================================

# Shared metadata templates for common patterns
_SEMANTIC_TEMPLATES = {
    "node_pattern": {
        "entity_types": ["Class"],
        "examples_suffix": ["Node", "ExtractNode", "DraftNode"]
    },
    "flow_pattern": {
        "entity_types": ["Class"],
        "bases": ["BaseFlow"],
        "examples_suffix": ["Flow", "Pipeline", "Campaign"]
    },
    "engine_pattern": {
        "entity_types": ["Class"],
        "bases": ["BaseEngine"],
        "examples_suffix": ["Engine", "Builder", "Driver"]
    },
    "template_pattern": {
        "entity_types": ["Class", "Dict"],
        "bases": ["BaseTemplate"],
        "examples_suffix": ["Template", "Layout", "Format"]
    }
}

SEMANTIC_L2_REGISTRY = {
    # === CORE SOVEREIGN LAYERS ===
    "L5_safety": {
        "guardrails": {
            "purpose": "Hard safety limits, mutation controls, deletion guards, circuit breakers, rate limits, throttling, and emergency stop mechanisms",
            "entity_types": ["Class"],
            "keywords": ["guardrail", "safety", "limit", "constraint", "circuit", "breaker", "throttle", "rate", "quota", "mutate", "delete", "emergency", "stop", "block", "prevent"],
            "imports": ["agentic_core.L5_safety.guardrails"],
            "bases": ["BaseGuardrail", "SafetyGuardrail", "CircuitBreaker", "RateLimiter"],
            "examples": ["MutationGuardrail", "DeletionGuardrail", "RateLimitGuardrail", "EmergencyStopGuardrail", "ContentFilterGuardrail"]
        },
        "red_teaming": {
            "purpose": "Adversarial testing agents, automated threat simulation, exploit probing, jailbreak attempts, prompt injection testing, and attack vector generation",
            "entity_types": ["Class", "Function"],
            "keywords": ["redteam", "red_team", "adversary", "adversarial", "attack", "exploit", "probe", "jailbreak", "threat", "simulate", "fuzz", "injection", "poison"],
            "imports": ["agentic_core.L5_safety.red_teaming"],
            "bases": ["RedTeamAgent", "AdversarialAgent", "ThreatSimulator"],
            "examples": ["JailbreakProber", "PromptInjectionAttacker", "ThreatSimulator", "AdversarialFuzzer", "ExploitGenerator"]
        },
        "gravity": {
            "purpose": "Import waterfall enforcement, dependency direction control, layer authority validation, gravity surgery execution, and upstream/downstream violation detection",
            "entity_types": ["Class", "Function"],
            "keywords": ["gravity", "waterfall", "import", "dependency", "direction", "layer", "authority", "upstream", "downstream", "violation", "enforce", "surgery"],
            "imports": ["agentic_core.L5_safety.gravity", "agentic_core.runtime.shared_runtime.void_compliance"],
            "bases": ["GravityEnforcer", "WaterfallValidator"],
            "examples": ["GravityValidator", "ImportWaterfallChecker", "DependencyDirectionGuard", "GravitySurgeryEngine", "LayerAuthorityAuditor"]
        },
        "validators": {
            "purpose": "Canon constitution validators, structural policy enforcement, naming law validation, runtime compliance auditing, and architectural drift detection",
            "entity_types": ["Class"],
            "keywords": ["validator", "canon", "constitution", "rule", "policy", "enforce", "compliance", "audit", "drift", "naming", "law", "check", "verify"],
            "imports": ["agentic_core.L5_safety.validators", "structure_blueprint"],
            "bases": ["CanonBaseAgent", "KeyValidator", "StructureValidator", "ComplianceAuditor", "DriftDetector"],
            "examples": ["CanonKeyValidator", "NamingLawValidator", "DepthValidator", "GravityComplianceValidator", "StructuralPolicyValidator", "RuntimeComplianceAuditor"]
        }
    },

    # === L0_maintenance: Sovereign Maintenance & Autonomous Evolution Layer ===
    "L0_maintenance": {
        "scripts": {
            "purpose": "Autonomous healing scripts, checkpoint management, self-updating systems, neural immune agents, and sovereign improvement missions",
            "entity_types": ["Class", "Function"],
            "keywords": ["autonomous", "heal", "repair", "checkpoint", "guardian", "self_update", "immune", "mission", "surgery", "refactor", "evolution"],
            "imports": ["agentic_core.L0_maintenance.scripts", "structure_blueprint"],
            "bases": ["CanonBaseAgent", "AutonomousAgent", "HealingEngine"],
            "examples": ["AutonomousCheckpointManager", "AutonomousStateGuardian", "SelfUpdatingSafetyEngine", "NeuralAutoImmuneAgent", "SovereignHealingMission"]
        },
        "logs": {
            "purpose": "Structured diagnostic logs, healing operation records, mission transcripts, and maintenance audit trails",
            "entity_types": ["Class", "Function"],
            "keywords": ["log", "diagnostic", "record", "transcript", "audit", "maintenance_log", "healing_trace", "mission_log"],
            "imports": ["agentic_core.L0_maintenance.logs", "logging", "json"],
            "bases": ["DiagnosticLogger", "MissionTranscript", "MaintenanceAudit"],
            "examples": ["HealingOperationLogger", "AutonomousMissionLog", "SovereignDiagnosticWriter", "MaintenanceTrace"]
        },
        "benchmarks": {
            "purpose": "Performance benchmarking suites, timing profiles, resource usage metrics, and autonomous optimization baselines",
            "entity_types": ["Class", "Function"],
            "keywords": ["benchmark", "perf", "timing", "profile", "metric", "baseline", "optimize", "resource", "efficiency"],
            "imports": ["agentic_core.L0_maintenance.benchmarks", "time", "asyncio", "psutil"],
            "bases": ["BenchmarkSuite", "PerformanceProfiler", "ResourceMonitor"],
            "examples": ["SovereignBenchmarkRunner", "ReasoningSpeedTest", "MemoryEfficiencyBenchmark", "HealingCycleProfiler"]
        }
    },

    "L1_cognition": {
        "thought_engine": {
            "purpose": "Core reasoning primitives, thought nodes, chain-of-thought execution, internal monologue structures, and advanced deliberation patterns",
            "entity_types": ["Class", "Protocol"],
            "keywords": ["thought", "reason", "node", "chain", "cot", "tot", "react", "monologue", "step", "decompose", "analyze", "reflect", "critique", "socratic", "deliberate", "ponder", "contemplate", "self_reflect"],
            "imports": ["agentic_core.L1_cognition.thought_engine", "pydantic", "typing"],
            "bases": ["ThoughtNode", "ReasoningStep", "BaseThought", "ChainOfThought", "TreeOfThoughts", "ReActStep", "BaseReasoningEngine"],
            "examples": ["ReasoningNode", "CritiqueStep", "ReflectionThought", "ChainOfThoughtExecutor", "SocraticReasoner", "TreeOfThoughtsNode", "ReActAgentStep"]
        },
        "intent_analysis": {
            "purpose": "User intent detection, goal extraction, multi-turn request classification, ambiguity resolution, and command parsing",
            "entity_types": ["Class", "Function"],
            "keywords": ["intent", "goal", "objective", "request", "classify", "detect", "extract", "parse", "understand", "ambiguity", "user_goal", "task_type", "command", "query_type", "multi_turn", "conversation"],
            "imports": ["agentic_core.L1_cognition.intent_analysis", "google.generativeai", "re", "pydantic"],
            "bases": ["IntentClassifier", "GoalExtractor", "RequestParser", "AmbiguityResolver"],
            "examples": ["IntentClassifier", "GoalDecomposer", "AmbiguityResolver", "UserRequestParser", "TaskTypeDetector", "MultiTurnIntentTracker"]
        },
        "planning": {
            "purpose": "Mission decomposition, strategy formulation, step sequencing, dependency mapping, plan validation, and execution roadmap generation",
            "entity_types": ["Class", "Function"],
            "keywords": ["plan", "strategy", "decompose", "sequence", "step", "task", "subtask", "dependency", "order", "validate", "breakdown", "hierarchy", "outline", "roadmap", "execute_order", "priority", "milestone"],
            "imports": ["agentic_core.L1_cognition.planning", "networkx", "pydantic", "typing"],
            "bases": ["Planner", "DecompositionEngine", "PlanValidator", "StrategyBuilder", "BasePlanner", "TaskGraph"],
            "examples": ["MissionDecomposer", "TaskSequencer", "DependencyResolver", "PlanValidator", "StrategicPlanner", "StepHierarchyBuilder", "PriorityScheduler"]
        }
    },
    "L2_execution": {
        "tool_registry": {
            "purpose": "Registration and discovery of external tools, base tool definitions, and tool metadata management",
            "entity_types": ["Class", "Function"],
            "keywords": ["tool", "registry", "register", "discover", "metadata", "available_tools", "toolset"],
            "imports": ["agentic_core.L2_execution.tool_registry", "pydantic", "typing"],
            "bases": ["BaseTool", "ToolRegistry"],
            "examples": ["ToolRegistry", "register_tool", "AvailableToolsList", "ToolMetadata"]
        },
        "action_handlers": {
            "purpose": "Action dispatch logic, handler mapping, execution routing, and fallback strategies for tool calls",
            "entity_types": ["Class", "Function"],
            "keywords": ["action", "handler", "execute", "dispatch", "route", "fallback", "perform", "invoke", "call_action"],
            "imports": ["agentic_core.L2_execution.action_handlers"],
            "bases": ["ActionHandler", "BaseActionDispatcher"],
            "examples": ["ActionDispatcher", "HandlerMap", "DefaultActionExecutor", "ToolCallRouter", "FallbackHandler"]
        },
        "mcp": {
            "purpose": "Multi-Component Protocol clients and tool implementations (figma, fetch, filesystem, semantic_cache, router, marketplace_filter)",
            "entity_types": ["Class"],
            "keywords": ["mcp", "client", "figma", "fetch", "filesystem", "semantic_cache", "router", "marketplace", "filter", "protocol"],
            "imports": ["agentic_core.L2_execution.mcp", "requests", "playwright", "selenium", "pinecone"],
            "bases": ["BaseTool", "MCPClientBase"],
            "examples": ["FigmaClient", "FetchClientSovereign", "FilesystemMCPClient", "SemanticCacheClient", "MCPRouter", "MarketplaceFilter"]
        }
    },
    "L3_orchestration": {
        "workflow_engines": {
            "purpose": "High-level agent orchestration, multi-agent workflow engines, task routing, mission lifecycle management, and coordination primitives",
            "entity_types": ["Class"],
            "keywords": ["orchestrator", "coordinator", "workflow", "engine", "manager", "supervisor", "crew", "team", "mission", "lifecycle", "route", "dispatch", "schedule"],
            "imports": ["agentic_core.L3_orchestration.workflow_engines", "langgraph", "pydantic"],
            "bases": ["CanonBaseAgent", "WorkflowEngine", "OrchestratorBase", "MissionManager"],
            "examples": ["SovereignOrchestrator", "MultiAgentWorkflow", "TaskRouter", "MissionLifecycleManager", "AgentSupervisor"]
        },
        "fission_logic": {
            "purpose": "Agent fission mechanics, dynamic sub-agent spawning, division of labor, and recursive self-delegation systems",
            "entity_types": ["Class", "Function"],
            "keywords": ["fission", "spawn", "subagent", "divide", "delegate", "recursive", "split", "branch", "fork", "proliferate"],
            "imports": ["agentic_core.L3_orchestration.fission_logic"],
            "bases": ["FissionEngine", "SubAgentSpawner", "CanonBaseAgent"],
            "examples": ["FissionManager", "DynamicSubAgentCreator", "RecursiveDelegator", "TaskFissionLogic"]
        },
        "S3_vitality": {
            "purpose": "System vitality monitoring, health checks, self-preservation protocols, anomaly detection, and resilience mechanisms",
            "entity_types": ["Class", "Function"],
            "keywords": ["vitality", "health", "monitor", "heartbeat", "anomaly", "resilience", "self_preserve", "watchdog", "liveness", "readiness"],
            "imports": ["agentic_core.L3_orchestration.S3_vitality"],
            "bases": ["VitalityMonitor", "HealthChecker", "CanonBaseAgent"],
            "examples": ["VitalityGuardian", "SystemHealthMonitor", "AnomalyDetector", "ResilienceEngine", "WatchdogAgent"]
        },
        "mcp": {
            "purpose": "Orchestration-level Multi-Component Protocol components (router, marketplace_filter, coordination logic)",
            "entity_types": ["Class"],
            "keywords": ["mcp", "router", "marketplace", "filter", "orchestrate", "coordinate", "gateway", "proxy"],
            "imports": ["agentic_core.L3_orchestration.mcp"],
            "bases": ["MCPRouterBase", "MarketplaceFilter", "CanonBaseAgent"],
            "examples": ["MCPRouter", "MarketplaceToolFilter", "OrchestrationGateway", "MCPCoordinator"]
        }
    },
    "L4_state": {
        "validation_context": {
            "purpose": "Runtime validation contexts, state integrity containers, and scoped validation environments",
            "entity_types": ["Class"],
            "keywords": ["validation", "context", "scope", "integrity", "state_check", "validate_in_context"],
            "imports": ["agentic_core.L4_state.validation_context", "pydantic", "typing"],
            "bases": ["ValidationContext", "BaseStateContext"],
            "examples": ["SovereignValidationContext", "MissionValidationScope", "StateIntegrityContainer"]
        },
        "ledger": {
            "purpose": "Immutable audit ledgers, historical state records, event sourcing, and tamper-evident logs",
            "entity_types": ["Class"],
            "keywords": ["ledger", "immutable", "audit", "trail", "history", "event_source", "append_only", "commit_log"],
            "imports": ["agentic_core.L4_state.ledger"],
            "bases": ["ImmutableLedger", "AuditTrail", "EventLedger"],
            "examples": ["SovereignLedger", "MissionHistoryLedger", "StateCommitLog", "TamperEvidentRecord"]
        },
        "filesystem": {
            "purpose": "Sovereign filesystem abstractions, MCP filesystem operations, and persistent file state management",
            "entity_types": ["Class"],
            "keywords": ["filesystem", "mcp", "file", "directory", "path", "persistent", "storage", "disk"],
            "imports": ["agentic_core.L4_state.filesystem", "pathlib"],
            "bases": ["FilesystemMCP", "BaseFilesystemClient", "BaseTool"],
            "examples": ["SovereignFilesystemClient", "PersistentStateStore", "FileLedgerAdapter"]
        },
        "memory": {
            "purpose": "In-memory state stores, session management, ephemeral caches, and short-term memory systems",
            "entity_types": ["Class"],
            "keywords": ["memory", "session", "cache", "ephemeral", "short_term", "in_memory", "working_memory"],
            "imports": ["agentic_core.L4_state.memory", "redis", "typing"],
            "bases": ["MemoryStore", "SessionManager", "EphemeralCache"],
            "examples": ["SovereignWorkingMemory", "SessionState", "ShortTermCache", "InMemoryLedger"]
        }
    },
    "schemas": {
        "models": {
            "purpose": "Pydantic data models, domain objects, and structured data contracts",
            "entity_types": ["Class"], "keywords": ["model", "pydantic", "dataclass", "schema", "dto", "definition"],
            "imports": ["pydantic"], "bases": ["BaseModel"]
        },
        "messages": {
            "purpose": "API message formats, request/response schemas, and protocol buffers",
            "entity_types": ["Class"], "keywords": ["message", "request", "response", "payload", "packet"],
            "imports": ["pydantic"], "bases": ["BaseModel"]
        }
    },
    "prompt_governance": {
        "templates": {
            "purpose": "Reusable prompt fragments, system instructions, and jinja templates",
            "entity_types": ["Class", "str constant"], "keywords": ["prompt", "template", "system", "instruction", "jinja", "persona"],
            "imports": ["jinja2"], "bases": []
        },
        "rendering": {
            "purpose": "Dynamic prompt assembly, variable substitution, and rendering logic",
            "entity_types": ["Class", "Function"], "keywords": ["render", "assemble", "build", "format", "interpolate"],
            "imports": ["jinja2"], "bases": []
        }
    },
    "semantic_memory": {
        "embeddings": {
            "purpose": "Embedding generation, caching, and dimension management",
            "entity_types": ["Class", "Function"], "keywords": ["embedding", "embed", "vectorize", "dimension", "latent"],
            "imports": ["google.generativeai"], "bases": []
        },
        "retrieval": {
            "purpose": "Semantic search, similarity scoring, and RAG retrieval",
            "entity_types": ["Class", "Function"], "keywords": ["retriev", "search", "similarity", "rag", "query", "lookup"],
            "imports": ["pinecone"], "bases": []
        }
    },

    # === ADDITIONAL CORE LAYERS ===
    "L0_maintenance": {
        "scripts": {
            "purpose": "Maintenance, healing, and autonomous improvement scripts",
            "entity_types": ["Function", "Class"],
            "keywords": ["heal", "repair", "autonomous", "checkpoint", "guardian", "self_update", "immune"],
            "imports": [], "bases": ["CanonBaseAgent"],
            "examples": ["AutonomousCheckpointManager", "SelfUpdatingSafetyEngine", "NeuralAutoImmuneAgent"]
        },
        "logs": {
            "purpose": "Structured logging utilities and log parsers for maintenance diagnostics",
            "entity_types": ["Class", "Function"],
            "keywords": ["log", "parser", "diagnostic", "archive", "trace"],
            "imports": ["logging"], "bases": []
        },
        "benchmarks": {
            "purpose": "Performance benchmarking suites and metric collection scripts",
            "entity_types": ["Class", "Function"],
            "keywords": ["benchmark", "perf", "metric", "timing", "profile"],
            "imports": ["time", "asyncio"], "bases": []
        }
    },
    "L2_execution": {
        "tool_registry": {
            "purpose": "External tool definitions, wrappers, and registration",
            "entity_types": ["Class"], "keywords": ["tool", "wrapper", "browser", "search", "scrape", "client", "api"],
            "imports": ["selenium", "playwright", "requests"], "bases": ["BaseTool"]
        },
        "action_handlers": {
            "purpose": "Action execution handlers and dispatch logic",
            "entity_types": ["Class", "Function"], "keywords": ["action", "handler", "execute", "dispatch"],
            "imports": [], "bases": []
        },
        "mcp": {
            "purpose": "Multi-Component Protocol clients (figma, fetch, semantic_cache, etc.)",
            "entity_types": ["Class"], "keywords": ["mcp", "client", "figma", "fetch", "cache"],
            "imports": ["requests", "playwright"], "bases": ["BaseTool"]
        }
    },
    "L3_orchestration": {
        "workflow_engines": {
            "purpose": "Agent orchestration, task routing, and mission lifecycle management",
            "entity_types": ["Class"], "keywords": ["agent", "manager", "orchestrator", "workflow", "engine", "planner"],
            "imports": [], "bases": ["CanonBaseAgent"]
        },
        "fission_logic": {
            "purpose": "Agent fission and dynamic sub-agent spawning",
            "entity_types": ["Class"], "keywords": ["fission", "spawn", "subagent", "divide"],
            "imports": [], "bases": ["CanonBaseAgent"]
        },
        "S3_vitality": {
            "purpose": "Vitality monitoring and self-preservation systems",
            "entity_types": ["Class"], "keywords": ["vitality", "health", "monitor", "preserve"],
            "imports": [], "bases": []
        },
        "mcp": {
            "purpose": "MCP router and marketplace filter orchestration",
            "entity_types": ["Class"], "keywords": ["router", "marketplace", "filter", "mcp"],
            "imports": [], "bases": []
        }
    },
    "L4_state": {
        "validation_context": {
            "purpose": "Runtime validation contexts and state integrity checks",
            "entity_types": ["Class"], "keywords": ["validation", "context", "integrity", "state_check"],
            "imports": ["pydantic"], "bases": ["BaseModel"]
        },
        "ledger": {
            "purpose": "Immutable ledger implementations for audit trails and state history",
            "entity_types": ["Class"], "keywords": ["ledger", "audit", "trail", "immutable", "history"],
            "imports": [], "bases": []
        },
        "filesystem": {
            "purpose": "MCP and sovereign filesystem abstractions",
            "entity_types": ["Class"], "keywords": ["filesystem", "mcp", "path", "file", "directory"],
            "imports": ["pathlib"], "bases": ["BaseTool"]
        },
        "memory": {
            "purpose": "In-memory state stores, caches, and session management",
            "entity_types": ["Class"], "keywords": ["memory", "cache", "session", "store", "ephemeral"],
            "imports": ["redis"], "bases": []
        }
    },
    "config": {
        "blueprint_sovereign": {
            "purpose": "Sovereign structure blueprints and constitution enforcement",
            "entity_types": ["Dict", "Class"], "keywords": ["blueprint", "sovereign", "constitution", "registry"],
            "imports": [], "bases": []
        },
        "environments": {
            "purpose": "Environment-specific configuration loaders",
            "entity_types": ["Class", "Function"], "keywords": ["env", "config", "loader", "dotenv"],
            "imports": [], "bases": []
        },
        "feature_flags": {
            "purpose": "Feature toggle management and rollout controls",
            "entity_types": ["Class"], "keywords": ["flag", "feature", "toggle", "rollout"],
            "imports": [], "bases": []
        },
        "secrets_manager": {
            "purpose": "Secure secret retrieval and vault integration",
            "entity_types": ["Class"], "keywords": ["secret", "vault", "key", "credential"],
            "imports": [], "bases": []
        }
    },
    "runtime": {
        "shared_runtime": {
            "purpose": "Shared runtime environment setup and void compliance",
            "entity_types": ["Class", "Function"], "keywords": ["runtime", "shared", "void", "compliance"],
            "imports": [], "bases": []
        },
        "resource_management": {
            "purpose": "Resource allocation, throttling, and cleanup",
            "entity_types": ["Class"], "keywords": ["resource", "throttle", "quota", "cleanup"],
            "imports": [], "bases": []
        }
    },
    "observability": {
        "metrics": {
            "purpose": "Metric collection and export",
            "entity_types": ["Class"], "keywords": ["metric", "counter", "gauge", "histogram"],
            "imports": ["prometheus_client"], "bases": []
        },
        "telemetry": {
            "purpose": "Distributed telemetry and event emission",
            "entity_types": ["Class"], "keywords": ["telemetry", "event", "emit", "trace"],
            "imports": ["opentelemetry"], "bases": []
        },
        "tracing": {
            "purpose": "Span tracing and context propagation",
            "entity_types": ["Class"], "keywords": ["trace", "span", "context", "propagate"],
            "imports": ["opentelemetry"], "bases": []
        },
        "compliance": {
            "purpose": "Compliance reporting and canon drift detection",
            "entity_types": ["Class", "Function"], "keywords": ["compliance", "drift", "report", "canon"],
            "imports": [], "bases": []
        }
    },
    "utils": {
        "core_extensions": {
            "purpose": "Core Python extensions and polyfills",
            "entity_types": ["Function", "Class"], "keywords": ["extension", "polyfill", "monkey"],
            "imports": [], "bases": []
        },
        "wrappers": {
            "purpose": "Decorators and generic wrappers",
            "entity_types": ["Function"], "keywords": ["wrapper", "decorator", "retry", "cache"],
            "imports": ["functools"], "bases": []
        },
        "helpers": {
            "purpose": "General helper functions",
            "entity_types": ["Function"], "keywords": ["helper", "util"],
            "imports": [], "bases": []
        },
        "naming": {
            "purpose": "Naming law enforcement and canon signal validation",
            "entity_types": ["Class", "Function"], "keywords": ["naming", "canon", "signal", "law"],
            "imports": [], "bases": []
        }
    },
    "patterns": {
        "agent_roles": {
            "purpose": "Pre-defined agent personas and role templates",
            "entity_types": ["Class", "Dict"], "keywords": ["role", "persona", "agent_type"],
            "imports": [], "bases": ["CanonBaseAgent"]
        },
        "communication_flow": {
            "purpose": "Inter-agent message passing patterns",
            "entity_types": ["Class"], "keywords": ["communication", "message", "flow", "protocol"],
            "imports": [], "bases": []
        },
        "interaction_patterns": {
            "purpose": "Common human-agent and agent-tool interaction patterns",
            "entity_types": ["Class"], "keywords": ["interaction", "pattern", "ui", "cli"],
            "imports": [], "bases": []
        },
        "reasoning_patterns": {
            "purpose": "Reusable reasoning strategies (CoT, ToT, ReAct, etc.)",
            "entity_types": ["Class"], "keywords": ["reasoning", "strategy", "cot", "tot", "react"],
            "imports": [], "bases": ["BaseReasoningEngine"]
        }
    },
    "knowledge": {
        "document_loaders": {
            "purpose": "Document ingestion and parsing utilities",
            "entity_types": ["Class"], "keywords": ["loader", "ingest", "parse", "document"],
            "imports": ["unstructured", "langchain"], "bases": []
        },
        "static_index": {
            "purpose": "Hard-coded knowledge bases and static facts",
            "entity_types": ["Dict", "Class"], "keywords": ["static", "index", "facts", "knowledge"],
            "imports": [], "bases": []
        },
        "research_cache": {
            "purpose": "Cached research results and external knowledge snapshots",
            "entity_types": ["Class"], "keywords": ["research", "cache", "snapshot"],
            "imports": [], "bases": []
        }
    },

    # === APPLICATION DOMAINS ===
    "apps_rg": {
        "logic_nodes": {
            "purpose": "Business logic nodes for resume extraction, parsing, and section formatting",
            "entity_types": ["Class"], 
            "keywords": ["resume", "cv", "node", "section", "experience", "education", "skill", "extract", "format", "parse"],
            "imports": ["apps_rg.logic_nodes", "pydantic"], 
            "bases": ["BaseNode", "ResumeNode", "ExtractionNode"], 
            "examples": ["ExperienceNode", "SkillExtractNode", "EducationFormatter", "HeaderLogicNode"]
        },
        "asset_library": {
            "purpose": "Static assets, hardcoded strings, action verbs, and skill taxonomies for resumes",
            "entity_types": ["Class", "Dict"], 
            "keywords": ["asset", "string", "text", "resource", "copy", "wording", "verbs", "skills", "taxonomy"],
            "imports": [], "bases": ["BaseAsset"], 
            "examples": ["ResumeAssets", "ActionVerbs", "SkillTaxonomy", "ResumeTemplateStrings"]
        },
        "system_flow": {
            "purpose": "Linear and branching pipelines for the resume generation lifecycle",
            "entity_types": ["Class"], 
            "keywords": ["flow", "pipeline", "sequence", "generate", "create", "process", "workflow", "lifecycle"],
            "imports": ["apps_rg.system_flow"], 
            "bases": ["BaseFlow", "ResumeGenerationFlow"], 
            "examples": ["GenerationFlow", "ReviewPipeline", "PdfGenerationWorkflow", "ContentRefinementFlow"]
        },
        "engines": {
            "purpose": "Core rendering engines for document export (PDF, Docx, HTML)",
            "entity_types": ["Class"], 
            "keywords": ["engine", "render", "export", "pdf", "docx", "builder", "latex", "jinja"],
            "imports": ["apps_rg.engines", "jinja2"], 
            "bases": ["BaseEngine", "DocumentBuilder"], 
            "examples": ["PdfEngine", "DocxBuilder", "HtmlRenderer", "LatexCompiler"]
        },
        "templates": {
            "purpose": "Visual layouts, CSS/Style definitions, and structural blueprints for documents",
            "entity_types": ["Class", "Dict"], 
            "keywords": ["template", "layout", "style", "theme", "design", "format", "css", "blueprint"],
            "imports": [], "bases": ["BaseTemplate", "ResumeLayout"], 
            "examples": ["ModernTemplate", "ClassicLayout", "ExecutiveBlueprint", "MinimalistStyle"]
        }
    },
    "apps_lic": {
        "logic_nodes": {
            "purpose": "Business logic nodes for profile analysis, connection requests, and message generation",
            "entity_types": ["Class"], 
            "keywords": ["linkedin", "lic", "node", "message", "connect", "invite", "profile", "scrutinize", "analyze"],
            "imports": ["apps_lic.logic_nodes"], 
            "bases": ["BaseNode", "LicNode", "MessagingNode"], 
            "examples": ["ConnectNode", "MessageDraftNode", "ProfileScrutinyNode", "LeadValidationNode"]
        },
        "asset_library": {
            "purpose": "Outreach scripts, message templates, connection notes, and sequence assets",
            "entity_types": ["Class", "Dict"], 
            "keywords": ["asset", "note", "message", "template", "script", "outreach", "sequence", "hook"],
            "imports": [], "bases": ["BaseAsset"], 
            "examples": ["ConnectionNotes", "FollowUpScripts", "OutreachTemplates", "MessageHooks"]
        },
        "system_flow": {
            "purpose": "Outreach campaign management, multi-step drip sequences, and cadence logic",
            "entity_types": ["Class"], 
            "keywords": ["flow", "campaign", "sequence", "cadence", "outreach", "drip", "funnel", "pipeline"],
            "imports": ["apps_lic.system_flow"], 
            "bases": ["BaseFlow", "OutreachCampaign"], 
            "examples": ["OutreachCampaign", "DailyFlow", "DripSequenceFlow", "FollowUpCadence"]
        },
        "engines": {
            "purpose": "Automated browser drivers for LinkedIn navigation and interaction",
            "entity_types": ["Class"], 
            "keywords": ["engine", "driver", "navigate", "automate", "browser", "playwright", "selenium", "scrape"],
            "imports": ["apps_lic.engines", "playwright", "selenium"], 
            "bases": ["BaseEngine", "BrowserDriver"], 
            "examples": ["NavigationEngine", "BrowserDriver", "ScrapingEngine", "InteractionDriver"]
        },
        "templates": {
            "purpose": "Message formatting schemas and campaign structural blueprints",
            "entity_types": ["Class"], 
            "keywords": ["template", "structure", "format", "blueprint", "schema"],
            "imports": [], "bases": ["BaseTemplate", "LicTemplate"], 
            "examples": ["CampaignTemplate", "MessageFormat", "OutreachBlueprint"]
        }
    },
    "apps_shared": {
        "base_definitions": {
            "purpose": "Abstract base classes, core interfaces, and type contracts shared across all application domains",
            "entity_types": ["Class", "Protocol", "TypeAlias"], 
            "keywords": ["base", "definition", "type", "shared", "interface", "abstract", "contract", "blueprint", "abc"],
            "imports": ["abc", "typing"], 
            "bases": ["ABC", "Protocol"], 
            "examples": ["BaseNode", "BaseFlow", "BaseEngine", "BaseTemplate", "BaseAsset"]
        },
        "common_utils": {
            "purpose": "Shared application-level utility functions for data manipulation, formatting, and common logic",
            "entity_types": ["Function", "Class"], 
            "keywords": ["util", "common", "shared", "helper", "date", "string", "collection", "formatter", "converter"],
            "imports": ["datetime", "re", "json"], "bases": [], 
            "examples": ["date_utils", "string_helpers", "collection_transformers", "CurrencyFormatter"]
        },
        "core_components": {
            "purpose": "Reusable architectural widgets and modular components used across multiple app flows",
            "entity_types": ["Class"], 
            "keywords": ["component", "module", "widget", "part", "element", "plugin", "extension"],
            "imports": [], "bases": ["BaseComponent"], 
            "examples": ["LoggerComponent", "ConfigLoader", "NotificationWidget", "AppPluginBase"]
        },
        "base_agents": {
            "purpose": "Shared application-level agent templates and worker base classes",
            "entity_types": ["Class"], 
            "keywords": ["agent", "base_agent", "worker", "bot", "task_executor", "app_worker"],
            "imports": ["agentic_core.L3_orchestration.workflow_engines"], 
            "bases": ["CanonBaseAgent", "AppBaseAgent"], 
            "examples": ["AppBaseAgent", "TaskWorker", "AsyncAppWorker", "StatefulAppAgent"]
        },
        "models": {
            "purpose": "Shared Pydantic data models, Data Transfer Objects (DTOs), and domain-agnostic schemas",
            "entity_types": ["Class"], 
            "keywords": ["model", "dto", "data", "struct", "object", "payload", "contract", "pydantic"],
            "imports": ["pydantic"], "bases": ["BaseModel"], 
            "examples": ["UserProfile", "TaskResult", "CommonMetadata", "SharedDataPacket"]
        }
    }
}
