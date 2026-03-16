"""
Test Manager class routing logic.

Validates:
- Manager routes to L4 with cache/state signals
- Manager routes to L3 with workflow/dag signals
- Manager routes to L2 with tool/subprocess signals
"""

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_manager_routing")
_emit_applies_guardrail("p0", "test_manager_routing", "p0_governance")
_emit_reads_policy_state("p0", "test_manager_routing", "policy_binding")
_emit_snapshots_state("p0", "test_manager_routing", "state_snapshot")
emit_replay_key("p0", "test_manager_routing")
emit_determinism_digest("p0", "test_manager_routing")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_manager_routing", "execution_auth")
_emit_validates_capability("p2", "test_manager_routing", "capability_check")
_emit_routes_to_capability("p2", "test_manager_routing", "capability_route")
_emit_writes_via_uwg("p2", "test_manager_routing", "uwg_write")
_emit_blocks_direct_write("p2", "test_manager_routing", "direct_write_block")
_emit_records_tool_invocation("p2", "test_manager_routing", "tool_invocation")
_emit_captures_execution_output("p2", "test_manager_routing", "exec_output")
_emit_dispatches_agent("p3", "test_manager_routing", "agent_dispatch")
_emit_coordinates_agents("p3", "test_manager_routing", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_manager_routing", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_manager_routing", "healing_outcome")
_emit_escalates_failure("p3", "test_manager_routing", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_manager_routing", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_manager_routing", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_manager_routing", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_manager_routing", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_manager_routing", "eval_metric")
_emit_stores_embedding("p4", "test_manager_routing", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_manager_routing", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_manager_routing", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestManagerRoutingSignals:
    """Tests for Manager routing based on content signals."""

    @pytest.fixture
    def mock_fca(self):
        """Create a mock FCA for testing suggest_manager_layer."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        return FileClassificationAgent()

    def test_manager_with_cache_signals_routes_to_l4(self, mock_fca, tmp_path):
        """Manager with cache/state signals should route to L4."""
        content = '''"""Manager with cache signals."""

class CacheManager:
    def __init__(self):
        self.cache = {}
        self.state = {}

    def persist(self):
        pass
'''
        test_file = tmp_path / "cache_manager.py"
        test_file.write_text(content)

        result = mock_fca.suggest_manager_layer(test_file)
        assert result == "L4_state", f"Expected L4_state, got {result}"

    def test_manager_with_workflow_signals_routes_to_l3(self, mock_fca, tmp_path):
        """Manager with workflow/dag signals should route to L3."""
        content = '''"""Manager with workflow signals."""

class WorkflowManager:
    def __init__(self):
        self.workflow = []
        self.dag = None
        self.pipeline = []

    def orchestrate(self):
        pass
'''
        test_file = tmp_path / "workflow_manager.py"
        test_file.write_text(content)

        result = mock_fca.suggest_manager_layer(test_file)
        assert result == "L3_orchestration", f"Expected L3_orchestration, got {result}"

    def test_manager_with_subprocess_signals_routes_to_l2(self, mock_fca, tmp_path):
        """Manager with subprocess/tool signals should route to L2."""
        content = '''"""Manager with subprocess signals."""
import subprocess

class ToolManager:
    def __init__(self):
        self.tool_registry = {}

    def execute(self, cmd):
        return subprocess.run(cmd)
'''
        test_file = tmp_path / "tool_manager.py"
        test_file.write_text(content)

        result = mock_fca.suggest_manager_layer(test_file)
        assert result == "L2_execution", f"Expected L2_execution, got {result}"

    def test_manager_with_weak_signals_returns_none(self, mock_fca, tmp_path):
        """Manager with weak/no signals should return None."""
        content = '''"""Manager with no strong signals."""

class GenericManager:
    def __init__(self):
        self.data = {}

    def process(self):
        pass
'''
        test_file = tmp_path / "generic_manager.py"
        test_file.write_text(content)

        result = mock_fca.suggest_manager_layer(test_file)
        assert result is None, f"Expected None for weak signals, got {result}"

    def test_manager_with_mixed_signals_uses_strongest(self, mock_fca, tmp_path):
        """Manager with mixed signals should use the strongest signal."""
        content = '''"""Manager with mixed signals - L4 strongest."""

class HybridManager:
    def __init__(self):
        self.cache = {}
        self.state = {}
        self.memory = {}
        self.ledger = {}
        self.checkpoint = {}
        # Only one L3 signal
        self.workflow = []
'''
        test_file = tmp_path / "hybrid_manager.py"
        test_file.write_text(content)

        result = mock_fca.suggest_manager_layer(test_file)
        # L4 has more signals (cache, state, memory, ledger, checkpoint) than L3 (workflow)
        assert result == "L4_state", f"Expected L4_state for strongest signal, got {result}"


class TestManagerRoutingEdgeCases:
    """Edge case tests for Manager routing."""

    @pytest.fixture
    def mock_fca(self):
        """Create a mock FCA for testing."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        return FileClassificationAgent()

    def test_nonexistent_file_returns_none(self, mock_fca, tmp_path):
        """Non-existent file should return None."""
        result = mock_fca.suggest_manager_layer(tmp_path / "nonexistent.py")
        assert result is None

    def test_empty_file_returns_none(self, mock_fca, tmp_path):
        """Empty file should return None."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        result = mock_fca.suggest_manager_layer(test_file)
        assert result is None

    def test_binary_file_returns_none(self, mock_fca, tmp_path):
        """Binary file should return None gracefully."""
        test_file = tmp_path / "binary.py"
        test_file.write_bytes(b"\x00\x01\x02\x03")

        result = mock_fca.suggest_manager_layer(test_file)
        assert result is None
