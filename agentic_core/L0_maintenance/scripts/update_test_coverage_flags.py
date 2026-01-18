#!/usr/bin/env python3
"""
Update has_tests flags in agent_discovery_full.json based on actual test file existence.
"""
import json
from pathlib import Path
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"
DISCOVERY_FILE = PROJECT_ROOT / "agent_discovery_full.json"

def find_test_file(agent_name: str) -> bool:
    """Check if a test file exists for the given agent."""
    test_patterns = [
        TESTS_DIR / f"test_{agent_name}.py",
        TESTS_DIR / "apps" / f"test_{agent_name}.py",
        TESTS_DIR / "l0" / f"test_{agent_name}.py",
        TESTS_DIR / "l1" / f"test_{agent_name}.py",
        TESTS_DIR / "l2" / f"test_{agent_name}.py",
        TESTS_DIR / "l3" / f"test_{agent_name}.py",
        TESTS_DIR / "l4" / f"test_{agent_name}.py",
        TESTS_DIR / "l5" / f"test_{agent_name}.py",
        TESTS_DIR / "l6" / f"test_{agent_name}.py",
        TESTS_DIR / "L6" / f"test_{agent_name}.py",
        TESTS_DIR / "unit" / f"test_{agent_name}.py",
        TESTS_DIR / "integration" / f"test_{agent_name}.py",
        TESTS_DIR / "autogen" / f"test_{agent_name}.py",
        TESTS_DIR / "base" / f"test_{agent_name}.py",
        TESTS_DIR / "utils" / f"test_{agent_name}.py",
    ]
    
    for pattern in test_patterns:
        if pattern.exists():
            return True
    
    return False

def main():
    """Update test coverage flags."""
    print("=" * 70)
    print("UPDATING TEST COVERAGE FLAGS")
    print("=" * 70)
    
    # Load discovery data
    with open(DISCOVERY_FILE, 'r', encoding='utf-8') as f:
        agents = json.load(f)
    
    print(f"\nTotal agents: {len(agents)}")
    
    updated_count = 0
    newly_marked = []
    
    for agent in agents:
        agent_name = agent['class_name']
        current_has_tests = agent.get('has_tests', False)
        
        # Check if test file exists
        test_exists = find_test_file(agent_name)
        
        if test_exists and not current_has_tests:
            agent['has_tests'] = True
            updated_count += 1
            newly_marked.append(agent_name)
            print(f"  [UPDATED] {agent_name}: has_tests = True")
    
    # Calculate new coverage
    total_with_tests = sum(1 for a in agents if a.get('has_tests', False))
    coverage_pct = (total_with_tests / len(agents)) * 100
    
    print(f"\n" + "=" * 70)
    print(f"SUMMARY")
    print("=" * 70)
    print(f"Updated agents: {updated_count}")
    print(f"Total with tests: {total_with_tests}/{len(agents)} ({coverage_pct:.1f}%)")
    
    if newly_marked:
        print(f"\nNewly marked as having tests:")
        for name in newly_marked:
            print(f"  - {name}")
    
    # Save updated discovery data
    with open(DISCOVERY_FILE, 'w', encoding='utf-8') as f:
        json.dump(agents, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Updated {DISCOVERY_FILE}")
    
    if coverage_pct >= 100.0:
        print("\n🎉 100% TEST COVERAGE ACHIEVED!")
    else:
        remaining = len(agents) - total_with_tests
        print(f"\n⚠️  {remaining} agents still need tests ({100-coverage_pct:.1f}% remaining)")

if __name__ == "__main__":
    main()
