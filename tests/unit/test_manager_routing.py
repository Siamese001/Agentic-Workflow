"""
Test Manager class routing logic.

Validates:
- Manager routes to L4 with cache/state signals
- Manager routes to L3 with workflow/dag signals
- Manager routes to L2 with tool/subprocess signals
"""

import pytest


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
