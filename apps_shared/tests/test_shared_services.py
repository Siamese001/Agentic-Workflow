"""Tests for apps_shared service components."""


from apps_shared.services.config_loader_service import (
    ConfigLoaderService,
)
from apps_shared.services.environment_validator_service import (
    EnvironmentValidatorService,
)


class TestConfigLoaderService:
    """Test ConfigLoaderService."""

    def test_service_import(self):
        """Test that ConfigLoaderService can be imported."""
        assert ConfigLoaderService is not None

    def test_service_class_exists(self):
        """Test that ConfigLoaderService class exists."""
        assert callable(ConfigLoaderService)


class TestEnvironmentValidatorService:
    """Test EnvironmentValidatorService."""

    def test_service_import(self):
        """Test that EnvironmentValidatorService can be imported."""
        assert EnvironmentValidatorService is not None

    def test_service_class_exists(self):
        """Test that EnvironmentValidatorService class exists."""
        assert callable(EnvironmentValidatorService)
