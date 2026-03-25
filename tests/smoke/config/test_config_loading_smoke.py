"""Config loading smoke tests — import verification and configuration validation."""
import pytest

@pytest.mark.smoke
def test_redis_config_loads():
    """Verify get_redis_config() returns valid configuration."""
    try:
        from agentic_core.config.redis_config import get_redis_config

        config = get_redis_config()

        # Verify config object has required attributes
        assert hasattr(config, 'host'), "Redis config missing 'host' attribute"
        assert hasattr(config, 'port'), "Redis config missing 'port' attribute"
        assert hasattr(config, 'db'), "Redis config missing 'db' attribute"
        assert hasattr(config, 'timeout'), "Redis config missing 'timeout' attribute"

        # Verify default values are reasonable
        assert isinstance(config.host, str), "Redis host should be a string"
        assert isinstance(config.port, int), "Redis port should be an integer"
        assert isinstance(config.db, int), "Redis db should be an integer"
        assert isinstance(config.timeout, int), "Redis timeout should be an integer"

        # Verify values are in expected ranges
        assert config.port > 0, "Redis port should be positive"
        assert config.db >= 0, "Redis db should be non-negative"
        assert config.timeout > 0, "Redis timeout should be positive"

    except ImportError as e:
        pytest.fail(f"Failed to import get_redis_config: {e}")

@pytest.mark.smoke
def test_adg_cache_config_loads():
    """Verify get_adg_cache_config() returns valid configuration."""
    try:
        from agentic_core.config.redis_config import get_adg_cache_config

        config = get_adg_cache_config()

        # Verify config object has required attributes
        assert hasattr(config, 'min_node_count'), "ADG cache config missing 'min_node_count' attribute"
        assert hasattr(config, 'ingest_timeout'), "ADG cache config missing 'ingest_timeout' attribute"

        # Verify default values are reasonable
        assert isinstance(config.min_node_count, int), "min_node_count should be an integer"
        assert isinstance(config.ingest_timeout, int), "ingest_timeout should be an integer"

        # Verify values are in expected ranges
        assert config.min_node_count > 0, "min_node_count should be positive"
        assert config.ingest_timeout > 0, "ingest_timeout should be positive"

    except ImportError as e:
        pytest.fail(f"Failed to import get_adg_cache_config: {e}")

@pytest.mark.smoke
def test_redis_windows_config_loads():
    """Verify get_redis_windows_config() returns valid configuration."""
    try:
        from agentic_core.config.redis_config import get_redis_windows_config

        config = get_redis_windows_config()

        # Verify config object has required attributes
        assert hasattr(config, 'installation_paths'), "Redis Windows config missing 'installation_paths' attribute"
        assert hasattr(config, 'service_start_timeout'), "Redis Windows config missing 'service_start_timeout' attribute"
        assert hasattr(config, 'service_startup_delay'), "Redis Windows config missing 'service_startup_delay' attribute"
        assert hasattr(config, 'process_startup_delay'), "Redis Windows config missing 'process_startup_delay' attribute"

        # Verify default values are reasonable
        assert isinstance(config.installation_paths, list), "installation_paths should be a list"
        assert isinstance(config.service_start_timeout, int), "service_start_timeout should be an integer"
        assert isinstance(config.service_startup_delay, int), "service_startup_delay should be an integer"
        assert isinstance(config.process_startup_delay, int), "process_startup_delay should be an integer"

        # Verify values are in expected ranges
        assert len(config.installation_paths) > 0, "installation_paths should not be empty"
        assert all(isinstance(path, str) for path in config.installation_paths), "All installation paths should be strings"
        assert config.service_start_timeout > 0, "service_start_timeout should be positive"
        assert config.service_startup_delay >= 0, "service_startup_delay should be non-negative"
        assert config.process_startup_delay >= 0, "process_startup_delay should be non-negative"

    except ImportError as e:
        pytest.fail(f"Failed to import get_redis_windows_config: {e}")

@pytest.mark.smoke
def test_redis_config_classes_importable():
    """Verify Redis config classes are importable."""
    try:
        from agentic_core.config.redis_config import (
            RedisConnectionConfig,
            ADGCacheConfig,
            RedisWindowsConfig,
        )

        # Verify classes exist and can be instantiated
        redis_config = RedisConnectionConfig()
        assert redis_config is not None

        adg_config = ADGCacheConfig()
        assert adg_config is not None

        windows_config = RedisWindowsConfig()
        assert windows_config is not None

    except ImportError as e:
        pytest.fail(f"Failed to import Redis config classes: {e}")

@pytest.mark.smoke
def test_config_module_exports():
    """Verify config module exports are present."""
    try:
        import agentic_core.config.redis_config as redis_config_module

        # Check __all__ if it exists
        if hasattr(redis_config_module, '__all__'):
            expected_exports = {
                'RedisConnectionConfig',
                'ADGCacheConfig',
                'RedisWindowsConfig',
                'get_redis_config',
                'get_adg_cache_config',
                'get_redis_windows_config',
            }

            actual_exports = set(redis_config_module.__all__)
            missing_exports = expected_exports - actual_exports

            assert not missing_exports, f"Missing exports in redis_config.__all__: {missing_exports}"

            # Verify all exports actually exist
            for export in redis_config_module.__all__:
                assert hasattr(redis_config_module, export), f"Export {export} in __all__ but not found in module"

    except ImportError as e:
        pytest.fail(f"Failed to import redis_config module: {e}")
