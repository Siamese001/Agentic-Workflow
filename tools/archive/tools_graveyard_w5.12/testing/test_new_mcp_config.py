#!/usr/bin/env python3
"""
Test script for new MCP configuration (Playwright + Task Manager).
Tests the concrete capability MCPs that replaced sequential-thinking.
"""

import sys
from pathlib import Path


def test_config_structure():
    """Test if MCP configuration files are valid and contain new servers."""
    print("🔍 Testing MCP configuration structure...")

    # Test YAML config
    yaml_config = Path(__file__).parent.parent.parent / "config" / "mcp_servers.yaml"
    if yaml_config.exists():
        print(f"✅ YAML config found: {yaml_config}")
        with open(yaml_config) as f:
            content = f.read()
            if "playwright:" in content:
                print("✅ Playwright server found in YAML config")
            else:
                print("❌ Playwright server NOT found in YAML config")
                return False

            if "task_manager:" in content:
                print("✅ Task Manager server found in YAML config")
            else:
                print("❌ Task Manager server NOT found in YAML config")
                return False

            if "sequential_thinking:" in content:
                print("❌ Sequential thinking still in YAML config (should be removed)")
                return False
            else:
                print("✅ Sequential thinking removed from YAML config")
    else:
        print(f"❌ YAML config not found: {yaml_config}")
        return False

    # Test JSON config (actually YAML format)
    json_config = Path(__file__).parent.parent.parent / ".windsurf" / "mcp_config.json"
    if json_config.exists():
        print(f"✅ JSON config found: {json_config}")
        with open(json_config) as f:
            content = f.read()
            if "playwright:" in content:
                print("✅ Playwright server found in JSON config")
            else:
                print("❌ Playwright server NOT found in JSON config")
                return False

            if "task_manager:" in content:
                print("✅ Task Manager server found in JSON config")
            else:
                print("❌ Task Manager server NOT found in JSON config")
                return False

            if "sequential_thinking:" in content:
                print("❌ Sequential thinking still in JSON config (should be removed)")
                return False
            else:
                print("✅ Sequential thinking removed from JSON config")
    else:
        print(f"❌ JSON config not found: {json_config}")
        return False

    return True


def test_prefix_consistency():
    """Test if MCP prefixes are consistent across both configs."""
    print("\n🔍 Testing MCP prefix consistency...")

    # Since .windsurf/mcp_config.json is YAML, we'll just do string matching
    json_config = Path(__file__).parent.parent.parent / ".windsurf" / "mcp_config.json"
    with open(json_config) as f:
        content = f.read()

        # Check for correct prefixes in the config
        checks = [
            ("gitkraken", 'prefix: "mcp0"'),
            ("adg_sqlite", 'prefix: "mcp1"'),
            ("brave_search", 'prefix: "mcp2"'),
            ("deepwiki", 'prefix: "mcp3"'),
            ("enhanced_http", 'prefix: "mcp4"'),
            ("filesystem", 'prefix: "mcp5"'),
            ("memory", 'prefix: "mcp6"'),
            ("playwright", 'prefix: "mcp7"'),
            ("vector_db", 'prefix: "mcp8"'),
            ("otel_mcp", 'prefix: "mcp9"'),
            ("task_manager", 'prefix: "mcp10"'),
            ("redis_mcp", 'prefix: "mcp11"'),
            ("pytest_mcp", 'prefix: "mcp12"'),
        ]

        for server_name, expected_prefix in checks:
            if server_name in content and expected_prefix in content:
                print(f"✅ {server_name}: {expected_prefix}")
            else:
                print(f"❌ {server_name}: prefix check failed")
                return False

    # Check validation rules
    expected_valid = [
        "mcp0",
        "mcp1",
        "mcp2",
        "mcp3",
        "mcp4",
        "mcp5",
        "mcp6",
        "mcp7",
        "mcp8",
        "mcp9",
        "mcp10",
        "mcp11",
        "mcp12",
    ]

    all_found = all(prefix in content for prefix in expected_valid)
    if all_found:
        print("✅ Validation prefixes correct in config")
    else:
        print("❌ Some validation prefixes missing")
        return False

    return True


def test_enforcement_rule():
    """Test if enforcement rule was updated."""
    print("\n🔍 Testing enforcement rule update...")

    rule_file = (
        Path(__file__).parent.parent.parent / ".windsurf" / "rules" / "sequential-thinking-enforcement.md"
    )
    if rule_file.exists():
        with open(rule_file, encoding="utf-8") as f:
            content = f.read()

            if "Structured Reasoning & Task Management" in content:
                print("✅ Rule title updated to reflect new approach")
            else:
                print("❌ Rule title not updated")
                return False

            if "Task Manager MCP (mcp10)" in content:
                print("✅ Rule references Task Manager MCP")
            else:
                print("❌ Rule doesn't reference Task Manager MCP")
                return False

            if "Playwright MCP (mcp7)" in content:
                print("✅ Rule references Playwright MCP")
            else:
                print("❌ Rule doesn't reference Playwright MCP")
                return False

            if "sequential-thinking MCP has been replaced" in content:
                print("✅ Rule documents the replacement")
            else:
                print("❌ Rule doesn't document the replacement")
                return False
    else:
        print(f"❌ Rule file not found: {rule_file}")
        return False

    return True


def main():
    """Main test function."""
    print("🚀 New MCP Configuration Test")
    print("=" * 60)

    results = {}

    # Test 1: Config structure
    results["config_structure"] = test_config_structure()

    # Test 2: Prefix consistency
    results["prefix_consistency"] = test_prefix_consistency()

    # Test 3: Enforcement rule
    results["enforcement_rule"] = test_enforcement_rule()

    # Summary
    print("\n📋 Test Summary:")
    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {test_name}: {status}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All tests passed! New MCP configuration is ready.")
        print("\n📝 Next Steps:")
        print("1. Restart Windsurf IDE to load the new MCP configuration")
        print("2. Verify Playwright and Task Manager appear in the available tools list")
        print("3. Test Task Manager by creating a sample task")
        print("4. Test Playwright by navigating to a simple URL if needed")
        return 0
    else:
        print("\n❌ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
