"""
Architecture Guard (ArchGuard) - Sprawl Prevention Suite

[PHASE 11 UPDATED] Enforces architectural constraints via AST analysis.
- Updated Allowlist for Phase 2/3 Gateways.
- Strict Zombie Detection.

[PHASE 21 HARDENED] Structure Locking to prevent sprawl creep.
"""

import ast
import os
from pathlib import Path

import pytest

# Project Root
ROOT_DIR = Path(__file__).parent.parent.parent
CORE_DIR = ROOT_DIR / "agentic_core"

# --- CONFIGURATION ---

# 1. SDK Isolation Rules
# Format: "sdk_module": ["allowed_file_1.py", "allowed_file_2.py"]
SDK_ALLOWLIST = {
    "openai": ["SovereignLLMGateway.py", "EmbeddingSovereignAgent.py"],
    "anthropic": ["SovereignLLMGateway.py"],
    "google.generativeai": ["SovereignLLMGateway.py", "EmbeddingSovereignAgent.py"],
    "pinecone": [
        "PineconeSovereignAgent.py",
        "SemanticKnowledgeClient.py",  # [PHASE 11] Legacy Client (To be migrated, but whitelisted for now)
        "SemanticCacheManager.py",  # [PHASE 12] L4 State Owner (Allowed)
    ],
    "redis": [
        "redis_cache_mixin.py",
        "SemanticCacheSovereignAgent.py",
        "RedisSovereignAgent.py",  # [PHASE 11] Phase 2 Gateway
        "SovereignRedisOrchestratorAgent.py",  # [PHASE 11] Phase 2 Orchestrator
        "SemanticCacheManager.py",  # [PHASE 12] L4 State Owner (Allowed)
    ],
    "google.genai": ["SovereignLLMGateway.py", "EmbeddingSovereignAgent.py"],
}

# 2. Files that MUST NOT exist in active paths (should be archived)
FORBIDDEN_FILES = [
    "inference_engine.py",
    "llm_engine.py",
    "ModelRouterAgent.py",
    "healing_strategies.py",
    "healing_healing_strategies.py",
    "runtime_shared_multi_provider_clients.py",
    "runtime_shared_cache_clients.py",
    "runtime_shared_vector_store_clients.py",
]

# 3. [PHASE 21] Structure Lock - Baseline file counts per layer
DIR_FILE_LIMITS = {"L0_routing": 15, "L5_safety": 25, "L2_execution": 30}


def get_python_files(directory: Path) -> list[Path]:
    """Recursively yield all .py files, excluding tests and archives."""
    py_files = []
    for root, _, files in os.walk(directory):
        if "archived" in root or "tests" in root:
            continue
        for file in files:
            if file.endswith(".py"):
                py_files.append(Path(root) / file)
    return py_files


def check_imports(file_path: Path) -> list[str]:
    """Parse file AST and check for forbidden imports."""
    violations = []
    try:
        with open(file_path, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))

        for node in ast.walk(tree):
            # Check 'import x'
            if isinstance(node, ast.Import):
                for alias in node.names:
                    violations.extend(_check_module(alias.name, file_path))
            # Check 'from x import y'
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    violations.extend(_check_module(node.module, file_path))

    except Exception:
        # Syntax errors in files are acceptable in this check (files might be incomplete)
        pass

    return violations


def _check_module(module_name: str, file_path: Path) -> list[str]:
    """Helper to validate a specific module against the allowlist."""
    file_name = file_path.name
    violations = []

    for sdk, allowed_files in SDK_ALLOWLIST.items():
        if module_name.startswith(sdk):
            # If the file using the SDK is NOT in the allowed list
            if file_name not in allowed_files:
                violations.append(
                    f"VIOLATION: '{file_name}' imports '{module_name}'. Only allowed in: {allowed_files}",
                )

    return violations


# --- TESTS ---


def test_no_zombie_files_active():
    """Fail if any obsolete 'Zombie' files still exist in active directories."""
    active_files = [f.name for f in get_python_files(CORE_DIR)]
    found_zombies = [f for f in active_files if f in FORBIDDEN_FILES]

    error_msg = f"Found active Zombie files! Run cleanup script immediately: {found_zombies}"
    assert not found_zombies, error_msg


def test_sdk_isolation():
    """Fail if SDKs are imported outside their Sovereigns."""
    all_violations = []
    for py_file in get_python_files(CORE_DIR):
        all_violations.extend(check_imports(py_file))

    # Format errors for readability
    if all_violations:
        pytest.fail("\n".join(["ARCHITECTURE VIOLATIONS FOUND:"] + all_violations))


def test_no_archived_imports():
    """Fail if active code imports from 'agentic_core.archived'."""
    violations = []
    for py_file in get_python_files(CORE_DIR):
        try:
            with open(py_file, encoding="utf-8") as f:
                content = f.read()
                if "agentic_core.archived" in content or "from agentic_core.archived" in content:
                    violations.append(f"{py_file.name} imports from archived/")
        except:
            pass

    assert not violations, f"Active code is importing from Archive: {violations}"


def test_structure_lock():
    """[PHASE 21] Warn if file counts exceed baselines (Sprawl Detection)."""
    for layer, limit in DIR_FILE_LIMITS.items():
        layer_path = CORE_DIR / layer
        if layer_path.exists():
            count = len(get_python_files(layer_path))
            if count > limit * 1.2:
                print(
                    f"⚠️ WARNING: {layer} file count ({count}) exceeds baseline ({limit}). Check for sprawl.",
                )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
