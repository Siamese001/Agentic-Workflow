#!/usr/bin/env python3
"""
Generate test files for agents lacking test coverage.
Priority: L5 > L4 > L3 > L2 > L1 > L0 > Base > Apps
"""

import json
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

project_root = Path(__file__).parent.parent

# Load untested agents
with open(project_root / "untested_agents.json", encoding="utf-8") as f:
    untested_agents = json.load(f)

# Priority order for test generation
LAYER_PRIORITY = ["L5", "L4", "L3", "L2", "L1", "L0", "Base", "L6", "Apps", "Utils"]


def get_test_template(agent: dict) -> str:
    """Generate a test file template for an agent."""
    class_name = agent["class_name"]
    agent_path = agent["path"].replace("\\", "/")
    layer = agent["layer"]

    # Determine test file path
    test_dir = project_root / TESTS_DIR / layer.lower()
    test_dir.mkdir(parents=True, exist_ok=True)

    template = f'''#!/usr/bin/env python3
"""
Test suite for {class_name}
Generated automatically to improve test coverage.
"""
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from {agent_path.replace("/", ".").replace(".py", "")} import {class_name}


class Test{class_name}:
    """Test suite for {class_name}."""

    @pytest.fixture
    def agent(self):
        """Create agent instance for testing."""
        return {class_name}()

    def test_instantiation(self, agent):
        """Test that agent can be instantiated."""
        assert agent is not None
        assert isinstance(agent, {class_name})

    def test_has_heal_repository(self, agent):
        """Test that agent has heal_repository method."""
        assert hasattr(agent, 'heal_repository')
        assert callable(getattr(agent, 'heal_repository'))

    def test_heal_repository_dry_run(self, agent):
        """Test heal_repository in dry-run mode."""
        result = agent.heal_repository(dry_run=True, execute=False)
        assert isinstance(result, dict)
        assert 'violations' in result or 'fixed' in result

    def test_mcp_hardened(self, agent):
        """Test that agent has MCP hardening."""
        # Check for MCPHardenedMixin in MRO
        mro_classes = [cls.__name__ for cls in type(agent).__mro__]
        assert 'MCPHardenedMixin' in mro_classes, f"Agent should have MCPHardenedMixin in MRO"

    def test_class_name(self, agent):
        """Test that agent has correct class name."""
        assert agent.__class__.__name__ == '{class_name}'

    # Add more specific tests based on agent methods
    # TODO: Expand with agent-specific test cases


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
'''

    return template


# guardian: allow-magic-config
def generate_tests_for_layer(layer: str, agents: list[dict], max_count: int = 10) -> int:
    """Generate test files for agents in a specific layer."""
    layer_agents = [a for a in agents if a["layer"] == layer]

    if not layer_agents:
        return 0

    print(f"\n{'=' * 70}")
    print(f"Generating tests for {layer} layer ({len(layer_agents)} agents)")
    print(f"{'=' * 70}")

    generated = 0
    for agent in layer_agents[:max_count]:
        class_name = agent["class_name"]
        test_file = project_root / TESTS_DIR / layer.lower() / f"test_{class_name}.py"

        # Skip if test already exists
        if test_file.exists():
            print(f"  ⏭️  {class_name}: test already exists")
            continue

        try:
            # Generate test template
            test_content = get_test_template(agent)

            # Write test file
            test_file.parent.mkdir(parents=True, exist_ok=True)
            test_file.write_text(test_content, encoding="utf-8")

            print(f"  ✅ {class_name}: test generated")
            generated += 1

        # guardian: allow-silent-swallow
        except Exception as e:
            print(f"  ❌ {class_name}: failed - {e}")

    if len(layer_agents) > max_count:
        print(f"  ... {len(layer_agents) - max_count} more agents in {layer} (not generated)")

    return generated


def main():
    """Generate tests for untested agents by priority."""
    print("=" * 70)
    print("AGENT TEST GENERATION")
    print("=" * 70)
    print(f"Total untested agents: {len(untested_agents)}")

    total_generated = 0

    # Generate tests by priority
    for layer in LAYER_PRIORITY:
        # guardian: allow-magic-config
        generated = generate_tests_for_layer(layer, untested_agents, max_count=10)
        total_generated += generated

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total tests generated: {total_generated}")
    print(f"Remaining untested: {len(untested_agents) - total_generated}")

    if total_generated > 0:
        print("\n✅ Test generation complete!")
        print("\nNext steps:")
        print("1. Review generated tests in tests/ directory")
        print("2. Run: pytest tests/ -v")
        print("3. Run: python scripts/full_agent_discovery.py")
        print("4. Verify improved test coverage % in dashboard")
    else:
        print("\n⚠️  No new tests generated (all agents already have tests)")


if __name__ == "__main__":
    main()
