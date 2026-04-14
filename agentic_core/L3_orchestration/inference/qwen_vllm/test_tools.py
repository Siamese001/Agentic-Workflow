"""Tests for Qwen vLLM tools."""

from agentic_core.L3_orchestration.inference.qwen_vllm.tools import (
    GPUMemoryInfo,
    GPUMemoryMonitor,
    GPURecommendation,
)


class TestGPUMemoryInfo:
    """Test GPUMemoryInfo dataclass."""

    def test_stats_creation(self):
        """Test creating GPU memory stats."""
        stats = GPUMemoryInfo(
            total_mb=16384,
            used_mb=8192,
            free_mb=8192,
            utilization_percent=50.0,
            timestamp=1234567890.0,
        )
        assert stats.total_mb == 16384
        assert stats.used_mb == 8192
        assert stats.free_mb == 8192
        assert stats.utilization_percent == 50.0
        assert stats.timestamp == 1234567890.0


class TestGPURecommendation:
    """Test GPURecommendation dataclass."""

    def test_recommendation_creation(self):
        """Test creating GPU recommendation."""
        rec = GPURecommendation(
            batch_size=4,
            max_concurrent=8,
            should_throttle=False,
            should_cooldown=False,
            free_mb=8192,
        )
        assert rec.batch_size == 4
        assert rec.max_concurrent == 8
        assert rec.should_throttle is False
        assert rec.should_cooldown is False
        assert rec.free_mb == 8192


class TestGPUMemoryMonitor:
    """Test GPUMemoryMonitor with mocked dependencies."""

    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = GPUMemoryMonitor()
        assert monitor is not None
        assert monitor.check_interval_sec == 5.0
        assert monitor.min_batch_size == 1
        assert monitor.max_batch_size == 16

    def test_monitor_initialization_with_params(self):
        """Test monitor initialization with custom parameters."""
        monitor = GPUMemoryMonitor(
            check_interval_sec=10.0,
            min_batch_size=2,
            max_batch_size=32,
        )
        assert monitor.check_interval_sec == 10.0
        assert monitor.min_batch_size == 2
        assert monitor.max_batch_size == 32
