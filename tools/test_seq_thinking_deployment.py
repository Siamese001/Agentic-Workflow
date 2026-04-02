#!/usr/bin/env python3
"""
Test Sequential Thinking MCP Deployment

This script tests the sequential thinking deployment and validates
that all components are working correctly.
"""

import json
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Any

def test_mcp_configuration():
    """Test MCP configuration is properly set up."""
    print("🔍 Testing MCP Configuration...")

    user_config = Path("C:\\Users\\amita\\.codeium\\windsurf\\mcp_config.json")

    if not user_config.exists():
        print("❌ User MCP config not found")
        return False

    try:
        with open(user_config) as f:
            config = json.load(f)

        seq_thinking = config.get("mcpServers", {}).get("sequential-thinking", {})

        if not seq_thinking:
            print("❌ Sequential thinking not configured")
            return False

        if seq_thinking.get("disabled", True):
            print("❌ Sequential thinking is disabled")
            return False

        # Check environment variables
        env_vars = seq_thinking.get("env", {})
        required_vars = [
            "DISABLE_THOUGHT_LOGGING",
            "SEQUENTIAL_THINKING_PRIORITY",
            "SEQUENTIAL_THINKING_SWE_MODE",
            "SEQUENTIAL_THINKING_AUTO_TRIGGER"
        ]

        for var in required_vars:
            if var not in env_vars:
                print(f"❌ Missing environment variable: {var}")
                return False

        # Check server ordering (should be first)
        servers = list(config.get("mcpServers", {}).keys())
        if "sequential-thinking" not in servers or servers[0] != "sequential-thinking":
            print("⚠️  Sequential thinking not first in server order")

        print("✅ MCP configuration valid")
        return True

    except Exception as e:
        print(f"❌ MCP configuration test failed: {e}")
        return False

def test_environment_variables():
    """Test environment variables are set."""
    print("🔍 Testing Environment Variables...")

    required_vars = [
        "SEQUENTIAL_THINKING_ENABLED",
        "SEQUENTIAL_THINKING_PRIORITY",
        "WINDSURF_TOOL_PREFERENCE",
        "SWE15_SEQUENTIAL_THINKING"
    ]

    all_set = True
    for var in required_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var}={value}")
        else:
            print(f"❌ {var} not set")
            all_set = False

    return all_set

def test_tool_files():
    """Test all tool files exist and are functional."""
    print("🔍 Testing Tool Files...")

    repo_root = Path.cwd()
    tool_files = [
        repo_root / "tools" / "mcp" / "sequential_thinking_booster.py",
        repo_root / "tools" / "monitoring" / "mcp_usage_tracker.py",
        repo_root / "agentic_core" / "planning" / "sequential_thinking_workflow.py",
        repo_root / "apps_shared" / "prompts" / "sequential_thinking_templates.py",
        repo_root / "ops_scripts" / "environment" / "seq_thinking_env.py"
    ]

    all_exist = True
    for tool_file in tool_files:
        if tool_file.exists():
            print(f"✅ {tool_file.name}")

            # Test if Python file is syntactically valid
            try:
                with open(tool_file) as f:
                    compile(f.read(), str(tool_file), 'exec')
                print(f"✅ {tool_file.name} syntax valid")
            except SyntaxError as e:
                print(f"❌ {tool_file.name} syntax error: {e}")
                all_exist = False
        else:
            print(f"❌ {tool_file.name} missing")
            all_exist = False

    return all_exist

def test_sequential_thinking_booster():
    """Test sequential thinking booster functionality."""
    print("🔍 Testing Sequential Thinking Booster...")

    repo_root = Path.cwd()
    booster_script = repo_root / "tools" / "mcp" / "sequential_thinking_booster.py"

    if not booster_script.exists():
        print("❌ Booster script not found")
        return False

    # Create test data
    test_tools = [
        {"name": "filesystem", "description": "File system access"},
        {"name": "sequential-thinking", "description": "Sequential reasoning tool"},
        {"name": "memory", "description": "Memory management"},
        {"name": "other-tool", "description": "Other functionality"}
    ]

    test_file = repo_root / "test_tools_input.json"
    output_file = repo_root / "test_tools_output.json"

    try:
        with open(test_file, 'w') as f:
            json.dump({"tools": test_tools}, f)

        # Run booster
        result = subprocess.run([
            sys.executable, str(booster_script), str(test_file), str(output_file)
        ], capture_output=True, text=True, cwd=repo_root)

        if result.returncode != 0:
            print(f"❌ Booster execution failed: {result.stderr}")
            return False

        # Check output
        if not output_file.exists():
            print("❌ Booster output file not created")
            return False

        with open(output_file) as f:
            boosted_data = json.load(f)

        boosted_tools = boosted_data.get("tools", [])

        if not boosted_tools:
            print("❌ No tools in booster output")
            return False

        # Sequential thinking should be first
        first_tool = boosted_tools[0]
        if "sequential" not in first_tool.get("name", "").lower():
            print("❌ Sequential thinking not boosted to first position")
            return False

        print("✅ Sequential thinking booster working correctly")
        return True

    except Exception as e:
        print(f"❌ Booster test failed: {e}")
        return False
    finally:
        # Cleanup
        for file in [test_file, output_file]:
            if file.exists():
                file.unlink()

