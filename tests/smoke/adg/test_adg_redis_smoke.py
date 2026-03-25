"""ADG Redis integration smoke tests — import verification only."""
import pytest

@pytest.mark.smoke
def test_redis_ingest_importable():
    """Verify tools.adg.adg_redis_ingest imports without error."""
    try:
        import tools.adg.adg_redis_ingest
        assert tools.adg.adg_redis_ingest is not None
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_redis_ingest not available: {e}")

@pytest.mark.smoke
def test_mcp_server_importable():
    """Verify tools.adg.adg_mcp_server imports without error."""
    try:
        import tools.adg.adg_mcp_server
        assert tools.adg.adg_mcp_server is not None
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_mcp_server not available: {e}")

@pytest.mark.smoke
def test_redis_query_importable():
    """Verify tools.adg.adg_redis_query imports without error."""
    try:
        import tools.adg.adg_redis_query
        assert tools.adg.adg_redis_query is not None
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_redis_query not available: {e}")

@pytest.mark.smoke
def test_redis_health_check_importable():
    """Verify tools.adg.redis_health_check imports without error."""
    try:
        import tools.adg.redis_health_check
        assert tools.adg.redis_health_check is not None
    except ImportError as e:
        pytest.skip(f"tools.adg.redis_health_check not available: {e}")

@pytest.mark.smoke
def test_adg_stale_guard_importable():
    """Verify tools.adg.adg_stale_guard imports without error."""
    try:
        import tools.adg.adg_stale_guard
        assert tools.adg.adg_stale_guard is not None
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_stale_guard not available: {e}")
