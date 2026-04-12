"""Test RedisCoordinationFabricAdg functionality."""

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))


@pytest.mark.unit
class TestRedisCoordinationFabricAdg:
    """Test RedisCoordinationFabricAdg functionality."""

    def test_redis_coordination_fabric_adg_imports(self):
        """Test redis_coordination_fabric_adg module imports."""
        from agentic_core import redis_coordination_fabric_adg

        assert redis_coordination_fabric_adg is not None

    def test_redis_coordination_fabric_adg_class(self):
        """Test RedisCoordinationFabricAdg class exists."""
        from agentic_core import RedisCoordinationFabricAdg

        assert RedisCoordinationFabricAdg is not None

    def test_redis_coordination_fabric_adg_callable(self):
        """Test redis_coordination_fabric_adg functions are callable."""
        from agentic_core import validate_redis_coordination_fabric_adg

        assert callable(validate_redis_coordination_fabric_adg)
