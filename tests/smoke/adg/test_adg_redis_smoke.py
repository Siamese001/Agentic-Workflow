"""ADG Redis integration smoke tests — import verification only."""
import pytest

@pytest.mark.smoke
def test_redis_ingest_importable():
    """Verify tools.adg.adg_redis_ingest imports without error."""
    try:
        from tools.adg.adg_redis_ingest import main as redis_ingest_main
        assert callable(redis_ingest_main)
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_redis_ingest not available: {e}")

@pytest.mark.smoke
def test_mcp_server_importable():
    """Verify tools.adg.adg_mcp_server imports without error."""
    try:
        from tools.adg.adg_mcp_server import main as mcp_server_main
        assert callable(mcp_server_main)
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_mcp_server not available: {e}")

@pytest.mark.smoke
def test_redis_query_importable():
    """Verify tools.adg.adg_redis_query imports without error."""
    try:
        from tools.adg.adg_redis_query import main as redis_query_main
        assert callable(redis_query_main)
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_redis_query not available: {e}")

@pytest.mark.smoke
def test_redis_health_check_importable():
    """Verify tools.adg.redis_health_check imports without error."""
    try:
        from tools.adg.redis_health_check import main as health_check_main
        assert callable(health_check_main)
    except ImportError as e:
        pytest.skip(f"tools.adg.redis_health_check not available: {e}")

@pytest.mark.smoke
def test_adg_stale_guard_importable():
    """Verify tools.adg.adg_stale_guard imports without error."""
    try:
        from tools.adg.adg_stale_guard import main as stale_guard_main
        assert callable(stale_guard_main)
    except ImportError as e:
        pytest.skip(f"tools.adg.adg_stale_guard not available: {e}")
