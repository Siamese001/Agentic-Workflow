#!/usr/bin/env python3
"""
Deterministic Guardian Test for Critical Core Components
Tests that all critical system files exist and are accessible.
"""

from pathlib import Path

# Critical files that must exist for system integrity (updated to match current structure)
CRITICAL_FILES = [
    "agentic_core/L3_orchestration/engine/SovereignMcpRouterAgent.py",
    "agentic_core/L5_safety/security/mcp_sovereign_authority.py",
    "agentic_core/L2_execution/mcp/SovereignPineconeMcpClientAgent.py",
    "agentic_core/L2_execution/mcp/SovereignMCPGatewayAgent.py",
    "agentic_core/L2_execution/engine/WebSearchTools.py",
    "agentic_core/base_agents/SovereignBaseAgent.py",
]


def test_critical_files_exist() -> None:
    """
    Test that all critical system files exist.

    Raises:
        SystemExit: 1 if any files missing, 0 if all exist
    """
    missing_files = []
    existing_files = []

    for filepath in CRITICAL_FILES:
        file_path = Path(filepath)
        if file_path.exists():
            existing_files.append(filepath)
            print(f"✅ FOUND: {filepath}")
        else:
            missing_files.append(filepath)
            print(f"❌ MISSING: {filepath}")

    print("\nSUMMARY:")
    print(f"Total files: {len(CRITICAL_FILES)}")
    print(f"Found: {len(existing_files)}")
    print(f"Missing: {len(missing_files)}")

    if missing_files:
        print("\nVIOLATION: Critical files missing:")
        for file in missing_files:
            print(f"  - {file}")
        assert False, f"Missing {len(missing_files)} critical files"
    else:
        print("\nCOMPLIANT: All critical files exist")


if __name__ == "__main__":
    test_critical_files_exist()
