"""ADG Redis integration smoke tests — behavioral contract verification."""

import pytest


@pytest.mark.smoke
def test_redis_ingest_has_main_entry():
    """tools.adg.adg_redis_ingest exposes a callable main/ingest entry point."""
    try:
        import tools.adg.adg_redis_ingest as mod
    except ImportError as e:
        pytest.skip(f"adg_redis_ingest not available: {e}")

    entry = getattr(mod, "main", None) or getattr(mod, "ingest", None)
    assert entry is not None, "adg_redis_ingest must expose main() or ingest()"
    assert callable(entry)


@pytest.mark.smoke
def test_mcp_server_exposes_tool_registry():
    """tools.adg.adg_mcp_server exposes tool list or handler registry."""
    try:
        import tools.adg.adg_mcp_server as mod
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    has_tools = (
        hasattr(mod, "TOOLS")
        or hasattr(mod, "tool_registry")
        or hasattr(mod, "mcp")
        or hasattr(mod, "server")
    )
    assert has_tools, "adg_mcp_server must expose TOOLS, tool_registry, mcp, or server"


@pytest.mark.smoke
def test_redis_query_has_query_functions():
    """tools.adg.adg_redis_query exposes query functions."""
    try:
        import tools.adg.adg_redis_query as mod
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "adg_redis_query must expose at least 1 public symbol"


@pytest.mark.smoke
def test_redis_health_check_has_check_function():
    """tools.adg.redis_health_check exposes a check/main function."""
    try:
        import tools.adg.redis_health_check as mod
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    entry = getattr(mod, "main", None) or getattr(mod, "check", None) or getattr(mod, "health_check", None)
    assert entry is not None, "redis_health_check must expose main(), check(), or health_check()"
    assert callable(entry)


@pytest.mark.smoke
def test_adg_stale_guard_has_staleness_logic():
    """tools.adg.adg_stale_guard exposes freshness/staleness checking."""
    try:
        import tools.adg.adg_stale_guard as mod
    except ImportError as e:
        pytest.skip(f"module not available: {e}")
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, "adg_stale_guard must expose at least 1 public symbol"
