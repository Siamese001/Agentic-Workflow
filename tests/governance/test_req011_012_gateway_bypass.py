"""REQ-011/012: Gateway bypass protection.

Assert AST scan finds 0 direct SDK imports outside allowlisted gateway paths;
negative control ensures the scan itself works.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
CI_SCRIPT = REPO_ROOT / "ops_scripts" / "ci" / "check_llm_sdk_imports.py"


@pytest.mark.governance
def test_gateway_bypass_ast_scan_finds_no_violations():
    """REQ-011/012: AST scan should find zero SDK imports outside allowed paths."""
    # Run the CI script
    result = subprocess.run(
        [sys.executable, str(CI_SCRIPT)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )

    # Should pass with no violations
    assert result.returncode == 0, f"CI script failed: {result.stderr}"
    assert "OK: no forbidden LLM/network SDK imports" in result.stdout


@pytest.mark.governance
def test_gateway_bypass_negative_control():
    """REQ-011/012: Negative control - scan should detect violations when present."""
    # Create a temporary file in a scanned directory
    temp_file = REPO_ROOT / "agentic_core" / "temp_test_blocked_import.py"
    try:
        temp_file.write_text("import openai\nimport google.generativeai\n")

        # Run the CI script
        result = subprocess.run(
            [sys.executable, str(CI_SCRIPT)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )

        # Should fail and detect violations
        assert result.returncode == 1, "CI script should have detected violations"
        assert "blocked import" in result.stdout
        assert "openai" in result.stdout
        # google.generativeai may not be reported if script stops at first violation per file

    finally:
        # Clean up
        if temp_file.exists():
            temp_file.unlink()


@pytest.mark.governance
def test_gateway_bypass_allowed_paths_honored():
    """REQ-011/012: Verify allowed paths are properly exempt from scanning."""
    # Check that SovereignLLMGateway.py can contain SDK imports
    gateway_file = REPO_ROOT / "agentic_core" / "L2_execution" / "enforcement" / "SovereignLLMGateway.py"

    if gateway_file.exists():
        # Parse the file
        tree = ast.parse(gateway_file.read_text(encoding="utf-8", errors="replace"))

        # Look for any imports that would be blocked elsewhere
        sdk_imports_found = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in ("openai", "anthropic", "google.generativeai"):
                            sdk_imports_found.append(alias.name)
                elif node.module and node.module in ("openai", "anthropic", "google.generativeai"):
                    sdk_imports_found.append(node.module)

        # If SDK imports are found, that's OK in the gateway file
        # The important thing is the CI script doesn't flag it
        result = subprocess.run(
            [sys.executable, str(CI_SCRIPT)],
            cwd=str(REPO_ROOT),
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, f"Gateway file should be allowed: {result.stderr}"


@pytest.mark.governance
def test_gateway_bypass_scan_coverage():
    """REQ-011/012: Verify scan covers all critical directories."""
    # Read the CI script to check SCAN_ROOTS
    script_content = CI_SCRIPT.read_text()

    # Verify it scans the key directories
    expected_roots = ["agentic_core", "apps_lic", "apps_rg", "apps_shared", "system_learning"]
    for root in expected_roots:
        assert f'"{root}"' in script_content, f"SCAN_ROOTS should include {root}"

    # Verify it has the proper blocked imports
    blocked_imports = ["openai", "anthropic", "requests", "httpx", "aiohttp"]
    for imp in blocked_imports:
        assert f'"{imp}"' in script_content, f"Should block {imp}"

    # Verify google.generativeai is blocked as tuple
    assert '("google", "generativeai")' in script_content, "Should block google.generativeai as tuple"
