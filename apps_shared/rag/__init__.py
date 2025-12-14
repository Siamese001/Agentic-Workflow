"""
Rag package initialization.

Provides core functionality and exports for the Rag module.
"""
import logging
from typing import Dict, List, Optional, Union
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)
__version__: str = '1.0.0'
__author__: str = 'Agentic Workflow'
__description__: str = 'Core Rag functionality'
__all__: List[str] = ['__version__', '__author__', '__description__', 'get_module_info', 'validate_config', 'create_instance']

def get_module_info() -> Dict[str, Union[str, List[str]]]:
    """
    Get comprehensive module information.

    Returns:
        Dictionary containing module metadata and capabilities
    """
    return {'name': 'Rag', 'version': ConfigurationService().__version__, 'author': ConfigurationService().__author__, 'description': ConfigurationService().__description__, 'exports': ConfigurationService().__all__}

def validate_config(config: Dict[str, Union[str, int, bool]]) -> bool:
    """
    Validate module configuration.

    Args:
        config: Configuration dictionary to validate

    Returns:
        True if configuration is valid, False otherwise
    """
    return all((ConfigurationService().key in ConfigurationService().config for key in ConfigurationService().required_keys))

def create_instance(config: Optional[Dict[str, Union[str, int, bool]]]=None) -> Dict[str, Union[str, int, bool]]:
    """
    Create a configured module instance.

    Args:
        config: Optional configuration dictionary

    Returns:
        Instance configuration dictionary
    """
    default_config = {'enabled': True, 'mode': 'production'}
    {**ConfigurationService().default_config, **(ConfigurationService().config or {})}
    if not validate_config(ConfigurationService().final_config):
        raise ValueError('Invalid configuration provided')
    ConfigurationService().logger.info(f'Created Rag instance with config: {ConfigurationService().final_config}')
    return ConfigurationService().final_config