"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth-3 for Apps/Support and Depth-4 for the Agentic Core.
[SSOT] This is the absolute source of truth for the entire repository structure.
"""
import re
from typing import Any, Dict, List, Optional, Protocol

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
    
    # === APPLICATION LIMBS (Depth 3: Root > Module > File) ===
    "apps_rg": {
        "depth": 3, 
        "subfolders": ["P1_core", "logic_nodes", "asset_library", "system_flow", "engines", "templates"]
    },
    "apps_lic": {
        "depth": 3, 
        "subfolders": ["P1_core", "logic_nodes", "asset_library", "system_flow", "engines", "templates"]
    },
    "apps_shared": {
        "depth": 3, 
        "subfolders": ["P1_core", "base_definitions", "common_utils", "core_components", "base_agents", "models", "utils"]
    },
    
    # === THE SOVEREIGN JUDGE (Depth 3: Root > Category > File) ===
    "tests": {
        "depth": 3, 
        "subfolders": ["unit", "integration", "e2e", "functional", "fixtures", "automation", "core", "data", "performance", "security"]
    },
}

# === AGENTIC_CORE L2 SUBFOLDER REGISTRY (The Rule of Two/Three) ===
# Each L1 layer must contain these L2 subfolders to hit Depth 4
CORE_SUBFOLDER_MAP = {
    "L0_maintenance": ["P1_core", "scripts", "logs", "benchmarks"],
    "L1_cognition": ["P1_core", "thought_engine", "intent_analysis", "planning"],
    "L2_execution": ["P1_core", "tool_registry", "action_handlers"],
    "L3_orchestration": ["P1_core", "workflow_engines", "fission_logic"],
    "L4_state": ["P1_core", "validation_context", "audit_trails", "ledger", "checkpoints"],
    "L5_safety": ["P1_core", "guardrails", "red_teaming"],
    "schemas": ["P1_core", "models", "requests", "responses", "types", "validators"],
    "config": ["P1_core", "blueprint_sovereign", "environments", "feature_flags", "secrets_manager"],
    # [DEPTH 4 FIX] Authorized config territories:
    # - blueprint_sovereign: Sovereign constitution
    # - environments: Env-specific overrides
    # - feature_flags: Feature toggles
    # - secrets_manager: Credential handling
    "prompt_governance": ["P1_core", "meta_prompts", "version_registry", "rendering", "templates", "versioning"],
    "runtime": ["P1_core", "shared_runtime", "environment_setup", "shared", "resource_management"],
    "observability": ["P1_core", "metrics", "telemetry", "schemas", "tracing"],
    "utils": ["P1_core", "core_extensions", "async_wrappers", "decorators", "formatters", "helpers", "naming"],
    "patterns": ["P1_core", "agent_roles", "communication_flow", "interaction_patterns", "reasoning_patterns"],
    "semantic_memory": ["P1_core", "vector_stores", "embedding_logic", "embeddings", "retrieval_logic", "vector_store"],
    "knowledge": ["P1_core", "document_loaders", "static_index", "research_cache"]
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

# === AGENTIC_CORE L3 SUBFOLDER REGISTRY ===
# Specialized territories under L2 folders
CORE_L3_SUBFOLDER_MAP = {
    # L3 under fission_logic
    "fission_logic": ["healing", "pruning", "registry", "protocol"],
    # L3 under workflow_engines
    "workflow_engines": ["coordinator", "router", "hop"],
    # L3 under L4_state (Depth 4 Enforcement)
    "validation_context": ["historian", "cache", "ledger"],
    # L3 under schemas (Depth 4 Enforcement)
    "models": ["core", "domain"],
    "requests": ["api", "internal"],
    "responses": ["api", "internal"]
}

# [L4 ENFORCEMENT] Required Depth 4 specialized territories
CORE_L4_SUBFOLDER_MAP = {
    # L3: fission_logic -> L4 specialization
    "healing": ["territory", "semantic", "scripts", "recursive"],
    "protocol": ["handshake"],
    "registry": ["subatomic"],
    
    # L3: workflow_engines -> L4 specialization
    "coordinator": ["multi_hop"],
    "router": ["task"],

    # L3: state_engines -> L4 specialization
    "vector": ["pinecone", "hybrid"],
    "cache": ["redis", "sovereign"],
    
    # L3: guardrails -> L4 specialization
    "policy": ["gemini", "neural"]
}

# --- BACKWARD COMPATIBILITY EXPORTS ---
AGENTIC_CORE_REGISTRY = CORE_SUBFOLDER_MAP
# [L6 ULTIMATE HARDENING] All depth requirements are now derived EXCLUSIVELY from SOVEREIGN_REGISTRY["depth"]
# Rationale: Eliminates duplicate constants that cause drift and NameError crashes in void_compliance.py
# CANONICAL_PRECISION_DEPTH, APPS_EXACT_DEPTH, TESTS_EXACT_DEPTH are DEPRECATED and REMOVED.
# void_compliance.py now uses SOVEREIGN_REGISTRY directly → single source of truth.

# Keep AGENTIC_CORE_EXACT_DEPTH only for backward compatibility in void_compliance (temporary bridge)
# It will be removed in next hardening cycle once void_compliance is fully refactored.
AGENTIC_CORE_EXACT_DEPTH = 4  # Legacy export — will be deleted after full migration

# [DEPRECATION NOTICE] The following constants are obsolete:
# - CANONICAL_PRECISION_DEPTH (duplicate of SOVEREIGN_REGISTRY["depth"])
# - APPS_EXACT_DEPTH (use SOVEREIGN_REGISTRY["apps_rg"]["depth"])
# - TESTS_EXACT_DEPTH (use SOVEREIGN_REGISTRY["tests"]["depth"])
# They have been removed to enforce SSOT and prevent future drift.

# Safe deprecation territory — outside active keys
DEPRECATION_ARCHIVE = "archives/deprecated_code"

# Semantic index metadata for known territories
TERRITORY_EXAMPLES = {
    "agentic_core/L1_cognition": "strategy planning reasoning mission decomposition",
    "agentic_core/L3_orchestration": "fission orchestration routing workflow manager",
    "agentic_core/L4_state": "memory cache pinecone redis historian audit",
    "agentic_core/L5_safety": "guardrail safety policy enforcer filter",
    "apps_rg/agents": "resume ranking narrative scoring jd match",
    "apps_lic/agents": "license compliance workflow validation",
    "apps_shared/utils": "shared helper validation adapter",
    "scripts": "operational tool cli integrity backup deploy",
}

# [L6 HARDENING] TERRITORY_POSITIVE_SIGNALS → CANON_SIGNALS_MK2
# Renamed and hardened to prevent naming drift.
# Now used exclusively by NamingLawHealerAgent and KeyCoverageAuditorAgent.
# Expanded with missing high-signal terms to reduce false negatives in Key 49 enforcement.
CANON_SIGNALS_MK2 = {
    0:  ["canon", "validator", "orchestrator", "sovereign", "constitution", "windsurf", "blueprint", "compliance"],
    1:  ["prompt", "persona", "instruction", "directive", "system_prompt", "meta_prompt", "governance", "template"],
    11: ["strategy", "reasoning", "planner", "decomposition", "intent", "mission", "cognition", "thought", "synthesis", "analysis"],
    12: ["orchestration", "fission", "workflow", "router", "hop", "coordinator", "healer", "pruner", "mapper", "registry", "governor"],
    13: ["state", "memory", "cache", "historian", "audit", "ledger", "persistence", "vector", "pinecone", "redis", "embedding", "context"],
    15: ["resume", "ranking", "narrative", "scoring", "compliance", "license", "specialist", "generator", "processor", "workflow"],
    17: ["test", "unit", "integration", "e2e", "functional", "fixture", "mock", "scenario", "pytest", "assertion"],
    18: ["script", "tool", "cli", "operational", "integrity", "backup", "deploy", "maintenance", "guardian", "rescue"],
    19: ["safety", "guardrail", "filter", "enforcer", "shield", "policy", "gravity", "neural", "subatomic", "gemini", "sentinel"],
    20: ["drift", "audit", "coverage", "naming", "compliance", "monitor", "detector", "aggregator", "hierarchy", "span", "depth"]
}

# Backward compatibility export — will be removed in next cycle
TERRITORY_POSITIVE_SIGNALS = CANON_SIGNALS_MK2

# [SOVEREIGN BOOTSTRAP] Auto-populate Pinecone index on first run
def bootstrap_territory_index():
    """
    Sovereign bootstrap – embeds TERRITORY_EXAMPLES into Pinecone using canonical store.
    Idempotent and safe for multiple runs.
    """
    import hashlib
    
    try:
        from agentic_core.semantic_memory.vector_stores.pinecone_pinecone_store import SovereignPineconeStore
        # Assumes basic embedding logic exists in the mapped territory
        from agentic_core.semantic_memory.embedding_logic.core_embedder import get_embedding 
        
        store = SovereignPineconeStore()
        vectors = []
        for territory, example in TERRITORY_EXAMPLES.items():
            embedding = get_embedding(example)
            vectors.append({
                "id": f"territory_{hashlib.sha256(territory.encode()).hexdigest()[:16]}",
                "values": embedding,
                "metadata": {"territory": territory, "source": "sovereign_constitution"}
            })
        if vectors:
            store.upsert(vectors=vectors, namespace="territory_examples")
            print(f"   [✓] Bootstrapped {len(vectors)} territory examples to Pinecone (namespace=territory_examples)")
    except Exception as e:
        print(f"   [!] Territory bootstrap failed: {e}")

# Run on import — eternal index readiness
# Note: Commented out to avoid auto-execution on import
# bootstrap_territory_index()

# --- CANON SIGNALS: HIGH-SIGNAL KEYWORDS FOR NAMING LAW (Key 49) ---
# [L6 HARDENING] Expanded and deduplicated set → now flat list for O(1) lookup
# Rationale: Previous dict caused unnecessary nesting; flat set is faster and clearer.
# All terms from CANON_SIGNALS_MK2 are merged here for global naming law enforcement.
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

# [KEY 49 HARDENING] FORBIDDEN NAMING PATTERNS — compiled regex list
# Rationale: Pre-compiled patterns are faster; list allows ordered matching.
# Added missing dangerous patterns (e.g., copy, backup, legacy).
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
    # Root + Operational [GAP 5]
    0:  [".", "scripts"],
    # Prompt Governance (Full Tree)
    1:  ["prompt_governance"],
    # Schemas (Full Tree)
    7:  ["schemas"],
    # Sovereign Core (The Brain)
    11: ["agentic_core/L1_cognition", "agentic_core/L1_cognition/thought_engine"],
    12: ["agentic_core/L3_orchestration", "agentic_core/L3_orchestration/healing", "agentic_core/L3_orchestration/registry"],
    13: ["agentic_core/L4_state"],
    # The Shield (Safety Layer) [GAP 2+3]
    19: ["agentic_core/L5_safety", "agentic_core/L5_safety/gravity"],
    # Support & Infrastructure Layers [GAP 9]
    20: ["agentic_core/L0_maintenance", "agentic_core/utils/naming", "agentic_core/observability/compliance"],
    # Execution & Pattern Layers [GAP 11]
    21: ["agentic_core/L2_execution", "agentic_core/patterns", "agentic_core/semantic_memory", "agentic_core/knowledge"],
    # Domain & Shared Infrastructure
    14: ["apps_shared", "apps_rg", "apps_lic"],
    15: ["apps_rg/agents", "apps_lic/agents"],
    16: ["apps_shared/utils"],
    17: ["tests"]
}

# [FINAL REGISTRY] CANON AGENT REGISTRY (Mandatory Framework Population)
CANON_AGENT_REGISTRY = {
    12: ["FissionManager", "ArchitectureGovernor", "AgentRegistryValidatorAgent", 
         "RecursiveSpanHealerAgent", "ScriptsConsolidatorAgent", "TerritoryHealerAgent", 
         "SemanticTerritoryMapperAgent", "DeadCodePrunerAgent"],
    13: ["MissionHistorian", "KeyCoverageAuditorAgent"],
    18: ["PreCommitGuardianAgent"],
    19: ["SafetyGuardrail", "SubAtomicEngine", "RedSentinel", "GeminiPolicyEnforcerAgent", "GravityEnforcerAgent"],
    20: ["DriftDetectorAgent", "NamingLawHealerAgent", "GlobalComplianceAggregatorAgent"]
}

# [GAP 16] ROOT PROTECTED FILES — SSOT centralized
ROOT_PROTECTED_FILES = {
    "canon_validator_agentic_v2.py", "pyproject.toml", "README.md", 
    "langgraph.json", ".env", "windsurfrules.md", ".gitignore"
}

# [L6 HARDENING] FORBIDDEN_ROOT_FOLDERS → frozen set + expanded legacy coverage
# Rationale: frozenset is immutable and hashable; prevents accidental mutation.
# Expanded to catch all known legacy numbered patterns.
FORBIDDEN_ROOT_FOLDERS: frozenset[str] = frozenset({
    "01_runtime_logic", "02_runtime_cache", "03_scripts_logic", "04_scripts_cache",
    "05_runtime_security", "06_runtime_runtime", "07_runtime_pipeline",
    "08_shared_security", "09_shared_runtime", "10_shared_pipeline",
    "11_shared_logic", "12_shared_cache", "13_scripts_security",
    "14_scripts_runtime", "15_scripts_pipeline",
    # Additional legacy patterns observed in wild
    "legacy_code", "legacy_engines", "legacy_resume_gen", "old_core"
})

# [SOVEREIGNTY HARDENING] SOVEREIGN_IGNORED_FOLDERS (SSOT)
# The immutable blacklist of folders that must NEVER be entered, scanned, or validated.
# Prevents resource exhaustion (WinError 1450), recursion loops, and noise.
SOVEREIGN_IGNORED_FOLDERS: frozenset[str] = frozenset({
    # Version Control & Metadata
    ".git", ".svn", ".hg", "refs", "remotes",
    # Python Environments & Caches
    ".venv", "venv", "venv_stable", "env", "__pycache__",
    ".pytest_cache", ".ruff_cache", ".mypy_cache", ".tox",
    # Dependencies (Noise)
    "node_modules", "site-packages", "Lib", "dist-info",
    "google", "gapic", "logging", # Common large/deep dependency folders
    # Data & Artifacts
    "archives", "data", "logs", "processed", "golden_state", "shared",
    "build", "dist",
    # Legacy & Dead Code
    "legacy_code", "legacy_engines", "legacy_resume_gen",
    # Documentation (if not part of knowledge base)
    "docs", "_build",
    # System
    ".DS_Store", "Thumbs.db"
})

# --- SYSTEM EXEMPTIONS ---
# [L6 HARDENING] ROOT_WHITELIST → derived set for immutability and speed
# Rationale: List → set conversion on import is wasteful; define as set directly.
# Added missing system folders to prevent false positives.
ROOT_WHITELIST: set[str] = {
    # Sovereign active roots
    "agentic_core", "apps_rg", "apps_lic", "apps_shared", "tests",
    # System & environment
    # NOTE: System exclusion is now handled by SOVEREIGN_IGNORED_FOLDERS.
    # ROOT_WHITELIST now strictly contains ALLOWED roots + necessary root-level exceptions.
    "scripts", "config", "schemas", "prompt_governance"
}

# Legacy mapping for backward compatibility (internal remap)
_LEGACY_KEY_REMAP = {
    11: 1, 12: 2, 21: 3, 24: 4, 26: 5, 28: 6,
    31: 7, 33: 8, 36: 9, 38: 10,
    40: 11, 42: 12, 51: 13,
    43: 14, 44: 15, 45: 16,
    47: 17, 50: 18,
}