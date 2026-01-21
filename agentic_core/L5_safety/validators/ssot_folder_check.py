#!/usr/bin/env python3
"""
SSOT Folder Structure Check - CLI Entry Point

This script is designed to be run by pre-commit hooks and CI pipelines.
It invokes the FilesystemSSOTReconcilerAgent in 'CI Verification' mode.

Returns:
    0: If structure is compliant.
    1: If drift/violations are detected.
"""

import asyncio
import sys
from pathlib import Path

from agentic_core.L5_safety.validators.FilesystemSSOTReconcilerAgent import (
    FilesystemSSOTReconcilerAgent,
)


async def main():
    project_root = Path(".").resolve()
    print(f"Running SSOT Folder Verification on: {project_root}")

    agent = FilesystemSSOTReconcilerAgent(project_root)
    is_compliant = await agent.run_ci_verification()

    if is_compliant:
        print("[OK] SSOT Structure Verified.")
        sys.exit(0)
    else:
        print("[X] SSOT Violations Detected. Run 'HierarchyAgent' to inspect.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
