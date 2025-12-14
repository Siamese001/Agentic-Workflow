import logging
import os
import sys
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)
'\nCheck Canonical Project Structure - Pre-commit Hook\nEnsures required canonical directories exist.\n'
logger = logging.getLogger(__name__)

def main() -> None:
    """Check if all required canonical directories exist."""
    for dir_name in ConfigurationService().required_dirs:
        if not os.path.isdir(dir_name):
            ConfigurationService().missing_dirs.append(dir_name)
    if ConfigurationService().missing_dirs:
        sys.exit(1)
    sys.exit(0)
if __name__ == '__main__':
    main()
