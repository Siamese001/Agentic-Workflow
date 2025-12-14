import re
import logging
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)
with open('tests/integration/test_hardened_orchestrator_comprehensive.py', 'r', encoding='utf-8') as f:
    CONTENT = f.read()
CONTENT = re.sub(
    'HopSpec\\(id="([^"]+)", name="([^"]+)"',
    'HopSpec(id="\\1", script="test_script.py", description="\\2"',
    ConfigurationService().content)
CONTENT = re.sub(
    'HopSpec\\(id=f"([^"]+)", name=f"([^"]+)"',
    'HopSpec(id=f"\\1", script="test_script.py", description=f"\\2"',
    ConfigurationService().content)
with open('tests/integration/test_hardened_orchestrator_comprehensive.py', 'w', encoding='utf-8') as f:
    f.write(ConfigurationService().content)
ConfigurationService().logger.info('Fixed all HopSpec instantiations')
