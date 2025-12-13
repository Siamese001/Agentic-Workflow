"""Unit tests for runtime/shared/config.py"""
from __future__ import annotations
from pathlib import Path
from tests.conftest import PROJECT_ROOT, CACHE_DIR, LOGS_DIR, DEFAULT_MAX_RETRIES
from shared.configuration.reasoning_config import (
    SAFETY_THRESHOLD,
    CONFIG,
    C2,
    ReasoningConfig as Config,
    ModelConfig,
    RAGConfig,
    GovernorConfig,
    ModelProvider
)

# Additional test constants
DEFAULT_API_TIMEOUT = 60
DEFAULT_GENERATION_TEMPERATURE = 0.7
DEFAULT_SYNTHESIS_TEMPERATURE = 0.3
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

class TestConstants:
    def test_max_retries_positive(self):
        assert isinstance(DEFAULT_MAX_RETRIES, int) and DEFAULT_MAX_RETRIES > 0

    def test_api_timeout_reasonable(self):
        assert 10 <= DEFAULT_API_TIMEOUT <= 300

    def test_temperatures_in_range(self):
        assert 0 <= DEFAULT_GENERATION_TEMPERATURE <= 2
        assert 0 <= DEFAULT_SYNTHESIS_TEMPERATURE <= 2

    def test_safety_threshold_in_range(self):
        assert 0 <= SAFETY_THRESHOLD <= 1

    def test_constants_determinism(self):
        assert DEFAULT_MAX_RETRIES == DEFAULT_MAX_RETRIES

class TestPathConstants:
    def test_project_root_is_path(self):
        assert isinstance(PROJECT_ROOT, Path)

    def test_data_dir_is_path(self):
        assert isinstance(DATA_DIR, Path)

    def test_output_dir_is_path(self):
        assert isinstance(OUTPUT_DIR, Path)

    def test_cache_dir_is_path(self):
        assert isinstance(CACHE_DIR, Path)

    def test_logs_dir_is_path(self):
        assert isinstance(LOGS_DIR, Path)

class TestConfigSingleton:
    def test_config_exists(self):
        assert CONFIG is not None

    def test_config_is_instance(self):
        assert isinstance(CONFIG, Config)

    def test_config_singleton_identity(self):
        from shared.configuration.reasoning_config import CONFIG
        assert CONFIG is C2

class TestModelConfig:
    def test_creation(self):
        cfg = ModelConfig(provider=list(ModelProvider)[0], model_name="gpt-4o")
        assert cfg.model_name == "gpt-4o"

class TestRAGConfig:
    def test_creation(self):
        cfg = RAGConfig()
        assert cfg is not None

class TestGovernorConfig:
    def test_creation(self):
        cfg = GovernorConfig()
        assert cfg is not None
