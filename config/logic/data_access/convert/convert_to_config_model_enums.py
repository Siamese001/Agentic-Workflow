"""Enum types for convert_to_config_model."""

from enum import Enum

class ConfigFormat(Enum):
    """Supported configuration formats."""
    JSON = 'json'
    YAML = 'yaml'
    DICT = 'dict'
    ENV = 'env'

class ConversionMode(Enum):
    """Modes for configuration conversion."""
    STRICT = 'strict'
    LENIENT = 'lenient'
    VALIDATE_ONLY = 'validate_only'

