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
