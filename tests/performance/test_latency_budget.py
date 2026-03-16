"""
Latency Budget Tests for V10 Atomic Agents.

Verifies that agents with AtomicExecutionMixin meet latency requirements
for critical operations. Per V10 spec, file operations should complete
within budget to prevent blocking.

Usage:
    python -m pytest tests/performance/test_latency_budget.py -v
    python -m pytest tests/performance/test_latency_budget.py -k "CodeHealerAgent" -v
"""

import tempfile
import time
from pathlib import Path

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_latency_budget")
_emit_applies_guardrail("p0", "test_latency_budget", "p0_governance")
_emit_reads_policy_state("p0", "test_latency_budget", "policy_binding")
_emit_snapshots_state("p0", "test_latency_budget", "state_snapshot")
emit_replay_key("p0", "test_latency_budget")
emit_determinism_digest("p0", "test_latency_budget")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

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
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("# Test file\nprint('hello')\n")
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()

    def test_atomic_execution_mixin_import_latency(self):
        """Test that AtomicExecutionMixin can be imported quickly."""
        start = time.perf_counter()
        from agentic_core.mixins.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        elapsed = time.perf_counter() - start

        assert elapsed < 1.0, f"Import took {elapsed:.3f}s, budget is 1.0s"
        assert AtomicExecutionMixin is not None

    def test_CodeHealerAgent_instantiation_latency(self):
        """Test CodeHealerAgent instantiation meets latency budget."""
        start = time.perf_counter()
        try:
            from agentic_core.L5_safety.reasoning.CodeHealerAgent import (
                CodeHealerAgent,
            )

            agent = CodeHealerAgent()
            elapsed = time.perf_counter() - start

            assert elapsed < 2.0, f"Instantiation took {elapsed:.3f}s, budget is 2.0s"
            assert agent is not None
        except (ImportError, AttributeError, TypeError) as e:
            pytest.fail(f"CodeHealerAgent not available: {e}")

    def test_file_hash_computation_latency(self, temp_file):
        """Test file hash computation meets latency budget."""
        from agentic_core.mixins.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        class TestAgent(AtomicExecutionMixin):
            pass

        agent = TestAgent()

        start = time.perf_counter()
        file_hash = agent._compute_file_hash(temp_file)
        elapsed = time.perf_counter() - start

        assert elapsed < LATENCY_BUDGETS["file_hash"], (
            f"Hash computation took {elapsed:.3f}s, budget is {LATENCY_BUDGETS['file_hash']}s"
        )
        assert file_hash is not None

    def test_atomic_write_latency(self, temp_file):
        """Test atomic write operation meets latency budget."""
        from agentic_core.mixins.atomic_execution_mixin import (
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
            f"Atomic write took {elapsed:.3f}s, budget is {LATENCY_BUDGETS['atomic_write']}s"
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
        from agentic_core.mixins.atomic_execution_mixin import (
            AtomicExecutionMixin,
        )

        agent_imports = {
            "CodeHealerAgent": (
                "agentic_core.L5_safety.reasoning.CodeHealerAgent",
                "CodeHealerAgent",
            ),
            "VerificationGate": (
                "agentic_core.L5_safety.enforcement.verification_gate",
                "VerificationGate",
            ),
            "LocationAgent": (
                "agentic_core.L5_safety.reasoning.LocationAgent",
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
            pytest.fail(f"Could not import {agent_name}: {e}")
