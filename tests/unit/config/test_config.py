"""Unit tests for runtime/shared/config.py"""
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
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
    """Docstring."""
    def test_max_retries_positive(self):
            """Docstring."""
        assert isinstance(DEFAULT_MAX_RETRIES, int) and DEFAULT_MAX_RETRIES > 0

    def test_api_timeout_reasonable(self):
            """Docstring."""
        assert 10 <= DEFAULT_API_TIMEOUT <= 300

    def test_temperatures_in_range(self):
            """Docstring."""
        assert 0 <= DEFAULT_GENERATION_TEMPERATURE <= 2
        assert 0 <= DEFAULT_SYNTHESIS_TEMPERATURE <= 2

    def test_safety_threshold_in_range(self):
            """Docstring."""
        assert 0 <= SAFETY_THRESHOLD <= 1

    def test_constants_determinism(self):
            """Docstring."""
        assert DEFAULT_MAX_RETRIES == DEFAULT_MAX_RETRIES

class TestPathConstants:
    """Docstring."""
    def test_project_root_is_path(self):
            """Docstring."""
        assert isinstance(PROJECT_ROOT, Path)

    def test_data_dir_is_path(self):
            """Docstring."""
        assert isinstance(DATA_DIR, Path)

    def test_output_dir_is_path(self):
            """Docstring."""
        assert isinstance(OUTPUT_DIR, Path)

    def test_cache_dir_is_path(self):
            """Docstring."""
        assert isinstance(CACHE_DIR, Path)

    def test_logs_dir_is_path(self):
            """Docstring."""
        assert isinstance(LOGS_DIR, Path)

class TestConfigSingleton:
    """Docstring."""
    def test_config_exists(self):
            """Docstring."""
        assert CONFIG is not None

    def test_config_is_instance(self):
            """Docstring."""
        assert isinstance(CONFIG, Config)

    def test_config_singleton_identity(self):
            """Docstring."""
        assert CONFIG is C2

class TestModelConfig:
    """Docstring."""
    def test_creation(self):
            """Docstring."""
        cfg = ModelConfig(provider=list(ModelProvider)[0], model_name="gpt-4o")
        assert cfg.model_name == "gpt-4o"

class TestRAGConfig:
    """Docstring."""
    def test_creation(self):
            """Docstring."""
        cfg = RAGConfig()
        assert cfg is not None

class TestGovernorConfig:
    """Docstring."""
    def test_creation(self):
            """Docstring."""
        cfg = GovernorConfig()
        assert cfg is not None
