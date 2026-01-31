#!/usr/bin/env python3
"""
Deterministic Guardian Test for Critical Core Components
Tests that all critical system files exist and are accessible.
"""
import sys
from pathlib import Path

# Critical files that must exist for system integrity
CRITICAL_FILES = [
    "agentic_core/L3_orchestration/workflow_engines/mcp_router_sovereign.py",
    "agentic_core/L5_safety/guardrails/mcp_sovereign.py",
    "agentic_core/L4_state/semantic_memory/pinecone_mcp_client.py",
    "agentic_core/L4_state/knowledge_graph/SovereignGraphClient.py",
    "agentic_core/L6_observability/deepwiki_client_sovereign.py",
    "agentic_core/L1_cognition/thought_engine/StrategicPlannerAgent.py",
    "agentic_core/L2_execution/tool_registry/WebSearchTools.py",
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
    
    print(f"\nSUMMARY:")
    print(f"Total files: {len(CRITICAL_FILES)}")
    print(f"Found: {len(existing_files)}")
    print(f"Missing: {len(missing_files)}")
    
    if missing_files:
        print(f"\nVIOLATION: Critical files missing:")
        for file in missing_files:
            print(f"  - {file}")
        sys.exit(1)
    else:
        print("\nCOMPLIANT: All critical files exist")
        sys.exit(0)


if __name__ == "__main__":
    test_critical_files_exist()
