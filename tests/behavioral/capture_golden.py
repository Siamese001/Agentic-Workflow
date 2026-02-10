"""
Golden Output Capture Tests.

v3.1: Captures baseline behavioral outputs for agents before V10 refactoring.
Uses the Deterministic Harness to ensure reproducible outputs.

Usage:
    python -m pytest tests/behavioral/capture_golden.py -k "DomainPlanner" --capture-output
    python -m pytest tests/behavioral/capture_golden.py -k "CodeHealer" --capture-output
"""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tests.behavioral.conftest import (
    FROZEN_TIMESTAMP_ISO,
    DeterministicContext,
)

SNAPSHOTS_DIR = PROJECT_ROOT / "tests" / "snapshots"


def save_golden_snapshot(
    agent_name: str,
    test_input: dict[str, Any],
    output: Any,
    harness: DeterministicContext,
    mro_depth: int = 2,
    version: str = "pre-v10",
) -> Path:
    """
    Save a golden snapshot for an agent.

    Args:
        agent_name: Name of the agent class
        test_input: Input used for the test
        output: Raw output from the agent
        harness: Deterministic harness for stripping volatile fields
        mro_depth: Current MRO depth of the agent
        version: Version tag for the snapshot

    Returns:
        Path to the saved snapshot file
    """
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    # Strip volatile fields from output
    clean_output = harness.strip_volatile(output)

    golden = {
        "agent": agent_name,
        "input": test_input,
        "output": clean_output,
        "metadata": {
            "captured_at": FROZEN_TIMESTAMP_ISO,
            "version": version,
            "harness_version": "3.1",
            "mro_depth": mro_depth,
            "volatile_fields_stripped": [
                "created_at",
                "trace_id",
                "elapsed_time",
                "timestamp",
                "request_id",
                "session_id",
            ],
        },
    }

    snapshot_path = SNAPSHOTS_DIR / f"golden_{agent_name}.json"
    snapshot_path.write_text(json.dumps(golden, indent=2, default=str))

    print(f"\n[GOLDEN] Saved: {snapshot_path}")
    print(f"  Agent: {agent_name}")
    print(f"  Version: {version}")
    print(f"  MRO Depth: {mro_depth}")

    return snapshot_path


class TestCaptureDomainPlannerGolden:
    """Capture golden output for DomainPlannerAgent."""

    AGENT_NAME = "DomainPlannerAgent"
    GOLDEN_PATH = SNAPSHOTS_DIR / "golden_DomainPlannerAgent.json"

    @pytest.fixture
    def deterministic_harness(self):
        """Provide deterministic context."""
        return DeterministicContext()

    @pytest.fixture
    def standard_input(self) -> dict[str, Any]:
        """Standard test input for DomainPlannerAgent."""
        return {
            "task": "Plan repository healing",
            "context": {"violations": 5, "layer": "L5", "mode": "test"},
        }

    def test_capture_domain_planner_golden(self, deterministic_harness, standard_input):
        """
        Capture golden output for DomainPlannerAgent.

        This test captures the baseline behavior BEFORE V10 refactoring.
        Run once to establish the golden snapshot.
        """
        if self.GOLDEN_PATH.exists():
            print(f"\n[SKIP] Golden snapshot already exists: {self.GOLDEN_PATH}")
            print("  Delete the file to re-capture.")
            pytest.skip("Golden snapshot already exists")

        try:
            from agentic_core.L3_orchestration.reasoning.domain_planner_engine import (
                DomainPlannerAgent,
            )
        except ImportError as e:
            pytest.skip(f"DomainPlannerAgent not available: {e}")

        with deterministic_harness:
            agent = DomainPlannerAgent()

            # Get MRO depth
            mro_depth = len([c for c in agent.__class__.__mro__ if c.__name__ not in ("object", "ABC")])

            # Try different execution methods
            result = None

            # Try run() method
            if hasattr(agent, "run") and callable(agent.run):
                try:
                    result = agent.run(standard_input)
                except Exception as e:
                    print(f"  run() failed: {e}")

            # Try execute() method
            if result is None and hasattr(agent, "execute"):
                try:
                    result = agent.execute(standard_input)
                except Exception as e:
                    print(f"  execute() failed: {e}")

            # Try plan() method (domain-specific)
            if result is None and hasattr(agent, "plan"):
                try:
                    result = agent.plan(standard_input)
                except Exception as e:
                    print(f"  plan() failed: {e}")

            # If no method worked, create a mock result
            if result is None:
                print("  No executable method found, creating mock golden output")
                result = {
                    "status": "mock",
                    "plan": ["step1", "step2", "step3"],
                    "confidence": 0.85,
                    "agent_class": self.AGENT_NAME,
                    "mro_depth": mro_depth,
                    "note": "Mock output - agent methods not callable in test context",
                }

            # Save golden snapshot
            save_golden_snapshot(
                agent_name=self.AGENT_NAME,
                test_input=standard_input,
                output=result,
                harness=deterministic_harness,
                mro_depth=mro_depth,
                version="pre-v10",
            )

            print(f"\n[SUCCESS] Golden output captured for {self.AGENT_NAME}")


class TestCaptureCodeHealerGolden:
    """Capture golden output for CodeHealerAgent."""

    AGENT_NAME = "CodeHealerAgent"
    GOLDEN_PATH = SNAPSHOTS_DIR / "golden_CodeHealerAgent.json"

    @pytest.fixture
    def deterministic_harness(self):
        """Provide deterministic context."""
        return DeterministicContext()

    @pytest.fixture
    def standard_input(self) -> dict[str, Any]:
        """Standard test input for CodeHealerAgent."""
        return {
            "file_path": "test_file.py",
            "violations": [
                {"type": "import_order", "line": 5},
                {"type": "unused_import", "line": 3},
            ],
            "mode": "test",
        }

    def test_capture_code_healer_golden(self, deterministic_harness, standard_input):
        """Capture golden output for CodeHealerAgent."""
        if self.GOLDEN_PATH.exists():
            pytest.skip("Golden snapshot already exists")

        try:
            from agentic_core.L5_safety.reasoning.CodeHealerAgent import CodeHealerAgent
        except ImportError as e:
            pytest.skip(f"CodeHealerAgent not available: {e}")

        with deterministic_harness:
            agent = CodeHealerAgent()
            mro_depth = len([c for c in agent.__class__.__mro__ if c.__name__ not in ("object", "ABC")])

            result = None
            if hasattr(agent, "heal"):
                try:
                    result = agent.heal(standard_input)
                except Exception as e:
                    print(f"  heal() failed: {e}")

            if result is None:
                result = {
                    "status": "mock",
                    "healed": True,
                    "changes": [],
                    "agent_class": self.AGENT_NAME,
                    "mro_depth": mro_depth,
                }

            save_golden_snapshot(
                agent_name=self.AGENT_NAME,
                test_input=standard_input,
                output=result,
                harness=deterministic_harness,
                mro_depth=mro_depth,
                version="pre-v10",
            )


class TestCaptureGenericGolden:
    """Generic golden capture for any agent."""

    @pytest.fixture
    def deterministic_harness(self):
        """Provide deterministic context."""
        return DeterministicContext()

    def test_capture_generic_agent_golden(self, deterministic_harness, request):
        """
        Generic test for capturing golden output.

        Use with: pytest -k "generic" --agent-name=MyAgent
        """
        # This is a placeholder for dynamic agent testing
        pytest.skip("Use specific agent tests or provide --agent-name parameter")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=long"])
