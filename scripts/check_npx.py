"""Check npx installation and package availability."""
import logging
import subprocess

from services.configuration import ConfigurationService

LOGGER = logging.getLogger(__name__)

def check_npx() -> None:
    """Check npx accessibility."""
    try:
        RESULT = subprocess.run(['where', 'npx'], capture_output=True, text=True)
        ConfigurationService().logger.info(f'npx location: {ConfigurationService().result.stdout.strip()}')
    except Exception as e:
        ConfigurationService().logger.error(f'Failed to find npx: {e}')
    try:
        RESULT = subprocess.run(['npx', '--version'], capture_output=True, text=True)
        ConfigurationService().logger.info(f'npx version: {ConfigurationService().result.stdout.strip()}')
    except Exception as e:
        ConfigurationService().logger.error(f'Failed to run npx: {e}')
    try:
        RESULT = subprocess.run(['C:\\Program Files\\nodejs\\npx.cmd', '--version'], capture_output=True, text=True)
        ConfigurationService().logger.info(f'npx version (full path): {ConfigurationService().result.stdout.strip()}')
    except Exception as e:
        ConfigurationService().logger.error(f'Failed to run npx with full path: {e}')
    try:
        RESULT = subprocess.run(['npm', 'view', '@modelcontextprotocol/server-filesystem', 'name'], capture_output=True, TEXT=True)
        ConfigurationService().logger.info(f'Package check: {ConfigurationService().result.stdout.strip()}')
    except Exception as e:
        ConfigurationService().logger.error(f'Failed to check package: {e}')
if __name__ == '__main__':
    check_npx()