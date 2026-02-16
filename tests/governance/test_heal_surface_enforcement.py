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


# Known base classes that provide heal/heal_repository via inheritance
# These are checked at runtime, not via AST
KNOWN_HEAL_PROVIDERS = frozenset(
    {
        "SovereignBaseAgent",
        "LICAgentBase",
        "RGAgentBase",
        "LocationHealerAgent",
    }
)

# Known protocol/interface classes that are exempt from heal requirements
# These define contracts, not implementations
KNOWN_PROTOCOL_CLASSES = frozenset(
    {
        "IOrchestratorAgent",
        "ITieredAgent",
        "IAgent",
        "Protocol",
    }
)

# Known Pydantic/dataclass models that happen to end with "Agent" but aren't agents
KNOWN_MODEL_CLASSES = frozenset(
    {
        "GateDecisionAgent",
        "GenerationAgent",
        "ProfileAnalysisAgent",
        "QAReportAgent",
        "ResearchAgent",
        "RoutingAgent",
        "SenderGroundingAgent",
        "ValidationAgent",
    }
)

# Known legacy/stub classes that are exempt (with justification)
KNOWN_EXEMPT_CLASSES = frozenset(
    {
        "BaseAgent",  # Abstract interface in apps_shared
        "AppContentValidatorAgent",  # Type definition, not runtime agent
        "CompetitorReconAgent",  # Type definition, not runtime agent
        "StackModernizationAgent",  # Type definition, not runtime agent
        "GapClosureArchitectAgent",  # Type definition, not runtime agent
    }
)


class TestHealSurfaceEnforcement:
    """Regression tests for heal surface availability."""

    def test_all_agents_have_heal_surface(self):
        """Verify all agents have heal() method (directly or via inheritance)."""
        audit_data = run_audit_cli()

        missing_heal = []
        for agent in audit_data["audit_results"]:
            if agent["has_heal"]:
                continue

            class_name = agent["class_name"]
            bases = set(agent["base_class_names"])

            # Skip protocols/interfaces
            if class_name in KNOWN_PROTOCOL_CLASSES:
                continue
            if bases & {"Protocol", "ABC"}:
                continue

            # Skip known model classes
            if class_name in KNOWN_MODEL_CLASSES:
                continue
            if "BaseModel" in bases:
                continue

            # Skip known exempt classes
            if class_name in KNOWN_EXEMPT_CLASSES:
                continue

            # Check if inherits from known heal provider
            if bases & KNOWN_HEAL_PROVIDERS:
                continue

            missing_heal.append(f"{agent['repo_relative_path']}:{agent['class_name']}")

        assert not missing_heal, "Agents missing heal() method:\n" + "\n".join(
            f"  - {m}" for m in sorted(missing_heal)
        )

    def test_all_agents_have_heal_repository_surface(self):
        """Verify all agents have heal_repository() method (directly or via inheritance)."""
        audit_data = run_audit_cli()

        missing_heal_repo = []
        for agent in audit_data["audit_results"]:
            if agent["has_heal_repository"]:
                continue

            class_name = agent["class_name"]
            bases = set(agent["base_class_names"])

            # Skip protocols/interfaces
            if class_name in KNOWN_PROTOCOL_CLASSES:
                continue
            if bases & {"Protocol", "ABC"}:
                continue

            # Skip known model classes
            if class_name in KNOWN_MODEL_CLASSES:
                continue
            if "BaseModel" in bases:
                continue

            # Skip known exempt classes
            if class_name in KNOWN_EXEMPT_CLASSES:
                continue

            # Check if inherits from known heal provider
            if bases & KNOWN_HEAL_PROVIDERS:
                continue

            missing_heal_repo.append(f"{agent['repo_relative_path']}:{agent['class_name']}")

        assert not missing_heal_repo, "Agents missing heal_repository() method:\n" + "\n".join(
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

        assert summary["total_agents"] >= summary["missing_heal"]
        assert summary["total_agents"] >= summary["missing_heal_repository"]
        assert summary["total_agents"] >= summary["missing_both"]
        assert summary["missing_both"] <= summary["missing_heal"]
        assert summary["missing_both"] <= summary["missing_heal_repository"]
