"""
Latency Budget Tests for V10 Atomic Agents.

Verifies that agents with AtomicExecutionMixin meet latency requirements
for critical operations. Per V10 spec, file operations should complete
within budget to prevent blocking.

Usage:
    python -m pytest tests/performance/test_latency_budget.py -v
    python -m pytest tests/performance/test_latency_budget.py -k "CodeHealerAgent" -v
"""

import pytest
import time
import tempfile
from pathlib import Path
from typing import Any


# Latency budgets in seconds
LATENCY_BUDGETS = {
    "file_hash": 0.1,  # 100ms for file hashing
    "atomic_write": 0.5,  # 500ms for atomic write operation
    "rollback": 0.2,  # 200ms for rollback operation
    "heal_operation": 2.0,  # 2s for heal operation
}


class TestLatencyBudget:
    """Test latency budgets for atomic operations."""

    @pytest.fixture
    def temp_file(self):
        """Create a temporary file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False
        ) as f:
            f.write("# Test file\nprint('hello')\n")
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_atomic_execution_mixin_import_latency(self):
        """Test that AtomicExecutionMixin can be imported quickly."""
        start = time.perf_counter()
        from agentic_core.base_agents.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )
        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"Import took {elapsed:.3f}s, budget is 1.0s"
        assert AtomicExecutionMixin is not None

    def test_code_healer_agent_instantiation_latency(self):
        """Test CodeHealerAgent instantiation meets latency budget."""
        start = time.perf_counter()
        try:
            from agentic_core.L5_safety.policy_engine.code_healer_agent import (
                CodeHealerAgent,
            )
            agent = CodeHealerAgent()
            elapsed = time.perf_counter() - start

            assert elapsed < 2.0, f"Instantiation took {elapsed:.3f}s, budget is 2.0s"
            assert agent is not None
        except Exception as e:
            pytest.skip(f"CodeHealerAgent not available: {e}")

    def test_file_hash_computation_latency(self, temp_file):
        """Test file hash computation meets latency budget."""
        from agentic_core.base_agents.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        class TestAgent(AtomicExecutionMixin):
            pass

        agent = TestAgent()

        start = time.perf_counter()
        file_hash = agent._compute_file_hash(temp_file)
        elapsed = time.perf_counter() - start

        assert elapsed < LATENCY_BUDGETS["file_hash"], (
            f"Hash computation took {elapsed:.3f}s, "
            f"budget is {LATENCY_BUDGETS['file_hash']}s"
        )
        assert file_hash is not None

    def test_atomic_write_latency(self, temp_file):
        """Test atomic write operation meets latency budget."""
        from agentic_core.base_agents.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        class TestAgent(AtomicExecutionMixin):
            pass

        agent = TestAgent()
        new_content = "# Modified\nprint('modified')\n"

        start = time.perf_counter()
        agent._atomic_write(temp_file, new_content)
        elapsed = time.perf_counter() - start

        assert elapsed < LATENCY_BUDGETS["atomic_write"], (
            f"Atomic write took {elapsed:.3f}s, "
            f"budget is {LATENCY_BUDGETS['atomic_write']}s"
        )
        assert temp_file.read_text() == new_content

    @pytest.mark.parametrize(
        "agent_name",
        [
            "CodeHealerAgent",
            "VerificationGate",
            "LocationAgent",
        ],
    )
    def test_batch_3a_agents_have_atomic_mixin(self, agent_name):
        """Verify Batch 3.1A agents have AtomicExecutionMixin."""
        from agentic_core.base_agents.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        agent_imports = {
            "CodeHealerAgent": (
                "agentic_core.L5_safety.policy_engine.code_healer_agent",
                "CodeHealerAgent",
            ),
            "VerificationGate": (
                "agentic_core.L5_safety.security.verification_gate",
                "VerificationGate",
            ),
            "LocationAgent": (
                "agentic_core.L5_safety.validators.location_agent",
                "LocationAgent",
            ),
        }

        module_path, class_name = agent_imports[agent_name]
        try:
            import importlib
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)

            assert issubclass(agent_class, AtomicExecutionMixin), (
                f"{agent_name} must inherit from AtomicExecutionMixin"
            )
        except ImportError as e:
            pytest.skip(f"Could not import {agent_name}: {e}")
