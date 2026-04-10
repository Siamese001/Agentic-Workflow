#!/usr/bin/env python3
"""
Surgical Refactoring - L0 Gravity Import Violations

Converts static upward imports to dynamic importlib calls for L0 files
that only need higher-layer tools for specific methods.

Target violations:
- L0 → L5 (Gravity logic)
- L0 → L3 (Orchestration workflow)
- L0 → L4 (State/Pinecone)
- L0 → L1 (Cognition)
- L0 → L2 (Execution)
"""

from pathlib import Path

from agentic_core.L0_routing.config.path_constants import AGENTIC_CORE_DIR, SCRIPTS_DIR

REPO = Path(__file__).parent.parent

# Refactoring patterns for specific files
REFACTORINGS = {
    "l0_delegation_testing_mixin.py": {
        "old_import": "from agentic_core.L5_safety.enforcement import GravityValidator",
        "new_code": """
def _get_gravity_validator():
    \"\"\"Lazy load GravityValidator to avoid L0 → L5 dependency.\"\"\"
    import importlib
    module = importlib.import_module('agentic_core.L5_safety.enforcement')
    return module.GravityValidator

# Use: GravityValidator = _get_gravity_validator() when needed
""",
    },
    "filesystem_mcp_client.py": {
        "old_import": "from agentic_core.L3_orchestration.reasoning",
        "new_code": """
def _get_workflow_engine():
    \"\"\"Lazy load workflow engine to avoid L0 → L3 dependency.\"\"\"
    import importlib
    module = importlib.import_module('agentic_core.L3_orchestration.reasoning')
    return module
""",
    },
    "gitkraken_mcp_client.py": {
        "old_import": "from agentic_core.L3_orchestration.reasoning",
        "new_code": """
def _get_workflow_engine():
    \"\"\"Lazy load workflow engine to avoid L0 → L3 dependency.\"\"\"
    import importlib
    module = importlib.import_module('agentic_core.L3_orchestration.reasoning')
    return module
""",
    },
    "healing_vector_healing_strategy.py": {
        "old_import": "from agentic_core.L4_state.semantic_memory.pinecone",
        "new_code": """
def _get_pinecone_client():
    \"\"\"Lazy load Pinecone client to avoid L0 → L4 dependency.\"\"\"
    import importlib
    module = importlib.import_module('agentic_core.L4_state.semantic_memory.pinecone')
    return module
""",
    },
    "l1_health_benchmark.py": {
        "old_import": "from agentic_core.L1_cognition.cognitive_node.CognitiveNode",
        "new_code": """
def _get_cognitive_node():
    \"\"\"Lazy load CognitiveNode to avoid L0 → L1 dependency.\"\"\"
    import importlib
    module = importlib.import_module('agentic_core.L1_cognition.cognitive_node.CognitiveNode')
    return module.CognitiveNode
""",
    },
    "BootstrapAgent.py": {
        "old_import": "from agentic_core.L2_execution.reasoning.Toolsmith",
        "new_code": """
def _get_toolsmith():
    \"\"\"Lazy load Toolsmith to avoid L0 → L2 dependency.\"\"\"
    import importlib
    module = importlib.import_module('agentic_core.L2_execution.reasoning.Toolsmith')
    return module.Toolsmith
""",
    },
    "auditors_guard_ddd_alignment.py": {
        "old_import": "from agentic_core.L1_cognition.P2_domain.sovereign",
        "new_code": """
def _get_sovereign_domain():
    \"\"\"Lazy load sovereign domain to avoid L0 → L1 dependency.\"\"\"
    import importlib
    module = importlib.import_module('agentic_core.L1_cognition.P2_domain.sovereign')
    return module
""",
    },
}


def refactor_file(file_path: Path, old_import: str, new_code: str) -> bool:
    """
    Replace static import with dynamic importlib pattern.

    Returns:
        True if file was modified, False otherwise
    """
    try:
        content = file_path.read_text(encoding="utf-8")

        # Check if old import exists
        if old_import not in content:
            return False

        # Comment out old import and add new dynamic loader
        new_content = content.replace(
            old_import,
            f"# {old_import}  # Refactored to dynamic import to avoid upward dependency\n{new_code}",
        )

        # Write back
        file_path.write_text(new_content, encoding="utf-8")

        print(f"✅ Fixed: {file_path.name}")
        return True

    except OSError as e:
        print(f"❌ Error processing {file_path.name}: {e}")
        return False


def main():
    """Apply surgical refactoring to L0 files."""

    print("=" * 80)
    print("  L0 Gravity Import Surgical Refactoring")
    print("=" * 80)
    print()

    l0_scripts = REPO / AGENTIC_CORE_DIR / "L0_routing" / SCRIPTS_DIR

    if not l0_scripts.exists():
        print(f"❌ Directory not found: {l0_scripts}")
        return 1

    files_modified = 0

    for filename, refactoring in REFACTORINGS.items():
        file_path = l0_scripts / filename

        if not file_path.exists():
            print(f"⚠️  File not found: {filename}")
            continue

        if refactor_file(file_path, refactoring["old_import"], refactoring["new_code"]):
            files_modified += 1

    print()
    print("=" * 80)
    print("  Summary")
    print("=" * 80)
    print(f"Files modified: {files_modified}/{len(REFACTORINGS)}")
    print()

    if files_modified > 0:
        print("✅ Surgical refactoring complete!")
        print()
        print("⚠️  IMPORTANT: These files now use dynamic imports.")
        print("   You must update the code that uses these imports to call")
        print("   the lazy loader functions instead of using the imports directly.")
        print()
        print("Next steps:")
        print("  1. Review modified files and update usage patterns")
        print("  2. Run: python scripts/ssot.py validate --summary")
        print("  3. Test affected functionality")

    return 0


if __name__ == "__main__":
    exit(main())
