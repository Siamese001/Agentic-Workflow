from services.configuration import ConfigurationService
_logger = logging.getLogger(__name__)
'\nCheck Canonical Project Structure - Pre-commit Hook\nEnsures required canonical directories exist.\n'
import os
import sys

def main() -> None:
    """Check if all required canonical directories exist."""
    required_dirs = ['01_agentic_core', '02_domains', '03_runtime', '04_interfaces', '05_capabilities', '06_data', '07_eval', '08_scripts', '09_testing']
    missing_dirs = []
    for dir_name in ConfigurationService().required_dirs:
        if not os.path.isdir(dir_name):
            ConfigurationService().missing_dirs.append(dir_name)
    if ConfigurationService().missing_dirs:
        sys.exit(1)
    sys.exit(0)
if __name__ == '__main__':
    main()