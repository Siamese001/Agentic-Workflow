#!/usr/bin/env python3
"""
Adapted Canon Validator execution script that works with the actual implementation.
This script sets up the environment and executes the Canon Validator with security protocols.
"""

import os
import sys
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock, Mock

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

def setup_test_environment():
    """Create a test Git repository with necessary files."""
    # Create test directory with timestamp to avoid conflicts
    import time
    test_dir = f"test_repo_{int(time.time())}"
    if os.path.exists(test_dir):
        try:
            shutil.rmtree(test_dir)
        except PermissionError:
            print(f"⚠️ Could not remove existing {test_dir}, will create new directory")

    os.makedirs(test_dir)
    os.chdir(test_dir)

    # Initialize Git repo
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)

    # Create target file
    with open("target_file.py", "w") as f:
        f.write("def old_func():\n    return 1\n")

    # Create tests directory for sandbox
    os.makedirs("tests", exist_ok=True)
    with open("tests/test_target_file.py", "w") as f:
        f.write("""
import unittest
import target_file

class TestTargetFile(unittest.TestCase):
    def test_old_func(self):
        self.assertEqual(target_file.old_func(), 1)
""")

    # Initial commit
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], check=True)

    print(f"✅ Test environment created in {os.getcwd()}")
    return test_dir

def create_missing_dependencies():
    """Create mock implementations for missing dependencies."""

    # Create sandbox_utils.py if it doesn't exist
    if not os.path.exists("sandbox_utils.py"):
        with open("sandbox_utils.py", "w") as f:
            f.write("""
import subprocess
import os

def execute_in_sandbox(repo_path: str, command: str) -> bool:
    \"\"\"Mock sandbox execution that returns success.\"\"\"
    print(f"[SANDBOX] Executing: {command}")
    try:
        result = subprocess.run(command, shell=True, cwd=repo_path,
                              capture_output=True, text=True, timeout=30)
        return result.returncode == 0
    except Exception as e:
        print(f"[SANDBOX] Error: {e}")
        return False
""")

    # Create consensus_engine.py if it doesn't exist
    if not os.path.exists("consensus_engine.py"):
        with open("consensus_engine.py", "w") as f:
            f.write("""
class MockJury:
    def judge_artifact(self, content: str, context: str = "") -> dict:
        \"\"\"Mock consensus that always passes.\"\"\"
        return {
            "status": "PASS",
            "score": 1.0,
            "votes": [
                {"model": "mock_model_1", "verdict": "YES", "reason": "Looks good"},
                {"model": "mock_model_2", "verdict": "YES", "reason": "Approved"},
                {"model": "mock_model_3", "verdict": "YES", "reason": "No issues"}
            ]
        }

    def propose_fix(self, code: str, error_message: str, context: str = "") -> dict:
        \"\"\"Mock fix proposal.\"\"\"
        return {
            "status": "SUCCESS",
            "fixed_code": code.replace("old_func()", "new_func():\n        return 2")
        }

jury = MockJury()
""")

    # Create mcp_hardening.py if it doesn't exist
    if not os.path.exists("mcp_hardening.py"):
        with open("mcp_hardening.py", "w") as f:
            f.write("""
def check_design_drift(file_id: str, canonical_version: str, logger=None) -> dict:
    \"\"\"Mock design drift check.\"\"\"
    return {"drift_detected": False}

def execute_vulnerability_search(query: str, logger=None) -> str:
    \"\"\"Mock vulnerability search.\"\"\"
    return json.dumps([{
        "title": "Mock vulnerability fix",
        "snippet": "Apply the fix by updating the function",
        "url": "https://example.com/fix"
    }])
""")

    # Create core_utils.py if it doesn't exist
    if not os.path.exists("core_utils.py"):
        with open("core_utils.py", "w") as f:
            f.write("""
import ast
import subprocess
import os
import json

def validate_python_syntax(file_path: str) -> tuple[bool, str]:
    \"\"\"Validate Python syntax.\"\"\"
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        ast.parse(content)
        return True, ""
    except SyntaxError as e:
        return False, str(e)

def sign_and_commit(file_path: str, message: str, key_id: str = None) -> bool:
    \"\"\"Mock GPG signing and commit.\"\"\"
    try:
        subprocess.run(["git", "add", file_path], check=True)
        # Skip actual GPG signing for demo - just commit normally
        subprocess.run(["git", "commit", "-m", message], check=True)
        return True
    except:
        return False

def search_nodes(query: str):
    \"\"\"Mock node search.\"\"\"
    return []

def add_observations(observations: list):
    \"\"\"Mock observation logging.\"\"\"
    print(f"[OBSERVATION] {observations}")

def semantic_score_draft(content: str) -> float:
    \"\"\"Mock semantic scoring.\"\"\"
    return 0.9

def write_file(path: str, content: str):
    \"\"\"Mock file writing.\"\"\"
    with open(path, 'w') as f:
        f.write(content)

def register_process():
    \"\"\"Mock process registration.\"\"\"
    pid = os.getpid()
    os.makedirs("run", exist_ok=True)
    with open("run/agent.pid", "w") as f:
        f.write(str(pid))

def log_action(action: str, details: str):
    \"\"\"Mock action logging.\"\"\"
    print(f"[ACTION] {action}: {details}")
""")

