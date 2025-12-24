"""
SOVEREIGN BRAIN: THE MASTER CONSTITUTION
Enforces Depth-3 for Apps/Support and Depth-4 for the Agentic Core.
[SSOT] This is the absolute source of truth for the entire repository structure.
"""
import re
from typing import Dict, List

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

# === AGENTIC_CORE L3 SUBFOLDER REGISTRY ===
# Specialized territories under L2 folders
CORE_L3_SUBFOLDER_MAP = {
    # L3 under fission_logic
    "fission_logic": ["healing", "pruning", "registry", "protocol"],
    # L3 under workflow_engines
    "workflow_engines": ["coordinator", "router", "hop"],
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
# [ULTIMATE FINAL HARDENING] Precision depth + general bounds + deprecation archive
CANONICAL_PRECISION_DEPTH = {
    "agentic_core": 4,   # Root > L# > Stage > File
    "apps_rg": 3,
    "apps_lic": 3,
    "apps_shared": 3,
    "tests": 3,
}

# Specific lock for the core brain
AGENTIC_CORE_EXACT_DEPTH = 4
# [ETERNAL PRECISION] All general min/max depth rules removed.
# Sovereignty is now defined by exact precision per root.

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

# [DOUBLE-LOCK] Positive signals — files with these BELONG in the territory
# [ETERNAL REFINEMENT] Territory-specific POSITIVE signals for hybrid search
# These confirm a file's belonging to a specific key territory.
TERRITORY_POSITIVE_SIGNALS = {
    # Key 0: Sovereign Root
    0: ["canon", "validator", "orchestrator", "sovereign", "constitution", "windsurf", "blueprint"],

    # Key 1: Prompt Governance
    1: ["prompt", "persona", "instructional", "directive", "system_prompt", "meta_prompt", "governance"],

    # Key 11: L1_cognition — reasoning
    11: ["strategy", "reasoning", "planner", "decomposition", "intent", "mission", "cognition", "thought", "synthesis"],

    # Key 12: L3_orchestration — workflow
    12: ["orchestration", "fission", "workflow", "router", "hop", "coordinator", "healer", "pruner", "mapper", "registry"],

    # Key 13: L4_state — persistence
    13: ["state", "memory", "cache", "historian", "audit", "ledger", "persistence", "vector", "pinecone", "redis", "embedding"],

    # Key 15: Domain Specialists
    15: ["resume", "ranking", "narrative", "scoring", "compliance", "license", "specialist", "generator", "processor"],

    # Key 17: Tests
    17: ["test", "unit", "integration", "e2e", "functional", "fixture", "mock", "scenario", "pytest"],

    # Key 18: Scripts / Operational
    18: ["script", "tool", "cli", "operational", "integrity", "backup", "deploy", "maintenance", "guardian"],

    # Key 19: L5_safety — shield
    19: ["safety", "guardrail", "filter", "enforcer", "shield", "policy", "gravity", "neural", "subatomic", "gemini"],

    # Key 20: Observability / Drift
    20: ["drift", "audit", "coverage", "naming", "compliance", "monitor", "detector", "aggregator", "hierarchy"]
}

# [SOVEREIGN BOOTSTRAP] Auto-populate Pinecone index on first run
def bootstrap_territory_index():
    """
    Called once — embeds TERRITORY_EXAMPLES into Pinecone for semantic healing.
    Safe to run multiple times (upserts).
    """
    import hashlib
    from pathlib import Path
    
    try:
        from agentic_core.L3_orchestration.healing.semantic_territory_mapper_agent import SemanticTerritoryMapperAgent
        mapper = SemanticTerritoryMapperAgent(Path("."), None)  # Dummy ctx
        vectors = []
        for territory, example in TERRITORY_EXAMPLES.items():
            embedding = mapper.get_embedding(example)
            vectors.append({
                "id": f"territory_{hashlib.sha256(territory.encode()).hexdigest()[:16]}",
                "values": embedding,
                "metadata": {"territory": territory}
            })
        if vectors:
            mapper.index.upsert(vectors=vectors)
            print(f"   [✓] Bootstrapped {len(vectors)} territory examples to Pinecone")
    except Exception as e:
        print(f"   [!] Territory bootstrap failed: {e}")

# Run on import — eternal index readiness
# Note: Commented out to avoid auto-execution on import
# bootstrap_territory_index()

# --- CANON SIGNALS: HIGH-SIGNAL KEYWORDS FOR NAMING LAW ---
# [KEY 49 ENFORCEMENT] Files must contain at least one of these keywords
CANON_SIGNALS = {
    # Core Roles
    "agent", "manager", "engine", "validator", "healer", "auditor", "enforcer", "detector",
    "orchestrator", "coordinator", "pruner", "mapper", "handler", "guardian",
    # Core Concepts
    "strategy", "reasoning", "fission", "workflow", "state", "memory", "cache",
    "safety", "guardrail", "prompt", "persona", "schema", "blueprint",
    # Infrastructure Specifics
    "vector", "embedding", "pinecone", "redis", "compliance", "drift", "hierarchy"
}

# [KEY 49] FORBIDDEN NAMING PATTERNS
FORBIDDEN_PATTERNS = {
    r"^utils\.py$", r"^helper\.py$", r"^temp\.py$", r".*_v\d+\.py$", # [GAP 14] Deduped
    r"^main\.py$", r"^test\.py$", r".*_final\.py$",
    r".*_new\.py$", r".*_old\.py$", r"^.+_\d+\.py$"
}

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

# [ULTIMATE HARDENING] Forbid numbered folders at ANY depth
FORBIDDEN_NUMBERED_PATTERN = re.compile(r"^\d{2}_")

# Legacy mapping for backward compatibility (internal remap)
_LEGACY_KEY_REMAP = {
    11: 1, 12: 2, 21: 3, 24: 4, 26: 5, 28: 6,
    31: 7, 33: 8, 36: 9, 38: 10,
    40: 11, 42: 12, 51: 13,
    43: 14, 44: 15, 45: 16,
    47: 17, 50: 18,
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
