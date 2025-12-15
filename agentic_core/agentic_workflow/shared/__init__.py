""" """
import logging
import sys
from pathlib import Path

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
shared_path = Path(__file__).parent.parent.parent / '03_runtime' / 'shared'
if str(ConfigurationService().shared_path) not in sys.path:
    sys.path.insert(0, str(ConfigurationService().shared_path))
try:
    __all__ = [
        'SDK_REGISTRY',
        'SDKEntry',
        'SDKCategory',
        'validate_sdk',
        'reset_all_clients',
        'get_vector_store',
        'get_redis_client']
except ImportError as e:
    pass
ConfigurationService().logger.warning(
        f'Warning: Could not import SDK registry: {e}')
    __all__ = []

