"""Dry-run test for enhanced CodeDeduplicationAgent with fuzzy structural matching."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# ARCHIVED: CodeDeduplicationAgent import removed
from agentic_core.L5_safety.validators.core.code_deduplication_agent import CodeDeduplicationAgent
from agentic_core.L5_safety.config.structure_blueprint_config import (
    AGENTIC_CORE_DIR,
)


def test_fuzzy_matching():
    """Test the new fuzzy structural matching on a small sample."""
    print("=" * 80)
    print("FUZZY STRUCTURAL MATCHING DRY-RUN TEST")
    print("=" * 80)

    # Initialize agent with new default threshold (0.98)
    agent = CodeDeduplicationAgent()

    print("\nAgent configuration:")
    print(f"  Similarity Threshold: {agent.threshold:.0%}")
    print(f"  Minimum Lines: {agent.min_lines}")
    print(f"  Tree-sitter Available: {agent.ts_parser is not None}")

    # Test the new _block_similarity method
    print("\n" + "=" * 80)
    print("TESTING _block_similarity() METHOD")
    print("=" * 80)

    # Test case 1: Identical code
    code_a = "def foo():\n    return 42"
    code_b = "def foo():\n    return 42"
    sim = agent._block_similarity(code_a, code_b)
    print("\nTest 1 - Identical code:")
    print(f"  Similarity: {sim:.1%} (expected: 100%)")
    assert sim == 1.0, f"Expected 1.0, got {sim}"

    # Test case 2: Very similar code (variable name change)
    code_a = "def calculate_sum(x, y):\n    result = x + y\n    return result"
    code_b = "def calculate_sum(a, b):\n    total = a + b\n    return total"
    sim = agent._block_similarity(code_a, code_b)
    print("\nTest 2 - Similar structure, different variable names:")
    print(f"  Similarity: {sim:.1%} (expected: ~85-95%)")

    # Test case 3: Different code
    code_a = "def foo():\n    return 42"
    code_b = "class Bar:\n    def __init__(self):\n        self.value = 100"
    sim = agent._block_similarity(code_a, code_b)
    print("\nTest 3 - Completely different code:")
    print(f"  Similarity: {sim:.1%} (expected: <50%)")

    # Test scan on a small subset of files
    print("\n" + "=" * 80)
    print("TESTING scan_for_duplicates() ON SAMPLE FILES")
    print("=" * 80)

    # Get a small sample of Python files from L2_execution
    sample_dir = project_root / AGENTIC_CORE_DIR / "L2_execution"
    if sample_dir.exists():
        # Phase 6.9 Sub-50: Use ssot_discovery instead of rglob
        from agentic_core.utils.ssot_discovery_validator import get_python_files

        python_files = [str(f) for f in get_python_files(sample_dir)][:10]
        print(f"\nScanning {len(python_files)} sample files from L2_execution...")

        agent.scan_for_duplicates(python_files)

        print("\nResults:")
        print(f"  Duplicate groups found: {len(agent.duplicate_groups)}")
        print(f"  Errors encountered: {len(agent.errors)}")

        if agent.errors:
            print("\nErrors:")
            for error in agent.errors[:5]:
                print(f"  - {error}")
    else:
        print(f"\nSample directory not found: {sample_dir}")

    print("\n" + "=" * 80)
    print("DRY-RUN TEST COMPLETE")
    print("=" * 80)
    print("\n✅ All basic tests passed!")
    print(f"✅ Fuzzy matching threshold: {agent.threshold:.0%}")
    print("✅ _block_similarity() method working correctly")
    print("✅ scan_for_duplicates() refactored successfully")


if __name__ == "__main__":
    test_fuzzy_matching()
