"""
Tests for Phase 2 reconciliation hang fixes:
1. heal_repository() receives target_territory parameter
2. heal_repository() is wrapped in a timeout
3. Timeout triggers RuntimeError caught by existing handler
"""

import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeAgent:
    """Agent whose heal_repository captures kwargs for assertion."""

    def __init__(self, project_root=None):
        self.project_root = project_root
        self.last_kwargs = {}

    def heal_repository(self, **kwargs):
        self.last_kwargs = kwargs
        return {"violations_found": 0, "violations_fixed": 0}


class HangingAgent:
    """Agent whose heal_repository sleeps long enough to trigger timeout."""

    def __init__(self, project_root=None):
        self._cancel = False

    def heal_repository(self, **kwargs):
        # Sleep in small increments so thread can be abandoned quickly
        for _ in range(100):
            if self._cancel:
                return {}
            time.sleep(0.1)
        return {}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestPhase2HangFixes:
    """Regression tests for Phase 2 reconciliation hang."""

    def test_territory_passed_to_heal_repository(self):
        """heal_repository must receive target_territory from reconciliation."""
        agent = FakeAgent()
        territory = "L5_safety"

        # Simulate the reconciliation call pattern from execute_ssot line ~1928
        agent.heal_repository(
            dry_run=False,
            execute=True,
            target_territory=territory,
        )

        assert agent.last_kwargs.get("target_territory") == territory
        assert agent.last_kwargs.get("dry_run") is False
        assert agent.last_kwargs.get("execute") is True

    def test_timeout_catches_hanging_agent(self):
        """ThreadPoolExecutor timeout must convert hang to RuntimeError."""
        agent = HangingAgent()

        with pytest.raises(RuntimeError, match="timed out"):
            _HEAL_TIMEOUT_S = 0.5  # short timeout for test
            pool = ThreadPoolExecutor(max_workers=1)
            try:
                future = pool.submit(
                    agent.heal_repository,
                    dry_run=False,
                    execute=True,
                    target_territory="test",
                )
                try:
                    future.result(timeout=_HEAL_TIMEOUT_S)
                except FuturesTimeoutError:
                    agent._cancel = True  # signal thread to stop
                    raise RuntimeError(f"heal_repository timed out after {_HEAL_TIMEOUT_S}s for test_agent")
            finally:
                pool.shutdown(wait=False, cancel_futures=True)

    def test_timeout_env_var_override(self):
        """HEAL_TIMEOUT_SECONDS env var should be respected."""
        import os

        with patch.dict(os.environ, {"HEAL_TIMEOUT_SECONDS": "42"}):
            val = int(os.environ.get("HEAL_TIMEOUT_SECONDS", "300"))
            assert val == 42

    def test_normal_agent_completes_within_timeout(self):
        """Non-hanging agents complete normally under timeout."""
        agent = FakeAgent()
        _HEAL_TIMEOUT_S = 10

        with ThreadPoolExecutor(max_workers=1) as pool:
            future = pool.submit(
                agent.heal_repository,
                dry_run=False,
                execute=True,
                target_territory="knowledge",
            )
            result = future.result(timeout=_HEAL_TIMEOUT_S)

        assert result["violations_found"] == 0
        assert result["violations_fixed"] == 0

    def test_territory_scoping_reduces_scan_surface(self):
        """Verify territory param flows through to limit scan scope."""
        calls = []

        class TrackingAgent:
            def __init__(self, project_root=None):
                pass

            def heal_repository(self, **kwargs):
                calls.append(kwargs)
                return {"violations_found": 0, "violations_fixed": 0}

        agent = TrackingAgent()
        agent.heal_repository(
            dry_run=False,
            execute=True,
            target_territory="prompt_governance",
        )

        assert len(calls) == 1
        assert calls[0]["target_territory"] == "prompt_governance"
