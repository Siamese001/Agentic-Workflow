"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth = 3 for Core and Apps, and Depth = 2 for the DMZ (Tests).
"""

# --- AGENTIC CORE (The Brain) ---
# Forced Depth 3: Every L2 folder MUST contain these L3 subfolders.
AGENTIC_CORE_REGISTRY = {
    "L0_maintenance": ["scripts", "logs", "benchmarks"],
    "L1_cognition": ["thought_engine", "semantic_memory", "intent_analysis"],
    "L2_execution": ["tool_registry", "action_handlers", "sandbox"],
    "L3_orchestration": ["workflow_engines", "fission_logic", "event_bus"],
    "L4_state": ["validation_context", "audit_trails", "session_manager"],
    "L5_safety": ["guardrails", "validators", "red_teaming"],
    "config": ["P1_core", "schemas", "environments"],
    "observability": ["P1_core", "logging", "telemetry", "tracing"],
    "prompt_governance": ["P1_core", "templates", "versioning", "rendering"],
    "utils": ["P1_core", "helpers", "decorators", "formatters"],
    "runtime": ["shared", "environment_setup", "resource_management"],
    "semantic_memory": ["P1_core", "vector_store", "retrieval_logic", "embeddings"],
    "knowledge": ["document_loaders", "static_index", "research_cache"],
    "patterns": ["P1_core", "reasoning_patterns", "interaction_patterns"]
}

# --- APP TERRITORIES (The Limbs) ---
# Forced Depth 3: Ensures apps don't become dumping grounds.
APP_TERRITORY_REGISTRY = {
    "apps_rg": {
        "engines": ["P1_core"],
        "templates": ["P1_core"],
        "P1_core": ["internal_logic"]
    },
    "apps_lic": {
        "engines": ["P1_core"],
        "templates": ["P1_core"],
        "P1_core": ["internal_logic"]
    },
    "apps_shared": {
        "models": ["P1_core"],
        "utils": ["P1_core"],
        "P1_core": ["shared_logic"]
    }
}

# --- THE JUDGE (The DMZ) ---
# Forced Depth 2: Tests are structured by type.
TESTS_REGISTRY = {
    "unit": ["agentic_core", "apps_rg", "apps_lic", "apps_shared"],
    "integration": ["workflow_tests", "api_tests"],
    "fixtures": ["mock_responses", "sample_data"]
}

# --- SYSTEM EXEMPTIONS ---
# Only these are allowed at the root.
ROOT_WHITELIST = [
    "agentic_core", "apps_rg", "apps_lic", "apps_shared", 
    "tests", "data", "archives", ".git", "venv", "docs"
]
