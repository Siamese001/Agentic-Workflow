"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth-3 for Apps/Support and Depth-4 for the Agentic Core.
[SSOT] This is the absolute source of truth for the entire repository structure.
"""

# [SOVEREIGN SSOT] THE MASTER REGISTRY
# Defines every legal territory, its subfolders (L1), and its required depth.
# This structure is derived from the canonical ASCII tree and must be kept in sync.
SOVEREIGN_REGISTRY = {
    # === THE HEAVY CORE (Depth 4: Root > Layer > Stage > File) ===
    "agentic_core": {
        "depth": 4, 
        "subfolders": [
            "L0_maintenance",     # Foundation & Support
            "L1_cognition",       # The Thought Engine
            "L2_execution",       # The Action Layer
            "L3_orchestration",   # The Manager
            "L4_state",           # The Ledger
            "L5_safety",          # The Shield
            "config",             # System Blueprints
            "prompt_governance",  # Prompt Authority
            "runtime",            # Infrastructure
            "observability",      # The Watchtower
            "utils",              # Core Helpers
            "patterns",           # Behavioral Templates
            "semantic_memory",    # Vector Context
            "knowledge"           # The Library (RAG Assets) - Anchor
        ]
    },
    
    # === APPLICATION LIMBS (Depth 3: Root > Module > File) ===
    "apps_rg": {
        "depth": 3, 
        "subfolders": ["logic_nodes", "asset_library", "system_flow"]
    },
    "apps_lic": {
        "depth": 3, 
        "subfolders": ["logic_nodes", "asset_library", "system_flow"]
    },
    "apps_shared": {
        "depth": 3, 
        "subfolders": ["base_definitions", "common_utils", "core_components"]
    },
    
    # === THE SOVEREIGN JUDGE (Depth 3: Root > Category > File) ===
    "tests": {
        "depth": 3, 
        "subfolders": ["unit", "integration", "e2e", "functional", "fixtures", "automation"]
    },
}

# === AGENTIC_CORE L2 SUBFOLDER REGISTRY (The Rule of Two/Three) ===
# Each L1 layer must contain these L2 subfolders to hit Depth 4
CORE_SUBFOLDER_MAP = {
    "L0_maintenance": ["scripts", "logs", "benchmarks"],
    "L1_cognition": ["thought_engine", "intent_analysis"],
    "L2_execution": ["tool_registry", "action_handlers"],
    "L3_orchestration": ["workflow_engines", "fission_logic"],
    "L4_state": ["validation_context", "audit_trails"],
    "L5_safety": ["guardrails", "red_teaming"],
    "config": ["blueprint_sovereign", "environments"],
    "prompt_governance": ["meta_prompts", "version_registry"],
    "runtime": ["shared_runtime", "environment_setup"],
    "observability": ["metrics", "telemetry"],
    "utils": ["core_extensions", "async_wrappers"],
    "patterns": ["agent_roles", "communication_flow"],
    "semantic_memory": ["vector_stores", "embedding_logic"],
    "knowledge": ["document_loaders", "static_index", "research_cache"]
}

# === APP L2 SUBFOLDER REGISTRIES ===
# These maps define the L2 folders that sit under the App L1s
APPS_RG_SUBFOLDER_MAP = {
    "logic_nodes": ["engines", "processors"],
    "asset_library": ["templates", "prompts"],
    "system_flow": ["pipeline", "services"]
}

APPS_LIC_SUBFOLDER_MAP = {
    "logic_nodes": ["engines", "processors"],
    "asset_library": ["report_templates", "prompts"],
    "system_flow": ["pipeline", "services"]
}

APPS_SHARED_SUBFOLDER_MAP = {
    "base_definitions": ["models", "constants"],
    "common_utils": ["helpers", "adapters"],
    "core_components": ["pipeline_abstracts", "components"]
}

# === TESTS L2 SUBFOLDER REGISTRY ===
TESTS_SUBFOLDER_MAP = {
    "unit": ["core_logic", "shared_logic"],
    "integration": ["layer_transitions", "service_contracts"],
    "e2e": ["smoke_tests", "scenarios"],
    "functional": ["resume_workflow", "license_workflow"],
    "fixtures": ["mock_data", "vcr_cassettes"],
    "automation": ["pytest_hooks", "conftest_logic"]
}

# --- BACKWARD COMPATIBILITY EXPORTS ---
AGENTIC_CORE_REGISTRY = CORE_SUBFOLDER_MAP
SOVEREIGN_DEPTH_MAP = {k: v["depth"] for k, v in SOVEREIGN_REGISTRY.items()}

# --- CANON SIGNALS: HIGH-SIGNAL KEYWORDS FOR NAMING LAW ---
# [KEY 49 ENFORCEMENT] Files must contain at least one of these keywords
CANON_SIGNALS = {
    "strategy", "reasoning", "planner", "node", "extraction", "synthesis",
    "orchestration", "fission", "hop", "router", "memory", "historian",
    "state", "cache", "safety", "guardrail", "filter", "engine",
    "compliance", "auditor", "validator", "healer", "prompt", "persona",
    "schema", "blueprint", "agent", "handler", "manager", "impl", "types"
}

# [KEY 49] FORBIDDEN NAMING PATTERNS
FORBIDDEN_PATTERNS = {
    r"^utils\.py$", r"^helper\.py$", r"^temp\.py$", r"^script\.py$",
    r"^main\.py$", r"^test\.py$", r".*_v\d+\.py$", r".*_final\.py$",
    r".*_new\.py$", r".*_old\.py$", r"^.+_\d+\.py$"
}

# --- SYSTEM EXEMPTIONS ---
ROOT_WHITELIST = list(SOVEREIGN_REGISTRY.keys()) + [
    "data", "archives", ".git", "venv", "venv_stable", "__pycache__", 
    ".pytest_cache", ".ruff_cache", "node_modules", "docs"
]

# [L6 HARDENING] Explicitly forbidden root folders (legacy/out-of-scope)
FORBIDDEN_ROOT_FOLDERS = {
    "01_runtime_logic", "02_runtime_cache", "03_scripts_logic", "04_scripts_cache",
    "05_runtime_security", "06_runtime_runtime", "07_runtime_pipeline",
    "08_shared_security", "09_shared_runtime", "10_shared_pipeline",
    "11_shared_logic", "12_shared_cache", "13_scripts_security",
    "14_scripts_runtime", "15_scripts_pipeline"
}
