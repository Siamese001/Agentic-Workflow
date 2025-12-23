"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth = 3 for Core and Apps, and Depth = 2 for the DMZ (Tests).
"""

# --- AGENTIC CORE (The Brain) ---
# Forced Depth 3: Every L2 folder MUST contain these L3 subfolders.
AGENTIC_CORE_REGISTRY = {
    "L0_maintenance": ["P1_core", "scripts", "migrations", "benchmarks"],
    "L1_cognition": ["P1_core", "thought_engine", "intent_analysis", "planning_logic"],
    "L2_execution": ["P1_core", "tool_registry", "action_handlers", "sandbox"],
    "L3_orchestration": ["P1_core", "workflow_engines", "handoff_logic", "event_bus"],
    "L4_state": ["P1_core", "persistence_layer", "session_manager", "checkpoints"],
    "L5_safety": ["P1_core", "guardrails", "red_teaming", "audit_logs"],
    "config": ["P1_core", "environments", "secrets_manager", "feature_flags"],
    "observability": ["P1_core", "logging", "telemetry", "tracing"],
    "prompt_governance": ["P1_core", "templates", "versioning", "rendering"],
    "schemas": ["P1_core", "validators", "types", "models"],
    "utils": ["P1_core", "helpers", "decorators", "formatters"],
    "runtime": ["P1_core", "environment_setup", "resource_management"],
    "semantic_memory": ["P1_core", "vector_store", "retrieval_logic", "embeddings"],
    "knowledge": ["P1_core", "document_loaders", "static_index"],
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
