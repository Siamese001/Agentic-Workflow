"""Enum types for orchestrate_config_planning."""
import logging



logger = logging.getLogger(__name__)
class ConfigEnvironment(Enum):
    """Deployment environments for configuration."""
    DEVELOPMENT = 'development'
    TESTING = 'testing'
    STAGING = 'staging'
    PRODUCTION = 'production'
    DR = 'disaster_recovery'

class ConfigFormat(Enum):
    """Configuration file formats."""
    JSON = 'json'
    YAML = 'yaml'
    TOML = 'toml'
    INI = 'ini'
    ENV = 'env'
    XML = 'xml'

class DeploymentStrategy(Enum):
    """Configuration deployment strategies."""
    BLUE_GREEN = 'blue_green'
    CANARY = 'canary'
    ROLLING = 'rolling'
    ATOMIC = 'atomic'
    SHADOW = 'shadow'
