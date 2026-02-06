"""
Dashboard Frontend Tests (Phase 3-4)
====================================

Tests for dashboard frontend components.

Migrated from: agentic_core/L0_maintenance/scripts/test_phase3_phase4_frontend.py
"""

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.mark.dashboard
class TestMetaLearningPanel:
    """Test Meta-Learning Panel JavaScript components."""

    def test_meta_learning_panel_js_exists(self, js_dir):
        """Verify meta-learning-panel.js exists."""
        js_file = js_dir / "components" / "meta-learning-panel.js"
        assert js_file.exists(), f"Missing: {js_file}"

    def test_meta_learning_panel_has_class(self, js_dir):
        """Verify meta-learning panel classes are defined."""
        js_file = js_dir / "components" / "meta-learning-panel.js"
        if js_file.exists():
            content = js_file.read_text(encoding="utf-8")
            # Check for class definition or window export (actual class is MetaLearningDashboard)
            assert "MetaLearning" in content, "MetaLearning classes not found in file"


@pytest.mark.dashboard
class TestRedisMonitor:
    """Test Redis Monitor JavaScript components."""

    def test_redis_monitor_js_exists(self, js_dir):
        """Verify redis-monitor.js exists."""
        js_file = js_dir / "components" / "redis-monitor.js"
        assert js_file.exists(), f"Missing: {js_file}"

    def test_redis_monitor_has_class(self, js_dir):
        """Verify Redis monitor classes are defined."""
        js_file = js_dir / "components" / "redis-monitor.js"
        if js_file.exists():
            content = js_file.read_text(encoding="utf-8")
            # Actual class is RedisOperationCounter/RedisOperationLog
            assert "Redis" in content, "Redis classes not found in file"


@pytest.mark.dashboard
class TestPineconeMonitor:
    """Test Pinecone Monitor JavaScript components."""

    def test_pinecone_monitor_js_exists(self, js_dir):
        """Verify pinecone-monitor.js exists."""
        js_file = js_dir / "components" / "pinecone-monitor.js"
        assert js_file.exists(), f"Missing: {js_file}"

    def test_pinecone_monitor_has_class(self, js_dir):
        """Verify Pinecone monitor classes are defined."""
        js_file = js_dir / "components" / "pinecone-monitor.js"
        if js_file.exists():
            content = js_file.read_text(encoding="utf-8")
            # Actual class is PineconeOperationsDashboard
            assert "Pinecone" in content, "Pinecone classes not found in file"


@pytest.mark.dashboard
class TestExecutionFlow:
    """Test Execution Flow JavaScript components."""

    def test_execution_flow_js_exists(self, js_dir):
        """Verify execution-flow.js exists."""
        js_file = js_dir / "components" / "execution-flow.js"
        assert js_file.exists(), f"Missing: {js_file}"

    def test_execution_flow_has_class(self, js_dir):
        """Verify ExecutionFlow class is defined."""
        js_file = js_dir / "components" / "execution-flow.js"
        if js_file.exists():
            content = js_file.read_text(encoding="utf-8")
            # Check for any execution flow related class
            assert "Execution" in content or "Timeline" in content, "Execution flow classes not found"


@pytest.mark.dashboard
class TestMetaLearningController:
    """Test Meta-Learning Controller JavaScript components."""

    def test_controller_js_exists(self, js_dir):
        """Verify meta-learning-controller.js exists."""
        js_file = js_dir / "controllers" / "meta-learning-controller.js"
        assert js_file.exists(), f"Missing: {js_file}"

    def test_controller_has_polling(self, js_dir):
        """Verify controller has polling functionality."""
        js_file = js_dir / "controllers" / "meta-learning-controller.js"
        if js_file.exists():
            content = js_file.read_text(encoding="utf-8")
            assert "poll" in content.lower() or "interval" in content.lower()
