"""Test SovereignHealingEngineEnforcer functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestSovereignHealingEngineEnforcer:
    """Test SovereignHealingEngineEnforcer functionality."""

    def test_sovereign_healing_engine_enforcer_imports(self):
        """Test sovereign_healing_engine_enforcer module imports."""
        from agentic_core import sovereign_healing_engine_enforcer

        assert sovereign_healing_engine_enforcer is not None

    def test_sovereign_healing_engine_enforcer_class(self):
        """Test SovereignHealingEngineEnforcer class exists."""
        from agentic_core import SovereignHealingEngineEnforcer

        assert SovereignHealingEngineEnforcer is not None

    def test_sovereign_healing_engine_enforcer_callable(self):
        """Test sovereign_healing_engine_enforcer functions are callable."""
        from agentic_core import validate_sovereign_healing_engine_enforcer

        assert callable(validate_sovereign_healing_engine_enforcer)

    def test_create_healing_commit_wraps_exception_as_runtime_error(self):
        """_create_healing_commit must wrap inner errors as RuntimeError(...) from e."""
        import asyncio
        from unittest.mock import AsyncMock

        from agentic_core.L5_safety.enforcement.sovereign_healing_engine_enforcer import (
            SovereignHealingEngine,
        )

        engine = SovereignHealingEngine.__new__(SovereignHealingEngine)
        engine.applied_fixes = 1
        mock_git = AsyncMock()
        mock_git.add_and_commit.side_effect = ConnectionError("git unreachable")
        engine.git_client = mock_git

        with pytest.raises(RuntimeError, match="Failed to create healing commit") as exc_info:
            asyncio.run(engine._create_healing_commit(["file.py"]))
        assert isinstance(exc_info.value.__cause__, ConnectionError)
