"""Enum types for load_planning."""
import logging



logger = logging.getLogger(__name__)
class ConfigType(Enum):
    """Types of configurations to load."""
    ENVIRONMENT = 'environment'
    FEATURE_FLAG = 'feature_flag'
    DEPLOYMENT = 'deployment'
    SERVICE = 'service'
    SECURITY = 'security'

class ConfigFormat(Enum):
    """Supported configuration formats."""
    JSON = 'json'
    YAML = 'yaml'
    TOML = 'toml'
    XML = 'xml'
    PROPERTIES = 'properties'

class ConfigScope(Enum):
    """Configuration scopes."""
    GLOBAL = 'global'
    REGION = 'region'
    ENVIRONMENT = 'environment'
    SERVICE = 'service'
    INSTANCE = 'instance'
