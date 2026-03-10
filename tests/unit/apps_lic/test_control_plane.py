"""3.9: Baseline tests for ControlPlane (3.6)."""

from __future__ import annotations

from apps_lic.engines.control_plane import ControlPlane, PolicyAction


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestControlPlaneInit:
    def test_instantiates_without_error(self):
        cp = ControlPlane()
        assert cp is not None

    def test_stats_returns_dict(self):
        cp = ControlPlane()
        stats = cp.get_stats()
        assert "total_decisions" in stats
        assert "total_blocks" in stats


class TestControlPlaneEvaluateInput:
    def test_safe_content_returns_allow(self):
        cp = ControlPlane()
        decision = cp.evaluate_input("Hello, I would like a software engineering resume.")
        assert decision.is_safe is True
        assert decision.action in (PolicyAction.ALLOW, PolicyAction.WARN)

    def test_pii_content_returns_block(self):
        cp = ControlPlane()
        decision = cp.evaluate_input("My social security number is 123-45-6789")
        assert decision.action == PolicyAction.BLOCK
        assert decision.is_safe is False
        assert len(decision.errors) > 0

    def test_pii_increments_block_count(self):
        cp = ControlPlane()
        cp.evaluate_input("credit card 1234-5678-9012-3456")
        stats = cp.get_stats()
        assert stats["total_blocks"] >= 1
        assert stats["total_decisions"] >= 1

    def test_evaluate_output_safe_content(self):
        cp = ControlPlane()
        decision = cp.evaluate_output("Here is a great resume for software engineering.")
        assert decision.is_safe is True
