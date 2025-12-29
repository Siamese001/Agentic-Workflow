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
            "purpose": "Safety limits, mutation controls, deletion guards, and circuit breakers",
            "entity_types": ["Class"], "keywords": ["guardrail", "safety", "limit", "constraint", "circuit", "breaker", "throttle"],
            "imports": ["agentic_core.L5_safety.guardrails"], "bases": ["SafetyGuardrail", "BaseGuardrail"]
        },
        "red_teaming": {
            "purpose": "Adversarial testing, threat simulation, exploit probing, and attack vectors",
            "entity_types": ["Class", "Function"], "keywords": ["redteam", "red_team", "adversary", "attack", "exploit", "probe", "jailbreak", "threat"],
            "imports": [], "bases": ["RedTeamAgent"]
        },
        "gravity": {
            "purpose": "Import waterfall enforcement, dependency direction control, and layer authority",
            "entity_types": ["Function", "Class"], "keywords": ["gravity", "waterfall", "import", "dependency", "layer", "authority"],
            "imports": ["agentic_core.runtime.shared_runtime.void_compliance"], "bases": []
        },
        "validators": {
            "purpose": "Canon key validators, structural checks, and policy enforcement",
            "entity_types": ["Class"], "keywords": ["validator", "canon", "key", "rule", "policy", "enforce", "compliance"],
            "imports": [], "bases": ["CanonBaseAgent", "KeyValidator"]
        }
    },
    "L1_cognition": {
        "thought_engine": {
            "purpose": "Core reasoning primitives, thought nodes, chain-of-thought execution, and internal monologue structures",
            "entity_types": ["Class", "Protocol"],
            "keywords": ["thought", "reason", "node", "chain", "cot", "monologue", "step", "decompose", "analyze", "reflect", "critique", "socratic", "deliberate", "ponder", "contemplate"],
            "imports": ["agentic_core.L1_cognition.thought_engine", "pydantic"],
            "bases": ["ThoughtNode", "ReasoningStep", "BaseThought", "ChainOfThought", "BaseReasoningEngine"],
            "examples": ["ReasoningNode", "CritiqueStep", "ReflectionThought", "ChainOfThoughtExecutor", "SocraticReasoner"]
        },
        "intent_analysis": {
            "purpose": "User intent detection, goal extraction, request classification, and ambiguity resolution",
            "entity_types": ["Class", "Function"],
            "keywords": ["intent", "goal", "objective", "request", "classify", "detect", "extract", "parse", "understand", "ambiguity", "user_goal", "task_type", "command", "query_type"],
            "imports": ["agentic_core.L1_cognition.intent_analysis", "google.generativeai", "re"],
            "bases": ["IntentClassifier", "GoalExtractor", "RequestParser"],
            "examples": ["IntentClassifier", "GoalDecomposer", "AmbiguityResolver", "UserRequestParser", "TaskTypeDetector"]
        },
        "planning": {
            "purpose": "Mission decomposition, strategy formulation, step sequencing, dependency mapping, and plan validation",
            "entity_types": ["Class", "Function"],
            "keywords": ["plan", "strategy", "decompose", "sequence", "step", "task", "subtask", "dependency", "order", "validate", "breakdown", "hierarchy", "outline", "roadmap", "execute_order"],
            "imports": ["agentic_core.L1_cognition.planning", "networkx", "pydantic"],
            "bases": ["Planner", "DecompositionEngine", "PlanValidator", "StrategyBuilder", "BasePlanner"],
            "examples": ["MissionDecomposer", "TaskSequencer", "DependencyResolver", "PlanValidator", "StrategicPlanner", "StepHierarchyBuilder"]
        }
    },
    "L2_execution": {
        "tool_registry": {
            "purpose": "External tool definitions, wrappers, and registration",
            "entity_types": ["Class"], "keywords": ["tool", "wrapper", "browser", "search", "scrape", "client", "api"],
            "imports": ["selenium", "playwright", "requests"], "bases": ["BaseTool"]
        }
    },
    "L3_orchestration": {
        "workflow_engines": {
            "purpose": "Agent orchestration, task routing, and mission lifecycle management",
            "entity_types": ["Class"], "keywords": ["agent", "manager", "orchestrator", "workflow", "engine", "planner"],
            "imports": [], "bases": ["CanonBaseAgent"]
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
    
    # === APPLICATION DOMAINS ===
    "apps_rg": {
        "logic_nodes": {
            "purpose": "Business logic nodes specific to resume generation workflows",
            "entity_types": ["Class"], "keywords": ["resume", "cv", "node", "section", "experience", "education", "skill"],
            "imports": ["apps_rg.logic_nodes"], "bases": ["BaseNode", "ResumeNode"], "examples": ["ExperienceNode", "SkillExtractNode"]
        },
        "asset_library": {
            "purpose": "Static assets, strings, and resource definitions for resumes",
            "entity_types": ["Class", "Dict"], "keywords": ["asset", "string", "text", "resource", "copy", "wording"],
            "imports": [], "bases": [], "examples": ["ResumeAssets", "ActionVerbs"]
        },
        "system_flow": {
            "purpose": "Orchestration flows and pipelines for resume creation",
            "entity_types": ["Class"], "keywords": ["flow", "pipeline", "sequence", "generate", "create", "process"],
            "imports": [], "bases": ["BaseFlow"], "examples": ["GenerationFlow", "ReviewPipeline"]
        },
        "engines": {
            "purpose": "Core drivers for resume rendering and export",
            "entity_types": ["Class"], "keywords": ["engine", "render", "export", "pdf", "docx", "builder"],
            "imports": [], "bases": ["BaseEngine"], "examples": ["PdfEngine", "DocxBuilder"]
        },
        "templates": {
            "purpose": "Visual templates and layout definitions for resumes",
            "entity_types": ["Class", "Dict"], "keywords": ["template", "layout", "style", "theme", "design", "format"],
            "imports": [], "bases": ["BaseTemplate"], "examples": ["ModernTemplate", "ClassicLayout"]
        }
    },
    "apps_lic": {
        "logic_nodes": {
            "purpose": "Business logic nodes for LinkedIn interaction and messaging",
            "entity_types": ["Class"], "keywords": ["linkedin", "lic", "node", "message", "connect", "invite", "profile"],
            "imports": ["apps_lic.logic_nodes"], "bases": ["BaseNode", "LicNode"], "examples": ["ConnectNode", "MessageDraftNode"]
        },
        "asset_library": {
            "purpose": "Message templates, connection notes, and outreach assets",
            "entity_types": ["Class", "Dict"], "keywords": ["asset", "note", "message", "template", "script", "outreach"],
            "imports": [], "bases": [], "examples": ["ConnectionNotes", "FollowUpScripts"]
        },
        "system_flow": {
            "purpose": "Campaign flows and outreach sequences",
            "entity_types": ["Class"], "keywords": ["flow", "campaign", "sequence", "cadence", "outreach", "drip"],
            "imports": [], "bases": ["BaseFlow"], "examples": ["OutreachCampaign", "DailyFlow"]
        },
        "engines": {
            "purpose": "Drivers for LinkedIn automation and navigation",
            "entity_types": ["Class"], "keywords": ["engine", "driver", "navigate", "automate", "browser"],
            "imports": ["selenium", "playwright"], "bases": ["BaseEngine"], "examples": ["NavigationEngine", "BrowserDriver"]
        },
        "templates": {
            "purpose": "Structure definitions for messages and campaigns",
            "entity_types": ["Class"], "keywords": ["template", "structure", "format", "blueprint"],
            "imports": [], "bases": ["BaseTemplate"], "examples": ["CampaignTemplate", "MessageFormat"]
        }
    },
    "apps_shared": {
        "base_definitions": {
            "purpose": "Base classes and types shared across all apps",
            "entity_types": ["Class", "TypeAlias"], "keywords": ["base", "definition", "type", "shared", "interface", "abstract"],
            "imports": ["abc"], "bases": ["ABC"], "examples": ["BaseNode", "BaseFlow"]
        },
        "common_utils": {
            "purpose": "Shared utilities specific to application business logic",
            "entity_types": ["Function", "Class"], "keywords": ["util", "common", "shared", "helper", "date", "string"],
            "imports": [], "bases": [], "examples": ["date_utils", "string_helpers"]
        },
        "core_components": {
            "purpose": "Reusable architectural components for apps",
            "entity_types": ["Class"], "keywords": ["component", "module", "widget", "part", "element"],
            "imports": [], "bases": [], "examples": ["LoggerComponent", "ConfigLoader"]
        },
        "base_agents": {
            "purpose": "Base agent definitions extended by specific apps",
            "entity_types": ["Class"], "keywords": ["agent", "base_agent", "worker", "bot"],
            "imports": [], "bases": ["CanonBaseAgent"], "examples": ["AppBaseAgent", "TaskWorker"]
        },
        "models": {
            "purpose": "Shared data models and DTOs for application domains",
            "entity_types": ["Class"], "keywords": ["model", "dto", "data", "struct", "object"],
            "imports": ["pydantic"], "bases": ["BaseModel"], "examples": ["UserProfile", "TaskResult"]
        }
    }
}
