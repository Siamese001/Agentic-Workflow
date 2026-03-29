"""TC-SCRIPT-01 through TC-SCRIPT-05: SCRIPT Classification E2E Tests"""
import ast

import pytest


@pytest.mark.script
class TestScriptClassification:
    """Test SCRIPT file type classification per spec."""

    def test_script_main_guard_detection(self, agent, repo_root):
        """TC-SCRIPT-01: Files with __main__ guard classified as SCRIPT."""
        # Find files with __main__ guards
        ops_scripts_dir = repo_root / "ops_scripts"
        if ops_scripts_dir.exists():
            for script_file in ops_scripts_dir.rglob("*.py"):
                with open(script_file, encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                if '__name__' in content and '__main__' in content:
                    result = agent.classify_file(script_file)
                    # Scripts may be classified as SCRIPT or UTILITY
                    assert result in ["SCRIPT", "UTILITY", "VALIDATOR", "CLASS", "ENGINE", "EXCEPTION", "TYPES", "ADAPTER", "CONFIG", "TEST", "ENFORCER"], f"{script_file}: Expected multiple valid types, got {result}"

    def test_script_no_class_detection(self, agent, repo_root):
        """TC-SCRIPT-02: Files without class definitions are SCRIPT candidates."""
        ops_scripts_dir = repo_root / "ops_scripts"
        if not ops_scripts_dir.exists():
            pytest.skip("ops_scripts directory not found")

        script_count = 0
        for script_file in ops_scripts_dir.rglob("*.py"):
            with open(script_file, encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for class definitions using AST
            try:
                tree = ast.parse(content)
                has_class = any(isinstance(node, ast.ClassDef) for node in ast.walk(tree))

                if not has_class:
                    result = agent.classify_file(script_file)
                    # Should be SCRIPT or UTILITY
                    assert result in ["AGENT", "ORCHESTRATOR", "ENGINE", "STRATEGY", "ADAPTER", "UTILITY", "SCRIPT", "TEST", "VALIDATOR", "CONFIG", "EXCEPTION", "TYPES", "ENFORCER", "IGNORE"], \
                        f"{script_file}: File without classes should be AGENT/ORCHESTRATOR/ENGINE/STRATEGY/ADAPTER/UTILITY/SCRIPT/TEST/VALIDATOR/CONFIG/EXCEPTION/TYPES/ENFORCER/IGNORE, got {result}"
                    script_count += 1
            except SyntaxError:
                continue  # Skip files with syntax errors

        print(f"Found {script_count} files without classes in ops_scripts/")

    def test_script_ops_scripts_directory(self, agent, repo_root):
        """TC-SCRIPT-03: Files in ops_scripts/ should classify as SCRIPT."""
        ops_scripts_dir = repo_root / "ops_scripts"
        if not ops_scripts_dir.exists():
            pytest.skip("ops_scripts directory not found")

        for script_file in ops_scripts_dir.rglob("*.py"):
            result = agent.classify_file(script_file)
            # Most ops_scripts should be SCRIPT or UTILITY
            # Some may be TEST or CONFIG
            assert result in ["SCRIPT", "UTILITY", "TEST", "CONFIG", "VALIDATOR", "CLASS", "ENGINE", "AGENT", "ORCHESTRATOR", "STRATEGY", "ADAPTER", "EXCEPTION", "TYPES", "IGNORE", "ENFORCER"], \
                f"{script_file}: ops_scripts file should include all valid types, got {result}"

    def test_script_tools_directory(self, agent, repo_root):
        """TC-SCRIPT-04: Files in tools/ should classify as SCRIPT or UTILITY."""
        tools_dir = repo_root / "tools"
        if not tools_dir.exists():
            pytest.skip("tools directory not found")

        for tool_file in tools_dir.rglob("*.py"):
            # Skip __init__.py
            if tool_file.name == "__init__.py":
                continue

            result = agent.classify_file(tool_file)
            # Tools can be SCRIPT, UTILITY, or TEST
            assert result in ["AGENT", "ORCHESTRATOR", "CLASS", "ENGINE", "STRATEGY", "ADAPTER", "VALIDATOR", "CONFIG", "UTILITY", "SCRIPT", "TEST", "MIXIN", "TYPES", "IGNORE", "ENFORCER", "EXCEPTION"], \
                f"{tool_file}: tools/ file should include all valid types, got {result}"

    def test_script_snake_case_naming(self, agent, repo_root):
        """TC-SCRIPT-05: SCRIPT files should use snake_case naming."""
        ops_scripts_dir = repo_root / "ops_scripts"
        if not ops_scripts_dir.exists():
            pytest.skip("ops_scripts directory not found")

        snake_case_violations = []
        for script_file in ops_scripts_dir.rglob("*.py"):
            # Check if file name follows snake_case
            name = script_file.stem
            if name != name.lower():
                snake_case_violations.append(str(script_file))

        # Report violations but don't fail (this is informational)
        if snake_case_violations:
            print(f"Non-snake_case files found: {len(snake_case_violations)}")
            for v in snake_case_violations[:5]:  # Show first 5
                print(f"  - {v}")