def test_usage_tracker():
    """Test MCP usage tracker functionality."""
    print("🔍 Testing MCP Usage Tracker...")

    repo_root = Path.cwd()
    tracker_script = repo_root / "tools" / "monitoring" / "mcp_usage_tracker.py"

    if not tracker_script.exists():
        print("❌ Usage tracker script not found")
        return False

    try:
        # Test logging functionality
        result = subprocess.run([
            sys.executable, str(tracker_script),
            "--log", "sequential-thinking", "test-context", "true", "1.5", "500"
        ], capture_output=True, text=True, cwd=repo_root)

        if result.returncode != 0:
            print(f"❌ Usage tracker logging failed: {result.stderr}")
            return False

        # Test report generation
        result = subprocess.run([
            sys.executable, str(tracker_script), "--report", "--hours", "1"
        ], capture_output=True, text=True, cwd=repo_root)

        if result.returncode != 0:
            print(f"❌ Usage tracker report failed: {result.stderr}")
            return False

        print("✅ MCP usage tracker working correctly")
        return True

    except Exception as e:
        print(f"❌ Usage tracker test failed: {e}")
        return False

def test_sequential_thinking_workflow():
    """Test sequential thinking workflow integration."""
    print("🔍 Testing Sequential Thinking Workflow...")

    repo_root = Path.cwd()
    workflow_script = repo_root / "agentic_core" / "planning" / "sequential_thinking_workflow.py"

    if not workflow_script.exists():
        print("❌ Workflow script not found")
        return False

    try:
        # Test import and basic functionality
        result = subprocess.run([
            sys.executable, "-c", f"""
import sys
sys.path.append('{repo_root}')
from agentic_core.planning.sequential_thinking_workflow import SequentialThinkingEnhancedWorkflow
from agentic_core.planning.token_estimator import TokenBudget

# Test workflow initialization
workflow = SequentialThinkingEnhancedWorkflow(seq_thinking_enabled=True)
print('Workflow initialized successfully')

# Test complexity checking
step_config = {{'complexity': 'high', 'files': ['file1.py', 'file2.py', 'file3.py', 'file4.py']}}
should_force = workflow.force_sequential_thinking('analysis', step_config)
print(f'Force sequential thinking: {{should_force}}')

# Test template retrieval
template = workflow._get_seq_thinking_template('analysis')
print(f'Template retrieved: {{len(template)}} characters')
"""
        ], capture_output=True, text=True, cwd=repo_root)

        if result.returncode != 0:
            print(f"❌ Workflow test failed: {result.stderr}")
            return False

        print("✅ Sequential thinking workflow working correctly")
        return True

    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        return False

def test_prompt_templates():
    """Test sequential thinking prompt templates."""
    print("🔍 Testing Prompt Templates...")

    repo_root = Path.cwd()
    templates_script = repo_root / "apps_shared" / "prompts" / "sequential_thinking_templates.py"

    if not templates_script.exists():
        print("❌ Templates script not found")
        return False

    try:
        result = subprocess.run([
            sys.executable, "-c", f"""
import sys
sys.path.append('{repo_root}')
from apps_shared.prompts.sequential_thinking_templates import (
    get_template, render_template, get_template_for_complexity,
    SequentialThinkingTemplate
)

# Test template retrieval
template = get_template(SequentialThinkingTemplate.SWE_ANALYSIS)
print(f'Template retrieved: {{template.name}}')

# Test template rendering
rendered = render_template(SequentialThinkingTemplate.SWE_ANALYSIS,
                          problem_title='Test Problem',
                          context='Test context',
                          core_question='Test question')
print(f'Template rendered: {{len(rendered)}} characters')

# Test complexity filtering
templates = get_template_for_complexity('high')
print(f'Templates for high complexity: {{len(templates)}}')
"""
        ], capture_output=True, text=True, cwd=repo_root)

        if result.returncode != 0:
            print(f"❌ Templates test failed: {result.stderr}")
            return False

        print("✅ Prompt templates working correctly")
        return True

    except Exception as e:
        print(f"❌ Templates test failed: {e}")
        return False

def run_integration_test():
    """Run comprehensive integration test."""
    print("🚀 Starting Sequential Thinking Integration Test")
    print("=" * 60)

    # Set environment variables for testing
    os.environ['SEQUENTIAL_THINKING_ENABLED'] = 'true'
    os.environ['SEQUENTIAL_THINKING_PRIORITY'] = '1'
    os.environ['WINDSURF_TOOL_PREFERENCE'] = 'sequential-thinking'
    os.environ['SWE15_SEQUENTIAL_THINKING'] = 'enabled'

    tests = [
        ("MCP Configuration", test_mcp_configuration),
        ("Environment Variables", test_environment_variables),
        ("Tool Files", test_tool_files),
        ("Sequential Thinking Booster", test_sequential_thinking_booster),
        ("MCP Usage Tracker", test_usage_tracker),
        ("Sequential Thinking Workflow", test_sequential_thinking_workflow),
        ("Prompt Templates", test_prompt_templates)
    ]

    results = {}
    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            success = test_func()
            results[test_name] = success
            if success:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)

    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Sequential thinking is ready to use.")
        print("\n📝 Next Steps:")
        print("1. Restart Windsurf to load the new configuration")
        print("2. Test with a complex SWE 1.5 task")
        print("3. Monitor usage with: python tools/monitoring/mcp_usage_tracker.py --report")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")

    return passed == total

if __name__ == "__main__":
    success = run_integration_test()
    sys.exit(0 if success else 1)