def apply_mock_edit(path: str, edits: list) -> bool:
    """Actually apply edits to the target file for the demo."""
    try:
        with open(path, 'r') as f:
            content = f.read()

        # For demo, replace old_func with new_func
        new_content = content.replace("def old_func():\n    return 1", "def new_func():\n    return 2")

        with open(path, 'w') as f:
            f.write(new_content)

        # Also update the test file to match
        with open("tests/test_target_file.py", 'r') as f:
            test_content = f.read()

        new_test_content = test_content.replace("target_file.old_func()", "target_file.new_func()").replace("self.assertEqual(target_file.old_func(), 1)", "self.assertEqual(target_file.new_func(), 2)").replace("def test_old_func(self):", "def test_new_func(self):").replace("self.assertEqual(target_file.new_func(), 1)", "self.assertEqual(target_file.new_func(), 2)")

        with open("tests/test_target_file.py", 'w') as f:
            f.write(new_test_content)

        print(f"[EDIT] Applied changes to {path} and updated test")
        return True
    except Exception as e:
        print(f"[EDIT] Error: {e}")
        return False

def execute_canon_validator():
    """Execute the Canon Validator with mocked dependencies."""

    # Set up environment variables
    os.environ["AGENT_MODE"] = "PRODUCTION"  # Not shadow mode
    os.environ["MAX_P6_ATTEMPTS"] = "1"
    os.environ["REGRESSION_SUITE_PATH"] = "tests/"

    # Import after creating mocks
    try:
        from canon_validator_engine import execute_dependency_refactor_zlm

        # Mock tools dictionary
        tools = {
            'issues_get_detail': lambda issue_id: json.dumps({
                "file_path": "target_file.py",
                "description": "Test issue"
            }),
            'search_records': lambda *args, **kwargs: json.dumps([]),
            'edit_file': lambda path, edits: apply_mock_edit(path, edits),
            'commit': lambda *args, **kwargs: "mock_commit_hash",
            'string_set': lambda key, value: None,
            'add_observations': lambda observations: print(f"[OBSERVATIONS] {observations}")
        }

        # Fix the undefined new_dependency in the module
        import canon_validator_engine
        canon_validator_engine.new_dependency = "mock_dependency"

        # Create a logger
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("CanonValidator")

        # Execute
        print("\n=== Executing Canon Validator ===")
        result = execute_dependency_refactor_zlm(
            issue_id="ISSUE-721",
            target_file="target_file.py",
            tools=tools,
            logger=logger
        )

        print(f"\n=== Result ===")
        print(json.dumps(result, indent=2))

        # Verify the changes
        print("\n=== Verification ===")
        print("Git log:")
        subprocess.run(["git", "log", "--oneline", "-n", "5"])

        print("\nTarget file content:")
        with open("target_file.py", "r") as f:
            print(f.read())

        return result

    except Exception as e:
        print(f"❌ Error executing Canon Validator: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "FAILED", "reason": str(e)}

def main():
    """Main execution function."""
    print("🚀 Setting up Canon Validator execution environment...")

    # Save original directory
    original_dir = os.getcwd()
    test_dir = None

    try:
        # 1. Setup test environment
        test_dir = setup_test_environment()

        # 2. Create missing dependencies
        print("\n📦 Creating missing dependencies...")
        create_missing_dependencies()

        # 3. Execute Canon Validator
        print("\n⚡ Executing Canon Validator...")
        result = execute_canon_validator()

        if result.get("status") in ["SUCCESS", "refactor_complete", "success"]:
            print("\n✅ Canon Validator executed successfully!")
        else:
            print(f"\n❌ Canon Validator failed: {result.get('reason', 'Unknown error')}")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup
        os.chdir(original_dir)
        if test_dir:
            print(f"\n🧹 Execution complete. Test files remain in: {test_dir}")
        else:
            print(f"\n🧹 Execution complete.")

if __name__ == "__main__":
    main()

