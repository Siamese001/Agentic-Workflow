#!/usr/bin/env python3
"""
Heal Surface Enforcement Test - Regression Guard

Phase 1, Wave 3: Ensures all Agent classes have discoverable heal surfaces.

This test uses AST-only scanning (no runtime imports) to verify that every
Agent class has both heal() and heal_repository() methods defined, either
directly or via known base classes.

Acceptance criteria:
- Fails if any Agent lacks heal() or heal_repository() after Phase 1 completion
- Uses deterministic AST scanning (no runtime imports)
- Provides clear error messages for missing methods
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.governance


def run_audit_cli() -> dict:
    """Run the audit CLI and return parsed JSON output."""
    cmd = [
        sys.executable,
        "-m",
        "agentic_core.L5_safety.enforcement.governance.agent_heal_audit",
        "--format",
        "json",
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent.parent,
    )

    if result.returncode != 0:
        pytest.fail(f"Audit CLI failed: {result.stderr}")

    return json.loads(result.stdout)


# No exemption lists - we use the audit tool's deterministic runtime-agent classification


class TestHealSurfaceEnforcement:
    """Regression tests for heal surface availability."""

    def test_all_agents_have_heal_surface(self):
        """Verify all runtime agents have heal() method."""
        audit_data = run_audit_cli()

        missing_heal = []
        # Only check runtime agents, not protocols/interfaces/models
        for agent in audit_data["runtime_agents"]:
            if not agent["has_heal"]:
                missing_heal.append(f"{agent['repo_relative_path']}:{agent['class_name']} ({agent['classification_reason']})")

        assert not missing_heal, "Runtime agents missing heal() method:\n" + "\n".join(
            f"  - {m}" for m in sorted(missing_heal)
        )

    def test_all_agents_have_heal_repository_surface(self):
        """Verify all runtime agents have heal_repository() method."""
        audit_data = run_audit_cli()

        missing_heal_repo = []
        # Only check runtime agents, not protocols/interfaces/models
        for agent in audit_data["runtime_agents"]:
            if not agent["has_heal_repository"]:
                missing_heal_repo.append(f"{agent['repo_relative_path']}:{agent['class_name']} ({agent['classification_reason']})")

        assert not missing_heal_repo, "Runtime agents missing heal_repository() method:\n" + "\n".join(
            f"  - {m}" for m in sorted(missing_heal_repo)
        )

    def test_audit_determinism(self):
        """Verify audit output is deterministic across runs."""
        result1 = run_audit_cli()
        result2 = run_audit_cli()

        # Convert to JSON for comparison
        json1 = json.dumps(result1, sort_keys=True)
        json2 = json.dumps(result2, sort_keys=True)

        assert json1 == json2, "Audit output not deterministic"

    def test_summary_counts_consistent(self):
        """Verify summary counts are logically consistent."""
        audit_data = run_audit_cli()
        summary = audit_data["summary"]

        runtime_summary = summary["runtime_agents"]
        all_summary = summary["all_classes"]

        # Runtime agent counts
        assert runtime_summary["total"] >= runtime_summary["missing_heal"]
        assert runtime_summary["total"] >= runtime_summary["missing_heal_repository"]
        assert runtime_summary["total"] >= runtime_summary["missing_both"]
        assert runtime_summary["missing_both"] <= runtime_summary["missing_heal"]
        assert runtime_summary["missing_both"] <= runtime_summary["missing_heal_repository"]

        # Overall counts
        assert all_summary["total"] == all_summary["runtime_count"] + all_summary["non_agent_count"]
        assert all_summary["runtime_count"] == runtime_summary["total"]
