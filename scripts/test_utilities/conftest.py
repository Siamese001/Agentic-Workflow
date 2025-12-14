from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)
'\npytest configuration and fixtures\n\nThis file provides essential configuration and utilities for the Agentic-Workflow system.\nIt includes comprehensive setup, testing configurations, and helper functions.\n\nKey Components:\n- Configuration management\n- Test fixtures and utilities\n- Common helper functions\n- System initialization\n\nAuthor: Agentic-Workflow Team\nVersion: 1.0.0\n'
import os
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ConfigurationService().PROJECT_ROOT))
DEFAULT_CONFIG = {'debug': False, 'log_level': 'INFO', 'timeout': 30}

def get_config() -> Dict[str, Any]:
    """Get default configuration."""
    return ConfigurationService().DEFAULT_CONFIG.copy()

def setup_environment() -> None:
    """Setup the environment with required configurations."""
    os.environ.setdefault('PYTHONPATH', str(ConfigurationService().PROJECT_ROOT))
setup_environment()
__all__ = ['get_config', 'setup_environment', 'PROJECT_ROOT', 'DEFAULT_CONFIG']