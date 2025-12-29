"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth-2 for Apps/Tests and Depth-3 for the Agentic Core.
[SSOT] This is the absolute source of truth for the entire repository structure.
"""
import os
import re
from typing import Any, Dict, List, Optional, Protocol

SOVEREIGN_REGISTRY = {
    # === THE LEAN CORE (Depth 3: Root > Layer > Stage > File) ===
    "agentic_core": {
        "depth": 3, 
        "subfolders": [
            "L0_maintenance",     # Foundation & Support
            "L1_cognition",       # The Thought Engine
            "L2_execution",       # The Action Layer
            "L3_orchestration",   # The Manager
            "L4_state",           # The Ledger
            "L5_safety",          # The Shield
            "config",             # System Blueprints
            "schemas",            # Data Contracts
            "prompt_governance",  # Prompt Authority
            "runtime",            # Infrastructure
            "observability",      # The Watchtower
            "utils",              # Core Helpers
            "patterns",           # Behavioral Templates
            "semantic_memory",    # Vector Context
            "knowledge"           # The Library (RAG Assets) - Anchor
        ]
    },
    
    # === APPLICATION LIMBS (Depth 2: Root > Module > File) ===
    "apps_rg": {
        "depth": 2, 
        "subfolders": ["logic_nodes", "asset_library", "system_flow", "engines", "templates"]
    },
    "apps_lic": {
        "depth": 2, 
        "subfolders": ["logic_nodes", "asset_library", "system_flow", "engines", "templates"]
    },
    "apps_shared": {
        "depth": 2, 
        "subfolders": ["base_definitions", "common_utils", "core_components", "base_agents", "models", "utils"]
    },
    
    # === THE SOVEREIGN JUDGE (Depth 2: Root > Category > File) ===
    "tests": {
        "depth": 2, 
        "subfolders": ["unit", "integration", "e2e", "functional", "fixtures", "automation", "core", "data", "performance", "security"]
    },
}

# === AGENTIC_CORE L2 SUBFOLDER REGISTRY (The Rule of Three) ===
# Each L1 layer must contain these L2 subfolders. Files sit directly inside these.
CORE_SUBFOLDER_MAP = {
    "L0_maintenance": ["scripts", "logs", "benchmarks"],
    # - scripts: Operational tools, healers, auditors
    # - logs: Runtime log storage
    # - benchmarks: Performance measurement utilities
    
    "L1_cognition": ["thought_engine", "intent_analysis", "planning"],
    # - thought_engine: Core reasoning and thought nodes
    # - intent_analysis: User intent parsing and classification
    # - planning: Strategy and mission decomposition
    
    "L2_execution": ["tool_registry", "action_handlers", "mcp"],
    # - tool_registry: External tool definitions and wrappers
    # - action_handlers: Execution logic for discrete actions
    # - mcp: Model Context Protocol client integrations
    
    "L3_orchestration": ["workflow_engines", "fission_logic", "S3_vitality", "mcp"],
    # - workflow_engines: Multi-step coordination and routing
    # - fission_logic: File splitting and healing protocols
    # - S3_vitality: Health monitors and signal handlers
    # - mcp: MCP router and marketplace integration
    
    "L4_state": ["validation_context", "ledger", "filesystem", "memory"],
    # - validation_context: Mission context and historian
    # - ledger: Audit trails and transaction logs
    # - filesystem: Atomic file operations via MCP
    # - memory: Working memory and context buffers
    
    "L5_safety": ["guardrails", "red_teaming", "gravity", "validators"],
    # - guardrails: Safety limits and mutation controls
    # - red_teaming: Adversarial testing and threat simulation
    # - gravity: Import waterfall enforcement
    # - validators: Schema and policy validators
    
    "schemas": ["models", "messages", "types", "validators"],
    # - models: Pydantic data models
    # - messages: API request/response schemas
    # - types: Type definitions and protocols
    # - validators: Schema validation utilities
    
    "config": ["blueprint_sovereign", "environments", "feature_flags", "secrets_manager"],
    # - blueprint_sovereign: Sovereign constitution (this file)
    # - environments: Env-specific overrides
    # - feature_flags: Feature toggles
    # - secrets_manager: Credential handling
    
    "prompt_governance": ["meta_prompts", "version_registry", "rendering", "templates"],
    # - meta_prompts: System instruction templates
    # - version_registry: Prompt version tracking
    # - rendering: Dynamic prompt assembly
    # - templates: Reusable prompt fragments
    
    "runtime": ["shared_runtime", "environment_setup", "shared", "resource_management"],
    # - shared_runtime: Cross-cutting runtime utilities
    # - environment_setup: Bootstrap and initialization
    # - shared: Common runtime helpers
    # - resource_management: Memory and connection pooling
    
    "observability": ["metrics", "telemetry", "tracing", "compliance"],
    # - metrics: Prometheus/custom metric definitions
    # - telemetry: OpenTelemetry instrumentation
    # - tracing: Distributed trace context
    # - compliance: Audit and compliance reporting
    
    "utils": ["core_extensions", "wrappers", "helpers", "naming"],
    # - core_extensions: Framework extensions
    # - wrappers: Third-party library adapters
    # - helpers: General-purpose utilities
    # - naming: Naming convention enforcement
    
    "patterns": ["agent_roles", "communication_flow", "interaction_patterns", "reasoning_patterns"],
    # - agent_roles: Role definitions and personas
    # - communication_flow: Inter-agent messaging patterns
    # - interaction_patterns: Human-agent interaction templates
    # - reasoning_patterns: Chain-of-thought and reasoning templates
    
    "semantic_memory": ["store", "embeddings", "retrieval", "index"],
    # - store: Vector database interfaces (Pinecone)
    # - embeddings: Embedding generation and caching
    # - retrieval: Semantic search and RAG utilities
    # - index: Index management and optimization
    
    "knowledge": ["document_loaders", "static_index", "research_cache"],
    # - document_loaders: File parsing and ingestion
    # - static_index: Pre-built knowledge indices
    # - research_cache: External research caching
}

# === DOMAIN L2 SUBFOLDER REGISTRIES (Depth 2 Enforcement) ===
# Map valid subfolders to signify leaf status at Depth 2
APPS_RG_SUBFOLDER_MAP = {
    "logic_nodes": ["node_definitions", "node_helpers"],
    # - node_definitions: Node type definitions
    # - node_helpers: Node utility functions
    
    "asset_library": ["asset_definitions", "asset_helpers"],
    # - asset_definitions: Asset type definitions
    # - asset_helpers: Asset utility functions
    
    "system_flow": ["flow_definitions", "flow_helpers"],
    # - flow_definitions: Flow type definitions
    # - flow_helpers: Flow utility functions
    
    "engines": ["engine_definitions", "engine_helpers"],
    # - engine_definitions: Engine type definitions
    # - engine_helpers: Engine utility functions
    
    "templates": ["template_definitions", "template_helpers"],
    # - template_definitions: Template type definitions
    # - template_helpers: Template utility functions
}

APPS_LIC_SUBFOLDER_MAP = {
    "logic_nodes": ["node_definitions", "node_helpers"],
    # - node_definitions: Node type definitions
    # - node_helpers: Node utility functions
    
    "asset_library": ["asset_definitions", "asset_helpers"],
    # - asset_definitions: Asset type definitions
    # - asset_helpers: Asset utility functions
    
    "system_flow": ["flow_definitions", "flow_helpers"],
    # - flow_definitions: Flow type definitions
    # - flow_helpers: Flow utility functions
    
    "engines": ["engine_definitions", "engine_helpers"],
    # - engine_definitions: Engine type definitions
    # - engine_helpers: Engine utility functions
    
    "templates": ["template_definitions", "template_helpers"],
    # - template_definitions: Template type definitions
    # - template_helpers: Template utility functions
}

APPS_SHARED_SUBFOLDER_MAP = {
    "base_definitions": ["definition_helpers", "definition_types"],
    # - definition_helpers: Definition utility functions
    # - definition_types: Definition type definitions
    
    "common_utils": ["utility_helpers", "utility_types"],
    # - utility_helpers: Utility function helpers
    # - utility_types: Utility type definitions
    
    "core_components": ["component_definitions", "component_helpers"],
    # - component_definitions: Component type definitions
    # - component_helpers: Component utility functions
    
    "base_agents": ["agent_definitions", "agent_helpers"],
    # - agent_definitions: Agent type definitions
    # - agent_helpers: Agent utility functions
    
    "models": ["model_definitions", "model_helpers"],
    # - model_definitions: Model type definitions
    # - model_helpers: Model utility functions
    
    "utils": ["utility_helpers", "utility_types"],
    # - utility_helpers: Utility function helpers
    # - utility_types: Utility type definitions
}

TESTS_L2_SUBFOLDER_MAP = {
    "unit": ["test_definitions", "test_helpers"],
    # - test_definitions: Test type definitions
    # - test_helpers: Test utility functions
    
    "integration": ["test_definitions", "test_helpers"],
    # - test_definitions: Test type definitions
    # - test_helpers: Test utility functions
    
    "e2e": ["test_definitions", "test_helpers"],
    # - test_definitions: Test type definitions
    # - test_helpers: Test utility functions
    
    "functional": ["test_definitions", "test_helpers"],
    # - test_definitions: Test type definitions
    # - test_helpers: Test utility functions
    
    "fixtures": ["fixture_definitions", "fixture_helpers"],
    # - fixture_definitions: Fixture type definitions
    # - fixture_helpers: Fixture utility functions
    
    "automation": ["automation_definitions", "automation_helpers"],
    # - automation_definitions: Automation type definitions
    # - automation_helpers: Automation utility functions
    
    "core": ["core_definitions", "core_helpers"],
    # - core_definitions: Core type definitions
    # - core_helpers: Core utility functions
    
    "data": ["data_definitions", "data_helpers"],
    # - data_definitions: Data type definitions
    # - data_helpers: Data utility functions
    
    "performance": ["performance_definitions", "performance_helpers"],
    # - performance_definitions: Performance type definitions
    # - performance_helpers: Performance utility functions
    
    "security": ["security_definitions", "security_helpers"],
    # - security_definitions: Security type definitions
    # - security_helpers: Security utility functions
}

# --- BACKWARD COMPATIBILITY EXPORTS ---
# [DEPRECATED] Use CORE_SUBFOLDER_MAP directly
AGENTIC_CORE_REGISTRY = CORE_SUBFOLDER_MAP
# [DEPRECATED] Use TESTS_L2_SUBFOLDER_MAP directly
TESTS_SUBFOLDER_MAP = TESTS_L2_SUBFOLDER_MAP
# [OBSOLETE] Removed with Depth 3 structure
CORE_L3_SUBFOLDER_MAP = {}
CORE_L4_SUBFOLDER_MAP = {}

# --- CANON SIGNALS: HIGH-SIGNAL KEYWORDS FOR NAMING LAW (Key 20) ---
CANON_SIGNALS: set[str] = {
    # Core Roles
    "agent", "manager", "engine", "validator", "healer", "auditor", "enforcer", "detector",
    "orchestrator", "coordinator", "pruner", "mapper", "handler", "guardian", "governor", "sentinel",
    # Core Concepts
    "strategy", "reasoning", "fission", "workflow", "state", "memory", "cache",
    "safety", "guardrail", "prompt", "persona", "schema", "blueprint", "template",
    "context", "ledger", "historian", "audit", "coverage",
    # Infrastructure & Compliance
    "vector", "embedding", "pinecone", "redis", "compliance", "drift", "hierarchy",
    "span", "depth", "naming", "rescue", "integrity", "gravity", "subatomic", "gemini"
}

# [KEY 20 HARDENING] FORBIDDEN NAMING PATTERNS — compiled regex list
# Rationale: Pre-compiled patterns are faster; list allows ordered matching.
# Used by Key 20 (agentic_core/utils/naming) for naming convention enforcement.
FORBIDDEN_PATTERNS = [
    re.compile(r"^utils\.py$"),
    re.compile(r"^helper\.py$"),
    re.compile(r"^temp\.py$"),
    re.compile(r".*_v\d+\.py$"),
    re.compile(r"^main\.py$"),
    re.compile(r"^test\.py$"),
    re.compile(r".*_final\.py$"),
    re.compile(r".*_new\.py$"),
    re.compile(r".*_old\.py$"),
    re.compile(r".*_copy\.py$"),
    re.compile(r".*_backup\.py$"),
    re.compile(r"^legacy_.*\.py$"),
    re.compile(r"^.+_\d+\.py$"),
    re.compile(r"^draft_.*\.py$")
]

# ==============================================================================
# CANON KEY CONSTITUTION [SSOT] - Final Sovereign Seal (Dec 24, 2025)
# ==============================================================================
ACTIVE_CANON_KEYS = list(range(0, 22))

CANON_KEY_TO_FOLDER_MAP: Dict[int, List[str]] = {
    0:  [".",],  # Root-level files only
    1:  ["agentic_core/prompt_governance"],
    7:  ["agentic_core/schemas"],
    11: ["agentic_core/L1_cognition"],
    12: ["agentic_core/L3_orchestration"],
    13: ["agentic_core/L4_state"],
    19: ["agentic_core/L5_safety"],
    20: ["agentic_core/L0_maintenance", "agentic_core/utils/naming", "agentic_core/observability/compliance"],
    21: ["agentic_core/L2_execution", "agentic_core/patterns", "agentic_core/semantic_memory", "agentic_core/knowledge"],
    14: ["apps_shared", "apps_rg", "apps_lic"],
    15: ["apps_rg/agents", "apps_lic/agents"],
    16: ["apps_shared/utils"],
    17: ["tests"]
}

# [L6 MCP CAPABILITIES SSOT] Modular Capability Provider Configuration
# Rationale: Formalizes the state of external tool integrations.
# Current Status (v2.9): All MCPs active for enhanced tooling capabilities.
MCP_CAPABILITIES = {
    "router": {
        "enabled": True,  # SovereignMCPRouter for tool routing
        "path": "agentic_core.L3_orchestration.mcp"
    },
    "marketplace_filter": {
        "enabled": True,
        "path": "agentic_core.L3_orchestration.mcp"
    },
    "filesystem": {
        "enabled": True,
        "path": "agentic_core.L4_state.filesystem"
    },
    "figma": {
        "enabled": True,
        "path": "agentic_core.L2_execution.mcp"
    },
    "fetch": {
        "enabled": True,
        "path": "agentic_core.L2_execution.mcp"
    },
    "semantic_cache": {
        "enabled": True,
        "path": "agentic_core.L2_execution.mcp"
    }
}

# [GAP 16] ROOT PROTECTED FILES — SSOT centralized
ROOT_PROTECTED_FILES = {
    "canon_validator_agentic_v2.py", "pyproject.toml", "README.md", 
    "langgraph.json", ".env", "windsurfrules.md", ".gitignore"
}

# [L6 SOVEREIGN EXCLUSIONS SSOT] All folders that must be ignored/skipped globally
# Rationale: Prevents span-of-two noise, depth false positives, and resource exhaustion (WinError 1450)
SOVEREIGN_EXCLUDED_FOLDERS: frozenset[str] = frozenset({
    # System / Tooling
    ".git", ".venv", "venv", "venv_stable", "__pycache__", 
    ".pytest_cache", ".ruff_cache", "node_modules", ".mypy_cache", ".tox",
    # Legacy / Archive
    "archives", "legacy_code", "legacy_engines", "legacy_resume_gen",
    # Data / Non-Code
    "data", "docs", "env", "build", "dist", "_build",
    # Venv / Pip Noise (Span-of-Two False Positives)
    "Lib", "site-packages", "google", "gapic", "logging", "licenses", 
    "src", "pip", "dist-info", "raw", "golden_state", "logs", "processed", 
    "shared", "refs", "remotes", "v",
    # [L6 NOISE SUPPRESSION] Transient & Healing Artifacts
    "stubs", ".sovereign_healing_backup", ".idea", ".vscode",
    # System
    ".DS_Store", "Thumbs.db"
})

# [L6 HARDENING] FORBIDDEN_FOLDER_PATTERNS — regex + static set
# Rationale: Catch all numbered folder prefixes (e.g., "08_*") anywhere in tree
FORBIDDEN_FOLDER_PATTERN = re.compile(r"^\d+_")  # Matches any folder starting with digits + underscore

# Static list of known legacy folders (for backward compat and explicit blocking)
FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset({
    "legacy_code", "legacy_engines", "legacy_resume_gen", "old_core"
})

# Backward compatibility exports - migrate all references to use the SSOT above
PROTECTED_FOLDERS = SOVEREIGN_EXCLUDED_FOLDERS  # Legacy name
IGNORE_DIRS = SOVEREIGN_EXCLUDED_FOLDERS          # For void_compliance span check
SOVEREIGN_IGNORED_FOLDERS = SOVEREIGN_EXCLUDED_FOLDERS  # Temporary alias for migration

# [L6 TESTS WHITELIST SSOT] Files allowed at depth 1 in tests/ (pytest requirement)
TESTS_ROOT_FILE_WHITELIST: frozenset[str] = frozenset({
    "conftest.py",
    "sovereign_smoke_test.py",
    "test_autonomous_improvements.py",
    # Add future root-level pytest config files here
})

# [L6 AUTONOMOUS WHITELIST SSOT] Self-healing agents allowed outside strict L2 mapping
AUTONOMOUS_AGENT_WHITELIST: frozenset[str] = frozenset({
    "autonomous_checkpoint_manager.py",
    "autonomous_state_guardian.py",
    "self_updating_safety_engine.py",
    "neural_auto_immune_agent.py"
})

# [L6 HEALING CONFIGURATION SSOT] Centralized healing budget parameters
HEALING_CONFIG = {
    "max_rounds": int(os.getenv('MAX_HEALING_ROUNDS', '10')),
    "max_per_file": int(os.getenv('MAX_HEALING_PER_FILE', '8')),
    "global_budget": int(os.getenv('GLOBAL_HEALING_BUDGET', '50'))
}

# [L6 AGENT RESILIENCE SSOT] Retry and backoff configuration
AGENT_RESILIENCE_CONFIG = {
    "retry_count": int(os.getenv("AGENT_RETRY_COUNT", "3")),
    "backoff_base": float(os.getenv("AGENT_RETRY_BACKOFF_BASE", "0.5"))
}

# [L6 SCOPE DISPLAY EXCLUSIONS] Folders hidden from scope summary output
SCOPE_SUMMARY_EXCLUSIONS: frozenset[str] = frozenset({
    "stubs", ".sovereign_healing_backup", "__pycache__"
})

# [L6 PYTHON STDLIB REFERENCE] Standard library modules for import validation
PYTHON_STDLIB_MODULES: frozenset[str] = frozenset({
    "os", "sys", "pathlib", "logging", "asyncio", "typing", "dataclasses",
    "collections", "json", "re", "datetime", "functools", "itertools",
    "abc", "enum", "contextlib", "threading", "time", "random", "math",
    "urllib", "http", "socket", "subprocess", "shutil", "hashlib", "uuid",
    "copy", "io", "traceback", "inspect", "importlib", "warnings", "pickle"
})

# [L6 MISSION CONTROLS SSOT] Global behavioral toggles
MISSION_CONFIG = {
    "gravity_surgery_enabled": True,            # Upstream → downstream import ban
    "hierarchy_healing_enabled": True,          # Auto-move files to correct depth/L2
    "span_surgery_enabled": True,               # Flatten redundant tunnels
    "fission_enabled": True,                    # Split large files
    "run_full_mission": True,                   # False = validation-only mode
    # [SURGERY FLAGS] High-risk mutation controls (disabled by default)
    "run_hierarchy_healing": False,             # [RISK: HIGH] Physical file relocation
    "run_gravity_refactor": False,              # [RISK: CRITICAL] LLM-based import refactoring
    "run_sprawl_surgery": False,                # [RISK: MEDIUM] Merge redundant folders
    "structural_only_mode": False,              # [RISK: LOW] Rule-based healing only
    # [TIMEOUT] Mission execution limit
    "timeout_seconds": int(os.getenv("MISSION_TIMEOUT_SECONDS", "1800"))
}

# [L6 DISCOVERY SSOT] Territories excluded from 50-key architectural discovery
# Rationale: Prevents ast.parse/import failures on legacy/example code.
DISCOVERY_EXCLUDED_TERRITORIES: frozenset[str] = frozenset({
    "runtime_shared",   # Contains broken examples (multi_provider_clients, etc.)
    "legacy_code",      # Archived code
    "legacy_engines",
    "archives",
    "stubs",            # Type stubs
    "examples",
})

# --- SYSTEM EXEMPTIONS ---
# [L6 HARDENING] ROOT_WHITELIST → derived directly from SOVEREIGN_REGISTRY keys
# Rationale: Single Source of Truth — only roots defined in SOVEREIGN_REGISTRY are allowed.
# Any other folders (scripts, config, schemas, prompt_governance) are subfolders of agentic_core.
ROOT_WHITELIST: set[str] = set(SOVEREIGN_REGISTRY.keys())
# Explicit approved roots: agentic_core, apps_rg, apps_lic, apps_shared, tests

# [L6 GRAVITY SSOT] Single Source of Truth for Gravity Surgery (Waterfall Enforcement)
# Rationale: Upstream sovereign roots (core brain) MUST NOT import from downstream domains (apps, tests).
# This prevents core contamination while allowing downstream to depend on core.
GRAVITY_CONFIG = {
    "enabled": False,  # Master toggle — set False to disable all gravity enforcement
    "upstream_sovereign_roots": [
        "agentic_core",            # The eternal brain — highest authority
        # Add future sovereign cores here (e.g., "prompt_governance", "schemas")
    ],
    "downstream_domains": [
        "apps_rg",
        "apps_lic",
        "apps_shared",
        "tests",
        # Add future downstream roots here
    ],
    "exemptions": [                # Allowed bidirectional flows (rare, justified)
        # Example: "agentic_core/utils" → "apps_shared" if truly shared runtime
    ]
}

# Backward compatibility — temporary bridge until full migration
GRAVITY_SURGERY_ENABLED = GRAVITY_CONFIG["enabled"]
UPSTREAM_SOVEREIGN_ROOTS = frozenset(GRAVITY_CONFIG["upstream_sovereign_roots"])
DOWNSTREAM_ROOTS = frozenset(GRAVITY_CONFIG["downstream_domains"])