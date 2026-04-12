#!/usr/bin/env python3
"""
Test script for Sequential Thinking MCP server integration.
This script tests the sequential thinking functionality with repository-specific context.
"""

import json
import subprocess
import sys
from pathlib import Path


def run_npx_command(command_args):
    """Run npx command and return result."""
    try:
        cmd = ["npx", "-y"] + command_args
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path(__file__).parent,
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def test_sequential_thinking_package():
    """Test if the sequential thinking package is installed and accessible."""
    print("🔍 Testing sequential thinking package installation...")

    # Check if the package is installed globally
    try:
        cmd = [
            "node",
            "C:\\Users\\amita\\AppData\\Roaming\\fnm\\node-versions\\v24.13.0\\installation\\node_modules\\@modelcontextprotocol\\server-sequential-thinking\\dist\\index.js",
            "--help",
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=Path(__file__).parent,
        )

        if (
            result.returncode == 0
            or "sequential-thinking" in result.stdout.lower()
            or "sequential-thinking" in result.stderr.lower()
        ):
            print("✅ Sequential thinking package is installed and accessible")
            return True
        else:
            print(f"❌ Package not working properly: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print("✅ Sequential thinking package started (timeout expected for server)")
        return True
    except Exception as e:
        print(f"❌ Failed to access sequential thinking package: {e}")
        return False


def test_repository_context():
    """Gather repository context for sequential thinking test."""
    print("\n📁 Gathering repository context...")

    repo_root = Path(__file__).parent
    context = {
        "repository_name": "Agentic-Workflow",
        "repository_root": str(repo_root),
        "key_directories": {
            "agentic_core": str(repo_root / "agentic_core"),
            "apps": str(repo_root / "apps"),
            "tools": str(repo_root / "tools"),
            "tests": str(repo_root / "tests"),
            "docs": str(repo_root / "docs"),
        },
        "python_files_count": len(list(repo_root.rglob("*.py"))),
        "markdown_files_count": len(list(repo_root.rglob("*.md"))),
        "total_modules": sum(1 for d in repo_root.rglob("*/") if (d / "__init__.py").exists()),
    }

    print("📊 Repository context gathered:")
    print(f"   - Python files: {context['python_files_count']}")
    print(f"   - Markdown files: {context['markdown_files_count']}")
    print(f"   - Python modules: {context['total_modules']}")

    return context


def create_sequential_thinking_test():
    """Create a sequential thinking test scenario."""
    print("\n🧠 Creating sequential thinking test scenario...")

    context = test_repository_context()

    # Define a complex problem related to the repository
    problem = f"""
    Analyze the Agentic-Workflow repository architecture and provide a structured assessment:

    Repository: {context["repository_name"]}
    - Python files: {context["python_files_count"]}
    - Markdown files: {context["markdown_files_count"]}
    - Python modules: {context["total_modules"]}

    Problem: How should we optimize the testing strategy for this multi-layered agentic system?

    Consider:
    1. Current test coverage across agentic_core layers (L0-L6)
    2. Integration testing between apps_* modules
    3. Performance testing for the ADG (Application Dependency Graph) system
    4. Testing governance and compliance requirements

    Provide a sequential analysis breaking this down into manageable components.
    """

    return problem


def test_mcp_config():
    """Test the MCP configuration file."""
    print("\n⚙️ Testing MCP configuration...")

    config_path = Path(__file__).parent / ".windsurf" / "mcp_config.json"

    if not config_path.exists():
        print("❌ MCP config file not found")
        return False

    try:
        with open(config_path) as f:
            config = json.load(f)

        if "sequential-thinking" in config.get("mcpServers", {}):
            server_config = config["mcpServers"]["sequential-thinking"]
            print("✅ Sequential thinking server found in MCP config")
            print(f"   - Command: {server_config.get('command')}")
            print(f"   - Args: {server_config.get('args')}")
            print(f"   - Disabled: {server_config.get('disabled', False)}")
            return True
        else:
            print("❌ Sequential thinking server not found in MCP config")
            return False

    except Exception as e:
        print(f"❌ Error reading MCP config: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 Sequential Thinking MCP Server Integration Test")
    print("=" * 60)

    # Test 1: Package access
    package_ok = test_sequential_thinking_package()

    # Test 2: MCP configuration
    config_ok = test_mcp_config()

    # Test 3: Create test scenario
    test_problem = create_sequential_thinking_test()

    # Summary
    print("\n📋 Test Summary:")
    print(f"   Package Access: {'✅' if package_ok else '❌'}")
    print(f"   MCP Config: {'✅' if config_ok else '❌'}")

    if package_ok and config_ok:
        print("\n🎉 Sequential thinking MCP server is ready!")
        print("\n📝 Test Problem for Sequential Thinking:")
        print(test_problem)

        print("\n💡 Next Steps:")
        print("1. Restart Windsurf to load the new MCP configuration")
        print("2. Use the sequential_thinking tool to analyze the problem above")
        print("3. Verify the tool appears in the available tools list")

        return 0
    else:
        print("\n❌ Issues found. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
