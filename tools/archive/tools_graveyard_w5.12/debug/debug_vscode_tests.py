#!/usr/bin/env python3
"""
Debug script to verify VS Code test discovery configuration
"""

import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run command and return result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:  # guardian: allow-broad-exception -- offline tooling, reports failure
        return 1, "", str(e)


def main():
    print("=== VS Code Test Discovery Debug ===\n")

    # 1. Check Python environment
    print("1. Python Environment:")
    print(f"   Python: {sys.executable}")
    print(f"   Version: {sys.version}")

    # 2. Check pytest
    returncode, stdout, stderr = run_command("python -m pytest --version")
    if returncode == 0:
        print(f"   Pytest: {stdout.strip()}")
    else:
        print(f"   Pytest error: {stderr}")

    # 3. Check test discovery
    print("\n2. Test Discovery:")
    returncode, stdout, stderr = run_command(
        "python -m pytest tests/test_vscode_discovery.py --collect-only -q"
    )
    if returncode == 0:
        lines = stdout.strip().split("\n")
        for line in lines:
            if "collected" in line:
                print(f"   Simple test: {line.strip()}")
                break
    else:
        print(f"   Discovery error: {stderr}")

    # 4. Check full test suite
    returncode, stdout, stderr = run_command("python -m pytest tests/ --collect-only -q")
    if returncode == 0:
        lines = stdout.strip().split("\n")
        for line in lines:
            if "collected" in line:
                print(f"   Full suite: {line.strip()}")
                break
    else:
        print(f"   Full suite error: {stderr}")

    # 5. Check configuration files
    print("\n3. Configuration Files:")

    # pytest.ini
    pytest_ini = Path("pytest.ini")
    if pytest_ini.exists():
        print("   ✓ pytest.ini exists")
        with open(pytest_ini) as f:
            content = f.read()
            if "testpaths = tests" in content:
                print("   ✓ testpaths configured")
            if "python_files = test_*.py *_test.py" in content:
                print("   ✓ file patterns configured")
    else:
        print("   ✗ pytest.ini missing")

    # VS Code settings
    vscode_settings = Path(".vscode/settings.json")
    if vscode_settings.exists():
        print("   ✓ .vscode/settings.json exists")
        with open(vscode_settings) as f:
            settings = json.load(f)
            if settings.get("python.testing.pytestEnabled"):
                print("   ✓ pytest enabled in VS Code")
            if settings.get("python.testing.unittestEnabled") == False:
                print("   ✓ unittest disabled in VS Code")
    else:
        print("   ✗ .vscode/settings.json missing")

    # 6. Test files
    print("\n4. Test Files:")
    test_file = Path("tests/test_vscode_discovery.py")
    if test_file.exists():
        print("   ✓ test_vscode_discovery.py exists")
    else:
        print("   ✗ test_vscode_discovery.py missing")

    print("\n=== Debug Complete ===")
    print("\nNext steps:")
    print("1. Open VS Code")
    print("2. Open the workspace file: agentic-workflow.code-workspace")
    print("3. Run: Ctrl+Shift+P → 'Developer: Reload Window'")
    print("4. Open Testing panel (beaker icon)")
    print("5. Click refresh icon 🔄")


if __name__ == "__main__":
    main()
