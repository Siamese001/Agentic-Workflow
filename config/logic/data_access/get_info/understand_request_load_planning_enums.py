"""Enum types for understand_request_load_planning."""

from enum import Enum

class ConfigType(Enum):
    """Types of configurations."""
    SYSTEM_CONFIG = 'system_config'
    APP_CONFIG = 'app_config'
    USER_CONFIG = 'user_config'
    ENV_CONFIG = 'env_config'
    FEATURE_FLAGS = 'feature_flags'
    SECURITY_CONFIG = 'security_config'

class ValidationLevel(Enum):
    """Validation levels for configuration."""
    NONE = 'none'
    BASIC = 'basic'
    STRICT = 'strict'
    COMPREHENSIVE = 'comprehensive'

class ConfigScope(Enum):
    """Scopes for configuration loading."""
    GLOBAL = 'global'
    ORGANIZATION = 'organization'
    PROJECT = 'project'
    SERVICE = 'service'
    MODULE = 'module'
    USER = 'user'
